import frappe
from frappe.utils import add_days, today, getdate
from startup_os.notifications.notifications import (
	notify_compliance_deadline,
	notify_compliance_score_drop,
)

def check_upcoming_deadlines():
	"""
	Check for upcoming regulatory deadlines and send alerts.
	"""
	upcoming_filings = frappe.get_all("Regulatory Calendar",
		filters={"status": "Upcoming", "due_date": ["<=", add_days(today(), 30)]},
		fields=["name", "filing_name", "due_date", "company"]
	)

	for filing in upcoming_filings:
		days_left = (getdate(filing.due_date) - getdate(today())).days
		if days_left in [30, 7, 1]:
			notify_compliance_deadline(filing, days_left)

def send_compliance_alert(filing, days_left):
	"""
	Send email/WhatsApp alert for upcoming deadline.
	"""
	# Placeholder for WhatsApp/Email notification logic
	subject = f"ACTION REQUIRED: {filing.filing_name} due in {days_left} days"
	message = f"Regulatory filing {filing.filing_name} for {filing.company} is due on {filing.due_date}."
	
	# Send email to Company's contact or Startup Founder role
	recipients = frappe.get_all("User", filters={"enabled": 1}, fields=["email"]) # Simplification
	for r in recipients:
		frappe.sendmail(
			recipients=[r.email],
			subject=subject,
			content=message
		)

def compute_compliance_scores():
	"""
	Compute compliance score for all companies.
	"""
	companies = frappe.get_all("Company", fields=["name"])
	for company in companies:
		calculate_company_score(company.name)

def calculate_company_score(company_name):
	"""
	Calculate compliance score based on filing status and checklists.
	"""
	score = 100
	deductions = []

	# Check Overdue Filings
	overdue_count = frappe.db.count("Regulatory Calendar", filters={"company": company_name, "status": "Overdue"})
	if overdue_count > 0:
		deduction = min(overdue_count * 10, 50)
		score -= deduction
		deductions.append(f"Overdue filings: -{deduction}")

	# Check Incorporation Checklist
	checklist = frappe.get_all("Incorporation Checklist", filters={"company": company_name}, limit=1)
	if not checklist:
		score -= 20
		deductions.append("Missing Incorporation Checklist: -20")
	else:
		doc = frappe.get_doc("Incorporation Checklist", checklist[0].name)
		if not doc.inc_20a:
			score -= 10
			deductions.append("INC-20A not filed: -10")
		if not doc.pan:
			score -= 5
			deductions.append("PAN not obtained: -5")

	# Update or Create Compliance Score doc
	score_doc_name = frappe.db.get_value("Compliance Score", {"company": company_name})
	if score_doc_name:
		score_doc = frappe.get_doc("Compliance Score", score_doc_name)
	else:
		score_doc = frappe.new_doc("Compliance Score")
		score_doc.company = company_name

	score_doc.score = max(score, 0)
	score_doc.last_computed = frappe.utils.now()
	score_doc.score_breakdown = frappe.as_json(deductions)

	# Notify on significant score drop
	old_score = getattr(score_doc, '_doc_before_save', None)
	if old_score and hasattr(old_score, 'score'):
		notify_compliance_score_drop(company_name, old_score.score, max(score, 0))

	score_doc.save(ignore_permissions=True)
