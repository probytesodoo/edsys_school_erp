from openerp import models, fields, api, _
# from datetime import datetime, timedelta
# from openerp.exceptions import except_orm, Warning, RedirectWarning
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning

class ReRegistrationFeePayManualyStudent(models.TransientModel):

    _name='re.registration.fee.pay.manualy.student'

    total_fee = fields.Float(string="You have to pay this amount")
    # total_remaining = fields.Float(string="Remaining amount")
    journal_id = fields.Many2one('account.journal',string="Payment Method")
    cheque = fields.Boolean(string='Cheque')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')

    @api.onchange('journal_id')
    def store_jounral(self):
        self.cheque = self.journal_id.is_cheque

    @api.model
    def default_get(self, fields):
        res = super(ReRegistrationFeePayManualyStudent,self).default_get(fields)
        active_id = self._context['active_id']
        stud_re_reg_rec = self.env['re.reg.waiting.responce.student'].browse(active_id)
        res['total_fee'] = stud_re_reg_rec.residual
        return res

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

    @api.multi
    def submit_re_registration_fee(self):
        """
        this method is used to student submit paymanualy re-registration fee.
        hear we create voucher of reletad payment with student name.
        and, fee collect as re-registration advance.
        :return:
        """
        active_id = self._context['active_id']
        stud_re_reg_rec = self.env['re.reg.waiting.responce.student'].browse(active_id)
        account_payment_obj = self.env['account.payment']
        voucher_obj = self.env['account.voucher']
        currency_id = self._get_currency()
        partner_rec = stud_re_reg_rec.name
        c_date = time.strftime('%Y-%m-%d')
        order_id = stud_re_reg_rec.code
        period_id = self._get_period().id
        account_id = self.journal_id.default_debit_account_id.id
        total_amount = self.total_fee

        # if self.total_fee >= brw_reg.next_year_advance_fee_id.residual:
        #     total_amount = brw_reg.next_year_advance_fee_id.residual
        open_invoice = self.env['account.invoice'].search([('partner_id','=',stud_re_reg_rec.name.id),('state','=','open')])
        #if stud_re_reg_rec.name.credit > 0.00 or len(open_invoice) > 0:
        #    raise except_orm(_('Warning!'),
        #        _("You have an outstanding balance of %s AED remaining. Please pay the open invoice to proceed with re-registration !")%stud_re_reg_rec.name.credit)
        re_reg_advance_account = partner_rec.re_reg_advance_account
        if not re_reg_advance_account.id:
            raise except_orm(_('Warning!'),
                _("Please define re-registration advance account for student %s!")%(partner_rec.name))

        # create voucher
#         voucher_data = {
#                 'period_id': period_id,
#                 'account_id': account_id,
#                 'partner_id': partner_rec.id,
#                 'journal_id': self.journal_id.id,
#                 'currency_id': currency_id,
#                 'reference': order_id,
#                 'amount': total_amount,
#                 'type': 'receipt' or 'payment',
#                 'state': 'draft',
#                 'pay_now': 'pay_later',
#                 'name': '',
#                 'date': c_date,
#                 'company_id': 1,
#                 'tax_id': False,
#                 'payment_option': 'without_writeoff',
#                 'comment': _('Write-Off'),
#                 'cheque_start_date':self.cheque_start_date,
#                 'cheque_expiry_date':self.cheque_expiry_date,
#                 'bank_name':self.bank_name,
#                 'cheque':self.cheque,
#                 'party_name' :self.party_name,
#                 'chk_num':self.chk_num,
#                 'advance_account_id':re_reg_advance_account.id,
#                 're_reg_fee' : True,
#                 # 'invoice_id':inv_obj.id,
#             }
#         voucher_rec = voucher_obj.create(voucher_data)
# 
#         # Add Journal Entries
#         voucher_rec.button_proforma_voucher()


        payment_vals ={
                               'partner_type' : 'customer',
                               'partner_id' : partner_rec.id,
                               'journal_id' : self.journal_id.id,
                               'amount' : total_amount,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
        payment_rec = account_payment_obj.create(payment_vals)
        payment_rec.post()
        self.env['re.reg.waiting.responce.parents'].create_attachment_payment_receipt(payment_rec,stud_re_reg_rec)

        stud_re_reg_rec.total_paid_amount += total_amount
        student_data = '<table border="2"><tr><td><b>Student Name</b></td><td><b>Class-Sec</b></td><td><b>Re-Registration Confirm</b></td><td><b>Amount Received for Re-Registration</b></td></tr>'
        student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
            stud_re_reg_rec.name.name,stud_re_reg_rec.next_year_course_id.name,total_amount)
        if stud_re_reg_rec.total_amount <= stud_re_reg_rec.total_paid_amount:
            stud_re_reg_rec.fee_status = 're_Paid'
            stud_re_reg_rec.state = 're_registration_confirmed'
            stud_re_reg_rec.name.re_reg_next_academic_year = 'yes'
        elif stud_re_reg_rec.total_paid_amount < stud_re_reg_rec.total_amount and stud_re_reg_rec.total_paid_amount != 0.00:
            stud_re_reg_rec.fee_status = 're_partially_paid'
            stud_re_reg_rec.state = 'awaiting_re_registration_fee'
            stud_re_reg_rec.name.re_reg_next_academic_year = 'no'

        flag_fee_status = True
        for all_stud_rec in stud_re_reg_rec.re_reg_parents.student_ids:
            if all_stud_rec.fee_status == 're_unpaid':
                flag_fee_status = False

        if flag_fee_status == True:
            stud_re_reg_rec.re_reg_parents.come_to_confirm()

#         email_server = self.env['ir.mail_server']
#         email_sender = email_server.search([], limit=1)
#         ir_model_data = self.env['ir.model.data']
#         template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
#         template_rec = self.env['email.template'].sudo().browse(template_id)
#         body_html = template_rec.body_html
#         body_dynamic_html = template_rec.body_html
#         body_dynamic_html += '%s'%(student_data)
#         template_rec.write({'email_to': stud_re_reg_rec.name.parents1_id.parents_email,
#                             'email_from': email_sender.smtp_user,
#                             'email_cc': '',
#                             'body_html': body_dynamic_html})
#         template_rec.send_mail(voucher_rec.id, force_send=False)
#         template_rec.body_html = body_html


class ReRegistrationFeePayManualyParent(models.TransientModel):

    _name='re.registration.fee.pay.manualy.parent'

    total_fee = fields.Float(string="You have to pay this amount")
    # total_remaining = fields.Float(string="Remaining amount")
    journal_id = fields.Many2one('account.journal',string="Payment Method")
    cheque = fields.Boolean(string='Cheque')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')

    @api.model
    def default_get(self, fields):
        res = super(ReRegistrationFeePayManualyParent,self).default_get(fields)
        active_id = self._context['active_id']
        stud_re_reg_rec = self.env['re.reg.waiting.responce.parents'].browse(active_id)
        res['total_fee'] = stud_re_reg_rec.residual
        return res

    @api.onchange('journal_id')
    def store_jounral(self):
        self.cheque = self.journal_id.is_cheque

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

    @api.multi
    def parent_submit_re_registration_fee(self):
        """
        this method is used to parent submit paymanualy re-registration fee.
        hear we create voucher of reletad payment with student name.
        :return:
        """
        active_id = self._context['active_id']
        parent_re_reg_rec = self.env['re.reg.waiting.responce.parents'].browse(active_id)
        total_amount = self.total_fee
        account_payment_obj = self.env['account.payment']
        voucher_obj = self.env['account.voucher']
        currency_id = self._get_currency()
        c_date = time.strftime('%Y-%m-%d')
        # order_id = parent_re_reg_rec.code
        period_id = self._get_period().id
        account_id = self.journal_id.default_debit_account_id.id
#         email_server = self.env['ir.mail_server']
#         email_sender = email_server.sudo().search([])
#         ir_model_data = self.env['ir.model.data']
#         template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
#         template_rec = self.env['email.template'].sudo().browse(template_id)
        for student_re_reg_rec in parent_re_reg_rec.student_ids:
#             if student_re_reg_rec.name.credit > 0.00:
#                 raise except_orm(_('Warning!'),
#                     _("You have an outstanding balance of %s AED remaining. Please pay the open invoice to proceed with re-registration !")%student_re_reg_rec.name.credit)
            student_data = '<table border="2"><tr><td><b>Student Name</b></td><td><b>Class-Sec</b></td><td><b>Re-Registration Confirm</b></td><td><b>Amount Received for Re-Registration</b></td></tr>'
            if student_re_reg_rec.fee_status != 're_Paid' and total_amount > 0:
                student_rec = student_re_reg_rec.name
                re_reg_advance_account = student_rec.re_reg_advance_account
                if not re_reg_advance_account.id:
                    raise except_orm(_('Warning!'),
                        _("Please define re-registration advance account for student %s!")%(student_rec.name))
                s_payable_amount = 0.00
                if total_amount > student_re_reg_rec.residual:
                    s_payable_amount = student_re_reg_rec.residual
                    total_amount -= s_payable_amount
                else:
                    s_payable_amount = total_amount
                    total_amount -= s_payable_amount

                if s_payable_amount > 0.00:
#                     voucher_data = {
#                         'period_id': period_id,
#                         'account_id': account_id,
#                         'partner_id': student_rec.id,
#                         'journal_id': self.journal_id.id,
#                         'currency_id': currency_id,
#                         'reference': student_re_reg_rec.code,
#                         'amount': s_payable_amount,
#                         'type': 'receipt' or 'payment',
#                         'state': 'draft',
#                         'pay_now': 'pay_later',
#                         'name': '',
#                         'date': c_date,
#                         'company_id': 1,
#                         'tax_id': False,
#                         'payment_option': 'without_writeoff',
#                         'comment': _('Write-Off'),
#                         'cheque_start_date':self.cheque_start_date,
#                         'cheque_expiry_date':self.cheque_expiry_date,
#                         'bank_name':self.bank_name,
#                         'cheque':self.cheque,
#                         'party_name' :self.party_name,
#                         'chk_num':self.chk_num,
#                         'advance_account_id':re_reg_advance_account.id,
#                         're_reg_fee' : True,
#                         # 'invoice_id':inv_obj.id,
#                     }

                    payment_vals ={
                               'partner_type' : 'customer',
                               'partner_id' : student_rec.id,
                               'journal_id' : self.journal_id.id,
                               'amount' : s_payable_amount,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
                    s_payment_rec = account_payment_obj.create(payment_vals)
#                     s_voucher_rec = voucher_obj.create(voucher_data)
                    student_re_reg_rec.total_paid_amount += s_payable_amount
                    if student_re_reg_rec.residual <= 0:
                        student_re_reg_rec.fee_status = 're_Paid'
                        student_re_reg_rec.state = 're_registration_confirmed'
                        student_re_reg_rec.name.re_reg_next_academic_year = 'yes'
                    elif student_re_reg_rec.total_paid_amount < student_re_reg_rec.total_amount and student_re_reg_rec.total_paid_amount != 0.00:
                        student_re_reg_rec.fee_status = 're_partially_paid'
                        student_re_reg_rec.state = 'awaiting_re_registration_fee'
                        student_re_reg_rec.name.re_reg_next_academic_year = 'no'

                    # Add Journal Entries
#                     s_voucher_rec.button_proforma_voucher()
                    s_payment_rec.post()
                    self.env['re.reg.waiting.responce.parents'].create_attachment_payment_receipt(s_payment_rec,parent_re_reg_rec)

                    student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
                        student_re_reg_rec.name.name,student_re_reg_rec.next_year_course_id.name,s_payable_amount)
#                     # Send email for Payment Receipt
#                     email_server = self.env['ir.mail_server']
#                     email_sender = email_server.search([], limit=1)
#                     ir_model_data = self.env['ir.model.data']
#                     template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
#                     template_rec = self.env['email.template'].sudo().browse(template_id)
#                     body_html = template_rec.body_html
#                     body_dynamic_html = template_rec.body_html
#                     body_dynamic_html += '%s'%(student_data)
#                     template_rec.write({'email_to': student_re_reg_rec.name.parents1_id.parents_email,
#                                         'email_from': email_sender.smtp_user,
#                                         'email_cc': '',
#                                         'body_html': body_dynamic_html})
#                     template_rec.send_mail(s_voucher_rec.id, force_send=False)
#                     template_rec.body_html = body_html

        flag_fee_status = True
        for student_fee_status in parent_re_reg_rec.student_ids:
            if student_fee_status.fee_status == 're_unpaid':
                flag_fee_status = False
        if flag_fee_status == True:
            parent_re_reg_rec.come_to_confirm()

        if total_amount > 0.00:
            # parent pay re-registation amount in advance
            partner_rec = parent_re_reg_rec.name
            re_reg_advance_account = partner_rec.re_reg_advance_account
            if not re_reg_advance_account.id:
                raise except_orm(_('Warning!'),
                    _("Please define re-registration advance account for Parent %s!")%(partner_rec.name))
#             parent_voucher_data = {
#                         'period_id': period_id,
#                         'account_id': account_id,
#                         'partner_id': partner_rec.id,
#                         'journal_id': self.journal_id.id,
#                         'currency_id': currency_id,
#                         'reference': parent_re_reg_rec.code,
#                         'amount': total_amount,
#                         'type': 'receipt' or 'payment',
#                         'state': 'draft',
#                         'pay_now': 'pay_later',
#                         'name': '',
#                         'date': c_date,
#                         'company_id': 1,
#                         'tax_id': False,
#                         'payment_option': 'without_writeoff',
#                         'comment': _('Write-Off'),
#                         'cheque_start_date':self.cheque_start_date,
#                         'cheque_expiry_date':self.cheque_expiry_date,
#                         'bank_name':self.bank_name,
#                         'cheque':self.cheque,
#                         'party_name' :self.party_name,
#                         'chk_num':self.chk_num,
#                         'advance_account_id':re_reg_advance_account.id,
#                         're_reg_fee' : True,
#                         'advance_account_id':re_reg_advance_account.id,
#                         # 'invoice_id':inv_obj.id,
#                     }
#             p_voucher_rec = voucher_obj.create(parent_voucher_data)
#             p_voucher_rec.button_proforma_voucher()
            payment_vals ={
                               'partner_type' : 'customer',
                               'partner_id' : partner_rec.id,
                               'journal_id' : self.journal_id.id,
                               'amount' : s_payable_amount,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
            p_payment_rec = account_payment_obj.create(payment_vals)
            p_payment_rec.post()
