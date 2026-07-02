from odoo import models, fields, api
from .repair_selection import (
    PRODUCT_LOCATION_SELECTION, 
    QUOTE_STATUS_SELECTION, 
    WARRANTY_STATUS_SELECTION, 
    ESTIMATE_STATUS_SELECTION,
    PRODUCT_CONDITION
)
import json
from odoo.exceptions import ValidationError
import re

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"

    # =========================================================================
    # 🎯 ENVIRONMENT DEFAULT GENERATORS
    # =========================================================================
    def _get_default_network(self):
        current_company = self.env.company
        current_role = current_company.company_type_role
        if current_role == 'service_provider':
            return self.env.ref('repair_clinics.company_default_network', raise_if_not_found=False)
        elif current_role == 'client':
            return current_company.parent_id.id if current_company.parent_id else False
        elif current_role == 'branch':
            if current_company.parent_id and current_company.parent_id.parent_id:
                return current_company.parent_id.parent_id.id
        return False

    def _get_default_client(self):
        current_company = self.env.company
        current_role = current_company.company_type_role
        if current_role == 'service_provider':
            return self.env.ref('repair_clinics.company_default_client', raise_if_not_found=False)
        elif current_role == 'client':
            return current_company.id
        elif current_role == 'branch':
            return current_company.parent_id.id if current_company.parent_id else False
        return False

    def _get_default_branch(self):
        current_company = self.env.company
        current_role = current_company.company_type_role
        if current_role == 'service_provider':
            return self.env.ref('repair_clinics.company_default_branch', raise_if_not_found=False)
        return False

    # =========================================================================
    # 🏢 HIERARCHY & ROLE SETUPS (Stored columns fixing validation drops)
    # =========================================================================
    network_id = fields.Many2one(
        'res.company', 
        string='Network',
        default=_get_default_network,
        domain="[('company_type_role', '=', 'network')]"
    )

    client_id = fields.Many2one(
        'res.company', 
        string='Client', 
        default=_get_default_client,
        domain="[('company_type_role', '=', 'client')]"
    )

    branch_id = fields.Many2one(
        'res.company', 
        string="Branch", 
        domain="[('company_type_role', '=', 'branch')]",
        default=_get_default_branch, 
        required=True
    )

    service_provider_id = fields.Many2one(
        'res.company', 
        string="Service Provider", 
        required=True, 
        default=lambda self: self.env.company if self.env.company.company_type_role == 'service_provider' else False,
        domain="[('company_type_role', '=', 'service_provider')]"
    )

    # UI Context Trackers
    current_company_role = fields.Char(compute="_compute_current_company_role", store=False)
    client_id_domain = fields.Char(compute='_compute_client_id_domain', store=False)
    network_id_read = fields.Boolean(compute='_compute_hierarchy_readonly_states', store=False)
    client_id_read = fields.Boolean(compute='_compute_hierarchy_readonly_states', store=False)
    branch_id_read = fields.Boolean(compute='_compute_hierarchy_readonly_states', store=False)
    is_custom_client = fields.Boolean(string="Is Custom Client Selected", default=False, store=False)

    # =========================================================================
    # 📝 STANDARD REPAIR OPERATIONAL DATA
    # =========================================================================
    summary = fields.Char('Summary', size=256, required=True)
    description = fields.Text("Complaint Details", required=True)
    customer_id = fields.Many2one(
        'res.partner', 
        string="Customer", 
        required=True,
        domain="["
               "('is_company', '=', False), "
               "('employee', '=', False), "
               "('user_ids', '=', False)"
               "]"
    )
    repair_type_id = fields.Many2one('repair.job.type', string="Diagnostic Classification", ondelete='cascade')
    device_condition = fields.Selection(PRODUCT_CONDITION, string="Product Condition", default='good')
    adjust_booking_date = fields.Boolean("Adjust Booking Date", default=False)
    reason_adjust_booking_date = fields.Char("Reason to Adjust Booking Date", size=255)
    
    # Device Definitions
    manufacturer_id = fields.Many2one("repair.device.manufacturer", string="Device Manufacturer", required=True)
    allowed_unit_type_ids = fields.Many2many("repair.device.unit.type", compute="_compute_allowed_unit_types", string="Allowed Unit Types")
    unit_type_id = fields.Many2one("repair.device.unit.type", string="Unit Type", required=True, domain="[('id', 'in', allowed_unit_type_ids)]")
    device_model_id = fields.Many2one("repair.device.model", string="Device Model", required=True, domain="[('manufacturer_id', '=', manufacturer_id), ('unit_type_id', '=', unit_type_id)]")
    imei = fields.Char('Imei', size=16)
    serial = fields.Char('Serial No', size=20)
    purchase_date = fields.Date('Date of purchase')
    
    # Logistics, Warranties, & Pipeline States
    in_warranty = fields.Boolean("In Warranty", default=False)
    warranty_exception = fields.Char("Reason for Warranty exception", size=255)
    warranty_notes = fields.Char("Warranty Notes", size=255)
    warranty_status = fields.Selection(WARRANTY_STATUS_SELECTION, string="Warranty Status", default="unclaimed")
    insurer = fields.Char('Insurance Company', size=128)
    policy_no = fields.Char("Policy Number", size=128)
    job_site = fields.Selection([("field_call", "Field Call"), ("workshop", "Workshop")], default='workshop')
    product_location = fields.Selection(PRODUCT_LOCATION_SELECTION, string="Product Location", required=True, default="customer")
    
    status_id = fields.Many2one('repair.status', string="Current Status", ondelete='restrict')
    status_history_ids = fields.One2many('repair.job.status.line', 'job_id', string="Status Logs", readonly=True)
    quote_status = fields.Selection(QUOTE_STATUS_SELECTION, string="Quote Status", default="not_required")
    repair_type = fields.Selection([("customer", "Customer"), ("installation", "Installation"), ("stock", "Stock")], default="customer")
    estimate_required = fields.Boolean("Estimate Required", default=False)
    estimate_accepted = fields.Boolean("Estimate Accepted", default=True)
    estimate_status = fields.Selection(ESTIMATE_STATUS_SELECTION, string="Estimate Status", default="required")
    escalation_required = fields.Boolean("Escalation Required", default=False)
    cancel_reason = fields.Text("Reason for Cancel")
    network_ref_number = fields.Char("Network Ref No", size=64)

    # =========================================================================
    # ⚙️ ORCHESTRATION PIPELINE LOGS (CRUD Overrides)
    # =========================================================================
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
        self.env['repair.job.status.line'].create({
            'job_id': self.id,
            'status_id': status_id,
            'user_id': self.env.user.id,
            'changed_date': fields.Datetime.now()
        })

    # =========================================================================
    # 📱 COMPUTE & CASCADING RE-SETS
    # =========================================================================
    @api.depends('manufacturer_id')
    def _compute_allowed_unit_types(self):
        for rec in self:
            if rec.manufacturer_id:
                matching_models = self.env['repair.device.model'].search([
                    ('manufacturer_id', '=', rec.manufacturer_id.id)
                ])
                rec.allowed_unit_type_ids = [(6, 0, matching_models.mapped('unit_type_id').ids)]
            else:
                rec.allowed_unit_type_ids = [(5, 0, 0)]

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_reset_children(self):
        self.unit_type_id = False
        self.device_model_id = False

    @api.onchange('unit_type_id')
    def _onchange_unit_type_reset_model(self):
        self.device_model_id = False

    @api.depends_context('company')
    def _compute_current_company_role(self):
        for record in self:
            record.current_company_role = self.env.company.company_type_role or 'other'

    # =========================================================================
    # 🔄 AUTOMATION AND DYNAMIC VIEW CONTROL STATES
    # =========================================================================
    @api.onchange('client_id')
    def _onchange_client_reset_children(self):
        default_client_ref = self.env.ref('repair_clinics.company_default_client', raise_if_not_found=False)
        if self.client_id:
            if default_client_ref and self.client_id.id != default_client_ref.id:
                self.is_custom_client = True
                if self.branch_id and self.branch_id.parent_id != self.client_id:
                    self.branch_id = False
            else:
                self.is_custom_client = False

            parent_network = self.client_id.parent_id
            if parent_network and parent_network.company_type_role == 'network':
                self.network_id = parent_network
        else:
            self.branch_id = False
            self.is_custom_client = False

    @api.depends('current_company_role', 'network_id')
    def _compute_client_id_domain(self):
        for record in self:
            if record.current_company_role in ('super_admin', 'other', 'service_provider'):
                domain = [('company_type_role', '=', 'client')]
            elif record.network_id:
                domain = [('company_type_role', '=', 'client'), ('parent_id', '=', record.network_id.id)]
            else:
                domain = [('company_type_role', '=', 'client')]
            record.client_id_domain = json.dumps(domain)

    @api.depends('current_company_role')
    def _compute_hierarchy_readonly_states(self):
        for record in self:
            role = record.current_company_role
            record.network_id_read = role in ('network', 'client', 'branch', 'service_provider')
            record.client_id_read = role in ('client', 'branch')
            record.branch_id_read = role == 'branch'

    @api.onchange('network_id')
    def _onchange_network_reset_children(self):
        """Top-down reset: clears sub-choices only if they don't match the new network choice"""
        if self.network_id:
            # 🎯 Safety Guard: Only clear the client if it belongs to a DIFFERENT network
            if self.client_id and self.client_id.parent_id != self.network_id:
                self.client_id = False
                self.branch_id = False
        else:
            # If the network field itself is completely cleared, wipe out the branches/clients
            self.client_id = False
            self.branch_id = False

    # =========================================================================
    # 🔍 IMEI VALIDATION LOGIC (Luhn Checksum Formula)
    # =========================================================================
    def _is_valid_luhn_imei(self, imei_str):
        """Mathematically verifies an IMEI string using the Mod 10 Luhn formula"""
        if not imei_str or len(imei_str) != 15 or not imei_str.isdigit():
            return False
            
        digits = [int(d) for d in imei_str]
        # Step 1: Double every second digit from right to left starting from the 14th
        for i in range(13, -1, -2):
            doubled = digits[i] * 2
            # Step 2: If result is > 9, add the digits together (e.g., 14 -> 1 + 4 = 5, or 14 - 9 = 5)
            digits[i] = doubled if doubled <= 9 else doubled - 9
            
        # Step 3: Sum all values. If it divides cleanly by 10, the checksum balances
        return sum(digits) % 10 == 0
    
    @api.onchange('imei')
    def _onchange_imei_verify_format(self):
        if self.imei:
            clean_imei = re.sub(r'[\s-]','',self.imei)
            self.imei = clean_imei
            if not self._is_valid_luhn_imei(clean_imei):
                return {
                    'warning': {
                        'title': "Invalid IMEI Format",
                        'message': "The IMEI entered is invalid. Please double-check the 15-digit number. It fails the checksum calculation.",
                        'type': 'notification'
                    }
                }

    @api.constrains('imei')
    def _check_imei_database_integrity(self):
        for record in self:
            if record.imei:
                # Disallow any saves if the field calculation fails the check
                if not record._is_valid_luhn_imei(record.imei):
                    raise ValidationError(
                        "Database Error: Cannot save record. The IMEI number '%s' is structurally malformed or failed the Luhn mathematical integrity check." % record.imei
                    )