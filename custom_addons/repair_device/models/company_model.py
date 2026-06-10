from odoo import models, fields, api
from odoo.models import UniqueIndex

class RepairCompanyModelRel(models.Model):
    _name = "repair.company.model.rel"
    _description = "Company Specific Device Model Details"
    _rec_name = "model_id"

    # Core Relational Links
    company_id = fields.Many2one(
        "res.company", 
        string="Service Provider", 
        required=True, 
        default=lambda self: self.env.company,
        ondelete="cascade"
    )
    model_id = fields.Many2one(
        "repair.device.model", 
        string="Model", 
        required=True, 
        ondelete="cascade"
    )
    active = fields.Boolean(string="Active", default=True, index=True)
    
    imei_required = fields.Boolean("IMEI Required", default=False)
    imei_length = fields.Integer("IMEI Length", default=15)
    serialno_required = fields.Boolean("Serial No Required", default=True)
    serial_no_format = fields.Char("Pattern for Serial No", size=20)
    
    etd_date_enabled = fields.Boolean("ETD Date Enabled", default=True)
    etd_date_days = fields.Integer("ETD Lead Time (Days)", default=0)
    pop_period = fields.Integer("POP Period (Days)", default=0)
    
    _unique_company_model = UniqueIndex(
        ["company_id", "model_id"], 
        msg="A configuration for this Device Model already exists for this Service Provider branch!"
    )