import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_pipeline_summary(company=None):
	"""Get fundraising pipeline summary grouped by stage."""
	filters = {}
	if company:
		filters["company"] = company

	stages = ["Intro", "Meeting", "Due Diligence", "Term Sheet", "Closing", "Closed Won", "Passed"]
	pipeline = {}

	for stage in stages:
		filters["stage"] = stage
		opportunities = frappe.get_all("Fundraising Opportunity",
			filters=filters,
			fields=["name", "investor", "amount", "probability", "close_date"]
		)
		weighted_amount = sum(flt(o.amount) * flt(o.probability) / 100.0 for o in opportunities)
		pipeline[stage] = {
			"count": len(opportunities),
			"total_amount": sum(flt(o.amount) for o in opportunities),
			"weighted_amount": weighted_amount,
			"opportunities": opportunities
		}

	return pipeline

@frappe.whitelist()
def move_opportunity(opportunity_name, new_stage):
	"""Move an opportunity to a new stage."""
	valid_stages = ["Intro", "Meeting", "Due Diligence", "Term Sheet", "Closing", "Closed Won", "Passed"]
	if new_stage not in valid_stages:
		frappe.throw(f"Invalid stage: {new_stage}")

	doc = frappe.get_doc("Fundraising Opportunity", opportunity_name)
	old_stage = doc.stage
	doc.stage = new_stage
	doc.save()

	# Trigger automated actions based on new stage
	_trigger_stage_actions(doc, old_stage, new_stage)

	frappe.db.commit()
	return {"status": "success", "opportunity": opportunity_name, "stage": new_stage}

def _trigger_stage_actions(opportunity_doc, old_stage, new_stage):
	"""Trigger automated actions when a deal moves stages."""
	if new_stage == "Closed Won":
		# Update cap table signals
		frappe.publish_realtime("deal_closed_won", {
			"investor": opportunity_doc.investor,
			"amount": opportunity_doc.amount,
			"company": opportunity_doc.company
		})
	elif new_stage == "Term Sheet":
		# Notify legal team
		frappe.publish_realtime("term_sheet_received", {
			"opportunity": opportunity_doc.name,
			"company": opportunity_doc.company
		})

@frappe.whitelist()
def generate_investor_update(company, period_type="Monthly"):
	"""AI-generate an investor update draft."""
	from startup_os.fundraising.report_generator import create_update_draft
	from frappe.utils import today, add_months

	# Check if one already exists for this period
	period_start = add_months(today(), -1) if period_type == "Monthly" else add_months(today(), -3)
	exists = frappe.db.count("Investor Update", {
		"company": company,
		"period_end": [">=", period_start]
	})

	if exists:
		return {"status": "exists", "message": "An investor update for this period already exists."}

	create_update_draft(company)
	return {"status": "success", "message": f"{period_type} investor update draft created."}

@frappe.whitelist()
def get_investor_list(company=None):
	"""Get all investors, optionally with their opportunity count."""
	investors = frappe.get_all("Investor",
		fields=["name", "investor_name", "investor_type", "contact_email", "total_investment"]
	)
	return investors
