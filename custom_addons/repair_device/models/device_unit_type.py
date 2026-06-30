from odoo import models, fields

class RepairDeviceUnityType(models.Model):
    _name = "repair.device.unit.type"
    _description = "Table for electronics gadgets devices models type"
    _order = "ranking desc, name asc"
    
    # Core Data Schema Columns
    ranking = fields.Integer(string="Ranking Priority", default=0)
    name = fields.Char("Device Type Name", size=64, required=True)
    imei_required = fields.Selection([("yes", "Yes"), ("no", "No")], string="IMEI Required",default='no')
    serial_no_required = fields.Selection([("yes", "Yes"), ("no", "No")], string="Serial No Required",default='no')
    serial_no_format = fields.Char("Pattern for Serial No", size=20)
    dop_warranty_period = fields.Integer(string="Warranty Period from Purchase (Months)", default=12)    
    active = fields.Boolean(string="Active", default=True)

    
    _unique_name = models.Constraint(
        'unique(name)', 
        'The Device Type Name must be unique! This classification name already exists in the system layout.'
    )