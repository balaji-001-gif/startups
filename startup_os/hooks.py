app_name = "startup_os"
app_title = "StartupOS"
app_publisher = "Balaji"
app_description = "The all-in-one Frappe/ERPNext custom application for Indian Startups"
app_email = "support@startupos.in"
app_license = "mit"
app_version = "0.0.1"
required_apps = ["frappe", "erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/startup_os/css/startup_os.css"
# app_include_js = "/assets/startup_os/js/startup_os.js"

# include js, css files in header of web template
# web_include_css = "/assets/startup_os/css/startup_os.css"
# web_include_js = "/assets/startup_os/js/startup_os.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "startup_os/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page_name" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "startup_os.utils.jinja_methods",
#	"filters": "startup_os.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "startup_os.install.before_install"
after_install = "startup_os.install.after_install"

# Uninstallation
# --------------

# before_uninstall = "startup_os.uninstall.before_uninstall"
# after_uninstall = "startup_os.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To setup dependencies during `bench setup requirements`
# exe_dependencies = ["weasyprint"]

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "startup_os.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in Python
# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Equity Transaction": {
		"after_insert": "startup_os.cap_table.calculator.on_equity_transaction",
		"on_update": "startup_os.cap_table.calculator.on_equity_transaction"
	},
	"ESOP Grant": {
		"after_insert": "startup_os.cap_table.calculator.on_esop_grant_save",
		"on_update": "startup_os.cap_table.calculator.on_esop_grant_save"
	},
	"Fundraising Opportunity": {
		"on_update": "startup_os.fundraising.report_generator.on_opportunity_stage_change"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"startup_os.api.all"
	],
	"daily": [
		"startup_os.financial.forecasting.update_all_runway_models",
		"startup_os.compliance.utils.check_upcoming_deadlines",
		"startup_os.cap_table.calculator.recompute_vesting_schedules"
	],
	"hourly": [
		"startup_os.api.hourly"
	],
	"weekly": [
		"startup_os.ai_assistant.rag_engine.refresh_knowledge_base",
		"startup_os.compliance.utils.compute_compliance_scores"
	],
	"monthly": [
		"startup_os.financial.forecasting.compute_unit_economics",
		"startup_os.fundraising.report_generator.prompt_investor_update"
	]
}

# Testing
# -------

# before_tests = "startup_os.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "startup_os.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "startup_os.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["startup_os.utils.before_request"]
# after_request = ["startup_os.utils.after_request"]

# Bean Events
# -----------
# before_bean_map = ["startup_os.utils.before_bean_map"]
# after_bean_map = ["startup_os.utils.after_bean_map"]
# bean_before_submit = ["startup_os.utils.bean_before_submit"]
# bean_after_submit = ["startup_os.utils.bean_after_submit"]
# bean_before_cancel = ["startup_os.utils.bean_before_cancel"]
# bean_after_cancel = ["startup_os.utils.bean_after_cancel"]

# Table Themes
# -------------
# include custom CSS in report views
# report_view_css = {"Transaction": "public/css/transaction.css"}

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_field}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_field}",
#		"partial": 1,
#	},
#	{
#		"field_map": {
#			"doctype": "User",
#			"filter_by": "name",
#			"redact_fields": ["first_name", "last_name"],
#		}
#	}
# ]

# Authentication and Authorization
# --------------------------------

# auth_hooks = [
#	"startup_os.auth.validate"
# ]

# Desk Widgets
# ------------------
# list of widget groups to be shown in the desk
# widget_groups = [
#	{
#		"title": "StartupOS",
#		"widgets": [
#			{"type": "shortcut", "label": "Compliance Hub", "route": "desk/StartupOS/Compliance Hub"},
#			{"type": "shortcut", "label": "Fundraising OS", "route": "desk/StartupOS/Fundraising OS"}
#		]
#	}
# ]
# ── Fixtures ───────────────────────────────────────────────
fixtures = [
    # Roles
    {'dt': 'Role', 'filters': [['name', 'in', [
        'Startup Admin',
        'Compliance Officer',
        'Finance Executive',
        'Legal Counsel',
        'Investor Relations',
        'Board Member',
        'ESOP Manager',
        'AI Assistant User',
    ]]]},

    # Workspace & UI
    {'dt': 'Workspace'},
    {'dt': 'Workflow'},
    {'dt': 'Workflow State'},
    {'dt': 'Workflow Action Master'},
    {'dt': 'Print Format'},
    {'dt': 'Report'},

    # Field & Form Customisation
    {'dt': 'Custom Field'},
    {'dt': 'Property Setter'},
    {'dt': 'Client Script'},
    {'dt': 'Server Script'},

    # StartupOS Config DocTypes
    {'dt': 'Visa Country Config'},          # keep if reused from travel app
    {'dt': 'Compliance Alert Setting'},
    {'dt': 'Compliance Score'},

    # Notification & Automation
    {'dt': 'Notification'},
    {'dt': 'Auto Repeat'},
    {'dt': 'Assignment Rule'},
]
