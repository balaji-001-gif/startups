# ESOP Grant Letter Generator + Exercise Tracking
import frappe
import base64
from frappe.utils import formatdate


@frappe.whitelist()
def generate_grant_letter(esop_grant_name):
    """Generate a PDF grant letter for an ESOP grant."""
    grant = frappe.get_doc("ESOP Grant", esop_grant_name)

    # Get employee details
    employee = frappe.db.get_value(
        "Employee", grant.employee,
        ["employee_name", "designation", "company"],
        as_dict=True
    )
    company = employee.company if employee else ""

    variables = {
        "company_name": company,
        "employee_name": employee.employee_name if employee else grant.employee,
        "employee_designation": employee.designation if employee else "",
        "options_count": int(grant.quantity or 0),
        "grant_date": formatdate(grant.grant_date, "dd MMMM yyyy"),
        "vesting_start": formatdate(grant.vesting_start_date, "dd MMMM yyyy"),
        "cliff_months": int(grant.cliff_period_months or 12),
        "vesting_months": int(grant.vesting_period_months or 48),
        "exercise_price": grant.exercise_price or "face value",
    }

    import os
    template_path = os.path.join(os.path.dirname(__file__), "templates", "esop_grant_letter.html")
    with open(template_path) as f:
        template_str = f.read()

    from jinja2 import Environment
    env = Environment(autoescape=False)
    template = env.from_string(template_str)
    html = template.render(**variables)

    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        filename = f"ESOP_Grant_Letter_{employee.employee_name if employee else grant.employee}_{grant.grant_date}.pdf".replace(" ", "_")
        return {
            "filename": filename,
            "filecontent": base64.b64encode(pdf).decode(),
            "type": "pdf"
        }
    except ImportError:
        return {
            "filename": "esop_grant_letter.html",
            "filecontent": base64.b64encode(html.encode()).decode(),
            "type": "html"
        }


@frappe.whitelist()
def get_vesting_summary(esop_grant_name):
    """Return vesting status summary for a grant."""
    schedule = frappe.get_all(
        "ESOP Vesting Schedule",
        filters={"parent": esop_grant_name},
        fields=["vesting_date", "options_vesting", "status"],
        order_by="vesting_date asc"
    )
    vested = sum(s.options_vesting for s in schedule if s.status == "Vested")
    pending = sum(s.options_vesting for s in schedule if s.status == "Pending")
    exercised = sum(s.options_vesting for s in schedule if s.status == "Exercised")
    return {
        "total": vested + pending + exercised,
        "vested": vested,
        "exercised": exercised,
        "pending": pending,
        "available_to_exercise": vested - exercised,
        "schedule": schedule,
    }


@frappe.whitelist()
def submit_exercise_request(esop_grant, options_to_exercise, exercise_date=None):
    """Submit an ESOP exercise request."""
    from frappe.utils import today
    grant = frappe.get_doc("ESOP Grant", esop_grant)
    summary = get_vesting_summary(esop_grant)

    if int(options_to_exercise) > summary["available_to_exercise"]:
        frappe.throw(
            f"Cannot exercise {options_to_exercise} options. "
            f"Only {summary['available_to_exercise']} vested options available."
        )

    req = frappe.new_doc("ESOP Exercise Request")
    req.employee = grant.employee
    req.esop_grant = esop_grant
    req.exercise_date = exercise_date or today()
    req.options_exercised = int(options_to_exercise)
    req.status = "Pending"
    req.insert(ignore_permissions=True)
    return {"request": req.name, "message": "Exercise request submitted for approval"}
