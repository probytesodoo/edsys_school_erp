# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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

# from openerp.osv import osv, fields
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # re_reg_advance_account = fields.Many2one('account.account',
    #                                          string="Account Re-Registration Advance",
    #                                          help="This account will be used for Re-Registration fee advance payment of Student/Parent",
    #                                          )

    def _supplier_customer_advance_get(self, cr, uid, ids, field, arg,
                                       context=None):
        res = {}
        for record_id in ids:
            res = {record_id: {'customer_advance': 0.0,
                               'supplier_advance': 0.0}}
        return res

    # @api.multi
    # def _get_re_reg_advance_account(self):
    #     re_reg_account_rec = self.env['account.account'].search([('code', '=', '210602')])
    #     for rec in self:
    #         if rec.is_student or rec.is_parent:
    #             if re_reg_account_rec.id:
    #                 rec.re_reg_advance_account = re_reg_account_rec.id
    #             else:
    #                 rec.re_reg_advance_account = False

    
    property_account_supplier_advance = fields.Many2one('account.account',
            string="Account Supplier Advance",
            help="This account will be used for advance payment of suppliers")
    property_account_customer_advance = fields.Many2one('account.account',
            string="Account Customer Advance",
            help="This account will be used for advance payment of custom")
        #        'customer_advance': fields.function(
        #            _supplier_customer_advance_get,
        #            type='float',
        #            string='Total Customer Advance',
        #            multi='sc',
        #            help="Total amount of advance payment of custom."),
        #        'supplier_advance': fields.function(
        #            _supplier_customer_advance_get,
        #            type='float',
        #            string='Total Supplier Advance',
        #            multi='sc',
        #            help="Total amount of advance payment of suppliers."),
    
