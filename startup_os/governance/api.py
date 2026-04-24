import frappe

@frappe.whitelist()
def get_board_meeting_list(company):
	"""Get all board meetings for a company."""
	meetings = frappe.get_all("Board Meeting",
		filters={"company": company},
		fields=["name", "meeting_date", "status"],
		order_by="meeting_date desc"
	)
	return meetings

@frappe.whitelist()
def create_board_meeting(company, meeting_date, agenda=""):
	"""Create a new board meeting."""
	doc = frappe.new_doc("Board Meeting")
	doc.company = company
	doc.meeting_date = meeting_date
	doc.agenda = agenda
	doc.status = "Scheduled"
	doc.insert()
	frappe.db.commit()
	return {"status": "success", "name": doc.name}

@frappe.whitelist()
def submit_minutes(meeting_name, minutes, resolutions=""):
	"""Submit minutes for a board meeting."""
	# Check if minutes already exist
	existing = frappe.db.get_value("Board Minutes", {"meeting": meeting_name})
	if existing:
		minutes_doc = frappe.get_doc("Board Minutes", existing)
	else:
		minutes_doc = frappe.new_doc("Board Minutes")
		minutes_doc.meeting = meeting_name

	minutes_doc.minutes = minutes
	minutes_doc.resolutions = resolutions
	minutes_doc.save()

	# Mark meeting as completed
	meeting_doc = frappe.get_doc("Board Meeting", meeting_name)
	meeting_doc.status = "Completed"
	meeting_doc.save()

	frappe.db.commit()
	return {"status": "success", "minutes": minutes_doc.name}

@frappe.whitelist()
def get_expiring_contracts(company, days=30):
	"""Get contracts expiring within N days."""
	from frappe.utils import add_days, today
	contracts = frappe.get_all("Contract Document",
		filters={
			"company": company,
			"status": "Active",
			"expiry_date": ["between", [today(), add_days(today(), int(days))]]
		},
		fields=["name", "contract_name", "party", "expiry_date"],
		order_by="expiry_date asc"
	)
	return contracts

@frappe.whitelist()
def add_contract(company, contract_name, party, expiry_date=None, file=None):
	"""Add a new contract to the repository."""
	doc = frappe.new_doc("Contract Document")
	doc.company = company
	doc.contract_name = contract_name
	doc.party = party
	doc.expiry_date = expiry_date
	doc.file = file
	doc.status = "Active"
	doc.insert()
	frappe.db.commit()
	return {"status": "success", "name": doc.name}
