import frappe
from startup_os.reports.pdf_generator import (
    generate_investor_report,
    generate_cap_table_report,
    generate_dpiit_report,
    generate_financial_projections,
    export_equity_audit,
)

# All functions already decorated with @frappe.whitelist() in pdf_generator
# This module re-exports them for hooks.py clarity

@frappe.whitelist()
def get_report_list(company):
    """Returns the list of available reports for a company with metadata."""
    return [
        {
            "id": "investor_report",
            "title": "Investor Summary Report",
            "description": "One-click investor-ready PDF with compliance score, financials, cap table, and pipeline",
            "icon": "📊",
            "api": "startup_os.reports.pdf_generator.generate_investor_report",
            "format": "pdf",
        },
        {
            "id": "cap_table",
            "title": "Cap Table Report",
            "description": "Full digital cap table with transaction history, ESOP grants, and ownership breakdown",
            "icon": "📋",
            "api": "startup_os.reports.pdf_generator.generate_cap_table_report",
            "format": "pdf",
        },
        {
            "id": "dpiit_report",
            "title": "DPIIT Compliance Report",
            "description": "DPIIT recognition status, incorporation checklist, compliance score, and all filings",
            "icon": "🇮🇳",
            "api": "startup_os.reports.pdf_generator.generate_dpiit_report",
            "format": "pdf",
        },
        {
            "id": "financial_projections",
            "title": "Financial Projections",
            "description": "Pitch-ready 24-month projections with 3-scenario runway analysis",
            "icon": "💸",
            "api": "startup_os.reports.pdf_generator.generate_financial_projections",
            "format": "pdf",
        },
        {
            "id": "equity_audit",
            "title": "Equity & Compliance Audit Export",
            "description": "Audit-ready XLSX export of all equity transactions + compliance events + cap table",
            "icon": "📥",
            "api": "startup_os.reports.pdf_generator.export_equity_audit",
            "format": "xlsx",
        },
    ]
