from odoo import models, fields
from odoo.models import Constraint, UniqueIndex, Index

class RepairDevice(models.Model):
    _name = "repair.device"
    _description = "Table for electronics gadgets devices models"

    name = fields.Char("Device Name", size=64, required=True)
    description = fields.Text("Device Description")
    code = fields.Char("Device Code", size=64, required=True)
    device_brand_id = fields.Many2one("repair.device.brand", string="Brand", required=True)
    device_category_id = fields.Many2one("repair.device.category", string="Category", required=True)
    imei_required = fields.Boolean("IMEI Required", default=False)
    serial_no_required = fields.Boolean("Serial No Required", default=True)
    active = fields.Boolean(string="Active", default=True)

    # Fixed syntax arrays for multiple fields
    _unique_manufacturer_code = UniqueIndex(['device_brand_id', 'code'])
    _unique_unit_type_code = UniqueIndex(['device_category_id', 'code'])
    
    _index_name_idx = Index(['name'])
    _index_code_idx = Index(['code'])