from odoo import models, fields
from odoo.models import UniqueIndex, Index

class RepairDeviceBrand(models.Model):
    _name = "repair.device.brand"
    _description = "Table for electronics gadgets brands"

    name = fields.Char("Brand Name", size=64, required=True)
    code = fields.Char("Code", size=64, required=True)
    logo = fields.Binary("Logo")
    imei_required = fields.Boolean("IMEI Required", default=True)
    serial_no_required = fields.Boolean("Serial No Required", default=True)
    active = fields.Boolean(string="Active", default=True)

    _unique_manufacturer_code = UniqueIndex(['code'])
    _index_name_idx = Index(['name'])
    _index_code_idx = Index(['code'])