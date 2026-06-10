from odoo import models, fields, api
from odoo.models import Constraint, UniqueIndex, Index
from .repair_selection import (
    PRODUCT_LOCATION_SELECTION, 
    QUOTE_STATUS_SELECTION, 
    WARRANTY_STATUS_SELECTION, 
    ESTIMATE_STATUS_SELECTION
)

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"

    
    company_id = fields.Many2one(
        'res.company', 
        string="Branch", 
        required=True, 
        default=lambda self: self.env.company
    )

    
    summary = fields.Char('Summary', size=256, required=True)
    description = fields.Text("Complaint Details", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    repair_type_id = fields.Many2one('repair.job.type', string="Diagnostic Classification", ondelete='cascade')
    
    adjust_booking_date = fields.Boolean("Adjust Booking Date", default=False)
    reason_adjust_booking_date = fields.Char("Reason to Adjust Booking Date", size=255)
    
    manufacturer_id = fields.Many2one("repair.device.manufacturer", string="Device Manufacturer", required=True)
    device_model_id = fields.Many2one("repair.device.model", string="Device Model", required=True)
    imei = fields.Char('Imei', size=16)
    serial = fields.Char('Serial No', size=20)
    purchase_date = fields.Date('Date of purchase')
    
    in_warranty = fields.Boolean("In Warranty", default=False)
    warranty_exception = fields.Char("Reason for Warranty exception", size=255, required=False)
    warranty_notes = fields.Char("Warranty Notes", size=255)
    warranty_status = fields.Selection(WARRANTY_STATUS_SELECTION, string="Warranty Status", default="unclaimed")
    
    insurer = fields.Char('Insurance Company', size=128)
    policy_no = fields.Char("Policy Number", size=128)
    
    job_site = fields.Selection([("field_call", "Field Call"), ("workshop", "Workshop")], default='workshop')
    product_location = fields.Selection(PRODUCT_LOCATION_SELECTION, string="Product Location", required=True, default="customer")

    
    status_id = fields.Many2one('repair.status', string="Current Status", required=True,ondelete='restrict')
    status_history_ids = fields.One2many('repair.job.status.line', 'job_id', string="Status Logs", readonly=True)
    
    
    quote_status = fields.Selection(QUOTE_STATUS_SELECTION, string="Quote Status", default="not_required")
    repair_type = fields.Selection([("customer", "Customer"), ("installation", "Installation"), ("stock", "Stock")], default="customer")
    estimate_required = fields.Boolean("Estimate Required", default=False)
    estimate_accepted = fields.Boolean("Estimate Accepted", default=True)  # Fixed string label typo
    estimate_status = fields.Selection(ESTIMATE_STATUS_SELECTION, string="Estimate Status", default="required")
    
    escalation_required = fields.Boolean("Escalation Required", default=False)
    cancel_reason = fields.Text("Reason for Cancel")
    network_ref_number = fields.Char("Network Ref No", size=64)
    

    @api.model_create_multi
    def create(self, vals_list):
        jobs = super().create(vals_list)
        for job in jobs:
            if job.status_id:
                job._log_status_change(job.status_id.id)
        return jobs

    def write(self, vals):
        res = super().write(vals)
        if 'status_id' in vals:
            for job in self:
                job._log_status_change(vals['status_id'])
        return res

    def _log_status_change(self, status_id):
        """ Helper method to generate a clean history row """
        self.env['repair.job.status.line'].create({
            'job_id': self.id,
            'status_id': status_id,
            'user_id': self.env.user.id,
            'changed_date': fields.Datetime.now()
        })