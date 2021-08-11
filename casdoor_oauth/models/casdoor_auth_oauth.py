# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class CasdoorOAuthProvider(models.Model):

    _inherit = 'auth.oauth.provider'

    client_secret = fields.Char(string='Client secret') # the secret for verification
    casdoor_username = fields.Char(string='Casdoor username') # Casdoor's username of current user
