# Data Room — Secure Investor Due Diligence Portal
# Provides per-investor token-based access, document tracking, and access logs

import secrets
import frappe
from frappe.utils import now, add_days, get_datetime


# ─────────────────────────────────────────────────────────────────
# CREATE & MANAGE DATA ROOMS
# ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_data_room(company, room_name, round_name=None, expires_days=30):
    """Create a new data room for a fundraising round."""
    doc = frappe.new_doc("Data Room")
    doc.company = company
    doc.room_name = room_name
    doc.round_name = round_name
    doc.status = "Active"
    doc.expires_on = add_days(now(), int(expires_days))
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"data_room": doc.name, "message": f"Data Room '{room_name}' created"}


@frappe.whitelist()
def add_document(data_room, document_name, category="Other", description=None):
    """Add a document entry to a data room (file attachment done via Frappe's file upload)."""
    doc = frappe.get_doc("Data Room", data_room)
    doc.append("documents", {
        "document_name": document_name,
        "category": category,
        "description": description,
        "added_on": frappe.utils.today(),
        "view_count": 0,
    })
    doc.save(ignore_permissions=True)
    return {"message": f"Document '{document_name}' added to {data_room}"}


@frappe.whitelist()
def remove_document(data_room, document_name):
    """Remove a document from the data room."""
    doc = frappe.get_doc("Data Room", data_room)
    doc.documents = [d for d in doc.documents if d.document_name != document_name]
    doc.save(ignore_permissions=True)
    return {"message": f"Document '{document_name}' removed"}


# ─────────────────────────────────────────────────────────────────
# INVESTOR ACCESS MANAGEMENT
# ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def grant_investor_access(data_room, investor, contact_name, email, expires_days=30):
    """
    Grant a specific investor access to the data room.
    Generates a unique secure token and returns the shareable link.
    """
    doc = frappe.get_doc("Data Room", data_room)

    # Check if already granted
    existing = [a for a in doc.access_list if a.email == email]
    if existing:
        token = existing[0].access_token
        link = _build_access_link(token)
        return {"message": "Access already granted", "link": link, "token": token}

    # Generate unique token
    token = secrets.token_urlsafe(32)
    expires_at = add_days(now(), int(expires_days))

    doc.append("access_list", {
        "investor": investor,
        "contact_name": contact_name,
        "email": email,
        "is_active": 1,
        "access_token": token,
        "token_expires": expires_at,
    })
    doc.save(ignore_permissions=True)

    # Log the access grant event
    _log_access(data_room=data_room, investor=investor, contact_name=contact_name,
                email=email, document_name="", action="Login")

    link = _build_access_link(token)
    return {
        "message": f"Access granted to {contact_name} ({email})",
        "link": link,
        "token": token,
        "expires_at": expires_at,
    }


@frappe.whitelist()
def revoke_investor_access(data_room, email):
    """Revoke a specific investor's access token."""
    doc = frappe.get_doc("Data Room", data_room)
    for row in doc.access_list:
        if row.email == email:
            row.is_active = 0
            row.access_token = ""
    doc.save(ignore_permissions=True)
    return {"message": f"Access revoked for {email}"}


@frappe.whitelist()
def refresh_token(data_room, email, expires_days=30):
    """Generate a new token for an investor (refresh expiry)."""
    doc = frappe.get_doc("Data Room", data_room)
    new_token = secrets.token_urlsafe(32)
    for row in doc.access_list:
        if row.email == email:
            row.access_token = new_token
            row.token_expires = add_days(now(), int(expires_days))
            row.is_active = 1
    doc.save(ignore_permissions=True)
    return {"link": _build_access_link(new_token), "token": new_token}


# ─────────────────────────────────────────────────────────────────
# TOKEN VERIFICATION (used by the portal page)
# ─────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def verify_token(token):
    """
    Verify a data room access token.
    Returns room details + document list if valid.
    Guest-whitelisted for the public portal page.
    """
    if not token:
        frappe.throw("Access token is required", frappe.AuthenticationError)

    # Find the access row with this token
    result = frappe.db.sql("""
        SELECT
            dr.name as data_room,
            dr.room_name,
            dr.company,
            dr.round_name,
            dr.status,
            dr.expires_on,
            da.investor,
            da.contact_name,
            da.email,
            da.token_expires,
            da.is_active
        FROM `tabData Room` dr
        JOIN `tabData Room Access` da ON da.parent = dr.name
        WHERE da.access_token = %s
        LIMIT 1
    """, token, as_dict=True)

    if not result:
        frappe.throw("Invalid access token. Please request a new link.", frappe.AuthenticationError)

    access = result[0]

    # Check data room status
    if access.status != "Active":
        frappe.throw("This data room has been closed.")

    # Check token expiry
    if access.token_expires and get_datetime(access.token_expires) < get_datetime(now()):
        frappe.throw("Your access link has expired. Please request a new link.")

    # Check investor-level active flag
    if not access.is_active:
        frappe.throw("Your access to this data room has been revoked.")

    # Update last_accessed
    frappe.db.sql("""
        UPDATE `tabData Room Access`
        SET last_accessed = %s
        WHERE parent = %s AND access_token = %s
    """, (now(), access.data_room, token))
    frappe.db.commit()

    # Fetch document list
    documents = frappe.get_all(
        "Data Room Document",
        filters={"parent": access.data_room},
        fields=["document_name", "category", "description", "added_on", "file"],
        order_by="category, document_name"
    )

    # Log the access
    _log_access(
        data_room=access.data_room,
        investor=access.investor,
        contact_name=access.contact_name,
        email=access.email,
        document_name="",
        action="Login"
    )

    return {
        "valid": True,
        "data_room": access.data_room,
        "room_name": access.room_name,
        "company": access.company,
        "round_name": access.round_name,
        "contact_name": access.contact_name,
        "email": access.email,
        "documents": documents,
        "expires_at": str(access.token_expires),
    }


@frappe.whitelist(allow_guest=True)
def log_document_view(token, document_name, action="View"):
    """Log when an investor views or downloads a document."""
    result = frappe.db.sql("""
        SELECT dr.name as data_room, da.investor, da.contact_name, da.email
        FROM `tabData Room` dr
        JOIN `tabData Room Access` da ON da.parent = dr.name
        WHERE da.access_token = %s AND da.is_active = 1
        LIMIT 1
    """, token, as_dict=True)

    if not result:
        return {"ok": False}

    access = result[0]

    # Increment view count on the document
    frappe.db.sql("""
        UPDATE `tabData Room Document`
        SET view_count = COALESCE(view_count, 0) + 1
        WHERE parent = %s AND document_name = %s
    """, (access.data_room, document_name))

    _log_access(
        data_room=access.data_room,
        investor=access.investor,
        contact_name=access.contact_name,
        email=access.email,
        document_name=document_name,
        action=action
    )
    frappe.db.commit()
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────
# ACCESS AUDIT REPORT
# ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_access_report(data_room):
    """Return full access log for a data room, grouped by investor."""
    logs = frappe.get_all(
        "Data Room Access Log",
        filters={"data_room": data_room},
        fields=["contact_name", "email", "document_name", "action", "timestamp", "ip_address"],
        order_by="timestamp desc",
        limit=500
    )

    # Investor summary
    access_list = frappe.get_all(
        "Data Room Access",
        filters={"parent": data_room},
        fields=["contact_name", "email", "is_active", "last_accessed", "token_expires"],
    )

    return {
        "access_list": access_list,
        "logs": logs,
        "total_views": len([l for l in logs if l.action == "View"]),
        "total_downloads": len([l for l in logs if l.action == "Download"]),
        "unique_visitors": len(set(l.email for l in logs)),
    }


# ─────────────────────────────────────────────────────────────────
# Internals
# ─────────────────────────────────────────────────────────────────

def _log_access(data_room, investor, contact_name, email, document_name, action):
    try:
        log = frappe.new_doc("Data Room Access Log")
        log.data_room = data_room
        log.investor = investor
        log.contact_name = contact_name
        log.email = email
        log.document_name = document_name
        log.action = action
        log.timestamp = now()
        log.ip_address = frappe.local.request_ip if frappe.local.request else ""
        log.insert(ignore_permissions=True)
    except Exception:
        pass  # never let logging break the main flow


def _build_access_link(token):
    site_url = frappe.utils.get_url()
    return f"{site_url}/startup_os/data_room?token={token}"
