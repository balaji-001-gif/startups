import frappe

def after_install():
	"""Run post-install setup for StartupOS."""
	frappe.logger("startup_os").info("StartupOS: Running after_install...")

	# 1. Create Roles
	_create_roles()

	# 2. Seed a regulatory calendar for any existing companies
	companies = frappe.get_all("Company", fields=["name"])
	for company in companies:
		try:
			from startup_os.compliance.api import seed_regulatory_calendar
			seed_regulatory_calendar(company.name)
		except Exception as e:
			frappe.log_error(str(e), f"StartupOS: Failed to seed calendar for {company.name}")

	frappe.db.commit()
	frappe.logger("startup_os").info("StartupOS: after_install complete.")

def _create_roles():
	"""Create custom StartupOS roles."""
	roles = [
		{"role_name": "Startup Founder", "desk_access": 1},
		{"role_name": "Startup CFO", "desk_access": 1},
		{"role_name": "Startup Legal", "desk_access": 1},
		{"role_name": "Startup Investor", "desk_access": 0},
		{"role_name": "Startup Admin", "desk_access": 1},
	]

	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.new_doc("Role")
			role.role_name = role_data["role_name"]
			role.desk_access = role_data["desk_access"]
			role.insert(ignore_permissions=True)
			frappe.db.commit()
