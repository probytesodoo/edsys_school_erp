 # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

{
    'name': 'Edsys Biometric',
    'version': '1.0',
    'author': 'Edsys',
    'category': 'TIAD',
    'sequence': 21,
    'website': 'https://www.redbytes.in',
    'summary': 'Jobs, Departments, Employees Details',
    'description': """
Human Resources Management
==========================

This application enables you to manage biometric attendances.


    """,
    'author': 'Redbytes',
    'depends': ['base','hr_attendance', 'edsys_hrm', 'base_workingdays'],
    'data': [
                'security/hr_security.xml',
                'security/ir.model.access.csv',
                'wizard/attendance_review_view.xml',
                'wizard/finalized_attendance_view.xml',
                'view/biometric_server_view.xml',
                'view/res_company_view.xml',
                'wizard/send_attendance_report_view.xml',
                'report/employee_attendance_report.xml',
                #'view/res_users_view.xml',
                'view/hr_view.xml',
                'view/email_template.xml',
                'data/biometric_data.xml',
                
                
            ],
            
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: