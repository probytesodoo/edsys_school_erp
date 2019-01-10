# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp
from odoo import SUPERUSER_ID

class pdc_detail(models.Model):
    _inherit = 'pdc.detail'
    
    bank_payment_name = fields.Many2one('account.account', 'Bank Payment Name', domain=[('user_type.name','=','Bank')])
    clear_cheque_date = fields.Date('Date of clearing cheque')
    bounce_cheque_date = fields.Date('Reject Cheque Date')
    state=fields.Selection(
            [('draft','Draft'),
             ('posted','Submitted'),
             ('cleared','Cleared'),
             ('bounced','Rejected'),
             ('cancel','Cancelled'),
            ],'Status', readonly=True, default='draft', track_visibility='onchange', copy=False,)
    reason = fields.Char(string="Cheque Reject Reason",size=126)
    
    
    @api.multi
    def post_cheque(self):
        view = self.env.ref('pdc_detail.post_cheque_wiz_view')
        return {
            'name': _('Submit Cheque'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'post.cheque.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }  


    @api.multi
    def cleared_cheque(self):
        view = self.env.ref('pdc_detail.clear_cheque_wiz_view')
        return {
            'name': _('Clear Cheque'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'clear.cheque.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }  
    
    @api.multi
    def bounce_cheque_wiz(self):
        
        view = self.env.ref('pdc_detail.bounce_reason_wiz_view')
        return {
            'name': _('Cheque Reject'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bounce.reason.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }
