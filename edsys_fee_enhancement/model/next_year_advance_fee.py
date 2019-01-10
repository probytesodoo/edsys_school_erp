from odoo import models, fields, api, _
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

class NextYearAdvanceFee(models.Model):

    _inherit = 'next.year.advance.fee'
    
    is_reconciled = fields.Boolean('Reconciled')
    
    
    @api.model
    def _get_period(self):
        """
        this method use for get account period.
        ---------------------------------------
        :return: record set of period
        """
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].search([])
        return periods and periods[0] or False
    
    
    @api.multi
    def reconcile_nyaf(self,invoice_rec):
        print invoice_rec, '=================reconcile nyaf========================='
        voucher_obj = self.env['account.voucher']
        advance_reconcillation_journal = self.env['account.journal'].search([('advance_reconcillation_journal', '=', True)])
        if len(advance_reconcillation_journal) < 1:
            raise except_orm(_('Warning!'),
            _("Please Define Advance Reconcillation Journal!"))
        if len(advance_reconcillation_journal) > 1:
            raise except_orm(_('Warning!'),
            _("Please Define only one Advance Reconcillation Journal!"))
        if len(advance_reconcillation_journal) == 1:
            if not advance_reconcillation_journal.default_debit_account_id.id:
                raise except_orm(_('Warning!'),
                _("Please Define Default Debit Account for Advance Reconcillation Journal!"))
        period_rec = self._get_period()
        voucher_data = {
            'period_id': period_rec.id,
            'account_id': advance_reconcillation_journal.default_debit_account_id.id,
            'partner_id': invoice_rec.partner_id.id,
            'journal_id': advance_reconcillation_journal.id,
            'currency_id': invoice_rec.currency_id.id,
            'reference': invoice_rec.name,
            # 'amount': 0.00,
            'type': invoice_rec.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
            'state': 'draft',
            'pay_now': 'pay_later',
            'name': '',
            'date': time.strftime('%Y-%m-%d'),
            'company_id': 1,
            'tax_id': False,
            'payment_option': 'without_writeoff',
            'comment': _('Write-Off'),
            
            'invoice_id':invoice_rec.id,
            }
        print voucher_data,'------------------------hhhhhhhhhhhhhhhhh'
        # create voucher
        voucher_id = voucher_obj.create(voucher_data)
        print voucher_id,'----------------------------kkkkkkkkkkk'
        date = time.strftime('%Y-%m-%d')
        if voucher_id.id:
            res = voucher_id.onchange_partner_id(invoice_rec.partner_id.id, self.journal_id.id, 0.00, invoice_rec.currency_id.id, invoice_rec.type, date)
            # Loop through each document and Pay only selected documents and create a single receipt
            if res :
                for line_data in res['value']['line_cr_ids']:
                    if not line_data['amount']:
                        continue
                    name = line_data['name']
        
                    if line_data['name'] in [invoice_rec.number]:
                        if not line_data['amount']:
                            continue
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'amount': line_data['amount_unreconciled'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher_id.id,
                    }
                    voucher_id.line_cr_ids.create(voucher_lines)
        
                for line_data in res['value']['line_dr_ids']:
                    if not line_data['amount']:
                        continue
                    if line_data['name'] in [invoice_rec.number]:
                        if not line_data['amount']:
                            continue
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'amount': line_data['amount_unreconciled'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher_id.id,
                    }
                    voucher_line_id = voucher_id.line_dr_ids.create(voucher_lines)
        
            # Add Journal Entries
            voucher_id.proforma_voucher()
            
    
    @api.multi
    def write(self, vals):
        invoice_obj = self.env['account.invoice']
        print invoice_obj,'====================invoice obj'
        if 'state' in vals and vals.has_key('state'):
            state = vals['state']
        else:
            state = self.state
        partner_id = self.partner_id
        print partner_id,'=====================partner_id'
        if state == 'fee_paid':
            if partner_id and partner_id.fee_computation_ids:
                print partner_id,'===================partner_id'
                invoice_rec = invoice_obj.search([('partner_id','=',partner_id.id), ('batch_id','=',partner_id.year_id.id), ('month','=', partner_id.fee_computation_ids[0].month_id.id)])
                print invoice_rec,'==================================invoice rec'
                self.reconcile_nyaf(invoice_rec)
        return super(NextYearAdvanceFee, self).write(vals)


    
#     @api.multi
#     def reconcile_nyaf(self,invoice_rec):
#         active_id=self._context['active_id']
#         brw_reg=self.env['registration'].browse(active_id)
#         partner_rec = brw_reg.student_id
#         nyaf_rec= brw_reg.next_year_advance_fee_id
#         print invoice_rec, '=================reconcile nyaf========================='
#         account_payment_obj = self.env['account.payment']
#         voucher_obj = self.env['account.voucher']
#         advance_reconcillation_journal = self.env['account.journal'].search([('advance_reconcillation_journal', '=', True)])
#         if len(advance_reconcillation_journal) < 1:
#             raise except_orm(_('Warning!'),
#             _("Please Define Advance Reconcillation Journal!"))
#         if len(advance_reconcillation_journal) > 1:
#             raise except_orm(_('Warning!'),
#             _("Please Define only one Advance Reconcillation Journal!"))
#         if len(advance_reconcillation_journal) == 1:
#             if not advance_reconcillation_journal.default_debit_account_id.id:
#                 raise except_orm(_('Warning!'),
#                 _("Please Define Default Debit Account for Advance Reconcillation Journal!"))
#         period_rec = self._get_period()
# #         voucher_data = {
# #             'period_id': period_rec.id,
# #             'account_id': advance_reconcillation_journal.default_debit_account_id.id,
# #             'partner_id': invoice_rec.partner_id.id,
# #             'journal_id': advance_reconcillation_journal.id,
# #             'currency_id': invoice_rec.currency_id.id,
# #             'reference': invoice_rec.name,
# #             # 'amount': 0.00,
# #             'type': invoice_rec.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
# #             'state': 'draft',
# #             'pay_now': 'pay_later',
# #             'name': '',
# #             'date': time.strftime('%Y-%m-%d'),
# #             'company_id': 1,
# #             'tax_id': False,
# #             'payment_option': 'without_writeoff',
# #             'comment': _('Write-Off'),
# #             
# #             'invoice_id':invoice_rec.id,
# #             }
# #         print voucher_data,'------------------------hhhhhhhhhhhhhhhhh'
# 
#         payment_vals ={
#                                'period_id': period_rec.id,
#                                'account_id': advance_reconcillation_journal.default_debit_account_id.id,
#                                'partner_type' : 'customer',
#                                'partner_id' : partner_rec.id,
#                                'journal_id' : advance_reconcillation_journal.id,
#                                 'amount' : nyaf_rec.total_amount,
#                                'payment_method_id' : 1,
#                                'payment_type' : 'inbound',
#                                'invoice_id':invoice_rec.id,
#                                }
#        
#         # create voucher
#         payment_rec = account_payment_obj.create(payment_vals)
#         payment_rec.post()
# #         voucher_id = voucher_obj.create(voucher_data)
# #         print voucher_id,'----------------------------kkkkkkkkkkk'
# #         date = time.strftime('%Y-%m-%d')
# #         if voucher_id.id:
# #             res = voucher_id.onchange_partner_id(invoice_rec.partner_id.id, self.journal_id.id, 0.00, invoice_rec.currency_id.id, invoice_rec.type, date)
# #             # Loop through each document and Pay only selected documents and create a single receipt
# #             if res :
# #                 for line_data in res['value']['line_cr_ids']:
# #                     if not line_data['amount']:
# #                         continue
# #                     name = line_data['name']
# #         
# #                     if line_data['name'] in [invoice_rec.number]:
# #                         if not line_data['amount']:
# #                             continue
# #                     voucher_lines = {
# #                         'move_line_id': line_data['move_line_id'],
# #                         'amount': line_data['amount_unreconciled'],
# #                         'name': line_data['name'],
# #                         'amount_unreconciled': line_data['amount_unreconciled'],
# #                         'type': line_data['type'],
# #                         'amount_original': line_data['amount_original'],
# #                         'account_id': line_data['account_id'],
# #                         'voucher_id': voucher_id.id,
# #                     }
# #                     voucher_id.line_cr_ids.create(voucher_lines)
# #         
# #                 for line_data in res['value']['line_dr_ids']:
# #                     if not line_data['amount']:
# #                         continue
# #                     if line_data['name'] in [invoice_rec.number]:
# #                         if not line_data['amount']:
# #                             continue
# #                     voucher_lines = {
# #                         'move_line_id': line_data['move_line_id'],
# #                         'amount': line_data['amount_unreconciled'],
# #                         'name': line_data['name'],
# #                         'amount_unreconciled': line_data['amount_unreconciled'],
# #                         'type': line_data['type'],
# #                         'amount_original': line_data['amount_original'],
# #                         'account_id': line_data['account_id'],
# #                         'voucher_id': voucher_id.id,
# #                     }
# #                     voucher_line_id = voucher_id.line_dr_ids.create(voucher_lines)
# #         
# #             # Add Journal Entries
# #             voucher_id.proforma_voucher()
# #             
#     
#     @api.multi
#     def write(self, vals):
#         invoice_obj = self.env['account.invoice']
#         print invoice_obj,'====================invoice obj'
#         if 'state' in vals and vals.has_key('state'):
#             state = vals['state']
#         else:
#             state = self.state
#         partner_id = self.partner_id
#         print partner_id,'=====================partner_id'
#         if state == 'fee_paid':
#             if partner_id and partner_id.fee_computation_ids:
#                 print partner_id,'===================partner_id'
#                 invoice_rec = invoice_obj.search([('partner_id','=',partner_id.id), ('batch_id','=',partner_id.year_id.id), ('month','=', partner_id.fee_computation_ids[0].month_id.id)])
#                 print invoice_rec,'==================================invoice rec'
#                 self.reconcile_nyaf(invoice_rec)
#         return super(NextYearAdvanceFee, self).write(vals)

