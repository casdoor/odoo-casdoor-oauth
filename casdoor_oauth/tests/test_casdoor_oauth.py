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
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import AccessDenied
from odoo.tests import TransactionCase, tagged

from ..models import res_users

USERINFO = {
    "sub": "casdoor-oauth-test-subject",
    "iss": "https://door.casdoor.com",
    "aud": "odoo-client-id",
    "preferred_username": "alice",
    "name": "Alice",
    "email": "casdoor-oauth-test@example.com",
}


class FakeResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status_code = status
        self.ok = status < 400

    def json(self):
        return dict(self.data)


@tagged("post_install", "-at_install")
class TestCasdoorOAuth(TransactionCase):
    def setUp(self):
        super().setUp()
        self.provider = self.env.ref("casdoor_oauth.provider_casdoor")
        self.provider.write(
            {
                "casdoor_endpoint": "https://casdoor.example.com/",
                "client_id": "odoo-client-id",
                "client_secret": "odoo-client-secret",
                "enabled": True,
            }
        )
        self.env["ir.config_parameter"].sudo().set_param("auth_signup.invitation_scope", "b2c")
        self.session = {}
        fake_request = SimpleNamespace(
            session=self.session, httprequest=SimpleNamespace(url_root="http://odoo.example.com/")
        )
        request_patcher = patch.object(res_users, "request", fake_request)
        request_patcher.start()
        self.addCleanup(request_patcher.stop)
        self.posts = []

    def params(self, nonce=None, **kwargs):
        if nonce is None:
            nonce = res_users.get_login_nonce(self.session)
        state = {"d": self.env.cr.dbname, "p": self.provider.id, "r": "http%3A%2F%2Fodoo.example.com%2Fweb", "n": nonce}
        return dict({"code": "the-code", "state": json.dumps(state)}, **kwargs)

    def sign_in(self, params, token=None, userinfo=None):
        token = token if token is not None else {"access_token": "the-access-token", "token_type": "Bearer"}
        userinfo = userinfo if userinfo is not None else USERINFO

        def fake_post(url, data=None, timeout=None):
            self.posts.append((url, data))
            return FakeResponse(token)

        def fake_get(url, headers=None, timeout=None):
            self.assertEqual(url, "https://casdoor.example.com/api/userinfo")
            self.assertEqual(headers, {"Authorization": "Bearer the-access-token"})
            return FakeResponse(userinfo)

        with patch.object(res_users.requests, "post", fake_post), patch.object(res_users.requests, "get", fake_get):
            return self.env["res.users"].sudo().auth_oauth(self.provider.id, params)

    def test_endpoints_follow_casdoor_url(self):
        self.assertEqual(self.provider.casdoor_endpoint, "https://casdoor.example.com")
        self.assertEqual(self.provider.auth_endpoint, "https://casdoor.example.com/login/oauth/authorize")
        self.assertEqual(self.provider.validation_endpoint, "https://casdoor.example.com/api/userinfo")

    def test_sign_in_creates_user(self):
        dbname, login, access_token = self.sign_in(self.params())
        self.assertEqual((dbname, login, access_token), (self.env.cr.dbname, "casdoor-oauth-test@example.com", "the-access-token"))
        self.assertEqual(
            self.posts,
            [
                (
                    "https://casdoor.example.com/api/login/oauth/access_token",
                    {
                        "grant_type": "authorization_code",
                        "client_id": "odoo-client-id",
                        "client_secret": "odoo-client-secret",
                        "code": "the-code",
                        "redirect_uri": "http://odoo.example.com/auth_oauth/signin",
                    },
                )
            ],
        )
        user = self.env["res.users"].search([("login", "=", "casdoor-oauth-test@example.com")])
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.oauth_uid, USERINFO["sub"])
        self.assertEqual(user.oauth_provider_id, self.provider)
        self.assertNotIn(res_users.NONCE_SESSION_KEY, self.session)

    def test_sign_in_again_finds_user_by_subject(self):
        self.sign_in(self.params())
        _, login, _ = self.sign_in(self.params(), userinfo=dict(USERINFO, email="new@example.com"))
        self.assertEqual(login, "casdoor-oauth-test@example.com")

    def test_rejects_wrong_state(self):
        res_users.get_login_nonce(self.session)
        with self.assertRaises(AccessDenied):
            self.sign_in(self.params(nonce="forged"))
        self.assertEqual(self.posts, [])

    def test_rejects_state_from_another_session(self):
        params = self.params()
        self.session.clear()
        with self.assertRaises(AccessDenied):
            self.sign_in(params)

    def test_state_is_single_use(self):
        params = self.params()
        self.sign_in(params)
        with self.assertRaises(AccessDenied):
            self.sign_in(params)

    def test_rejects_implicit_flow_token(self):
        params = self.params()
        del params["code"]
        params["access_token"] = "token-of-another-app"
        with self.assertRaises(AccessDenied):
            self.sign_in(params)

    def test_rejects_casdoor_error(self):
        with self.assertRaises(AccessDenied):
            self.sign_in(self.params(error="access_denied"))

    def test_rejects_token_error(self):
        with self.assertRaises(AccessDenied):
            self.sign_in(self.params(), token={"error": "invalid_grant", "error_description": "code has been used"})

    def test_rejects_token_of_another_application(self):
        with self.assertRaises(AccessDenied):
            self.sign_in(self.params(), userinfo=dict(USERINFO, aud="another-client-id"))

    def test_rejects_invalid_userinfo(self):
        with self.assertRaises(AccessDenied):
            self.sign_in(self.params(), userinfo={"status": "error", "msg": "Invalid JWT token"})

    def test_other_providers_are_untouched(self):
        other = self.env["auth.oauth.provider"].create(
            {
                "name": "Other",
                "auth_endpoint": "https://other.example.com/auth",
                "validation_endpoint": "https://other.example.com/userinfo",
                "body": "Other",
            }
        )
        self.assertFalse(other.casdoor_endpoint)
        with patch("odoo.addons.auth_oauth.models.res_users.ResUsers._auth_oauth_rpc", return_value={"error": "x"}):
            with self.assertRaises(Exception):
                self.env["res.users"].sudo().auth_oauth(other.id, {"access_token": "x", "state": "{}"})
        self.assertEqual(self.posts, [])
