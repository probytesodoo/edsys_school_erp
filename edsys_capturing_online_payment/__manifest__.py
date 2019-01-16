# -*- coding: utf-8 -*-

{
    'name': 'Edsys Capturing Online Payment',
    'version': '1.0',
    'category': 'Edsys Education',
    "sequence": 8,
    'summary': 'Manage Online Payment',
    'complexity': "easy",
    'description': """
            This module use to Capturing Online Payment.
    """,
    'author': "Edsys",
    "website": "https://www.edsys.in/",

    'images': [],
    'depends': ['base','edsys_edu_fee','edsys_edu','edsys_strike_off','edsys_edu_re_registration','edsys_transfer_certificate'],
    'data': [
        'security/ir.model.access.csv',
        'view/payfort_config.xml',
        'view/payfort_payment_capture_view.xml',
        'view/payfort_error_capture.xml',
        'view/menu_view.xml',
        'view/payfort_payment_error_templet.xml',
        'view/payfort_submission_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'test': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
