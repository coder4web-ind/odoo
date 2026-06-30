from odoo import models,fields
from odoo.models import Constraint,UniqueIndex,Index

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
    manufacturer_ids = fields.Many2many(
        "repair.device.manufacturer",
        "repair_job_type_manufacturer_rel",
        "job_type_id",
        "manufacturer_id",
        string="Allowed Manufacturer"
    )

    _unique_name = Constraint("unique(name)", "The name must be unique!")
    _unique_code = Constraint("unique(code)", "The code must be unique!")


