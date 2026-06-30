import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"
    _inherit = ['mail.thread']


    name = fields.Char('Ticket #', default='New', readonly=True, copy=False)
    summary = fields.Char('Summary', size=256, required=True)
    description = fields.Text("Complaint Details", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    
    manufacturer_id = fields.Many2one("repair.device.manufacturer", string="Device Manufacturer", required=True)
    allowed_unit_type_ids = fields.Many2many("repair.device.unit.type", compute="_compute_allowed_unit_types", string="Allowed Unit Types")
    device_type_id = fields.Many2one("repair.device.unit.type", string="Unit Type", required=True, domain="[('id', 'in', allowed_unit_type_ids)]")
    device_model_id = fields.Many2one("repair.device.model", string="Device Model", required=True, domain="[('manufacturer_id', '=', manufacturer_id), ('device_type_id', '=', device_type_id)]")
    
    imei_required = fields.Boolean(compute='_compute_imei_serial_required', store=False)
    serial_required = fields.Char(compute='_compute_imei_serial_required', store=False)

    imei = fields.Char('IMEI', size=16)
    serial = fields.Char('Serial No', size=64)

    
    
    in_warranty = fields.Boolean("In Warranty", default=False)
    purchase_date = fields.Date('Date of purchase')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('repairing', 'Repairing'), 
        ('done', 'Done'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)
    invoice_id = fields.Many2one('account.move', 'Invoice', copy=False)
    cancel_reason = fields.Text('Cancel Reason')
    repair_complete_date = fields.Datetime("Date of Repair Complete")

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

            serial_mask = False
            if rec.device_model_id and getattr(rec.device_model_id, 'serial_no_required', True) and rec.device_model_id.serial_no_format:
                serial_mask = rec.device_model_id.serial_no_format
            elif rec.device_type_id and getattr(rec.device_type_id, 'serial_no_required', True) and rec.device_type_id.serial_no_format:
                serial_mask = rec.device_type_id.serial_no_format
            elif rec.manufacturer_id and getattr(rec.manufacturer_id, 'serial_no_required', True) and rec.manufacturer_id.serial_no_format:
                serial_mask = rec.manufacturer_id.serial_no_format
            
            rec.imei_required = imei_req
            rec.serial_required = serial_mask


    

    @api.depends('manufacturer_id')
    def _compute_allowed_unit_types(self):
        for rec in self:
            if rec.manufacturer_id:
                matching_models = self.env['repair.device.model'].search([
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

    # =========================================================================
    # 🔍 IMEI VALIDATION LOGIC (Luhn Checksum Formula)
    # =========================================================================
    def _is_valid_luhn_imei(self, imei_str):
        """Mathematically verifies an IMEI string using the Mod 10 Luhn formula"""
        if not imei_str or len(imei_str) != 15 or not imei_str.isdigit():
            return False
            
        digits = [int(d) for d in imei_str]        
        for i in range(13, -1, -2):
            doubled = digits[i] * 2            
            digits[i] = doubled if doubled <= 9 else doubled - 9
            
        return sum(digits) % 10 == 0
    
    @api.onchange('imei')
    def _onchange_imei_verify_format(self):
        if self.imei:
            # 🎯 FIX 2: Safe string clean up execution
            clean_imei = re.sub(r'[\s-]', '', str(self.imei))
            if self.imei != clean_imei:
                self.imei = clean_imei
                
            if not self._is_valid_luhn_imei(clean_imei):
                return {
                    'warning': {
                        'title': "Invalid IMEI Format",
                        'message': "The IMEI entered is invalid. It fails the standard Luhn checksum calculation validation checks.",
                        'type': 'notification'
                    }
                }
            
    # =========================================================================
    # 🛡️ INTEGRITY DATABASE CONSTRAINTS
    # =========================================================================

    def _convert_mask_to_regex(self, mask_string):
        """
        Converts user-friendly layout formats into rigid Python Regular Expressions:
        'A' -> Letters only [A-Za-z]
        'N' -> Numbers only [0-9]
        'X' -> Alphanumeric [A-Za-z0-9]
        All other symbols (like dashes, dots, spaces) are treated as literal characters.
        """
        if not mask_string:
            return False
            
        regex_parts = []
        for char in mask_string:
            if char == 'A':
                regex_parts.append(r'[A-Za-z]')
            elif char == 'N':
                regex_parts.append(r'\d')
            elif char == 'X':
                regex_parts.append(r'[A-Za-z0-9]')
            else:                
                regex_parts.append(re.escape(char))
                
        return "".join(regex_parts)


    @api.constrains('serial', 'device_model_id', 'device_type_id', 'manufacturer_id')
    def _check_serial_format_fallback(self):
        for record in self:
            # 🎯 FIX: If a mask layout is configured, make sure they don't leave it blank!
            if record.serial_required and not record.serial:
                raise ValidationError("Operation Aborted: A serial number matching the mask '%s' is required." % record.serial_required)
            
            if record.serial:
                if record.serial_required:                   
                    regex_pattern = record._convert_mask_to_regex(record.serial_required)
                    pattern = re.compile(rf"^{regex_pattern}$")
                    if not pattern.match(record.serial):
                        raise ValidationError(
                            "Invalid Serial Number Format!\n\n"
                            "The serial '%s' does not match the required configuration layout mask: '%s'.\n\n"
                            "Format Guide:\n"
                            "• A = Letters only\n"
                            "• N = Numbers only\n"
                            "• X = Alphanumeric (Letters/Numbers)" 
                            % (record.serial, record.serial_required)
                        )
                

    @api.constrains('imei', 'device_model_id', 'device_type_id', 'manufacturer_id')
    def _check_imei_database_integrity(self):
        for record in self:            
            if record.imei_required and not record.imei:
                raise ValidationError("Operation Aborted: An IMEI number is required for this type of device.")

            if record.imei:                
                if not record._is_valid_luhn_imei(record.imei):
                    raise ValidationError(
                        "Database Error: The IMEI number '%s' is structurally malformed or failed the Luhn mathematical check." % record.imei
                    )
                
                check_job_exist = self.env['repair.job'].search_count([
                    ('id', '!=', record.id),
                    ('imei', '=', record.imei),
                    ('repair_complete_date', '=', False)
                ])

                if check_job_exist:
                    raise ValidationError(
                        "Operation Aborted: A repair job is already open for IMEI: %s" % record.imei
                    )
                
                
    @api.constrains('serial')
    def _check_serial_database_integrity(self):
        for record in self:
            if record.serial:                
                check_job_exist = self.env['repair.job'].search_count([
                    ('id', '!=', record.id),
                    ('serial', '=', record.serial),
                    ('repair_complete_date', '=', False)
                ])

                if check_job_exist:
                    raise ValidationError(
                        "Operation Aborted: A repair job is already open for Serial: %s" % record.serial
                    )