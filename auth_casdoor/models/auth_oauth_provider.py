# Copyright 2021 The Casdoor Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from odoo import api, fields, models


class AuthOAuthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    casdoor_endpoint = fields.Char(
        string="Casdoor URL",
        help="URL of the Casdoor server, e.g. https://door.casdoor.com. Setting it makes this provider "
        "a Casdoor provider and fills in the authorization and user info URLs.",
    )
    client_secret = fields.Char(groups="base.group_system")

    @api.model
    def _casdoor_endpoint_values(self, endpoint):
        endpoint = (endpoint or "").strip().rstrip("/")
        if not endpoint:
            return {}
        return {
            "casdoor_endpoint": endpoint,
            "auth_endpoint": endpoint + "/login/oauth/authorize",
            "validation_endpoint": endpoint + "/api/userinfo",
            "data_endpoint": False,
        }

    @api.onchange("casdoor_endpoint")
    def _onchange_casdoor_endpoint(self):
        for provider in self:
            provider.update(self._casdoor_endpoint_values(provider.casdoor_endpoint))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(self._casdoor_endpoint_values(vals.get("casdoor_endpoint")))
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("casdoor_endpoint"):
            vals = dict(vals, **self._casdoor_endpoint_values(vals["casdoor_endpoint"]))
        return super().write(vals)

    def _casdoor_token_endpoint(self):
        self.ensure_one()
        return self.casdoor_endpoint + "/api/login/oauth/access_token"
