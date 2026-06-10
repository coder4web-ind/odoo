from odoo import models,fields
from odoo.models import Constraint, UniqueIndex, Index

class RepairDeviceManufacturer(models.Model):
    _name = "repair.device.manufacturer"
    _description = "Table for electronics gadgets manufacturer"

    name = fields.Char("Manufacturer Name",size=64,required=True)
    acronym = fields.Char("Acronym",size=64,required=True)
    logo = fields.Binary("Logo")    
    pop_period = fields.Integer("POP Period")
    fault_code_required = fields.Boolean("Fault Code Required",default=False)
    serial_no_required = fields.Boolean("Serial No Required",default=True)
    serial_no_format = fields.Char("Serial No Format",size=20)
    active = fields.Boolean(string="Active", default=True)
    etd_date_enabled = fields.Boolean("ETD date enabled",default=True)
    etd_date_days = fields.Integer("ETD date days")