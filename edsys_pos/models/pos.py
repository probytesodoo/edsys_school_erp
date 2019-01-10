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

#import logging
#from openerp import SUPERUSER_ID
#import re
from odoo import models, fields, api, _
#import new
#from openerp.exceptions import except_orm, Warning, RedirectWarning
#import base64
#from openerp import api, tools
#from openerp.osv import osv
#import datetime
#from lxml import etree
#from chameleon.nodes import Default
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class pos_order(models.Model):
    
    _inherit = 'pos.order'
    
    def compute_untaxed_amount(self):
        amount_untaxed = 0.0
        for order in self:
            if order:
                for line in order.lines:
                    if line:
                        amount_untaxed  += line.price_subtotal
        self.amount_untaxed = amount_untaxed

    amount_untaxed = fields.Float('Employee Name',compute='compute_untaxed_amount')
    
    @api.model
    def create(self, vals):
        partner_id = ''
        partner_id = vals['partner_id']
        res = super(pos_order, self).create(vals)
        if partner_id and res.id :
            self.create_res_partner_pos(partner_id,res.id)
        return res
    
    
    
    def create_res_partner_pos(self, partner_id,res_id):
        res_partner_obj = self.env['res.partner']
        res_partner_ids = res_partner_obj.search([])
        for res_partner_id in res_partner_ids:
            if res_partner_id.id == partner_id:
                    partner_vals = {}
                    partner_vals = {
                                    'pos_order_id' : [[4,res_id]],
                                    
                                    }
                    res_partner_id.write(partner_vals)
    
    
    


class res_partner(models.Model):
    
    _inherit = 'res.partner'
    
    pos_order_id = fields.Many2many('pos.order','partner_mail','partner_id','pos_id','Campaign')
    
#     @api.multi
#     def write(self, vals):
#         res = super(res_partner, self).write(vals)
#         return res
    
class res_user_view(models.Model):
    _inherit = 'res.users'


        
    
    





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
