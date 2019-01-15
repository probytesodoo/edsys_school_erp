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
    'name': 'Edsys HRM',
    'version': '1.0',
    'category': 'TIAS',
    'sequence': 21,
    'summary': 'Jobs, Departments, Employees Details',
    'author': 'Edsys',
    'website': 'https://www.edsys.in/',
    'description': """
Human Resources Management
==========================

This application enables you to manage important aspects of your company's staff and other details such as their skills, contacts, working time...


You can manage:
---------------
* Employees and hierarchies : You can define your employee with User and display hierarchies
* HR Departments
* HR Jobs
    """,
    'author': 'Redbytes',
    'depends': ['base','hr','website', 'document','product_email_template'],
    'data': [
                'security/hr_employee_security.xml',
                'security/ir.model.access.csv',
                'wizard/employement_form_wizard_view.xml',
                'wizard/extend_probation_wizard_view.xml',
                'view/hr_view.xml',
                'view/new_employee.xml',
                'view/employement_application_form_view.xml',
                'view/employement_verification_templet.xml',
                'view/template.xml',
                'view/email_template.xml',
                'view/pro_activities_view.xml',
                'view/hr_department_view.xml',
                'view/sequence_view.xml',
                
            ],
            
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: