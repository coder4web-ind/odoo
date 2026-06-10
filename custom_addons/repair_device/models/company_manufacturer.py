from odoo import models,fields,api
from odoo.models import Constraint, UniqueIndex, Index

class RepairCompanyManufacturerRel(models.Model):
    _name = "repair.company.manufacturer.rel"
    _description = "Company Specific Manufacturer Details"
    _rec_name = "manufacturer_id" 
    company_id = fields.Many2one("res.company", string="Service Provider", required=True, default=lambda self: self.env.company)
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