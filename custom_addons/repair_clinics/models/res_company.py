from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    company_type_role = fields.Selection(
        selection='_get_company_type_role_selection',
        string="Company Type Role", 
        required=True, 
        index=True
    )
    
    def _get_company_type_role_selection(self):
        options = [
            ('network', 'Network'),
            ('client', 'Client'),
            ('branch', 'Branch'),
            ('service_provider', 'Service Provider')
        ]
        if self.company_type_role == 'super_admin' or self.env.is_admin():
            if ('super_admin', 'Super Admin') not in options:
                options.append(('super_admin', 'Super Admin'))
        return options
    
    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        if 'company_type_role' in vals:
            # Find all users linked to this company
            users = self.env['res.users'].search([('company_id', 'in', self.ids)])
            if users:
                users.sudo()._manage_manufacturer_manager_group()
        return res

    
    company_type_role = fields.Selection(
        selection='_get_company_type_role_selection',
        string="Company Type Role", 
        required=True, 
        index=True
    )