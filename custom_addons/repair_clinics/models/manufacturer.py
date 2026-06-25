from odoo import models,fields

class RepairDeviceManufacturer(models.Model):
    _inherit = "repair.device.manufacturer"
    job_type_ids = fields.Many2many(
        'repair.job.type',
        'repair_job_type_manufacturer_rel',
        'manufacturer_id',
        'job_type_id',
        string="Linked Job Types"
    )