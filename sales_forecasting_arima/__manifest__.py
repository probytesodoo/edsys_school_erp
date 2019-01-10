# -*- coding: utf-8 -*-
{
    'name': "Sales Forecasting Using ARIMA models",

    'summary': """
    """,

    'description': """
Sales Forecasting Using ARIMA models
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "www.linkedin.com/in/aasimansari",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/sales_prediction_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'support': 'aasim333@gmail.com',
    'license': 'LGPL-3',
    'price': 75.00,
    'currency': 'EUR',
}