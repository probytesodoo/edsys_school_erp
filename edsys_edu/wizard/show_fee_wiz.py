from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

class show_fee_wiz(models.TransientModel):
    _name='show.fee.wiz'
    
    total_fee = fields.Float(string="You have to pay this amount")
    total_remaining = fields.Float(string="Remaining amount")
    label_change = fields.Boolean(string="Label Change")
    journal_id = fields.Many2one('account.journal',string="Payment Method")
    cheque = fields.Boolean(string='Cheque')
    jounral_id_store = fields.Char(string='Jounral Store')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')

    @api.onchange('journal_id')
    def store_jounral(self):
        self.jounral_id_store = self.journal_id.type
        self.cheque=self.journal_id.is_cheque

    @api.onchange('cheque_start_date','cheque_expiry_date')
    def cheque_start(self):
        if self.cheque_start_date and self.cheque_expiry_date:
            if self.cheque_start_date > self.cheque_expiry_date:
                raise except_orm(_('Warning!'),
                    _("Start Date must be lower than to Expiry date!"))

    @api.model
    def default_get(self, fields):
        res = super(show_fee_wiz, self).default_get(fields)
        active_id = self._context['active_id']
        brw_reg = self.env['registration'].browse(active_id)
        if brw_reg.fee_status == 'reg_fee_pay':
            raise except_orm(_("Warning!"), _('Registration fees are already paid!'))
        elif brw_reg.fee_status == 'academy_fee_pay':
            raise except_orm(_("Warning!"), _('Academic fees are already paid!'))
        if brw_reg.state == 'reg':
            amount = 0
            for each in brw_reg.reg_fee_line:
                amount = amount + each.amount
            res['total_fee'] = amount
            res['label_change'] = False

        if brw_reg.state == 'awaiting_fee':

            if brw_reg.fee_structure_confirm != True:
                raise except_orm(_("Warning!"), _('Please Confirm the fee structure before paying fee'))

            if not brw_reg.invoice_id:
                if not brw_reg.next_year_advance_fee_id:
                    month_diff = brw_reg.batch_id.month_ids.search_count(
                        [('batch_id', '=', brw_reg.batch_id.id), ('leave_month', '=', False)])
                    joining_date = datetime.strptime(brw_reg.admission_date, "%Y-%m-%d").date()
                    start_date = datetime.strptime(brw_reg.batch_id.start_date, "%Y-%m-%d").date()
                    get_unpaid_diff = brw_reg.get_person_age(start_date, joining_date)
                    leave_month = []
                    for l_month in brw_reg.batch_id.month_ids.search(
                            [('batch_id', '=', brw_reg.batch_id.id), ('leave_month', '=', True)]):
                        leave_month.append((int(l_month.name), int(l_month.year)))
                    month_in_stj = brw_reg.months_between(start_date, joining_date)
                    unpaid_month = 0
                    if get_unpaid_diff.get('months') > 0:
                        unpaid_month = get_unpaid_diff.get('months')
                        if len(month_in_stj) > 0 and len(leave_month) > 0:
                            for leave_month_year in leave_month:
                                if leave_month_year in month_in_stj:
                                    unpaid_month -= 1
                    month_diff -= unpaid_month
                    total_pay_amount = 0.00
                    for fee_structure_rec in brw_reg.student_fee_line:
                        amount = fee_structure_rec.amount or 0.00
                        discount = fee_structure_rec.discount or 0.00
                        pay_amount, dis_amount = brw_reg.acd_manually_fee_calculation(
                            cal_type=fee_structure_rec.fee_pay_type.name,
                            pay_amount=amount, discount=discount,
                            month_diff=month_diff)
                        total_pay_amount += pay_amount

                    res['total_fee'] = total_pay_amount
                    res['total_remaining'] = total_pay_amount
                    res['label_change'] = True
                else:
                    if brw_reg.next_year_advance_fee_id.residual > 0 :
                        res['total_fee'] = brw_reg.next_year_advance_fee_id.residual
                        res['label_change'] = True
                        res['total_remaining'] = brw_reg.next_year_advance_fee_id.residual
                    else :
                        brw_reg.next_year_advance_fee_id.state = 'fee_paid'
                        brw_reg.fee_status = 'academy_fee_pay'
            else:
                res['total_fee'] = brw_reg.invoice_id.residual
                res['label_change'] = True
                res['total_remaining'] = brw_reg.invoice_id.residual
        return res

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
    def _get_move_line_id(self,name,partner_id,journal_id,period_id,account_id,c_date):
        move_line_obj = self.env['account.move.line']
        move_line_data = {
            'name': name,
            'ref': name,
            'partner_id': partner_id,
            'journal_id':journal_id,
            # 'period_id':period_id,
            'account_id':account_id,
            'date': c_date,

        }
        move_rec = move_line_obj.create(move_line_data)
        return move_rec

    @api.multi
    def submit_fee(self):
        print'====================submit fee======== registration======='
        """
        this method is used to manualy subbimit fee.
        -------------------------------------------------
        :return:
        """
        active_id=self._context['active_id']
        brw_reg=self.env['registration'].browse(active_id)
        print "------------------------------------------------------",brw_reg
        bankname = self.bank_name
        sdate = self.cheque_start_date or False
        exdate = self.cheque_expiry_date or False
        chk_num=self.chk_num or False
        party_name=self.party_name or False
        if brw_reg.state=='reg':
            print "ooooo"
            journal_id=self.journal_id.id
            brw_reg.reg_pay_manually(journal_id,bank_name=bankname,chk_num=chk_num,
                    sdate=sdate,exdate=exdate,cheque_pay=self.journal_id.is_cheque,party_name=party_name)
            

        if brw_reg.state=='awaiting_fee':
            print "awaiting_fee"
            voucher_pool = self.env['account.voucher']
            voucher_line_pool = self.env['account.voucher.line']

            # if self.total_fee > self.total_remaining:
            #     raise except_orm(_("Warning!"), _('You can not pay greater than %d amount ')% (self.total_remaining,))
            print brw_reg.invoice_id
            if not brw_reg.invoice_id:
                print "------",brw_reg.invoice_id
                # cheque next acd year id..
                # if not then this.. else create woucher with .... and that account is advance account ------
                if not brw_reg.next_year_advance_fee_id:
                    invoice_id=brw_reg.reg_pay_acd_manually(False)
                    # code to create voucher
                    inv_obj=brw_reg.invoice_id
                    voucher_data = {
                            'period_id': inv_obj.period_id.id,
                            'account_id': self.journal_id.default_debit_account_id.id,
                            'partner_id': inv_obj.partner_id.id,
                            'journal_id':self.journal_id.id,
                            'currency_id': inv_obj.currency_id.id,
                            'reference': inv_obj.name,
                            'amount': self.total_fee,
                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'cheque_start_date':self.cheque_start_date,
                            'cheque_expiry_date':self.cheque_expiry_date,
                            'bank_name':self.bank_name,
                            'cheque':self.cheque,
                            'party_name' :self.party_name,
                            'chk_num':self.chk_num,
                            'invoice_id':inv_obj.id,
                        }
                    voucher_id = voucher_pool.create(voucher_data)
                    date = time.strftime('%Y-%m-%d')
                    print voucher_id
                    if voucher_id:
                        res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, self.journal_id.id, self.total_fee, inv_obj.currency_id.id, inv_obj.type,date)
                        total_amount = self.total_fee
                        if self.total_fee >= inv_obj.residual:
                            total_amount = inv_obj.residual
                        # Loop through each document and Pay only selected documents and create a single receipt
                        for line_data in res['value']['line_cr_ids']:
                            if not line_data['amount']:
                                continue
                            name = line_data['name']

                            if line_data['name'] in [inv_obj.number]:
                                if not line_data['amount']:
                                    continue
                                voucher_lines = {
                                    'move_line_id': line_data['move_line_id'],
                                    'amount': total_amount,
                                    'name': line_data['name'],
                                    'amount_unreconciled': line_data['amount_unreconciled'],
                                    'type': line_data['type'],
                                    'amount_original': line_data['amount_original'],
                                    'account_id': line_data['account_id'],
                                    'voucher_id': voucher_id.id,
                                }

                                voucher_line_pool.create(voucher_lines)

                        for line_data in res['value']['line_dr_ids']:

                            if not line_data['amount']:
                                continue

                            if line_data['name'] in [inv_obj.number]:
                                if not line_data['amount']:
                                    continue
                                voucher_lines = {
                                    'move_line_id': line_data['move_line_id'],
                                    'amount': total_amount,
                                    'name': line_data['name'],
                                    'amount_unreconciled': line_data['amount_unreconciled'],
                                    'type': line_data['type'],
                                    'amount_original': line_data['amount_original'],

                                    'account_id': line_data['account_id'],
                                    'voucher_id': voucher_id.id,
                                }
                                voucher_line_id = voucher_line_pool.create(voucher_lines)

                        # Add Journal Entries
                        voucher_id.proforma_voucher()

                        brw_reg.paid_amount= brw_reg.paid_amount+self.total_fee

                        if inv_obj.state == 'open':
                            mail_obj=self.env['mail.mail']
                            email_server=self.env['ir.mail_server']
                            email_sender=email_server.search([])
                            ir_model_data = self.env['ir.model.data']
                            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_open')[1]
                            template_rec = self.env['mail.template'].browse(template_id)
                            template_rec.write({'email_to' : brw_reg.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                            template_rec.send_mail(voucher_id.id, force_send=True)

                        elif inv_obj.state == 'paid':
                            mail_obj=self.env['mail.mail']
                            email_server=self.env['ir.mail_server']
                            email_sender=email_server.search([])
                            ir_model_data = self.env['ir.model.data']
                            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                            template_rec = self.env['email.template'].browse(template_id)
                            template_rec.write({'email_to' : brw_reg.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                            template_rec.send_mail(voucher_id.id, force_send=True)
                else:
                    currency_id = self._get_currency()
                    partner_rec = brw_reg.next_year_advance_fee_id.partner_id
                    date = time.strftime('%Y-%m-%d')
                    order_id = brw_reg.next_year_advance_fee_id.order_id
                    period_id = self._get_period().id
                    account_id = self.journal_id.default_debit_account_id.id
                    total_amount = self.total_fee
                    # if self.total_fee >= brw_reg.next_year_advance_fee_id.residual:
                    #     total_amount = brw_reg.next_year_advance_fee_id.residual
                    if not partner_rec.property_account_customer_advance:
                        raise except_orm(_('Warning!'),
                            _("Please define advance account of student %s!")%(partner_rec.name))
                    voucher_data = {
                            'period_id': period_id,
                            'account_id': account_id,
                            'partner_id': partner_rec.id,
                            'journal_id': self.journal_id.id,
                            'currency_id': currency_id,
                            'reference': order_id,
                            'amount': total_amount,
                            'type': 'receipt',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'cheque_start_date':self.cheque_start_date,
                            'cheque_expiry_date':self.cheque_expiry_date,
                            'bank_name':self.bank_name,
                            'cheque':self.cheque,
                            'party_name' :self.party_name,
                            'chk_num':self.chk_num,
                            'advance_account_id':partner_rec.property_account_customer_advance.id,
                            # 'invoice_id':inv_obj.id,
                        }
                    voucher_id = voucher_pool.create(voucher_data)

                    # Add Journal Entries
                    voucher_id.proforma_voucher()
                    brw_reg.next_year_advance_fee_id.total_paid_amount += total_amount
                    if round(brw_reg.next_year_advance_fee_id.total_amount,2) <= round(brw_reg.next_year_advance_fee_id.total_paid_amount,2):
                        brw_reg.next_year_advance_fee_id.state = 'fee_paid'
                        brw_reg.fee_status = 'academy_fee_pay'
                    elif round(brw_reg.next_year_advance_fee_id.total_paid_amount,2) < round(brw_reg.next_year_advance_fee_id.total_amount,2) and brw_reg.next_year_advance_fee_id.total_paid_amount != 0.00:
                        brw_reg.next_year_advance_fee_id.state = 'fee_partial_paid'
                        brw_reg.fee_status = 'academy_fee_partial_pay'
                    brw_reg.next_year_advance_fee_id.payment_ids = [(4, voucher_id.id)]
                    brw_reg.next_year_advance_fee_id.journal_ids = [(4,self.journal_id.id)]
                    brw_reg.next_year_advance_fee_id.journal_id = self.journal_id.id

                    # send mail for advance payment recipt
                    mail_obj = self.env['mail.mail']
                    email_server = self.env['ir.mail_server']
                    email_sender = email_server.search([])
                    ir_model_data = self.env['ir.model.data']
                    template_id = \
                    ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                    template_rec = self.env['email.template'].browse(template_id)
                    template_rec.write({'email_to': brw_reg.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
                    template_rec.send_mail(voucher_id.id, force_send=True)
            else:
                print "else part"
                # code to create voucher
                inv_obj=brw_reg.invoice_id
                print "----",inv_obj.state
                if inv_obj.state=='open':
                    print "open"
                    voucher_data = {
                            'period_id': inv_obj.period_id.id,
                            'account_id': self.journal_id.default_debit_account_id.id,
                            'partner_id': inv_obj.partner_id.id,
                            'journal_id': self.journal_id.id,
                            'currency_id': inv_obj.currency_id.id,
                            'reference': inv_obj.name,
                            'amount': self.total_fee,
                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'cheque_start_date':self.cheque_start_date or False,
                            'cheque_expiry_date':self.cheque_expiry_date or False,
                            'bank_name':self.bank_name or "",
                            'cheque':self.cheque,
                            'party_name' :self.party_name or "",
                            'chk_num':self.chk_num or "",
                            'invoice_id':inv_obj.id,
                            }

                # create voucher
                voucher_id = voucher_pool.create(voucher_data)
                print "voucher_id ===",voucher_id
                date = time.strftime('%Y-%m-%d')
                if voucher_id:
                    print self.journal_id.id
                    res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, self.journal_id.id, self.total_fee, inv_obj.currency_id.id, inv_obj.type,date)
                    total_amount = self.total_fee
                    if self.total_fee >= inv_obj.residual:
                        total_amount = inv_obj.residual
                    #Loop through each document and Pay only selected documents and create a single receipt
                    for line_data in res['value']['line_cr_ids']:
                        if not line_data['amount']:
                            continue
                        name = line_data['name']

                        if line_data['name'] in [inv_obj.number]:
                            if not line_data['amount']:
                                continue
                            voucher_lines = {
                                'move_line_id': line_data['move_line_id'],
                                'amount': total_amount,
                                'name': line_data['name'],
                                'amount_unreconciled': line_data['amount_unreconciled'],
                                'type': line_data['type'],
                                'amount_original': line_data['amount_original'],
                                'account_id': line_data['account_id'],
                                'voucher_id': voucher_id.id,
                            }
                            voucher_line_pool.create(voucher_lines)

                    for line_data in res['value']['line_dr_ids']:
                        if not line_data['amount']:
                            continue
                        if line_data['name'] in [inv_obj.number]:
                            if not line_data['amount']:
                                continue
                            voucher_lines = {
                                'move_line_id': line_data['move_line_id'],
                                'amount': total_amount,
                                'name': line_data['name'],
                                'amount_unreconciled': line_data['amount_unreconciled'],
                                'type': line_data['type'],
                                'amount_original': line_data['amount_original'],
                                'account_id': line_data['account_id'],
                                'voucher_id': voucher_id.id,
                            }
                            voucher_line_id = voucher_line_pool.create(voucher_lines)

                    #Add Journal Entries
                    voucher_id.proforma_voucher()

                    brw_reg.paid_amount= brw_reg.paid_amount+self.total_fee
                    # send mail for recipt of payment,
                    if inv_obj.state == 'open':
                        mail_obj=self.env['mail.mail']
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_open')[1]
                        template_rec = self.env['email.template'].browse(template_id)
                        template_rec.write({'email_to' : brw_reg.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                        template_rec.send_mail(voucher_id.id, force_send=True)

                    elif inv_obj.state == 'paid':
                        mail_obj=self.env['mail.mail']
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                        template_rec = self.env['email.template'].browse(template_id)
                        template_rec.write({'email_to' : brw_reg.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                        template_rec.send_mail(voucher_id.id, force_send=True)




