from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    
    def _get_company_type_role_selection(self):
        options = [
            ('network', 'Network'),
            ('client', 'Client'),
            ('branch', 'Branch'),
            ('service_provider', 'Service Provider')
        ]
        # Only display Super Admin if the current record ALREADY is a Super Admin,
        # or if a system administrator is logged in. Otherwise, hide it!
        if self.company_type_role == 'super_admin' or self.env.is_admin():
            if ('super_admin', 'Super Admin') not in options:
                options.append(('super_admin', 'Super Admin'))
        return options

    
    company_type_role = fields.Selection(
        selection='_get_company_type_role_selection',
        string="Company Type Role", 
        required=True, 
        index=True
    )