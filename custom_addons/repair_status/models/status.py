from odoo import models,fields

class RepairStatus(models.Model):
    _name = "repair.status"
    _description = "Status for job life cycle"
    _order = "sequence, id"

    name = fields.Char(string="Status Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    notes = fields.Text(string="Internal Notes")
    active = fields.Boolean(string="Active", default=True)
    