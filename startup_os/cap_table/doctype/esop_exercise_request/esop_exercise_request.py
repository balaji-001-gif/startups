# Copyright (c) 2024, Balaji and contributors
import frappe
from frappe.model.document import Document


class ESOPExerciseRequest(Document):
    def before_save(self):
        """Auto-fill strike price and total exercise cost from the ESOP grant."""
        if self.esop_grant and self.options_exercised:
            # Get strike price from ESOP Grant if available
            grant = frappe.db.get_value("ESOP Grant", self.esop_grant,
                                        ["exercise_price"], as_dict=True)
            if grant and grant.exercise_price:
                self.strike_price = grant.exercise_price
                self.total_exercise_cost = self.options_exercised * self.strike_price

    def on_update(self):
        """When Approved — auto-create Equity Transaction for the allotment."""
        if self.status == "Approved" and self.share_allotment_date and self.shares_allotted:
            # Check no equity transaction created yet
            existing = frappe.db.exists("Equity Transaction", {
                "esop_exercise_request": self.name
            })
            if not existing:
                company = frappe.db.get_value(
                    "Employee", self.employee, "company"
                )
                eq = frappe.new_doc("Equity Transaction")
                eq.company = company
                eq.transaction_type = "Issuance"
                eq.share_type = "Equity"
                eq.quantity = self.shares_allotted
                eq.price_per_share = self.strike_price or 0
                eq.total_value = self.shares_allotted * (self.strike_price or 0)
                eq.date = self.share_allotment_date
                eq.insert(ignore_permissions=True)
