import frappe
from frappe.utils import add_months, getdate, today, flt


def recompute_vesting_schedules():
	"""
	Scheduled task to update vesting status.
	"""
	grants = frappe.get_all("ESOP Grant", fields=["name"])
	for g in grants:
		calculate_vesting_schedule(g.name)

def on_equity_transaction(doc, method=None):
	"""
	Doc event: recompute shareholder ownership when an equity transaction is saved.
	"""
	recompute_shareholder_ownership(doc.company)

def on_esop_grant_save(doc, method=None):
	"""
	Doc event: generate vesting schedule on ESOP Grant save if not already generated.
	"""
	if not doc.vesting_schedule:
		calculate_vesting_schedule(doc.name)

def recompute_shareholder_ownership(company):
	"""
	Recompute and save ownership percent for all shareholders of a company.
	"""
	shareholders = frappe.get_all("Shareholder", filters={"company": company}, fields=["name"])

	# Aggregate all equity transactions
	transaction_sums = {}
	for sh in shareholders:
		quantity = frappe.db.sql("""
			SELECT
				SUM(CASE WHEN transaction_type IN ('Issuance','Transfer') THEN quantity ELSE 0 END) -
				SUM(CASE WHEN transaction_type IN ('Buyback','Cancellation') THEN quantity ELSE 0 END)
				AS net_quantity
			FROM `tabEquity Transaction`
			WHERE shareholder = %s AND company = %s
		""", (sh.name, company), as_dict=True)
		transaction_sums[sh.name] = flt(quantity[0].net_quantity) if quantity and quantity[0].net_quantity else 0

	total_shares = sum(transaction_sums.values())

	for sh_name, net_qty in transaction_sums.items():
		frappe.db.set_value("Shareholder", sh_name, {
			"total_shares": net_qty,
			"ownership_percent": round(net_qty / total_shares * 100, 4) if total_shares else 0
		})


def calculate_vesting_schedule(grant_name):
	"""
	Generate or update vesting schedule based on grant terms.
	"""
	doc = frappe.get_doc("ESOP Grant", grant_name)
	if doc.vesting_schedule:
		# Update existing: mark 'Pending' as 'Vested' if date passed
		for item in doc.vesting_schedule:
			if item.status == "Pending" and getdate(item.vesting_date) <= getdate(today()):
				item.status = "Vested"
	else:
		# Generate new schedule
		# Simplification: Monthly linear vesting after cliff
		total_qty = doc.quantity
		cliff_months = doc.cliff_period_months or 0
		total_months = doc.vesting_period_months or 48
		
		start_date = doc.vesting_start_date or doc.grant_date
		
		# 1. Cliff Vesting (cumulative)
		cliff_date = add_months(start_date, cliff_months)
		cliff_qty = (total_qty / total_months) * cliff_months if total_months > 0 else total_qty
		
		doc.append("vesting_schedule", {
			"vesting_date": cliff_date,
			"quantity": cliff_qty,
			"status": "Vested" if getdate(cliff_date) <= getdate(today()) else "Pending"
		})
		
		# 2. Monthly Vesting for the rest
		remaining_qty = total_qty - cliff_qty
		remaining_months = total_months - cliff_months
		if remaining_months > 0:
			monthly_qty = remaining_qty / remaining_months
			for i in range(1, remaining_months + 1):
				v_date = add_months(cliff_date, i)
				doc.append("vesting_schedule", {
					"vesting_date": v_date,
					"quantity": monthly_qty,
					"status": "Vested" if getdate(v_date) <= getdate(today()) else "Pending"
				})
	
	doc.save()
