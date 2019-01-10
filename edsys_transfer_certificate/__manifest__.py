# -*- coding: utf-8 -*-
{
    'name': 'Edsys Education Transfer Certificate',
    'version': '1.0',
    'category': 'Edsys Education',
    "sequence": 5,
    'summary': 'Manage Student Transfer Certificate',
    'complexity': "easy",
    'description': """
            This module provide Transfer Certificate management system over OpenERP
    """,
    'author': 'Redbytes Software Solutions',
    'website': 'edsys.com',
    'images': [],
    'depends': ['base','edsys_edu_masters','edsys_edu','edsys_edu_fee','edsys_edu_re_registration','edsys_promotion'],
    'data': [
        'wizard/reminder_tc_form_view.xml',
        'wizard/tc_send_req_form_view.xml',
        'wizard/reminder_tc_fee_payment_link_view.xml',
        'wizard/tc_fee_pay_manually_view.xml',
        # 'wizard/tc_cancel_wizard_view.xml',
        'wizard/ministry_approval_confirm_wiz_view.xml',
        'view/trensfer_certificate_send_form.xml',
        # 'view/sequence_view.xml',
        'view/tc_form_templet.xml',
        'view/tc_fee_balance_re_view.xml',
        'view/tc_fee_structure_view.xml',
        'view/tc_final_fee_awaited.xml',
        'view/transfer_certificate_cancel_form.xml',
        'view/tc_invoice_refund.xml',
        'view/tc_ministry_approval_view.xml',
        'view/tc_withdrawn_view.xml',
        'view/email_templet.xml',
	    'view/all_tc_view.xml',
        'view/menu_view.xml',
        'view/template.xml',
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
