from odoo import models, fields
from odoo.models import UniqueIndex, Index


class RepairDeviceCategory(models.Model):
    _name = "repair.device.category"
    _description = "Table for electronics gadgets devices categories"
    _order = "ranking desc, name asc"

    ranking = fields.Integer(string="Ranking Priority", default=0)
    name = fields.Char("Device Category", size=64, required=True)
    
    # Converted to Booleans to match your other files perfectly
    imei_required = fields.Boolean("IMEI Required", default=False)
    serial_no_required = fields.Boolean("Serial No Required", default=True)
    active = fields.Boolean(string="Active", default=True)

    # Fixed syntax to match Odoo 18/19 constraint standards
    _unique_name = UniqueIndex(['name'])