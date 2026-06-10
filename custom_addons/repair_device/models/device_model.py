from odoo import models, fields
from odoo.models import Constraint, UniqueIndex, Index

class RepairDeviceModel(models.Model):
    _name = "repair.device.model"
    _description = "Table for electronics gadgets devices models"
    
    name = fields.Char("Model Name", size=64, required=True)
    description = fields.Text("Model Description")
    code = fields.Char("Model Code", size=64, required=True)
    manufacturer_id = fields.Many2one("repair.device.manufacturer", string="Manufacturer", required=True)
    imei_required = fields.Boolean("IMEI Required", default=False)
    imei_length = fields.Integer("IMEI Length", default=15)
    serialno_required = fields.Boolean("Serial No Required", default=True)
    serial_no_format = fields.Char("Pattern for Serial No", size=20)
    active = fields.Boolean(string="Active", default=True)
    etd_date_enabled = fields.Boolean("ETD date enabled",default=True)
    etd_date_days = fields.Integer("ETD date days")
    pop_period = fields.Integer("POP Period")
    
    # =========================================================================
# 🎯 FIXED ODOO 19 INDEXES (Explicit SQL Expressions, No Message String)
# =========================================================================
_unique_manufacturer_code = UniqueIndex("(manufacturer_id, code)")

_index_name_idx = Index("(name)") 
_index_code_idx = Index("(code)")