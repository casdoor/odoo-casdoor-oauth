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
import json
from urllib.parse import urlencode

from odoo.http import request

from odoo.addons.auth_oauth.controllers.main import OAuthLogin

from ..models.res_users import get_login_nonce, get_redirect_uri


class CasdoorOAuthLogin(OAuthLogin):
    def list_providers(self):
        providers = super().list_providers()
        for provider in providers:
            provider.pop("client_secret", None)
            if not provider.get("casdoor_endpoint"):
                continue

            state = self.get_state(provider)
            state["n"] = get_login_nonce(request.session)
            params = {
                "response_type": "code",
                "client_id": provider["client_id"],
                "redirect_uri": get_redirect_uri(request.httprequest),
                "scope": provider["scope"],
                "state": json.dumps(state),
            }
            provider["auth_link"] = "%s?%s" % (provider["auth_endpoint"], urlencode(params))
        return providers
