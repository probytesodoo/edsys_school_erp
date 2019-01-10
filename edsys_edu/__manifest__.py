# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

{
    'name': 'Edsys Education',
    'version': '1.0',
    'category': 'Edsys Education',
    "sequence": 3,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'description': """
            This module provide overall education management system over OpenERP
            Features includes managing
                * Student
                * Faculty
                * Admission
                * Course
                * Batch
                * Books
                * Library
                * Lectures
                * Exams
                * Marksheet
                * Result
                * Transportation
                * Hostel

    """,
    'author': 'Redbytes Software Solutions',
    'website': 'edsys.com',
    'images': [],
    'depends': ['base','edsys_edu_masters',
                'edsys_edu_fee','account_accountant',
                'account','sale','account_period'],
    'data': [
	         'wizard/update_fee_computation_status_view.xml',
             'security/registration_security.xml',
             'security/ir.model.access.csv',

             'security/payment_menu_hide.xml',

             'wizard/reject_reason_wiz.xml',
             'wizard/send_academic_fee_receipt_wizard.xml',
             'wizard/show_fee_wiz.xml',
             'view/registration_form_view.xml',
             'view/enquiry_view.xml',
             'view/awaiting_fee_view.xml',
             'view/waiting_list_view.xml',
             'view/decision_pending_view.xml',
             'view/rejected_form_view.xml',
             'view/configuration_view.xml',
             'view/student_view.xml',
             'view/all_registration.xml',
             'view/sequence_view.xml',
             'view/account_view.xml',
             'report/proforma_invoice_view.xml',
             'report/registration_fee_reciept.xml',
             'report/fee_invoice_receipt.xml',
             'report/student_payment_receipt.xml',
             'report/report_layout_inherit.xml',
             'report/report_account_invoice_view.xml',
      	     'view/email_template.xml',
             'view/payfort_config.xml',
             'view/registration_fee_form.xml',
             'view/language_view.xml',
             'view/product_view.xml',
             'view/menu_view.xml',
             'view/journal_view.xml',
             'view/point_of_sale_report.xml',
             'view/point_of_sale_template.xml',

             'view/calender_menu_hide.xml',

            
	   #  'wizard/update_student_status.xml'


             ],

    'update_xml' : ['security/payment_menu_hide.xml'],
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
