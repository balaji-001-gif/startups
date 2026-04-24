import frappe

@frappe.whitelist()
def get_compliance_score(company):
	"""Get the compliance score for a company."""
	score_doc = frappe.get_all("Compliance Score",
		filters={"company": company},
		fields=["score", "last_computed", "score_breakdown"],
		limit=1
	)
	if score_doc:
		import json
		breakdown = json.loads(score_doc[0].score_breakdown or "[]")
		return {
			"score": score_doc[0].score,
			"last_computed": score_doc[0].last_computed,
			"breakdown": breakdown
		}
	return {"score": 0, "last_computed": None, "breakdown": []}

@frappe.whitelist()
def get_upcoming_deadlines(company, days=30):
	"""Get filings due within the given number of days."""
	from frappe.utils import add_days, today
	filings = frappe.get_all("Regulatory Calendar",
		filters={
			"company": company,
			"due_date": ["<=", add_days(today(), int(days))],
			"status": "Upcoming"
		},
		fields=["name", "filing_name", "form_type", "due_date", "status"],
		order_by="due_date asc"
	)
	return filings

@frappe.whitelist()
def mark_filing_complete(filing_name):
	"""Mark a regulatory filing as complete."""
	from frappe.utils import today
	doc = frappe.get_doc("Regulatory Calendar", filing_name)
	doc.status = "Filed"
	doc.completion_date = today()
	doc.save()
	frappe.db.commit()
	return {"status": "success", "message": f"{filing_name} marked as Filed."}

@frappe.whitelist()
def generate_document(template, variables):
	"""Generate a document from template."""
	import json
	if isinstance(variables, str):
		variables = json.loads(variables)
	# In a full implementation, this would render a Jinja2 template to PDF via WeasyPrint
	return {"status": "success", "message": f"Document '{template}' generated.", "variables": variables}

@frappe.whitelist()
def get_dpiit_status(company):
	"""Get DPIIT application status for a company."""
	apps = frappe.get_all("DPIIT Application",
		filters={"company": company},
		fields=["name", "application_number", "status", "certificate_number", "recognition_date"],
		order_by="creation desc",
		limit=1
	)
	return apps[0] if apps else {}

@frappe.whitelist()
def seed_regulatory_calendar(company):
	"""
	Seed the regulatory calendar with standard ROC/MCA/GST/TDS filing deadlines.
	One-time setup per company.
	"""
	from frappe.utils import today, nowdate, get_first_day, get_last_day, add_months
	import datetime

	year = datetime.date.today().year

	filings = [
		{"filing_name": "Annual Return", "form_type": "MGT-7 / MGT-7A", "due_date": f"{year}-11-29"},
		{"filing_name": "Financial Statements", "form_type": "AOC-4", "due_date": f"{year}-10-29"},
		{"filing_name": "Auditor Appointment", "form_type": "ADT-1", "due_date": f"{year}-10-14"},
		{"filing_name": "GST Return - GSTR-1 (Monthly)", "form_type": "GSTR-1", "due_date": f"{year}-04-11"},
		{"filing_name": "GST Return - GSTR-3B (Monthly)", "form_type": "GSTR-3B", "due_date": f"{year}-04-20"},
		{"filing_name": "TDS Return Q4", "form_type": "26Q / 24Q", "due_date": f"{year}-05-31"},
		{"filing_name": "Income Tax Return", "form_type": "ITR-6", "due_date": f"{year}-10-31"},
	]

	created = 0
	for f in filings:
		exists = frappe.db.exists("Regulatory Calendar", {"company": company, "filing_name": f["filing_name"]})
		if not exists:
			doc = frappe.new_doc("Regulatory Calendar")
			doc.company = company
			doc.filing_name = f["filing_name"]
			doc.form_type = f["form_type"]
			doc.due_date = f["due_date"]
			doc.status = "Upcoming"
			doc.insert(ignore_permissions=True)
			created += 1

	frappe.db.commit()
	return {"status": "success", "created": created, "message": f"Seeded {created} regulatory calendar entries."}
