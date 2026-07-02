from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"
    _inherit = ['mail.thread']

    name = fields.Char('Ticket #', default='New', readonly=True, copy=False)
    summary = fields.Text('Summary', required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    
    manufacturer_id = fields.Many2one("repair.manufacturer", string="Device Manufacturer", required=True)
    allowed_unit_type_ids = fields.Many2many("repair.unit.type", compute="_compute_allowed_unit_types", string="Allowed Unit Types")
    device_type_id = fields.Many2one("repair.unit.type", string="Unit Type", required=True, domain="[('id', 'in', allowed_unit_type_ids)]")
    device_model_id = fields.Many2one("repair.model", string="Device Model", required=True, domain="[('manufacturer_id', '=', manufacturer_id), ('device_type_id', '=', device_type_id)]")
    
    imei_required = fields.Boolean(compute='_compute_imei_serial_required', store=False)
    serial_required = fields.Boolean(compute='_compute_imei_serial_required', store=False)

    imei = fields.Char('IMEI', size=16)
    serial = fields.Char('Serial No', size=64)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('repairing', 'Repairing'), 
        ('done', 'Done'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)    
    cancel_reason = fields.Text('Cancel Reason')
    repair_complete_date = fields.Datetime("Date of Repair Complete")
    active = fields.Boolean(string="Active", default=True)

    # =========================================================================
    # 📱 COMPUTE & CASCADING RE-SETS
    # =========================================================================

    @api.depends('manufacturer_id', 'device_type_id', 'device_model_id')
    def _compute_imei_serial_required(self):
        for rec in self:            
            imei_req = False
            if rec.device_model_id and getattr(rec.device_model_id, 'imei_required', False):
                imei_req = rec.device_model_id.imei_required
            elif rec.device_type_id and getattr(rec.device_type_id, 'imei_required', False):
                imei_req = rec.device_type_id.imei_required
            elif rec.manufacturer_id and getattr(rec.manufacturer_id, 'imei_required', False): 
                imei_req = rec.manufacturer_id.imei_required

            # ✅ Fixed: Evaluates the existing 'serial_no_required' fields safely
            serial_req = False
            if rec.device_model_id and getattr(rec.device_model_id, 'serial_no_required', False):
                serial_req = rec.device_model_id.serial_no_required
            elif rec.device_type_id and getattr(rec.device_type_id, 'serial_no_required', False):
                serial_req = rec.device_type_id.serial_no_required
            elif rec.manufacturer_id and getattr(rec.manufacturer_id, 'serial_no_required', False):
                serial_req = rec.manufacturer_id.serial_no_required
            
            rec.imei_required = imei_req
            rec.serial_required = serial_req

    @api.depends('manufacturer_id')
    def _compute_allowed_unit_types(self):
        for rec in self:
            if rec.manufacturer_id:
                # ✅ Fixed: Changed model key from 'repair.clinic.model' to your actual 'repair.model'
                matching_models = self.env['repair.model'].search([
                    ('manufacturer_id', '=', rec.manufacturer_id.id)
                ])
                rec.allowed_unit_type_ids = [(6, 0, matching_models.mapped('device_type_id').ids)]
            else:
                rec.allowed_unit_type_ids = [(6, 0, [])]

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_reset_children(self):
        self.device_type_id = False
        self.device_model_id = False

    @api.onchange('device_type_id')
    def _onchange_unit_type_reset_model(self):
        self.device_model_id = False