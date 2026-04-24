import frappe
from frappe.utils import flt, now_datetime, get_last_day, add_months

def update_all_runway_models():
	"""
	Scheduled task to update runway for all companies.
	"""
	companies = frappe.get_all("Company", fields=["name"])
	for company in companies:
		update_runway_model(company.name)

def update_runway_model(company_name):
	"""
	Calculate burn and runway based on GL entries.
	"""
	# 1. Get Cash Balance
	# In ERPNext, cash is usually in accounts with account_type="Cash" or "Bank"
	cash_accounts = frappe.get_all("Account", 
		filters={"company": company_name, "account_type": ["in", ["Cash", "Bank"]]},
		fields=["name"]
	)
	
	total_cash = 0
	for acc in cash_accounts:
		balance = frappe.db.get_value("GL Entry", 
			{"account": acc.name, "company": company_name}, 
			"sum(debit) - sum(credit)"
		)
		total_cash += flt(balance)

	# 2. Calculate Burn Rate (avg of last 3 months)
	# Simplification: Burn = Total Expenses - Total Income (negative means cash outflow)
	# Usually burn is calculated from operating cash flow
	expenses = frappe.db.get_value("GL Entry", 
		{
			"company": company_name, 
			"posting_date": [">=", add_months(now_datetime(), -3)],
			"is_cancelled": 0
		},
		"sum(debit) - sum(credit)"
	) # This is a very rough proxy

	monthly_burn = flt(expenses) / 3.0
	if monthly_burn <= 0:
		monthly_burn = 1 # Avoid division by zero, though negative burn means profit
	
	runway_base = total_cash / monthly_burn
	
	# Scenarios
	# Optimistic: 25% efficiency gain (burn * 0.75)
	# Pessimistic: 30% cost overrun (burn * 1.3)
	runway_opt = total_cash / (monthly_burn * 0.75) if monthly_burn > 0 else 99
	runway_pess = total_cash / (monthly_burn * 1.3) if monthly_burn > 0 else 0

	# Update Doc
	runway_doc_name = frappe.db.get_value("Runway Model", {"company": company_name})
	if runway_doc_name:
		doc = frappe.get_doc("Runway Model", runway_doc_name)
	else:
		doc = frappe.new_doc("Runway Model")
		doc.company = company_name

	doc.cash_balance = total_cash
	doc.base_burn = monthly_burn
	doc.runway_base = runway_base
	doc.runway_optimistic = runway_opt
	doc.runway_pessimistic = runway_pess
	doc.last_updated = frappe.utils.now()
	doc.save(ignore_permissions=True)

def compute_unit_economics():
	"""
	Scheduled task to update unit economics.
	"""
	# ARPU and CAC are often manual or pulled from CRM/Marketing modules
	# Here we just compute LTV and Payback based on existing data
	docs = frappe.get_all("Unit Economics", fields=["name"])
	for d in docs:
		doc = frappe.get_doc("Unit Economics", d.name)
		if doc.arpu and doc.churn_rate:
			# LTV = ARPU / Churn (Simplification)
			doc.ltv = doc.arpu / (doc.churn_rate / 100.0)
		
		if doc.cac and doc.arpu:
			# Payback = CAC / ARPU (Simplification)
			doc.payback_period = doc.cac / doc.arpu
		
		doc.save()
