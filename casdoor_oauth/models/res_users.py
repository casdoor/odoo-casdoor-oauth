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
import hmac
import json
import logging
import secrets

import requests

from odoo import api, models
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)

NONCE_SESSION_KEY = "casdoor_oauth_nonce"


def get_login_nonce(session):
    """Return the nonce put in the state of the Casdoor login link, bound to the browser's session."""
    nonce = session.get(NONCE_SESSION_KEY)
    if not nonce:
        nonce = secrets.token_urlsafe(32)
        session[NONCE_SESSION_KEY] = nonce
    return nonce


def get_redirect_uri(httprequest):
    return httprequest.url_root + "auth_oauth/signin"


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def auth_oauth(self, provider, params):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)
        if not oauth_provider.casdoor_endpoint:
            return super().auth_oauth(provider, params)

        if params.get("error"):
            _logger.info("Casdoor sign-in failed: %s %s", params["error"], params.get("error_description", ""))
            raise AccessDenied()
        self._casdoor_check_state(params)
        if not params.get("code"):
            # never accept an access token passed in the URL (implicit flow), it could be issued to another app
            raise AccessDenied()

        access_token = self._casdoor_get_access_token(oauth_provider, params["code"])
        return super().auth_oauth(provider, dict(params, access_token=access_token))

    @api.model
    def _casdoor_check_state(self, params):
        try:
            nonce = json.loads(params.get("state") or "{}").get("n")
        except (ValueError, AttributeError):
            nonce = None
        expected = request.session.pop(NONCE_SESSION_KEY, None) if request else None
        if not nonce or not expected or not hmac.compare_digest(str(nonce), expected):
            _logger.info("Casdoor sign-in failed: invalid state")
            raise AccessDenied()

    @api.model
    def _casdoor_get_access_token(self, oauth_provider, code):
        response = requests.post(
            oauth_provider._casdoor_token_endpoint(),
            data={
                "grant_type": "authorization_code",
                "client_id": oauth_provider.client_id,
                "client_secret": oauth_provider.sudo().client_secret,
                "code": code,
                "redirect_uri": get_redirect_uri(request.httprequest),
            },
            timeout=10,
        )
        try:
            token = response.json()
        except ValueError:
            token = None
        if not isinstance(token, dict):
            token = {}
        access_token = token.get("access_token")
        if not access_token or access_token.startswith("error:"):
            _logger.info(
                "Casdoor sign-in failed: cannot get the access token: %s",
                token.get("error_description") or token.get("error") or access_token or response.status_code,
            )
            raise AccessDenied()
        return access_token

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)
        if not oauth_provider.casdoor_endpoint:
            return super()._auth_oauth_validate(provider, access_token)

        response = requests.get(
            oauth_provider.validation_endpoint,
            headers={"Authorization": "Bearer %s" % access_token},
            timeout=10,
        )
        try:
            validation = response.json() if response.ok else {}
        except ValueError:
            validation = {}
        if not isinstance(validation, dict) or not validation.get("sub"):
            _logger.info("Casdoor sign-in failed: invalid user info: %s", validation)
            raise AccessDenied()
        if validation.get("aud") != oauth_provider.client_id:
            _logger.info("Casdoor sign-in failed: the access token was issued to %s", validation.get("aud"))
            raise AccessDenied()

        validation["user_id"] = validation.pop("sub")
        return validation
