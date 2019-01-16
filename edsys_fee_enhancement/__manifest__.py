# -*- coding: utf-8 -*-
{
    'name': 'Fee Enhancement',
    'version': '1.0',
    'category': 'Edsys',
    "sequence": 4,
    'summary': 'Manage Fee structure',
    'complexity': "medium",
    'description': """
            This module provide fee management system over OpenERP
    """,
    'author': 'Edsys',
    'website': 'https://www.edsys.in/',
    'images': [],
    'depends': ['base','edsys_promotion','edsys_edu_fee'],
    'data': [
                'view/registration_view.xml',
                'view/student_view.xml',
                'view/promote_student_view.xml',
                'view/fee_computation_view.xml',
                'view/fee_computation_line_view.xml',
                'view/fee_payment_view.xml',
                'view/discount_category_view.xml',
                'view/account_view.xml',
                'view/next_year_advance_fee_view.xml',
                
                'report/fee_computation_report.xml',
                'report/fee_computaion_wizard_report.xml',
                
                'wizard/fee_computation_report_view.xml',
                'wizard/send_monthly_fee_wizard.xml',
                'wizard/generate_fee_computation_wizard.xml',
                'wizard/show_fee_wiz.xml',
                'wizard/send_invoice_wizard.xml',
                
             ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'test': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
