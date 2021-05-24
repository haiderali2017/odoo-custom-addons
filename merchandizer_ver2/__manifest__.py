# -*- coding: utf-8 -*-
{
    'name': "Merchandizer Visit",

    'summary': """Manage merchandizer business""",

    'description': """Manage merchandizer business""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/monthly_plan.xml',
        'views/daily_plan.xml',
        'views/branch_data.xml',
        'data/branch_data.xml',
        'data/monthly_plan_data.xml',
    ],
}
