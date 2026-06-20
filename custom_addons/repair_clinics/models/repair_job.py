from odoo import models, fields, api
from odoo.models import Constraint, UniqueIndex, Index
from .repair_selection import (
    PRODUCT_LOCATION_SELECTION, 
    QUOTE_STATUS_SELECTION, 
    WARRANTY_STATUS_SELECTION, 
    ESTIMATE_STATUS_SELECTION,
    PRODUCT_CONDITION
)

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"

    branch_id = fields.Many2one(
        'res.company', 
        string="Branch", 
        required=False,
        domain="[('company_type_role', '=', 'branch')]",
        default=lambda self: self.env.company if self.env.company.company_type_role == 'branch' else False,
    )

    
    client_id = fields.Many2one(
        'res.company', 
        string='Client', 
        domain="[('company_type_role', '=', 'client')]",
        store=False,
    )

    network_id = fields.Many2one(
        'res.company', 
        string='Network', 
        domain="[('company_type_role', '=', 'network')]",
        store=False,
    )

    current_company_role = fields.Char(
        compute="_compute_current_company_role",
        store=False
    )

    service_provider_id = fields.Many2one(
        'res.company', 
        string="Service Provider", 
        required=True, 
        default=lambda self: self.env.company if self.env.company.company_type_role == 'service_provider' else False,
        domain="[('company_type_role', '=', 'service_provider')]"
    )

    
    summary = fields.Char('Summary', size=256, required=True)
    description = fields.Text("Complaint Details", required=True)
    customer_id = fields.Many2one(
        'res.partner', 
        string="Customer", 
        required=True,
        domain="[('is_company', '=', False), ('user_ids', '=', False)]"
    )
    repair_type_id = fields.Many2one('repair.job.type', string="Diagnostic Classification", ondelete='cascade')

    device_condition = fields.Selection(PRODUCT_CONDITION,string="Product Condition", default='good')
    
    adjust_booking_date = fields.Boolean("Adjust Booking Date", default=False)
    reason_adjust_booking_date = fields.Char("Reason to Adjust Booking Date", size=255)
    
    manufacturer_id = fields.Many2one(
        "repair.device.manufacturer", 
        string="Device Manufacturer", 
        required=True,
        
    )

    allowed_unit_type_ids = fields.Many2many(
        "repair.device.unit.type", 
        compute="_compute_allowed_unit_types",
        string="Allowed Unit Types"
    )

    unit_type_id = fields.Many2one(
        "repair.device.unit.type", 
        string="Unit Type",
        required=True,
        domain="[('id', 'in', allowed_unit_type_ids)]"
    )

    device_model_id = fields.Many2one(
        "repair.device.model", 
        string="Device Model", 
        required=True,
        domain="[('manufacturer_id', '=', manufacturer_id), ('unit_type_id', '=', unit_type_id)]"
    )

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

    @api.depends('manufacturer_id')
    def _compute_allowed_unit_types(self):
        """Scans the Model registry to extract ONLY distinct Unit Types for the chosen brand"""
        for rec in self:
            if rec.manufacturer_id:
                # Find all device models matching the selected manufacturer
                matching_models = self.env['repair.device.model'].search([
                    ('manufacturer_id', '=', rec.manufacturer_id.id)
                ])
                # Extract all distinct unit type IDs using Python set mapping
                unit_type_ids = matching_models.mapped('unit_type_id').ids
                rec.allowed_unit_type_ids = [(6, 0, unit_type_ids)]
            else:
                # If no manufacturer is chosen, clear the helper array
                rec.allowed_unit_type_ids = [(5, 0, 0)]

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_reset_children(self):
        """Wipes down cascading values if the user alters the core brand choice"""
        self.unit_type_id = False
        self.device_model_id = False

    @api.onchange('unit_type_id')
    def _onchange_unit_type_reset_model(self):
        """Wipes downstream model selection if category shifts"""
        self.device_model_id = False

    @api.depends_context('company')
    def _compute_current_company_role(self):
        for record in self:
            record.current_company_role = self.env.company.company_type_role or 'other'

    @api.onchange('branch_id')
    def _onchange_branch_id_populate_hierarchy(self):
        """Bottom-up automation: sets parent fields in the UI cache if branch is picked"""
        if self.branch_id:
            parent_client = self.branch_id.parent_id
            if parent_client and parent_client.company_type_role == 'client':
                self.client_id = parent_client
                
                parent_network = parent_client.parent_id
                if parent_network and parent_network.company_type_role == 'network':
                    self.network_id = parent_network

    @api.onchange('network_id')
    def _onchange_network_reset_children(self):
        """Top-down reset: clears sub-choices when network changes"""
        if self.network_id:
            # We explicitly check if client belongs to this network to avoid clearing it prematurely
            if self.client_id and self.client_id.parent_id != self.network_id:
                self.client_id = False
                self.branch_id = False
        else:
            self.client_id = False
            self.branch_id = False

    @api.onchange('client_id')
    def _onchange_client_reset_children(self):
        """Top-down reset: clears branch if client changes"""
        if self.client_id:
            if self.branch_id and self.branch_id.parent_id != self.client_id:
                self.branch_id = False
        else:
            self.branch_id = False