from odoo import models,fields

class RepairJobType(models.Model):
    _name = "repair.job.type"
    _description = "Type of Repair"
    name = fields.Char("Job Type", size=128,required=True)
    code = fields.Char("Code",size=64,required=True)
    description = fields.Text("Description",required=True)
    active = fields.Boolean("Active",default=True)
    imei_required = fields.Boolean("IMEI Required",default=False)
    serial_required = fields.Boolean("Serial Required", default=False)
    pop_validation = fields.Boolean("POP Validation",default=True)
    allow_exchange_unit = fields.Boolean("Allow Exchange Unit",default=False)

    _sql_constraints = [
        ('unique_name_constraint', 'UNIQUE(name)', 'Repair Type must be unique'),
        ('unique_code_constraint', 'UNIQUE(code)', 'Repair Type code must be unique'),
    ]

