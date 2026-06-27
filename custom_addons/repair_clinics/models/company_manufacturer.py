from odoo import models,fields,api
from odoo.models import Constraint, UniqueIndex, Index

class RepairCompanyManufacturerRel(models.Model):
    _name = "repair.company.manufacturer.rel"
    _description = "Company Specific Manufacturer Details"
    _rec_name = "manufacturer_id" 
    company_id = fields.Many2one(
        "res.company", 
        string="Service Provider", 
        required=True, 
        default=lambda self: self.env.company,
        domain="[('company_type_role','=','service_provider')]"
    )
    manufacturer_id = fields.Many2one("repair.device.manufacturer", string="Manufacturer", required=True, ondelete='cascade')
    communication = fields.Selection([
        ("enabled", "Enabled"),
        ("disabled", "Disabled")
    ], string="Job Communication", default="disabled")
    account_no = fields.Char("Account No", size=64)
    comm_user_name = fields.Char("API User Name",size=64)
    comm_password = fields.Char("API Password",size=64)
    token = fields.Char("Access Token",size=255)
    active = fields.Boolean(string="Active", default=True)    
    contact_person = fields.Char(string="Contact Person")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")    
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip/Postal Code")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")

    
    _unique_company_manufacturer = UniqueIndex("(company_id, manufacturer_id)")

    def action_open_popup(self):
        """ Opens the row inside a popup while safely preserving the relationship link """
        self.ensure_one()
        
        # 1. Safely find the parent manufacturer ID
        # If it's a new line, pull it from the active context window
        manufacturer_id = self.manufacturer_id.id or self.env.context.get('active_id')
        
        # 2. Return the window action layout dynamically
        return {
            'name': 'Service Provider Details',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,  # Passes the exact row ID if it exists (False if it's a new line)
            'view_mode': 'form',
            'view_id': self.env.ref('repair_clinics.repair_clinic_comapany_manufacturer_rel_form').id,
            'target': 'new',    # Forces it into a modal popup dialog box
            'context': {
                **self.env.context,
                'default_manufacturer_id': manufacturer_id,  # Guarantees the link is never lost!
            }
        }