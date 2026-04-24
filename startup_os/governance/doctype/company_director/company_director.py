# Copyright (c) 2024, Balaji and contributors
import frappe
from frappe.model.document import Document


class CompanyDirector(Document):
    def validate(self):
        if self.status in ('Ceased', 'Resigned', 'Disqualified') and not self.cessation_date:
            frappe.throw('Please enter Date of Cessation for non-active directors.')
