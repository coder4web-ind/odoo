from odoo import models, fields
from odoo.models import UniqueIndex, Index

class RepairDeviceManufacturer(models.Model):
    _name = "repair.manufacturer"
    _description = "Table for electronics gadgets manufacturer"

    name = fields.Char("Manufacturer Name", size=64, required=True)
    acronym = fields.Char("Acronym", size=64, required=True)
    logo = fields.Binary("Logo")
    imei_required = fields.Boolean("IMEI Required", default=True)
    serial_no_required = fields.Boolean("Serial No Required", default=True)
    active = fields.Boolean(string="Active", default=True)

    _unique_manufacturer_acronym = UniqueIndex(['acronym'])
    _index_name_idx = Index(['name'])
    _index_acronym_idx = Index(['acronym'])