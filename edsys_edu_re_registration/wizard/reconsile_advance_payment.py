from openerp import models, fields, api, _
import time
from openerp.exceptions import except_orm

class ReconsileReRegAdvanceFee(models.Model):
    _name = 're.reg.reconsile.advance.payment.wiz'

    @api.model
    def _make_journal_search(self, ttype):
        journal_pool = self.env['account.journal']
        return journal_pool.search([('type', '=', ttype)])

    @api.model
    def _get_journal(self):
        """
        this method  is used for get journal,
        --------------------------------------
        :return:
        """
        if self._context is None: self._context = {}
        invoice_pool = self.env['account.invoice']
        journal_pool = self.env['account.journal']
        if self._context.get('invoice_id', False):
            invoice = invoice_pool.browse(self._context['invoice_id'])
            journal_id = journal_pool.search([('currency', '=', invoice.currency_id.id),
                                              ('company_id', '=', invoice.company_id.id)],
                                             limit=1)
            return journal_id and journal_id[0] or False
        if self._context.get('journal_id', False):
            return self._context.get('journal_id')
        if not self._context.get('journal_id', False) and self._context.get('search_default_journal_id', False):
            return self._context.get('search_default_journal_id')

        ttype = self._context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(ttype)
        return res and res[0] or False

    @api.model
    def _get_currency(self):
        """
        this method use for get account currency.
        --------------------------------------------
        :return: record set of  currency.
        """
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

    @api.model
    def re_reg_fee_reconcile_partner_advance(self, re_reg_partner_rec, amount):
        """
        This method is used for create voucher and reconsile fee form
        advance to re-registration advance.
        ----------------------------------------------------------------------
        :param re_reg_partner_rec:
        :param amount:
        :return:
        """
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        journal_rec = self._get_journal()
        account_id = journal_rec.default_debit_account_id.id
        partner_rec = re_reg_partner_rec.name
        currency_id = self._get_currency()
        period_id = self._get_period().id
        c_date = time.strftime('%Y-%m-%d')
        re_reg_advance_account = partner_rec.re_reg_advance_account or False
        if not re_reg_advance_account.id:
            raise except_orm(_('Warning!'),
                            _("Please define re-registration advance account!"))
        voucher_data = {
            'period_id': period_id,
            'account_id': account_id,
            'partner_id': partner_rec.id,
            'journal_id': journal_rec.id,
            'currency_id': currency_id,
            'reference': re_reg_partner_rec.code,
            'amount': 0.00,
            'type': 'receipt' or 'payment',
            'state': 'draft',
            'pay_now': 'pay_later',
            'name': re_reg_partner_rec.code,
            'date': c_date,
            'company_id': 1,
            'tax_id': False,
            'payment_option': 'without_writeoff',
            'comment': _('Write-Off'),
            'advance_account_id': re_reg_advance_account.id or False,
            're_reg_fee': True,
        }
        voucher_rec = voucher_obj.create(voucher_data)
        if voucher_rec.id:
            res = voucher_rec.with_context({'re_reg_reconcile':True}).onchange_partner_id(partner_rec.id, journal_rec.id, amount,
                                                  currency_id, voucher_rec.type, c_date)

            for line_data in res['value']['line_dr_ids']:
                if amount > 0:
                    set_amount = line_data['amount_original']
                    if amount <= set_amount:
                        set_amount = amount
                    reconcile = False
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher_rec.id,
                    }
                    voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
                    reconsile_vals = voucher_line_rec.onchange_amount(line_data['amount_original'],set_amount)
                    voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                    if voucher_line_rec.reconcile:
                        voucher_line_rec.amount_unreconciled = set_amount
                        # amount_vals = voucher_line_rec.onchange_reconcile()
                        voucher_line_rec.amount = set_amount
                    else:
                        voucher_line_rec.amount = set_amount
                    # a = 10 / 0
                    amount -= set_amount
            # validate voucher
            voucher_rec.button_proforma_voucher()

    @api.multi
    def reconsile_re_reg_advance(self):
        active_ids = self._context['active_ids']
        re_reg_student_obj = self.env['re.reg.waiting.responce.student']
        for re_reg_student_rec in re_reg_student_obj.browse(active_ids):
            if re_reg_student_rec.state in ['awaiting_re_registration_fee','re_registration_confirmed']:
                # if re_reg_student_rec.fee_status in ['re_unpaid','re_partially_paid']:
                    if re_reg_student_rec.name.advance_total_recivable > 0 or\
                                    re_reg_student_rec.re_reg_parents.name.advance_total_recivable > 0:
                        advance_amount = re_reg_student_rec.name.advance_total_recivable + re_reg_student_rec.re_reg_parents.name.advance_total_recivable
                        total_amount = 0.00

                        if advance_amount < re_reg_student_rec.residual:
                            total_amount = advance_amount
                            re_reg_student_rec.total_paid_amount += total_amount
                            re_reg_student_rec.name.re_reg_next_academic_year = 'yes'
                            self.re_reg_fee_reconcile_partner_advance(re_reg_student_rec,total_amount)
                        else:
                            total_amount = re_reg_student_rec.residual
                            re_reg_student_rec.total_paid_amount += total_amount
                            re_reg_student_rec.fee_status = 're_Paid'
                            re_reg_student_rec.state = 're_registration_confirmed'
                            re_reg_student_rec.name.re_reg_next_academic_year = 'no'
                            self.re_reg_fee_reconcile_partner_advance(re_reg_student_rec,total_amount)
