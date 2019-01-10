# -*- coding: utf-8 -*-


{
    'name': 'Edsys Education Student Promotion',
    'version': '1.0',
    'category': 'Edsys Education',
    "sequence": 4,
    'summary': 'Manage Student Promotion',
    'complexity': "easy",
    'description': """
            This module provide student promotion system over OpenERP
    """,
    'author': 'Redbytes Software Solutions',
    'website': 'edsys.com',
    'images': [],
    'depends': ['base', 'edsys_edu', 'edsys_edu_fee','edsys_strike_off'],
    'data': [
        'wizard/awaiting_promotion_wiz.xml',
        'view/email_template.xml',
        'view/awaiting_promotion.xml',
        'view/confirm_fees_structure_view.xml',
        'view/alumni_student_view.xml',
        'view/promotion_view.xml',
        'view/menu_view.xml',
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
