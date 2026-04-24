import frappe
from frappe.utils import add_months, getdate, today

def recompute_vesting_schedules():
	"""
	Scheduled task to update vesting status.
	"""
	grants = frappe.get_all("ESOP Grant", fields=["name"])
	for g in grants:
		calculate_vesting_schedule(g.name)

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
