from odoo import models, fields
from odoo.models import Constraint, UniqueIndex, Index

class RepairDeviceModel(models.Model):
    _name = "repair.model"
    _description = "Table for electronics gadgets devices models"

    name = fields.Char("Model Name", size=64, required=True)
    description = fields.Text("Model Description")
    code = fields.Char("Model Code", size=64, required=True)
    manufacturer_id = fields.Many2one("repair.manufacturer", string="Manufacturer", required=True)
    device_type_id = fields.Many2one("repair.unit.type", string="Unit Type", required=True)
    imei_required = fields.Boolean("IMEI Required", default=False)
    serial_no_required = fields.Boolean("Serial No Required", default=True)
    active = fields.Boolean(string="Active", default=True)

    # Fixed syntax arrays for multiple fields
    _unique_manufacturer_code = UniqueIndex(['manufacturer_id', 'code'])
    _unique_unit_type_code = UniqueIndex(['device_type_id', 'code'])
    
    _index_name_idx = Index(['name'])
    _index_code_idx = Index(['code'])