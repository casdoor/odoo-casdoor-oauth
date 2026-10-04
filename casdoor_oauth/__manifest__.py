{
    "name": "Casdoor OAuth",
    "summary": "Sign in to Odoo with Casdoor",
    "description": """
Sign in to Odoo with Casdoor (https://casdoor.ai) using the OAuth 2.0 authorization code flow.
Works with Odoo 14.0 to 19.0.
""",
    "author": "Casdoor",
    "website": "https://github.com/casdoor/odoo-casdoor-oauth",
    "category": "Tools",
    "version": "2.0.0",
    "license": "Other OSI approved licence",
    "depends": ["auth_oauth"],
    "data": [
        "data/auth_oauth_data.xml",
        "views/auth_oauth_views.xml",
    ],
    "images": ["static/description/login_page_screenshot.png"],
    "installable": True,
}
