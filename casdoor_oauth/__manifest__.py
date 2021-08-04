# -*- coding: utf-8 -*-
{
    'name': "Casdoor OAuth",

    'summary': """OAuth plugin for Odoo by Casdoor""",

    'description': """
        It uses Casdoor's OAuth feature to log in Odoo for convenience.
    """,

    'author': "ffyuanda",
    'website': "https://github.com/casdoor/odoo-casdoor-oauth",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_oauth'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'data/casdoor_oauth_data.xml',
    ],
}
