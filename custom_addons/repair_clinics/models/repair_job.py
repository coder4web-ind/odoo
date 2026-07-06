from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime,timezone

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"
    

    name = fields.Char('Ticket #', default='New', readonly=True, copy=False)
    summary = fields.Text('Summary', required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    
    device_brand_id = fields.Many2one("repair.device.brand", string="Device Brand", required=True)
    allowed_device_category_ids = fields.Many2many("repair.device.category", compute="_compute_allowed_device_categories", string="Allowed Categories")
    device_category_id = fields.Many2one("repair.device.category", string="Device Category", required=True, domain="[('id', 'in', allowed_device_category_ids)]")
    device_id = fields.Many2one("repair.device", string="Device", required=True, domain="[('device_brand_id', '=', device_brand_id), ('device_category_id', '=', device_category_id)]")
    
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
    cancel_notes = fields.Text('Cancel Notes')
    repair_complete_date = fields.Datetime("Date of Repair Complete")
    active = fields.Boolean(string="Active", default=True)

    '''
        check if IMEI and Serial No required on Repair Job Booking
        at Device level,Category Level or Brand level
    '''

    @api.depends('device_brand_id', 'device_category_id', 'device_id')
    def _compute_imei_serial_required(self):
        for rec in self:            
            imei_req = False
            if rec.device_id and getattr(rec.device_id, 'imei_required', False):
                imei_req = rec.device_id.imei_required
            elif rec.device_category_id and getattr(rec.device_category_id, 'imei_required', False):
                imei_req = rec.device_category_id.imei_required
            elif rec.device_brand_id and getattr(rec.device_brand_id, 'imei_required', False): 
                imei_req = rec.device_brand_id.imei_required

            
            serial_req = False
            if rec.device_id and getattr(rec.device_id, 'serial_no_required', False):
                serial_req = rec.device_id.serial_no_required
            elif rec.device_category_id and getattr(rec.device_category_id, 'serial_no_required', False):
                serial_req = rec.device_category_id.serial_no_required
            elif rec.device_brand_id and getattr(rec.device_brand_id, 'serial_no_required', False):
                serial_req = rec.device_brand_id.serial_no_required
            
            rec.imei_required = imei_req
            rec.serial_required = serial_req

            

    @api.depends('device_brand_id')
    def _compute_allowed_device_categories(self):
        for rec in self:
            if rec.device_brand_id:                
                matching_models = self.env['repair.device'].search([
                    ('device_brand_id', '=', rec.device_brand_id.id)
                ])
                rec.allowed_device_category_ids = [(6, 0, matching_models.mapped('device_category_id').ids)]
            else:
                rec.allowed_device_category_ids = [(6, 0, [])]

    @api.onchange('device_brand_id')
    def _onchange_brand_reset_children(self):
        self.device_category_id = False
        self.device_id = False

    @api.onchange('device_category_id')
    def _onchange_category_reset_model(self):
        self.device_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New" or vals.get("name", "/") == "/":
                now = datetime.now()
                date_str = now.strftime("%Y%m%d") 
                
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                country_code = partner.country_id.code if partner.country_id and partner.country_id.code else 'XX'
                
                search_prefix = f"Repair{date_str}"                
                last_job = self.search([('name', '=like', f"{search_prefix}%")], order='name desc', limit=1)
                next_number = 1
                
                if last_job:
                    try:
                        last_sequence_str = last_job.name.split("_")[-1]
                        next_number = int(last_sequence_str) + 1
                    except (ValueError, IndexError):
                        next_number = 1

                vals['name'] = f"{search_prefix}{country_code}_{next_number}"


                if vals.get('state') == 'draft':
                    vals['state'] = 'received'
        
        return super().create(vals_list)
    

    def wrtie(self,vals):
        if 'state' in vals:
            new_state = vals.get('state')
            if new_state in ('done','delivered'):
                vals['repair_complete_date'] = datetime.now(timezone.utc)
            else:
                vals['repair_complete_date'] = False

        return super().write(vals)
    

    def unlink(self):
        for job in self:
            # Block deletion if the job has progressed past draft or received
            if job.state not in ['draft', 'received']:
                raise UserError(_(
                    "Security Restriction: You can only delete repair jobs that are in 'Draft' or 'Received' status. "
                    "Job (%s) is currently '%s' and cannot be removed."
                ) % (job.name, job.state.capitalize()))        
        
        return super(RepairJob, self).unlink()
