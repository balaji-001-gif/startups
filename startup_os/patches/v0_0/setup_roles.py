import frappe

def execute():
	"""Create custom roles for StartupOS."""
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
			print(f"Created role: {role_data['role_name']}")
		else:
			print(f"Role already exists: {role_data['role_name']}")
