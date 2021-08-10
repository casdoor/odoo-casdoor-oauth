# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    auth_oauth_casdoor_enabled = fields.Boolean(string='Active')
    auth_oauth_casdoor_client_id = fields.Char(string='Casdoor Client ID')  # Our identifier
    auth_oauth_casdoor_client_secret = fields.Char(string='Casdoor Client Secret')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        casdoor_provider = self.env.ref('casdoor_oauth.provider_casdoor', False)
        casdoor_provider and res.update(
            auth_oauth_casdoor_enabled=casdoor_provider.enabled,
            auth_oauth_casdoor_client_id=casdoor_provider.client_id,
            auth_oauth_casdoor_client_secret=casdoor_provider.client_secret,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        casdoor_provider = self.env.ref('casdoor_oauth.provider_casdoor', False)
        casdoor_provider and casdoor_provider.write({
            'enabled': self.auth_oauth_casdoor_enabled,
            'client_id': self.auth_oauth_casdoor_client_id,
            'client_secret': self.auth_oauth_casdoor_client_secret,
        })
