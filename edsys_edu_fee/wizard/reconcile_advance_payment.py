from odoo import models, fields, api, _
import datetime as d
from datetime import datetime
from odoo.exceptions import except_orm
import time

class ReconsileAdvanceFee(models.Model):

    _name = 'reconsile.advance.fee'

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
    def reconcile_advance_payment(self):
        next_year_advance_obj = self.env['next.year.advance.fee']
        exists_invoice = False
        for record in next_year_advance_obj.browse(self._context['active_ids']):
            if record.state == 'fee_paid':
                if not record.batch_id.advance_payment_reconcile_date:
                    raise except_orm(_('Warning!'),
                    _("Please Define Advance Payment Reconcile Date on Academic Year"))

                reconcile_date = datetime.strptime(record.batch_id.advance_payment_reconcile_date, "%Y-%m-%d").date()
                c_date = d.date.today()
                if c_date < reconcile_date:
                    raise except_orm(_('Warning!'),
                    _("You Can Not Reconcile Advance Payment for Academic Year %s\n"
                      "before %s date") % (record.batch_id.name, record.batch_id.advance_payment_reconcile_date))
                else:
                    invoice_obj = self.env['account.invoice']
                    voucher_obj = self.env['account.voucher']
                    voucher_line_obj = self.env['account.voucher.line']
                    #month_rec = record.batch_id.month_ids[0]
                    fee_month_obj = self.env['fee.month']
                    admission_date=datetime.strptime(record.partner_id.admission_date, "%Y-%m-%d")
                    month_rec = fee_month_obj.search([('name','=', admission_date.month),('batch_id','=', record.batch_id.id)])
                    if record.partner_id.payment_status :
                        for payment_status in record.partner_id.payment_status :
                            exists_invoice = invoice_obj.search([('month_id', '=', payment_status.month_id.id), ('partner_id', '=', record.partner_id.id), ('batch_id', '=', record.partner_id.batch_id.id), ('batch_id', '=', record.partner_id.year_id.id)])
                            if exists_invoices :
                                if exists_invoice.state == 'open' :
                                    inv_rec = exists_invoice
                                elif exists_invoice.state == 'paid' :
                                    raise except_orm(_('Warning!'), _("Next Year invoice is already paid and invoice id is %s " % (exists_invoice.number)))
                    else :
                        invoice_line_list = []
                        for inv_line_rec in record.next_year_advance_fee_line_ids:
                            invoice_line_ids = {}
                            invoice_line_ids.update({
                                'product_id' : inv_line_rec.name.id,
                                'account_id' : inv_line_rec.name.property_account_income_id.id,
                                'name' : inv_line_rec.name.name,
                                'quantity' : 1.00,
                                'price_unit' : round(inv_line_rec.amount, 2),
                                'rem_amount' : round(inv_line_rec.amount, 2),
                                'parent_id' : record.partner_id.parents1_id.id,
                                'priority' : inv_line_rec.priority
                            })
                            invoice_line_list.append((0, 0, invoice_line_ids))
                        # create invoice
                        inv_rec = invoice_obj.create({
                            'partner_id' : record.partner_id.id,
                            'month_id' : month_rec.id,
                            'account_id' : record.partner_id.property_account_receivable.id,
                            'invoice_line_ids' : invoice_line_list,
                            'month' : month_rec.name,
                            'year' : month_rec.year,
                            'batch_id' : record.batch_id.id,
                            })
                        # validating invoice
                        inv_rec.action_invoice_open()
                        record.reg_id.invoice_id = inv_rec.id
                    #raise except_orm(_('Warning!'), _("Stop"))
                    # create voucher
                    # inv_rec=brw_reg.invoice_id
                    advance_reconcillation_journal = self.env['account.journal'].search([
                        ('advance_reconcillation_journal', '=', True)])
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
                    if inv_rec.state == 'paid':
                        record.state = 'invoice_reconcile'
                        continue
                    if inv_rec.state == 'open':
                        period_rec = self._get_period()
                        voucher_data = {
                            'period_id': period_rec.id,
                            'account_id': advance_reconcillation_journal.default_debit_account_id.id,
                            'partner_id': inv_rec.partner_id.id,
                            'journal_id': advance_reconcillation_journal.id,
                            'currency_id': inv_rec.currency_id.id,
                            'reference': inv_rec.name,
                            # 'amount': 0.00,
                            'type': inv_rec.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'invoice_id':inv_rec.id,
                            }

                        # create voucher
                        voucher_id = voucher_obj.create(voucher_data)
                        date = time.strftime('%Y-%m-%d')
                        if voucher_id.id:
                            res = voucher_id.onchange_partner_id(inv_rec.partner_id.id, record.journal_id.id, 0.00, inv_rec.currency_id.id, inv_rec.type, date)

                            # total_amount = record.total_amount
                            # if record.total_amount >= inv_rec.residual:
                            #     total_amount = inv_rec.residual
                            # Loop through each document and Pay only selected documents and create a single receipt

                            for line_data in res['value']['line_cr_ids']:
                                if not line_data['amount']:
                                    continue
                                name = line_data['name']

                                if line_data['name'] in [inv_rec.number]:
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
                                if line_data['name'] in [inv_rec.number]:
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
                            record.state = 'invoice_reconcile'
                raise except_orm(_('Warning!'), _("Stop"))
            elif record.state == 'invoice_reconcile':
                raise except_orm(_('Warning!'),
                    _("This Record(%s) Already Reconcile") % (record.order_id))
            else:
                raise except_orm(_('Warning!'),
                    _("Without Advance payment you can't Reconcile record(%s)") % (record.order_id))
