from odoo import models,fields,api

class RepairJobStatusLine(models.Model):
    _name = "repair.job.status.line"
    _description = "Repair Job Status Tracking Log"
    _order = "changed_date desc" 

    job_id = fields.Many2one('repair.job', string="Repair Job", ondelete='cascade', required=True)
    status_id = fields.Many2one('repair.status', string="Status Attained", required=True)
    user_id = fields.Many2one('res.users', string="Technician", default=lambda self: self.env.user)
    changed_date = fields.Datetime(string="Date & Time Updated", default=fields.Datetime.now)