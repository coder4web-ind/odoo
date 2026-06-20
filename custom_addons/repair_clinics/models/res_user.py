from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        users.sudo()._manage_manufacturer_manager_group()
        return users

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'company_id' in vals or 'company_ids' in vals:
            self.sudo()._manage_manufacturer_manager_group()
        return res

    def _manage_manufacturer_manager_group(self):
        """Safely updates security groups using Odoo 19 'group_ids' field naming"""
        manager_group = self.env.ref('repair_device.group_repair_manufacturer_manager', raise_if_not_found=False)
        if not manager_group:
            return

        for user in self:
            company_role = user.company_id.company_type_role
            
            if company_role in ('service_provider', 'super_admin'):
                # 🎯 Odoo 19 standard: Use 'group_ids' with Command 4 (Link)
                if manager_group not in user.group_ids:
                    user.write({'group_ids': [(4, manager_group.id)]})
            else:
                # 🎯 Odoo 19 standard: Use 'group_ids' with Command 3 (Unlink)
                if manager_group in user.group_ids:
                    user.write({'group_ids': [(3, manager_group.id)]})