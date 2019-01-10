from odoo import models, fields, api, _
import time

class pay_manually_wiz(models.TransientModel):

    _name='tc.fee.pay.manually.wiz'

    amount = fields.Float(string='Amount')
    journal_id = fields.Many2one('account.journal',string="Payment Method")
    cheque = fields.Boolean(string='Cheque')
    jounral_id_store = fields.Char(string='Jounral Store')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')
    label_change = fields.Boolean(string="Label Change")

    @api.onchange('journal_id')
    def store_jounral(self):
        self.cheque=self.journal_id.is_cheque

    @api.model
    def default_get(self, fields):
        id = self._context.get('active_id')
        res = super(pay_manually_wiz,self).default_get(fields)
        student_tc_rec = self.env['trensfer.certificate'].browse(id)
        res['amount'] = student_tc_rec.credit + student_tc_rec.parent_credit
        return res

    @api.model
    def _get_period(self):
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].search([])
        return periods and periods[0] or False

    @api.model
    def _get_currency(self):
        if self._context is None: self._context = {}
        journal_pool = self.env['account.journal']
        journal_id = self._context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return self.env['res.users'].browse(self._uid).company_id.currency_id.id
    
    
    @api.one
    def submit_fee(self):
        print '=======3333333333333333=submit fee========='
        """
        :return:
        """
        active_id = self._context['active_ids']
        print(active_id,'==========active_id  ----amount----->>>',self.amount)
        trensfer_certificate_obj = self.env['trensfer.certificate']
        account_payment_obj = self.env['account.payment']
        payment_vals = {}
        for trensfer_certificate_rec in trensfer_certificate_obj.browse(active_id):
            if self.amount > 0.00:
                payment_vals =self.get_payment_vals('customer', 'inbound', trensfer_certificate_rec)
            if self.amount < 0.00:
                payment_vals =self.get_payment_vals('supplier', 'outbound', trensfer_certificate_rec)
                trensfer_certificate_rec.credit -= self.amount
            if payment_vals:
                payment_rec = account_payment_obj.create(payment_vals)
                payment_rec.post()
                print(payment_rec,trensfer_certificate_rec.credit,trensfer_certificate_rec.state,'==============payment_rec===---vals ---> ')
                # print(paymment_vals)

    def get_payment_vals(self, partner_type, payment_type, trensfer_certificate_rec):
        if abs(self.amount) > 0.00:
            payment_vals = {
                # 'period_id': period_id,
                'partner_type': partner_type,
                'partner_id': trensfer_certificate_rec.name.id,
                'journal_id': self.journal_id.id,
                'amount': abs(self.amount),
                'payment_method_id': 1,
                'payment_type': payment_type,
            }
            return payment_vals

#     @api.one
#     def submit_fee(self):
#         print '========submit fee========='
#         """
#         :return:
#         """
#         active_id = self._context['active_ids']
#         trensfer_certificate_obj = self.env['trensfer.certificate']
#         account_voucher_obj = self.env['account.voucher']
#         voucher_line_obj = self.env['account.voucher.line']
#         for trensfer_certificate_rec in trensfer_certificate_obj.browse(active_id):
#             if self.amount > 0.00:
#                 period_rec = self._get_period()
#                 curency_id = self._get_currency()
#                 vouch_sequence = self.env['ir.sequence'].get('voucher.payfort') or '/'
#                 voucher_data = {
#                     'period_id': period_rec.id,
#                     'journal_id': self.journal_id.id,
#                     'account_id': self.journal_id.default_debit_account_id.id,
#                     'partner_id': trensfer_certificate_rec.name.id,
#                     'currency_id': curency_id,
#                     'reference': trensfer_certificate_rec.code,
#                     'amount': self.amount,
#                     'type': 'receipt' or 'payment',
#                     'state': 'draft',
#                     'pay_now': 'pay_later',
#                     'name': trensfer_certificate_rec.code,
#                     'date': time.strftime('%Y-%m-%d'),
#                     'company_id': 1,
#                     'tax_id': False,
#                     'payment_option': 'without_writeoff',
#                     'comment': _('Write-Off'),
#                     'payfort_type': True,
#                     'payfort_link_order_id' : vouch_sequence,
#                     'cheque_start_date':self.cheque_start_date,
#                     'cheque_expiry_date':self.cheque_expiry_date,
#                     'bank_name':self.bank_name,
#                     'cheque':self.cheque,
#                     'party_name' :self.party_name,
#                     'chk_num':self.chk_num,
#                     'voucher_type':'sale' or 'purchase',
#                     }
#                 print voucher_data,'====================voucher_data'
#                 voucher_rec = account_voucher_obj.create(voucher_data)
#                 print voucher_rec,'=====================voucher rec'
#                 date = time.strftime('%Y-%m-%d')
#                 res = voucher_rec.onchange_partner_id(voucher_rec.partner_id.id, self.journal_id.id,
#                                       self.amount,
#                                       voucher_rec.currency_id.id,
#                                       voucher_rec.type, date)
#                 print res,'----------------res-----'
#                 for line_data in res['value']['line_cr_ids']:
#                     print line_data,'====================== line data ============'
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': line_data['amount_unreconciled'] or line_data['amount'],
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_rec.id,
#                         'reconcile': True
#                     }
#                     print voucher_lines,'====================---------------------voucher_lines pay manualy-'
#                     self.env['account.voucher.line'].sudo().create(voucher_lines)
# 
#                 # Validate voucher (Add Journal Entries)
#                 voucher_rec.proforma_voucher()
#                 trensfer_certificate_rec.send_fee_receipt_mail(voucher_rec)
# 
#             if self.amount < 0.00:
#                 period_rec = self._get_period()
#                 curency_id = self._get_currency()
#                 vouch_sequence = self.env['ir.sequence'].get('voucher.payfort') or '/'
#                 voucher_data = {
#                     'period_id': period_rec.id,
#                     'journal_id': self.journal_id.id,
#                     'account_id': self.journal_id.default_debit_account_id.id,
#                     'partner_id': trensfer_certificate_rec.name.id,
#                     'currency_id': curency_id,
#                     'reference': trensfer_certificate_rec.name.name,
#                     'amount': self.amount,
#                     'type': 'receipt' or 'payment',
#                     'state': 'draft',
#                     'pay_now': 'pay_later',
#                     'name': '',
#                     'date': time.strftime('%Y-%m-%d'),
#                     'company_id': 1,
#                     'tax_id': False,
#                     'payment_option': 'without_writeoff',
#                     'comment': _('Write-Off'),
#                     'payfort_type': True,
#                     'payfort_link_order_id': vouch_sequence,
#                     'cheque_start_date':self.cheque_start_date,
#                     'cheque_expiry_date':self.cheque_expiry_date,
#                     'bank_name':self.bank_name,
#                     'cheque':self.cheque,
#                     'party_name' :self.party_name,
#                     'chk_num':self.chk_num,
#                     }
#                 print voucher_data,'1111111111111111111111111  voucher idata'
#                 voucher_rec = account_voucher_obj.create(voucher_data)
#                 date = time.strftime('%Y-%m-%d')
#                 res = voucher_rec.onchange_partner_id(voucher_rec.partner_id.id, self.journal_id.id,
#                                       self.amount,
#                                       voucher_rec.currency_id.id,
#                                       voucher_rec.type, date)
#                 print res,'===============5555555555555555555555555  voucher rec'
#                 for line_data in res['value']['line_dr_ids']:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': line_data['amount_unreconciled'] or line_data['amount'],
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_rec.id,
#                         'reconcile': True
#                     }
#                     print voucher_lines,'99999999999999999999999 voucher lines'
#                     voucher_line_obj.sudo().create(voucher_lines)
# 
#                 # Validate voucher (Add Journal Entries)
#                 voucher_rec.proforma_voucher()