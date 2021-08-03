# -*- coding: utf-8 -*-
# from odoo import http


# class CasdoorOauth(http.Controller):
#     @http.route('/casdoor_oauth/casdoor_oauth/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/casdoor_oauth/casdoor_oauth/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('casdoor_oauth.listing', {
#             'root': '/casdoor_oauth/casdoor_oauth',
#             'objects': http.request.env['casdoor_oauth.casdoor_oauth'].search([]),
#         })

#     @http.route('/casdoor_oauth/casdoor_oauth/objects/<model("casdoor_oauth.casdoor_oauth"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('casdoor_oauth.object', {
#             'object': obj
#         })
