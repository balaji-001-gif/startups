# Legal Template Rendering API
import frappe
from jinja2 import Environment
from frappe.utils import today, formatdate


@frappe.whitelist()
def get_template_list():
    """Return all legal templates grouped by category."""
    templates = frappe.get_all(
        "Legal Template",
        fields=["name", "template_name", "category", "description"],
        order_by="category, template_name"
    )
    grouped = {}
    for t in templates:
        grouped.setdefault(t.category, []).append(t)
    return grouped


@frappe.whitelist()
def render_template(template_name, variables=None):
    """
    Render a legal template with given variables.
    variables: dict — key/value pairs to substitute
    Returns rendered HTML ready for PDF generation.
    """
    import json
    if isinstance(variables, str):
        variables = json.loads(variables)
    variables = variables or {}

    doc = frappe.get_doc("Legal Template", template_name)

    env = Environment(autoescape=False)
    env.filters["upper"] = str.upper
    template = env.from_string(doc.template_body)

    # Inject defaults
    defaults = {
        "date": formatdate(today(), "dd MMMM yyyy"),
        "company_name": variables.get("company_name", ""),
    }
    defaults.update(variables)

    rendered = template.render(**defaults)
    return {"html": rendered, "template_name": template_name, "category": doc.category}


@frappe.whitelist()
def render_and_download(template_name, variables=None, filename=None):
    """Render template and return as PDF via WeasyPrint."""
    import base64
    result = render_template(template_name, variables)
    html = f"""
    <html><head>
    <style>
        body {{font-family:'Times New Roman',serif;font-size:12pt;line-height:1.8;color:#1a1a1a;padding:40px 60px;}}
        h1{{font-size:16pt;text-align:center;text-transform:uppercase;margin-bottom:6px;}}
        h2{{font-size:12pt;text-decoration:underline;margin-top:20px;}}
        .parties{{background:#f8f8f8;padding:16px;border-radius:6px;margin:16px 0;}}
        .signature-block{{margin-top:60px;display:grid;grid-template-columns:1fr 1fr;gap:40px;}}
        .sig-line{{border-top:1px solid #000;padding-top:6px;font-size:10pt;color:#555;}}
    </style>
    </head><body>{result["html"]}</body></html>
    """
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        name = filename or f"{template_name.replace(' ', '_')}_{frappe.utils.today()}.pdf"
        return {
            "filename": name,
            "filecontent": base64.b64encode(pdf).decode(),
            "type": "pdf"
        }
    except ImportError:
        return {
            "filename": f"{template_name}.html",
            "filecontent": base64.b64encode(html.encode()).decode(),
            "type": "html"
        }
