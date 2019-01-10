# -*- coding: utf-8 -*-
from datetime import date,datetime,timedelta
from odoo import models, fields, api, _
import time


class AccountInvoiceInheritReconcile(models.Model):

    _inherit = 'account.invoice'



    @api.multi
    def bulk_reconciliation(self):
        print '---------------bulk reconcilation---------------'
        journal_id = self.env['account.journal'].search([('advance_reconcillation_journal', '=', True)], limit=1)
        account_id = journal_id.default_debit_account_id.id
        account_payment_obj = self.env['account.payment']
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        c_date = time.strftime('%Y-%m-%d')
        t_date = date.today()
        if self.residual > 0.0 and ((self.partner_id.advance_total_recivable or self.partner_id.re_reg_total_recivable) or \
            (self.partner_id.parents1_id.advance_total_recivable or self.partner_id.parents1_id.re_reg_total_recivable)):
            payment_vals = {
                'partner_type': 'customer',
                'partner_id': self.partner_id.id,
                'journal_id': self.journal_id.id,
                'amount': self.amount_total,
                'payment_method_id': 1,
                # 'account_id': account_id,
                'payment_type': 'inbound',
                # 'advance_account_id':partner_rec.property_account_customer_advance.id,
            }
            payment_rec = account_payment_obj.create(payment_vals)
            print payment_rec, '11111111111111111111111111111111payment rec'
            payment_rec.post()
            return True

        # @api.multi
        # def invoice_validate(self):
        #     res = super(AccountInvoiceInheritReconcile, self).invoice_validate()
        #     if self.type =="out_invoice" :
        #         self.bulk_reconciliation()
        #     return res

    ##########################################################################################
    #                   This is Change by prashant
    ##########################################################################################
    #         voucher_data = {
    #                 'account_id': account_id,
    #                 'journal_id': journal_id.id,
    #                 'partner_id': self.partner_id.id,
    #                 'amount': 0.0,
    #                 'type': 'receipt' or 'payment',
    #                 'state': 'draft',
    #                 'pay_now': 'pay_later',
    #                 'name': '',
    #                 'date': c_date,
    #                 'company_id': 1,
    #                 'tax_id': False,
    #                 'payment_option': 'without_writeoff',
    #                 'comment': _('Write-Off'),
    #                 'advance_account_id': self.partner_id.property_account_customer_advance.id,
    #                 'payfort_pay_date': t_date,
    #                 'narration': 'Advance Auto-Reconciliation through code'
    #                 }
    #         voucher_rec = voucher_obj.create(voucher_data)
    #         if voucher_rec.id:
    #             res_voucher = voucher_rec.onchange_partner_id(self.partner_id.id, journal_id.id, 0.00, self.currency_id.id, self.type,c_date)
    #
    #             amount = 0.00
    #             advance_amount = 0.00
    #             for line_data in res_voucher['value']['line_dr_ids']:
    #                 voucher_lines = {
    #                     'move_line_id': line_data['move_line_id'],
    #                     'amount': line_data['amount_unreconciled'],
    #                     'name': line_data['name'],
    #                     'amount_unreconciled': line_data['amount_unreconciled'],
    #                     'type': line_data['type'],
    #                     'amount_original': line_data['amount_original'],
    #                     'account_id': line_data['account_id'],
    #                     'voucher_id': voucher_rec.id,
    #                     'reconcile': True
    #                 }
    #                 advance_amount += line_data['amount_unreconciled']
    #                 res = voucher_line_obj.create(voucher_lines)
    #                 print("res===================63 bulk reconcilation====",res)
    #             if advance_amount <= self.residual:
    #                 amount += advance_amount
    #             else:
    #                 amount += self.residual
    #
    #             for line_data in res_voucher['value']['line_cr_ids']:
    #                 if line_data['name'] in [self.number]:
    #                     if amount > 0:
    #                         set_amount = line_data['amount_unreconciled']
    #                         if amount <= set_amount:
    #                             set_amount = amount
    #                         voucher_lines = {
    #                             'move_line_id': line_data['move_line_id'],
    #                             'name': line_data['name'],
    #                             'amount_unreconciled': line_data['amount_unreconciled'],
    #                             'type': line_data['type'],
    #                             'amount_original': line_data['amount_original'],
    #                             'account_id': line_data['account_id'],
    #                             'voucher_id': voucher_rec.id,
    #                             'reconcile': True
    #                         }
    #
    #                         voucher_line_rec = voucher_line_obj.create(voucher_lines)
    #                         reconsile_vals = voucher_line_rec.onchange_amount(set_amount, line_data['amount_unreconciled'])
    #                         voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
    #                         if voucher_line_rec.reconcile:
    #                             voucher_line_rec.amount_unreconciled = set_amount
    #                             voucher_line_rec.amount = set_amount
    #                         else:
    #                             voucher_line_rec.amount = set_amount
    #                         amount -= set_amount
    #                         voucher_rec.partner_id.advance_total_recivable = advance_amount - set_amount
    #
    #         voucher_rec.proforma_voucher()
    #         return True
    #
    # @api.multi
    # def invoice_validate(self):
    #     res = super(AccountInvoiceInheritReconcile, self).invoice_validate()
    #     if self.type =="out_invoice" :
    #         self.bulk_reconciliation()
    #     return res
    #
