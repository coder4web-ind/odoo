from odoo import models, fields, api
import json

class RepairJob(models.Model):
    _name = "repair.job"
    _description = "Repair Job Management"

    # =========================================================================
    # 🎯 STEP 1: DEFINE STABLE HIERARCHY FIELDS WITH INTRINSIC DEFAULTS
    # =========================================================================
    network_id = fields.Many2one(
        'res.company', string='Network',
        default=lambda self: self.env.ref('repair_clinics.company_default_network', raise_if_not_found=False),
        domain="[('company_type_role', '=', 'network')]"
    )

    client_id = fields.Many2one(
        'res.company', string='Client', 
        default=lambda self: self.env.ref('repair_clinics.company_default_client', raise_if_not_found=False),
        domain="[('company_type_role', '=', 'client')]"
    )

    branch_id = fields.Many2one(
        'res.company', string="Branch", 
        default=lambda self: self.env.ref('repair_clinics.company_default_branch', raise_if_not_found=False), 
        domain="[('company_type_role', '=', 'branch')]"
    )

    # UI Flow Helper Fields (Not stored in database)
    current_company_role = fields.Char(compute="_compute_current_company_role", store=False)
    client_id_domain = fields.Char(compute='_compute_client_id_domain', store=False)
    
    # 🎯 NEW: Tracks if the SP departed from the default walk-in client configuration
    is_custom_client = fields.Boolean(string="Is Custom Client Selected", default=False, store=False)

    @api.depends_context('company')
    def _compute_current_company_role(self):
        for record in self:
            record.current_company_role = self.env.company.company_type_role or 'other_user'

    @api.depends('current_company_role', 'network_id')
    def _compute_client_id_domain(self):
        for record in self:
            if record.current_company_role in ('super_admin', 'other_user'):
                domain = [('company_type_role', '=', 'client')]
            elif record.current_company_role == 'service_provider':
                # Allow SP to choose ANY client in the system, not just defaults!
                domain = [('company_type_role', '=', 'client')]
            else:
                domain = [('company_type_role', '=', 'client'), ('parent_id', '=', record.network_id.id)]
            record.client_id_domain = json.dumps(domain)

    # =========================================================================
    # 🔄 STEP 2: TOP-DOWN AUTOMATION (Sets parent Network & enforces rules)
    # =========================================================================
    @api.onchange('client_id')
    def _onchange_client_id_pull_network(self):
        """If client changes, auto-calculate its parent network, and toggle UI rule flags"""
        default_client_ref = self.env.ref('repair_clinics.company_default_client', raise_if_not_found=False)
        
        if self.client_id:
            # 1. If it's different from the default "Direct" record, flip our rule tracker to True
            if default_client_ref and self.client_id.id != default_client_ref.id:
                self.is_custom_client = True
                # Clear out old branch choice to force them to select a branch matching this new client
                if self.branch_id and self.branch_id.parent_id != self.client_id:
                    self.branch_id = False
            else:
                self.is_custom_client = False

            # 2. Automatically trace up and assign the Network ID from the selected Client's parent
            parent_network = self.client_id.parent_id
            if parent_network and parent_network.company_type_role == 'network':
                self.network_id = parent_network
        else:
            self.is_custom_client = False