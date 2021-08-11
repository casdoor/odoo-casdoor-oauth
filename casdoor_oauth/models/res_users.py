# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessDenied

from odoo.addons import base
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _auth_oauth_rpc(self, endpoint, provider, access_token):
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.name == "Casdoor":
            params = {
                "id": "built-in/" + str(oauth_provider.casdoor_username),
                "clientId": oauth_provider.client_id,
                "clientSecret": oauth_provider.client_secret,
            }
            return requests.get(endpoint, params=params).json()
        else:
            super(ResUsers, self)._auth_oauth_rpc(endpoint, access_token)

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.name == "Casdoor":
            validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, provider, access_token)
        else:
            validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        return validation

    @api.model
    def auth_oauth(self, provider, params):
        access_token = params.get('access_token') 
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.name == "Casdoor":

            casdoor_params = {
                "grant_type": "authorization_code",
                "client_id": oauth_provider.client_id,
                "client_secret": oauth_provider.client_secret,
                "code": params.get('code'),
            }

            r = requests.post(
                "http://test.casbin.com:8000/api/login/oauth/access_token", params=casdoor_params
            )        
            
            access_token = r.json().get("access_token")
            if "access_token" not in params:
                params["access_token"] = access_token

        validation = self._auth_oauth_validate(provider, access_token)
        # required check
        if not validation.get('user_id'):
            # Workaround: facebook does not send 'user_id' in Open Graph Api
            if validation.get('id'):
                validation['user_id'] = validation['id']
            else:
                raise AccessDenied()

        # retrieve and sign in user
        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            raise AccessDenied()
        # return user credentials
        return (self.env.cr.dbname, login, access_token)
