import frappe
from frappe.utils import today, add_months

def prompt_investor_update():
	"""
	Scheduled task to alert founders to prepare investor updates.
	"""
	companies = frappe.get_all("Company", fields=["name"])
	for company in companies:
		# Check if an update for this month already exists
		exists = frappe.db.count("Investor Update", {
			"company": company.name,
			"period_end": [">=", add_months(today(), -1)]
		})
		
		if not exists:
			create_update_draft(company.name)

def create_update_draft(company_name):
	"""
	Auto-draft an investor update using live metrics.
	"""
	runway = frappe.get_doc("Runway Model", {"company": company_name}) if frappe.db.exists("Runway Model", {"company": company_name}) else None
	metrics = frappe.get_doc("Unit Economics", {"company": company_name}) if frappe.db.exists("Unit Economics", {"company": company_name}) else None
	
	update_text = f"## Monthly Update for {company_name}\n\n"
	
	if runway:
		update_text += f"- **Cash Balance:** {runway.cash_balance}\n"
		update_text += f"- **Monthly Burn:** {runway.base_burn}\n"
		update_text += f"- **Runway:** {runway.runway_base} months\n\n"
	
	if metrics:
		update_text += f"- **ARPU:** {metrics.arpu}\n"
		update_text += f"- **LTV/CAC:** {metrics.ltv / metrics.cac if metrics.cac else 'N/A'}\n\n"
		
	update_text += "### Key Highlights\n- Item 1\n- Item 2\n"
	
	doc = frappe.new_doc("Investor Update")
	doc.company = company_name
	doc.period_start = add_months(today(), -1)
	doc.period_end = today()
	doc.update_text = update_text
	doc.status = "Draft"
	doc.save(ignore_permissions=True)
	
	# Notify Founder
	frappe.publish_realtime("investor_update_ready", {"company": company_name}, user="Administrator")

def on_opportunity_stage_change(doc, method=None):
	"""
	Doc event: triggered when a Fundraising Opportunity stage changes.
	Fires automated actions based on the new stage.
	"""
	if doc.stage == "Closed Won":
		frappe.publish_realtime("deal_closed_won", {
			"investor": doc.investor,
			"amount": doc.amount,
			"company": doc.company
		})
	elif doc.stage == "Term Sheet":
		frappe.publish_realtime("term_sheet_received", {
			"opportunity": doc.name,
			"company": doc.company
		})
	elif doc.stage == "Due Diligence":
		frappe.publish_realtime("due_diligence_started", {
			"opportunity": doc.name,
			"investor": doc.investor
		})
