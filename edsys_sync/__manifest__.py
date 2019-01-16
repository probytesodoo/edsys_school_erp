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
    'name': 'Edsys Sync',
    'version': '1.0',
    'category': 'Edsys',
    'sequence': 21,
    'author': 'Edsys',
    'website': 'https://www.edsys.in/',
    'summary': 'To sync data with Odoo with limited access',
    'description': """

    """,
    'author': 'Redbytes',
    'depends': ['base','edsys_edu_masters', 'openeducat_library'],
    'data': [
                 'security/edsys_sync_security.xml',
                 'security/ir.model.access.csv',
                 'view/partner_view.xml',
                'data/sync_user.xml'
            ],
            
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
