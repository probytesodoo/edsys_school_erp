# -*- coding: utf-8 -*-


{
    'name': 'Edsys PDC Managment',
    'version': '1.0',
    'category': 'Edsys PDC Managment',
    "sequence": 6,
    'summary': 'Manage post date cheque',
    'complexity': "easy",
    'description': """
            This module provide PDC cheque management
    """,
    'author': 'edsys',
    'website': 'www.redbytes.in',
    'images': [],
    'depends': ['base','pdc_detail'],
    'data': [
             'account_move.xml',
             'pdc_detail_view.xml',
             'wizard/bounce_reason_view.xml',
            # 'account_voucher_payment_view.xml',
             'wizard/post_cheque_wiz_view.xml',
             'wizard/clear_cheque_wiz_view.xml',

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