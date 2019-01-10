# -*- coding: utf-8 -*-
{
    'name': 'Fee Master Extended',
    'version': '1.0',
    'category': 'Edsys',
    "sequence": 4,
    'summary': 'Manage Fee structure',
    'complexity': "easy",
    'description': """
            This module provide fee management system over OpenERP
    """,
    'author': 'Edsys',
    'website': 'www.redbytes.in',
    'images': [],
    'depends': ['base','edsys_capturing_online_payment','edsys_edu_fee'],
    'data': [
             'view/account_view.xml',
             'wizard/send_monthly_fee_wizard.xml',
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
