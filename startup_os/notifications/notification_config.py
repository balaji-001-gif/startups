import frappe


def get_notification_config():
	"""
	Returns Frappe desk notification badge configuration for StartupOS.
	Drives the red-dot counts on sidebar module icons.
	"""
	return {
		"for_doctype": {
			# Compliance – overdue regulatory filings
			"Regulatory Calendar": {"status": "Overdue"},

			# ESOP – grants pending vesting action
			"ESOP Grant": {"vesting_status": "Pending"},

			# Fundraising – open opportunities
			"Fundraising Opportunity": {"status": ["in", ["Lead", "Due Diligence", "Term Sheet"]]},
		}
	}
