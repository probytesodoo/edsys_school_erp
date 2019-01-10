from odoo import api, SUPERUSER_ID
from odoo import models, fields, api, _
from odoo import http
from odoo.http import request,db_filter
import time
import odoo
import base64, re
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
import csv
import datetime
from datetime import datetime


class payfort_payment_status(http.Controller):

    @http.route(['/ticket1227_DIB'], type='http', auth="public")
    def t_1227_DIB(self, **post):
        voucher_obj = request.env['account.voucher']
        active_payforts_rec = request.env['payfort.config'].sudo().search([('active', '=', 'True')])
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.journal_id.id:
                journal_id = active_payforts_rec.journal_id
        voucher_rec = voucher_obj.sudo().search([('payfort_type','=',True),('state','=','draft')])
        for v_rec in voucher_rec:
            if v_rec.amount == 0:
                v_rec.journal_id = journal_id.id
        return 'Sucess Fully Updated record....'

    @http.route("/ticket2388/", auth='none')
    def ticket_2388(self):
        """
        resolve ticket 2388
        -----------------
        :return:
        """
        count=0
        acc_obj =request.env["account.invoice"]
        query = '''select invoice_id from account_invoice_line as line INNER JOIN account_invoice as invoice ON line.invoice_id=invoice.id where invoice.state='paid' and line.rem_amount >0.0'''
        params = ()
        request.env.cr.execute(query,params)
        invoice_ids = map(lambda x:x[0],request.env.cr.fetchall())
        
        print "total invoice {}".format(len(invoice_ids))
        #import ipdb;ipdb.set_trace()
        for invoice in acc_obj.sudo().browse(invoice_ids)  :
            count+=1;print count 
            for line in invoice.invoice_line_ids : 
                if line.rem_amount >0.0 or line.rem_amount <0.0 :
                    line.write({"rem_amount" : 0.0})
                    print "---------REMAINIGN AMOUNT UPDATED-------------"
        print "-----------OVER----------"
        return "SUCESS" 

    @http.route("/ticket_2829_2831/", auth='none')
    def get_cust_advance_account(self):
        """
        Add Advance account to customer
        -----------------
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        res_part = env['res.partner']
        count = 0
        for partner in res_part.search([]):
            count += 1; print count
            if not partner.property_account_customer_advance:
                partner.property_account_customer_advance = 678
                print "Updated"

        return "Sucecess"
    @api.model
    def _get_period(self):
        print'----------------------get periop main------------'
        """
        This method is used for getting
        current period.
        -------------------------------
        :return: period id
        """
#         env = request.env(user=odoo.SUPERUSER_ID)
#         env = self.env.user.id()
        env = request.env(user=SUPERUSER_ID)
#         env = request.env.user == request.website.user_id

#         if self._context is None: context = {}
#         if self._context.get('period_id', False):
#             return self._context.get('period_id')
#         ctx = dict(self._context, account_period_prefer_normal=True)
#         periods = http.request.env['account.period'].sudo().search([])
#         return periods and periods[0] or False

        context =  env.context
        print context,'========================context main'
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = http.request.env['account.period'].sudo().search([])
        return periods and periods[0] or False


    

    def get_journal_from_payfort(self):
        """
        This method is use to get payment method
        from payfort master.
        ----------------------------------------
        :return: record set of account.journal object
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')])
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.journal_id.id:
                return active_payforts_rec.journal_id.id
            else:
                return 12
        else:
            return 12

    def _get_currency(self):
        """
        this method use for get account currency.
        -----------------------------------------
        :return: record set of currency.
        """
        env = request.env(user=SUPERUSER_ID)
        # if self._context is None: self._context = {}
        journal_pool = env['account.journal']
        journal_id = env.context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.sudo().browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return env['res.users'].sudo().browse(env.uid).company_id.currency_id.id

    # def re_registration_parent_payment(self, env, re_reg_parent_rec, amount, pay_id, order_id):
    #     """
    #     when parent pay re-registration fee online.
    #     -----------------
    #     :param env:
    #     :param re_reg_parent_rec: re-registration parent payment
    #     :param amount: amount
    #     :param pay_id: payment id
    #     :param order_id:order id
    #     :return:
    #     """
    #     voucher_obj = env['account.voucher']
    #     currency_id = self._get_currency()
    #     c_date = time.strftime('%Y-%m-%d')
    #     t_date = date.today()
    #     # order_id = parent_re_reg_rec.code
    #     period_id = self._get_period().id
    #     journal_id = self.get_journal_from_payfort()
    #     account_id = env['account.journal'].sudo().browse(journal_id).default_debit_account_id.id
    #     total_amount = self.get_orignal_amount(amount)
    #     email_server = env['ir.mail_server']
    #     email_sender = email_server.sudo().search([])
    #     ir_model_data = env['ir.model.data']
    #     template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
    #     template_rec = env['email.template'].sudo().browse(template_id)
    #     for student_re_reg_rec in re_reg_parent_rec.student_ids:
    #         if student_re_reg_rec.fee_status != 're_Paid' and total_amount > 0:
    #             student_data = '<table border="2"><b><tr><td>Student Name</td><td>Class-Sec</td><td>Re-Registrition Confirm</td><td>Amount Recived for Re-Registration</td></tr></b>'
    #             student_rec = student_re_reg_rec.name
    #             re_reg_advance_account = student_rec.re_reg_advance_account or False
    #             s_payable_amount = 0.00
    #             if total_amount > student_re_reg_rec.residual:
    #                 s_payable_amount = student_re_reg_rec.residual
    #                 total_amount -= s_payable_amount
    #             else:
    #                 s_payable_amount = total_amount
    #                 total_amount -= s_payable_amount
    #
    #             if s_payable_amount > 0.00:
    #                 voucher_data = {
    #                     'period_id': period_id,
    #                     'account_id': account_id,
    #                     'partner_id': student_rec.id,
    #                     'journal_id': journal_id,
    #                     'currency_id': currency_id,
    #                     'reference': student_re_reg_rec.code,
    #                     'amount': s_payable_amount,
    #                     'type': 'receipt' or 'payment',
    #                     'state': 'draft',
    #                     'pay_now': 'pay_later',
    #                     'name': '',
    #                     'date': c_date,
    #                     'company_id': 1,
    #                     'tax_id': False,
    #                     'payment_option': 'without_writeoff',
    #                     'comment': _('Write-Off'),
    #                     'advance_account_id':re_reg_advance_account.id or student_rec.property_account_customer_advance.id or False,
    #                     'payfort_payment_id' : pay_id,
    #                     'payfort_pay_date' : t_date,
    #                     're_reg_fee' : True,
    #                 }
    #                 exist_voucher = voucher_obj.sudo().search([('partner_id','=',student_rec.id),
    #                                                     ('payfort_payment_id','=','payfort_payment_id')])
    #                 if not exist_voucher.id:
    #                     s_voucher_rec = voucher_obj.create(voucher_data)
    #
    #                     # update on re-registration student
    #                     student_re_reg_rec.total_paid_amount += s_payable_amount
    #                     if student_re_reg_rec.residual <= 0:
    #                         student_re_reg_rec.fee_status = 're_Paid'
    #                         student_re_reg_rec.name.re_reg_next_academic_year = 'yes'
    #                     elif student_re_reg_rec.total_paid_amount < student_re_reg_rec.total_amount and student_re_reg_rec.total_paid_amount != 0.00:
    #                         student_re_reg_rec.fee_status = 're_partially_paid'
    #                         student_re_reg_rec.name.re_reg_next_academic_year = 'yes'
    #
    #                     # Add Journal Entries
    #                     s_voucher_rec.button_proforma_voucher()
    #
    #                     self.create_attachment_re_reg_payment_receipt(s_voucher_rec,student_re_reg_rec)
    #                     # Send mail to Parent For Payment Recipt
    #                     student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
    #                         student_re_reg_rec.name.name,student_re_reg_rec.next_year_course_id.name,s_payable_amount)
    #                     template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
    #                     template_rec = env['email.template'].sudo().browse(template_id)
    #                     template_rec.sudo().write({
    #                         'email_to': student_re_reg_rec.name.parents1_id.parents_email,
    #                         'email_from': email_sender.smtp_user,
    #                         'email_cc': '',
    #                         'body_html': '<div><p>Dear %s, </p><br/>'
    #                                          '<p>Thank you for completing the re-registration process by paying an amount of %s and'
    #                                          ' confiriming a place for your child(ren) in the next academic year.'
    #                                          ' Please find the receipt herewith attached for the payment made for the following students:</p>'
    #                                          '<br/>'
    #                                          '<p>%s</p>'
    #                                          '<p>The amount paid towards re-registration is collected as advanced and will be adjusted in next year academic fee.</p>'
    #                                          '<p>Thank you for your prompt response and confirming a seat for your child(ren) in the next academic year with us.'
    #                                          ' We wish your child(ren) better prospects in the next grade and together we will ensure the best of learning for them.</p>'
    #                                          
    #                     template_rec.send_mail(s_voucher_rec.id, force_send=False)
    #
    #     flag_fee_status = True
    #     for student_fee_status in re_reg_parent_rec.student_ids:
    #         if student_fee_status.fee_status == 're_unpaid':
    #             flag_fee_status = False
    #     if flag_fee_status == True:
    #         re_reg_parent_rec.come_to_confirm()
    #
    #     if total_amount > 0.00:
    #         # parent pay amount in advance
    #         partner_rec = re_reg_parent_rec.name
    #         parent_voucher_data = {
    #                     'period_id': period_id,
    #                     'account_id': account_id,
    #                     'partner_id': partner_rec.id,
    #                     'journal_id': journal_id,
    #                     'currency_id': currency_id,
    #                     'reference': re_reg_parent_rec.code,
    #                     'amount': total_amount,
    #                     'type': 'receipt' or 'payment',
    #                     'state': 'draft',
    #                     'pay_now': 'pay_later',
    #                     'name': '',
    #                     'date': c_date,
    #                     'company_id': 1,
    #                     'tax_id': False,
    #                     'payment_option': 'without_writeoff',
    #                     'comment': _('Write-Off'),
    #                     'advance_account_id':partner_rec.property_account_customer_advance.id,
    #                     're_reg_fee' : True,
    #                     'payfort_payment_id' : pay_id,
    #                     'payfort_pay_date' : t_date,
    #                     # 'invoice_id':inv_obj.id,
    #                 }
    #         p_voucher_rec_exist = voucher_obj.sudo().search([('partner_id','=',partner_rec.id),('payfort_payment_id' ,'=', pay_id)])
    #         if not p_voucher_rec_exist.id:
    #             p_voucher_rec = voucher_obj.sudo().create(parent_voucher_data)
    #
    #             # Add Journal Entries
    #             p_voucher_rec.button_proforma_voucher()
    #
    #             # template_rec.write({
    #             #     'email_to': partner_rec.parents_email,
    #             #     'email_from': email_sender.smtp_user,
    #             #     'body_html': '<div><p>Dear, %s </p><br/>'
    #             #                      '<p>Thank you for completing the re-registration process by paying an amount of %s and'
    #             #                      ' confiriming a place for your child(ren) in the next academic year.'
    #             #                      ' Please find the receipt herewith attached for the payment made.</p>'
    #             #                      '<p>The amount paid towards re-registration is collected as advanced and will be adjusted in next year academic fee.</p>'
    #             #                      '<p>Thank you for your prompt response and confirming a seat for your child(ren) in the next academic year with us.'
    #             #                      ' We wish your child(ren) better prospects in the next grade and together we will ensure the best of learning for them.</p>'
    #             #                      
    #             # })
    #             # template_rec.send_mail(p_voucher_rec.id, force_send=False)

    def next_year_advance_payment(self,env,next_year_advance_fee_rec,order_id,amount,pay_id):
        """
        This method use to online payment for next acdemic year in Advance.
        --------------------------------------------------------------------
        :param env: SUPERUSER object
        :param next_year_advance_fee_rec: record set of next year adv payment object
        :param order_id: unique order id
        :param amount: advance payment amount
        :return:
        """
        voucher_obj = env['account.voucher']
        partner_id = next_year_advance_fee_rec.partner_id
        t_date = date.today()
        period_id = self._get_period().id
        journal_id = self.get_journal_from_payfort()
        account_id = env['account.journal'].sudo().browse(journal_id).default_debit_account_id.id
#         total_amount = self.get_orignal_amount(amount)
        currency_id = self._get_currency()
        voucher_data = {
                'period_id': period_id,
                'account_id': account_id,
                'partner_id': partner_id.id,
                'journal_id': journal_id,
                'currency_id': currency_id,
                'reference': order_id,
                'amount': amount,
                'type': 'receipt' or 'payment',
                'state': 'draft',
                'pay_now': 'pay_later',
                'name': '',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': 1,
                'tax_id': False,
                'payment_option': 'without_writeoff',
                'comment': _('Write-Off'),
                'payfort_payment_id' : pay_id,
                'payfort_pay_date' : t_date,
                'advance_account_id':partner_id.property_account_customer_advance.id
            }
        voucher_id_exist = voucher_obj.sudo().search([('partner_id' ,'=', partner_id.id),('payfort_payment_id' ,'=', pay_id)])
        if not voucher_id_exist.id:
            voucher_id = voucher_obj.sudo().create(voucher_data)

            # Add Journal Entries with Advance Acc.
            voucher_id.proforma_voucher()

            next_year_advance_fee_rec.total_paid_amount += amount
            if next_year_advance_fee_rec.total_amount <= next_year_advance_fee_rec.total_paid_amount:
                next_year_advance_fee_rec.state = 'fee_paid'
                next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_pay'
                next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
                next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
            elif next_year_advance_fee_rec.total_paid_amount < next_year_advance_fee_rec.total_amount and next_year_advance_fee_rec.total_paid_amount != 0.00:
                next_year_advance_fee_rec.state = 'fee_partial_paid'
                next_year_advance_fee_rec.reg_id.fee_status = 'academy_fee_partial_pay'
                next_year_advance_fee_rec.reg_id.acd_pay_id = str(pay_id)
                next_year_advance_fee_rec.reg_id.acd_trx_date = t_date
            next_year_advance_fee_rec.payment_ids = [(4,voucher_id.id)]
            next_year_advance_fee_rec.journal_ids = [(4, journal_id)]
            next_year_advance_fee_rec.journal_id = journal_id

            #send mail to perent with fee recipt
            email_server = env['ir.mail_server']
            email_sender = email_server.sudo().search([])
            ir_model_data = env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu','email_template_academic_fee_receipt_paid')[1]
            template_rec = env['mail.template'].sudo().browse(template_id)
            template_rec.sudo().write(
            {'email_to': next_year_advance_fee_rec.partner_id.parents1_id.parents_email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
            template_rec.send_mail(voucher_id.id, force_send=False)
        return True


	#======================new code for calculate invoice amount===================
    def get_orignal_amount_new(self,amount,original_amount):
        """
        this method use to convert orignal amount
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')],limit=1)
        amount = float(amount)
        original_amount = float(original_amount)
        bank_service_charge = 0.0
        transaction_charg_amount = 0.0
        charge = 0.0
        if active_payforts_rec:
            if active_payforts_rec.transaction_charg_amount > 0:
                transaction_charg_amount = active_payforts_rec.transaction_charg_amount
            else:
                transaction_charg_amount = 0.00
            amount -= transaction_charg_amount
#             if active_payforts_rec.bank_service_charge:
#                 bank_service_charge = (original_amount/100) * active_payforts_rec.bank_service_charge
#             else:
#                 bank_service_charge = 0.0 
            # removed payfort charge amount
            if active_payforts_rec.charge > 0:
                charge = (original_amount/100) * active_payforts_rec.charge
            else:
                charge = 0.0
            
            total_amount = amount - charge
            return round(total_amount,2)
        
        else:
            amount -= 0.00
            dummy_amount = 100.00 + 0.00
            act_amount=round(((amount/dummy_amount)*100.00),2)
            return act_amount
        
    #======================new code for calculate invoice amount===================

    def get_orignal_amount(self,amount):
        """
        this method use to convert orignal amount
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')])
        amount = float(amount)
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.transaction_charg_amount > 0:
                transaction_charg_amount = active_payforts_rec.transaction_charg_amount
            else:
                transaction_charg_amount = 0.00
            amount -= transaction_charg_amount
            # removed payfort charge amount
            if active_payforts_rec.charge > 0:
                dummy_amount = 100.00 + active_payforts_rec.charge
                act_amount=round(((amount/dummy_amount)*100.00),2)
            else:
                dummy_amount = 100.00 + 0.00
                act_amount=round(((amount/dummy_amount)*100.00),2)
            return act_amount
        else:
            amount -= 0.00
            dummy_amount = 100.00 + 0.00
            act_amount=round(((amount/dummy_amount)*100.00),2)
            return act_amount

    def resend_academic_fee_payment(self, voucher_rec, amount, env, pay_id):
        """
        This method use when fee payment from resend payfort link, pay from parent.
        hear, already create voucher with 0.00 amount of parent.
        ------------------------------------------------------------
        :param voucher_rec: parent voucher record set with 0.00 amount
        :param amount: amount to pay from parent
        :param env: environment object
        :param payment_id: unique payment id genaret from payfort payment,
        :return:
        """
                
                
        voucher_line_obj = env['account.voucher.line']
        voucher_line_obj = env['account.voucher.line']
        date = time.strftime('%Y-%m-%d')
        journal_id = self.get_journal_from_payfort()
	period_id = self._get_period().id
        # assign payble amount to voucher
        if len(voucher_rec) == 1 and amount != 0:
            amount = float(amount)
            #=======================removed===========================
#             amount = self.get_orignal_amount(amount)
            #=======================removed===========================
            voucher_rec.amount = amount
            voucher_rec.date = time.strftime('%Y-%m-%d')
	    voucher_rec.period_id = period_id
        for voucher in voucher_rec:
            voucher.sudo().write({'payfort_payment_id' : pay_id,'journal_id' : journal_id})
            res = voucher.onchange_partner_id(voucher.partner_id.id, journal_id, float(amount), voucher.currency_id.id,
                                              voucher.type, date)

            advance_amount = 0.00
            for line_data in res['value']['line_dr_ids']:
                if isinstance(line_data, dict):
                    voucher_lines = {
                        'move_line_id': line_data['move_line_id'],
                        'amount':line_data['amount_unreconciled'],
                        'name': line_data['name'],
                        'amount_unreconciled': line_data['amount_unreconciled'],
                        'type': line_data['type'],
                        'amount_original': line_data['amount_original'],
                        'account_id': line_data['account_id'],
                        'voucher_id': voucher.id,
                        'reconcile': True
                    }
                    advance_amount += line_data['amount_unreconciled']
                    voucher_line_obj.sudo().create(voucher_lines)
            amount += advance_amount
            for line_data in res['value']['line_cr_ids']:
                if isinstance(line_data, dict):
                    if amount > 0:
                        set_amount = line_data['amount_unreconciled']
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
                            'voucher_id': voucher.id,
                            'reconcile': True
                        }
                        voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
                        reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
                        if reconsile_vals['value']:
                            voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                            if voucher_line_rec.reconcile:
                                voucher_line_rec.amount_unreconciled=set_amount
                                voucher_line_rec.amount = set_amount
                            else:
                                voucher_line_rec.amount = set_amount
                            amount -= set_amount

            # Validate voucher (Add Journal Entries)
            voucher.proforma_voucher()

            # send mail to perent with fee recipt
            email_server = env['ir.mail_server']
            email_sender = email_server.sudo().search([])
            ir_model_data = env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu','email_template_academic_fee_receipt_paid')[1]
            template_rec = env['mail.template'].sudo().browse(template_id)
            template_rec.sudo().write(
            {'email_to': voucher.partner_id.parents_email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
            template_rec.send_mail(voucher.id, force_send=True)

#     @http.route([
#         '/show_payment_status'
#     ], type='http', auth="public", website=True)
#     def show_payment_status(self, **post):
#         """
#         This method use When Online Payment using Payfot getway.
#         ----------------------------------------------------------
#         :param post:
#         :return:it redirect thankyou page if transactions success
#                 otherwise redirect to transactions fail page.
#         """
#         env = request.env(user=SUPERUSER_ID)
#         try:
#             if post['STATUS'] == '9':
#                 pay_id = post['PAYID']
#                 return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
#                         'pay_id': pay_id})
#             else:
#                 return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
#         except:
#             return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})\\

    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use When Online Payment using Payfot getway.
        ----------------------------------------------------------
        :param post:
        :return:it redirect thankyou page if transactions success
                otherwise redirect to transactions fail page.
        """
        current_date = time.strftime('%Y-%m-%d')
        res = {}
        if post:
            post['TRXDATE'] = time.strftime("%Y-%m-%d")
            if 'status' in post:
                status = post['status']
            if 'response_code' in post:
                response_code = post['response_code']
            if status == '14':
                        
                env = request.env(user=SUPERUSER_ID)
                cr = env.cr
                voucher_pool = env['account.voucher']
                voucher_line_pool = env['account.voucher.line']
                reg_ids = env['registration'].sudo().search([('registration_number', '=', post['merchant_reference'])])
                invoice_ids = env['account.invoice'].sudo().search([('invoice_number', '=', post['merchant_reference'])])
                voucher_rec = env['account.voucher'].sudo().search(
                    [('payfort_type', '=', True), ('voucher_number', '=', post['merchant_reference'])])
                next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['merchant_reference'])])
                journal_id = self.get_journal_from_payfort()
        
                # registration fee payment
                
                if len(reg_ids) > 0:
                    pay_id = ''
                    if post['status'] == '14':
                        for each in reg_ids:
                            paid_amount = 0.00
                            each.fee_status = 'reg_fee_pay'
                            each.pay_id = post['fort_id']
                            datestring = post['TRXDATE']
                            each.trx_date = datestring
                            pay_id = each.pay_id
                            jounral_dict1 = {}
                            jounral_dict2 = {}
                            account_move_obj = env['account.move']
                            exist_stu_fee = account_move_obj.sudo().search_count([('ref', '=', each.enquiry_no)])
                            account_move_obj = env['account.move']
                            account_id = env['account.journal'].search([('bank_acc_number', '=', '402050 Registration Fees')], limit=1)
                            if exist_stu_fee == 0:
                                for student_fee_rec in each.reg_fee_line:
                                    paid_amount = student_fee_rec.amount
                                    if student_fee_rec.amount:
                                        full_name = str(each.name or '') + ' ' + str(each.middle_name or '') + ' ' + str(
                                            each.last_name or '')
                                        jounral_dict1.update({'name': full_name, 'debit': student_fee_rec.amount})
                                        jounral_dict2.update(
                                            {'name': full_name, 'credit': student_fee_rec.amount, 'account_id': account_id.id})
                                move_id = account_move_obj.sudo().create(
                                    {'journal_id': journal_id, 'line_id': [(0, 0, jounral_dict1), (0, 0, jounral_dict2)],
                                     'ref': each.enquiry_no})
                                each.reg_fee_receipt = move_id.id
                            # code for sending fee receipt to student
                            mail_obj = env['mail.mail']
                            email_server = env['ir.mail_server']
                            email_sender = email_server.sudo().search([])
                            ir_model_data = env['ir.model.data']
                            template_id = \
                            ir_model_data.get_object_reference('edsys_edu', 'email_template_registration_receipt')[1]
                            template_rec = env['mail.template'].sudo().browse(template_id)
                            template_rec.sudo().write({'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
                            template_rec.send_mail(each.id, force_send=True)
                            #----------------------New Code For Payment Capture========================
                            payfort_capture_obj = env['payfort.payment.capture']
                            bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                            self.calculate_payfort_charges_value((paid_amount))
                     
                            partner = False
                            payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                            if not payfort_capture_rec.id:
                                payfort_capture_data = {
                                    'date' : current_date,
                                    'partner': partner,
                                    'pay_id' : post.get('fort_id') or '',
                                    'reference_number' :  post.get('merchant_reference'),
                                    'paid_amount' : paid_amount,
                                    'bank_charges' : bank_charges,
                                    'gross_transaction_value' : gross_transaction_value,
                                    'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                    'transaction_charges' : transaction_charges,
                                    'net_amount' : net_amount,
                                }
                                temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                 cr.commit()
                                    
                            return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
                                'pay_id': pay_id})
                    else:
                        return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
                        })
        
                # invoice payment
                if len(invoice_ids) > 0:
                    if post['status'] == '14':
                        datestring = post['TRXDATE']
                        # amount = float(post['amount'])
                        tran_date = datestring
                        reg_obj = env['registration']
                        inv_id = ""
                        c_amount = post['amount']
                        c_amount = float(c_amount) / 100
                        for inv_obj in invoice_ids:
                            if inv_obj.state != 'open':
        
                                # -----------------------------------------------------------------
                                #================= Written new function to calculate the correct amount=======
                                amount = inv_obj.residual
                                #================= Written new function to calculate the correct amount=======
                                journal_rec = env['account.journal'].sudo().browse(journal_id)
                                voucher_data = {
                                    'period_id': inv_obj.period_id.id,
                                    'account_id': journal_rec.default_debit_account_id.id,
                                    'partner_id': inv_obj.partner_id.id,
                                    'journal_id': journal_rec.id,
                                    'currency_id': inv_obj.currency_id.id,
                                    'reference': post['merchant_reference'],  # payplan.name +':'+salesname
                                    'amount': inv_obj.residual,
                                    'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                                    'state': 'draft',
                                    'pay_now': 'pay_later',
                                    'name': '',
                                    'date': time.strftime('%Y-%m-%d'),
                                    'company_id': 1,
                                    'tax_id': False,
                                    'payment_option': 'without_writeoff',
                                    'comment': _('Write-Off'),
                                    'payfort_payment_id' : post['fort_id'],
                                    'payfort_pay_date' : tran_date,
                                }
                                voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
                                                                                 ('payfort_payment_id' ,'=', post['fort_id'])])
                                if voucher_pool_exist.id:
                                    
                                    #----------------------New Code For Payment Capture========================
                                    payfort_capture_obj = env['payfort.payment.capture']
                                    bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                                    self.calculate_payfort_charges_value((inv_obj.residual))
                                    if inv_obj.partner_id.id:
                                        partner = inv_obj.partner_id.id
                                    else:
                                        partner = False
                                    payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                                    if not payfort_capture_rec.id:
                                        payfort_capture_data = {
                                            'date' : current_date,
                                            'partner': partner,
                                            'pay_id' : post.get('fort_id') or '',
                                            'reference_number' :  post.get('merchant_reference'),
                                            'paid_amount' : inv_obj.residual,
                                            'bank_charges' : bank_charges,
                                            'gross_transaction_value' : gross_transaction_value,
                                            'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                            'transaction_charges' : transaction_charges,
                                            'net_amount' : net_amount,
                                        }
                                        temp = payfort_capture_obj.sudo().create(payfort_capture_data)
                                    cr.commit()
                                    
                                    #----------------------New Code For Payment Capture========================
                                                
                                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                        'pay_id': post['fort_id']})
                                else:
                                    voucher_id = voucher_pool.sudo().create(voucher_data)
                                    #================= Commite current state For exception=======
#                                     cr.commit()
                                    #================= Commite current state For exception=======
                                    
                                    # return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
                                    #----------------------New Code For Payment Capture========================
                                    payfort_capture_obj = env['payfort.payment.capture']
                                    bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                                    self.calculate_payfort_charges_value((inv_obj.residual))
                                    if inv_obj.partner_id.id:
                                        partner = inv_obj.partner_id.id
                                    else:
                                        partner = False
                                    payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                                    if not payfort_capture_rec.id:
                                        payfort_capture_data = {
                                            'date' : current_date,
                                            'partner': partner,
                                            'pay_id' : post.get('fort_id') or '',
                                            'reference_number' :  post.get('merchant_reference'),
                                            'paid_amount' : inv_obj.residual,
                                            'bank_charges' : bank_charges,
                                            'gross_transaction_value' : gross_transaction_value,
                                            'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                            'transaction_charges' : transaction_charges,
                                            'net_amount' : net_amount,
                                        }
                                        temp = payfort_capture_obj.sudo().create(payfort_capture_data)
                                    cr.commit()
                                    
                                    #----------------------New Code For Payment Capture========================
                                
                                    voucher_id.proforma_voucher()
                                # payment date and payment id store in invoice
                                inv_obj.payfort_pay_date = tran_date
                                inv_obj.payfort_payment_id = post['fort_id']
        
                                reg_ids = reg_obj.sudo().search([('student_id', '=', inv_obj.partner_id.id)])
        
                                # code for sending fee receipt to student
                                if len(reg_ids) > 0:
                                    for each in reg_ids:
                                        each.fee_status = 'academy_fee_pay'
                                        each.acd_pay_id = post['fort_id']
                                        each.acd_trx_date = tran_date
        #                                 email_server = env['ir.mail_server']
        #                                 email_sender = email_server.sudo().search([])
        #                                 ir_model_data = env['ir.model.data']
        #                                 template_id = ir_model_data.get_object_reference(
        #                                     'edsys_edu',
        #                                     'email_template_academic_fee_receipt_paid')[1]
        #                                 template_rec = env['email.template'].sudo().browse(template_id)
        #                                 template_rec.sudo().write(
        #                                     {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
        #                                 template_rec.send_mail(voucher_id.id)
                                
                                return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                    'pay_id': post['fort_id']})
                                # --------------------------------------------------------------------
        
        
                            else:
                                print '===========else'
                                #================= Written new function to calculate the correct amount=======
                                amount = inv_obj.residual
                                #================= Written new function to calculate the correct amount=======
                                journal_rec = env['account.journal'].sudo().browse(journal_id)
                                voucher_data = {
                                    'period_id': inv_obj.period_id.id,
                                    'account_id': journal_rec.default_debit_account_id.id,
                                    'partner_id': inv_obj.partner_id.id,
                                    'journal_id': journal_rec.id,
                                    'currency_id': inv_obj.currency_id.id,
                                    'reference': inv_obj.name,  # payplan.name +':'+salesname
                                    'amount': inv_obj.residual,
                                    'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                                    'state': 'draft',
                                    'pay_now': 'pay_later',
                                    'name': '',
                                    'date': time.strftime('%Y-%m-%d'),
                                    'company_id': 1,
                                    'tax_id': False,
                                    'payment_option': 'without_writeoff',
                                    'comment': _('Write-Off'),
                                    'payfort_payment_id' : post['fort_id'],
                                    'payfort_pay_date' : tran_date,
                                }
                                voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
                                                                                 ('payfort_payment_id' ,'=', post['fort_id'])])
                                print voucher_pool_exist,'========voucher_pool_exist'
                                if voucher_pool_exist.id:
                                    #----------------------New Code For Payment Capture========================
                                    payfort_capture_obj = env['payfort.payment.capture']
                                    bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                                    self.calculate_payfort_charges_value((inv_obj.residual))
                                    if inv_obj.partner_id.id:
                                        partner = inv_obj.partner_id.id
                                    else:
                                        partner = False
                                    payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                                    if not payfort_capture_rec.id:
                                        payfort_capture_data = {
                                            'date' : current_date,
                                            'partner': partner,
                                            'pay_id' : post.get('fort_id') or '',
                                            'reference_number' :  post.get('merchant_reference'),
                                            'paid_amount' : inv_obj.residual,
                                            'bank_charges' : bank_charges,
                                            'gross_transaction_value' : gross_transaction_value,
                                            'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                            'transaction_charges' : transaction_charges,
                                            'net_amount' : net_amount,
                                        }
                                        temp = payfort_capture_obj.sudo().create(payfort_capture_data)
                                    cr.commit()
                                    
                                    #----------------------New Code For Payment Capture========================
                                    return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                        'pay_id': post['fort_id']})
                                else:
                                    voucher_id = voucher_pool.sudo().create(voucher_data)
                                    print voucher_id,'=======voucher_id'
                                    #================= Commite current state For exception=======
#                                     cr.commit()
                                    #================= Commite current state For exception=======
                                    
                                    date = time.strftime('%Y-%m-%d')
                                    if voucher_id:
                                        res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, journal_id,
                                                                             inv_obj.amount_total,
                                                                             inv_obj.currency_id.id, inv_obj.type, date)
                                        advance_amount = 0.00
                                        for line_data in res['value']['line_dr_ids']:
                                            voucher_lines = {
                                                'move_line_id': line_data['move_line_id'],
                                                'amount':line_data['amount_unreconciled'],
                                                'name': line_data['name'],
                                                'amount_unreconciled': line_data['amount_unreconciled'],
                                                'type': line_data['type'],
                                                'amount_original': line_data['amount_original'],
                                                'account_id': line_data['account_id'],
                                                'voucher_id': voucher_id.id,
                                                'reconcile': True
                                            }
                                            advance_amount += line_data['amount_unreconciled']
                                            voucher_cr_lines = voucher_line_pool.sudo().create(voucher_lines)
                                            print voucher_cr_lines,'-===========voucher_dr_lines'
                                            #================= Commite current state For exception=======
#                                             cr.commit()
                                            #================= Commite current state For exception=======
                                        amount += advance_amount
                                        for line_data in res['value']['line_cr_ids']:
                                            # if not line_data['amount']:
                                            #     continue
                                            # name = line_data['name']
                                            if line_data['name'] in [inv_obj.number]:
                                                if amount > 0:
                                                    set_amount = line_data['amount_unreconciled']
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
                                                        'voucher_id': voucher_id.id,
                                                        'reconcile': True
                                                    }
                                                    voucher_line_rec = voucher_line_pool.sudo().create(voucher_lines)
                                                    print voucher_line_rec,'===========cr line=====voucher_line_rec'
                                                    #================= Commite current state For exception=======
                                                    cr.commit()
                                                    #================= Commite current state For exception=======
                                                    reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
                                                    voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                                                    if voucher_line_rec.reconcile:
                                                        voucher_line_rec.amount_unreconciled = set_amount
                                                        voucher_line_rec.amount = set_amount
                                                    else:
                                                        voucher_line_rec.amount = set_amount
                                                    amount -= set_amount
                                        
                                        #----------------------New Code For Payment Capture========================
                                        payfort_capture_obj = env['payfort.payment.capture']
                                        bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                                        self.calculate_payfort_charges_value((inv_obj.residual))
                                        if inv_obj.partner_id.id:
                                            partner = inv_obj.partner_id.id
                                        else:
                                            partner = False
                                        payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                                        if not payfort_capture_rec.id:
                                            payfort_capture_data = {
                                                'date' : current_date,
                                                'partner': partner,
                                                'pay_id' : post.get('fort_id') or '',
                                                'reference_number' :  post.get('merchant_reference'),
                                                'paid_amount' : inv_obj.residual,
                                                'bank_charges' : bank_charges,
                                                'gross_transaction_value' : gross_transaction_value,
                                                'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                                'transaction_charges' : transaction_charges,
                                                'net_amount' : net_amount,
                                            }
                                            temp = payfort_capture_obj.sudo().create(payfort_capture_data)
                                            print temp,'====11111111111111============temp'
                                        cr.commit()
                                        
                                        voucher_id.proforma_voucher()
                                        #----------------------New Code For Payment Capture========================
                                        # Add Journal Entries
                                        
                                        # payment date and payment id store in invoice
                                        inv_obj.payfort_pay_date = tran_date
                                        inv_obj.payfort_payment_id = post['fort_id']
        
                                        partner_id = inv_obj.partner_id
                                        reg_ids = reg_obj.sudo().search([('student_id', '=', partner_id.id)])
        
                                        # code for sending fee receipt to student
                                        if len(reg_ids) > 0:
                                            for each in reg_ids:
                                                each.fee_status = 'academy_fee_pay'
                                                each.acd_pay_id = post['fort_id']
                                                each.acd_trx_date = tran_date
                                                email_server = env['ir.mail_server']
                                                email_sender = email_server.sudo().search([])
                                                ir_model_data = env['ir.model.data']
                                                template_id = ir_model_data.get_object_reference(
                                                    'edsys_edu',
                                                    'email_template_academic_fee_receipt_paid')[1]
                                                template_rec = env['email.template'].sudo().browse(template_id)
                                                template_rec.sudo().write(
                                                    {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
                                                template_rec.send_mail(voucher_id.id, force_send=True)
                                                print '========================end'
                                                return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                                    'pay_id': post['fort_id']})
                    else:
                        return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                        })
        
                # for re-send academic link
                if len(voucher_rec) > 0:
                    #=========================new code to collect payable voucher amount====================
                    total_amount =0.0
                    if voucher_rec.partner_id:
                        voucher_datetime = datetime.strptime(voucher_rec.date, "%Y-%m-%d")
                        voucher_date = voucher_datetime.date()
                        #voucher_date = voucher_rec.date
                        account_invoice_obj = env['account.invoice']
                        for parent_rec in voucher_rec.partner_id:
                            student_id_list = []
                            total_advance = 0.0
                            parent_cedit = 0.00
                            if parent_rec.chield1_ids:
                                for child_rec in parent_rec.chield1_ids:
                                        if child_rec.active != False:
                                            student_id_list.append(child_rec.id)
                                stud_rec = env['res.partner'].browse(student_id_list)
                                if len(stud_rec) > 0:
                                    # check for parent advance payment#this is my logic
                                    if parent_rec.credit :
                                        parent_cedit += parent_rec.credit
                                    total_amount += parent_cedit                    
                
                                    for student_rec in stud_rec:
                                        invoice_residual_amount = 0
                                        
                                        # COLLECT STUDENT ADVANCES
                                        total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                        advance_total_recivable = 0.0
                                        if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
                                            advance_total_recivable = 0.0
                                        elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
                                            advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                        
                                        #for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund')]):
                                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund'),('date_invoice','<=',voucher_date)]):
                                            #GET OPEN INVOICES
                                            if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
                                                # CHECK FOR NEGATIVE AMOUNT
                                                if invoice_rec.amount_total < 0 : 
                                                    invoice_residual_amount = -invoice_rec.residual
                                                else : 
                                                    invoice_residual_amount += invoice_rec.residual
                #                                                     
                                        #total_amount += student_rec.credit
                                        total_amount += invoice_residual_amount
                                        #Remove student advances
                                        if student_rec.credit < 0:
                                            total_amount += student_rec.credit
                    #=========================new code to collect payable voucher amount====================
                    
                    if post['status']=='14':
                        amount = post['amount']
                        #=========================new code to collect payable voucher amount====================
                        c_amount = float(amount) / 100
                        #amount = total_amount
                        #=========================new code to collect payable voucher amount====================
                        total_amount = voucher_rec.voucher_amount
                        self.resend_academic_fee_payment(voucher_rec=voucher_rec,
                                                         amount=total_amount,
                                                         env=env,
                                                         pay_id = post['fort_id'])
                        #----------------------New Code For Payment Capture========================
                        payfort_capture_obj = env['payfort.payment.capture']
                        bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                        self.calculate_payfort_charges_value((total_amount))
                        if voucher_rec:
                            partner = voucher_rec.partner_id.id
                        else:
                            partner = False
                        payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                        if not payfort_capture_rec.id:
                            payfort_capture_data = {
                                'date' : current_date,
                                'partner': partner,
                                'pay_id' : post.get('fort_id') or '',
                                'reference_number' :  post.get('merchant_reference'),
                                'paid_amount' : total_amount,
                                'bank_charges' : bank_charges,
                                'gross_transaction_value' : c_amount,
                                'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                'transaction_charges' : transaction_charges,
                                'net_amount' : net_amount,
                            }
                            temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                             cr.commit()
                        
                        #----------------------New Code For Payment Capture========================
                        return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                        'pay_id': post['fort_id']})
                    else:
                        return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                              })
        
                # for next year advance fee payment
                if len(next_year_advance_fee_rec) > 0:
                    if post['status']=='14':
                        order_id = post['merchant_reference']
                        c_amount = post['amount']
                        c_amount = float(c_amount) / 100
                        original_amount = 0.00
                        original_amount = next_year_advance_fee_rec.residual
                        amount = original_amount
                        payment_id = post['fort_id']
                        voucher_obj = env['account.voucher']
                        voucher_rec = voucher_obj.sudo().search([('payfort_payment_id','=',payment_id),('reference','=',order_id)],
                                                         limit=1)
                        if not voucher_rec.id:
                            self.next_year_advance_payment(env=env,
                                                           next_year_advance_fee_rec=next_year_advance_fee_rec,
                                                           order_id=order_id,
                                                           amount=amount,
                                                           pay_id = payment_id)
                            
                            #----------------------New Code For Payment Capture========================
                            payfort_capture_obj = env['payfort.payment.capture']
                            bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                            self.calculate_payfort_charges_value((original_amount))
                            if next_year_advance_fee_rec:
                                partner = next_year_advance_fee_rec.partner_id.id
                            else:
                                partner = False
                            payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                            if not payfort_capture_rec.id:
                                payfort_capture_data = {
                                    'date' : current_date,
                                    'partner': partner,
                                    'pay_id' : post.get('fort_id') or '',
                                    'reference_number' :  post.get('merchant_reference'),
                                    'paid_amount' : original_amount,
                                    'bank_charges' : bank_charges,
                                    'gross_transaction_value' : gross_transaction_value,
                                    'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                    'transaction_charges' : transaction_charges,
                                    'net_amount' : net_amount,
                                }
                                temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                 cr.commit()
                            
                            #----------------------New Code For Payment Capture========================
        
                            return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                            'pay_id':post['fort_id']})
                        else:
                            return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
                                            'pay_id':post['fort_id']})
                    else:
                        return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})


#     @http.route([
#         '/show_acd_payment'
#     ], type='http', auth="public", website=True)
#     def show_acd_payment(self, **post):
#         """
#         This method use When Online Payment using Payfot getway.
#         ----------------------------------------------------------
#         :param post:
#         :return:it redirect thankyou page if transactions success
#                 otherwise redirect to transactions fail page.
#         """
#         current_date = time.strftime('%Y-%m-%d')
#         res = {}
#         if post:
#             post['TRXDATE'] = time.strftime("%Y-%m-%d")
#             if 'status' in post:
#                 status = post['status']
#             if 'response_code' in post:
#                 response_code = post['response_code']
#             if status == '14':
#                         
#                 env = request.env(user=SUPERUSER_ID)
#                 cr = env.cr
#                 voucher_pool = env['account.voucher']
#                 voucher_line_pool = env['account.voucher.line']
#                 reg_ids = env['registration'].sudo().search([('registration_number', '=', post['merchant_reference'])])
#                 invoice_ids = env['account.invoice'].sudo().search([('invoice_number', '=', post['merchant_reference'])])
#                 voucher_rec = env['account.voucher'].sudo().search(
#                     [('payfort_type', '=', True), ('voucher_number', '=', post['merchant_reference'])])
#                 next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['merchant_reference'])])
#                 journal_id = self.get_journal_from_payfort()
#                 # registration fee payment
#                     
#                         
# 
#                 if len(reg_ids) > 0:
#                     pay_id = ''
#                     if post['status'] == '14':
#                         for each in reg_ids:
#                             paid_amount = 0.00
#                             each.fee_status = 'reg_fee_pay'
#                             each.pay_id = post['fort_id']
#                             datestring = post['TRXDATE']
#                             each.trx_date = datestring
#                             pay_id = each.pay_id
#                             jounral_dict1 = {}
#                             jounral_dict2 = {}
#                             account_move_obj = env['account.move']
#                             exist_stu_fee = account_move_obj.sudo().search_count([('ref', '=', each.enquiry_no)])
#                             account_move_obj = env['account.move']
#                             account_id = env['account.account'].search([('code', '=', '402050')], limit=1)
#                             if exist_stu_fee == 0:
#                                 for student_fee_rec in each.reg_fee_line:
#                                     paid_amount = student_fee_rec.amount
#                                     if student_fee_rec.amount:
#                                         full_name = str(each.name or '') + ' ' + str(each.middle_name or '') + ' ' + str(
#                                             each.last_name or '')
#                                         jounral_dict1.update({'name': full_name, 'debit': student_fee_rec.amount})
#                                         jounral_dict2.update(
#                                             {'name': full_name, 'credit': student_fee_rec.amount, 'account_id': account_id.id})
#                                 move_id = account_move_obj.sudo().create(
#                                     {'journal_id': journal_id, 'line_id': [(0, 0, jounral_dict1), (0, 0, jounral_dict2)],
#                                      'ref': each.enquiry_no})
#                                 each.reg_fee_receipt = move_id.id
#                             # code for sending fee receipt to student
#                             email_server = env['ir.mail_server']
#                             email_sender = email_server.sudo().search([])
#                             ir_model_data = env['ir.model.data']
#                             template_id = \
#                             ir_model_data.get_object_reference('edsys_edu', 'email_template_registration_receipt')[1]
#                             template_rec = env['email.template'].sudo().browse(template_id)
#                             template_rec.sudo().write({'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
#                             template_rec.send_mail(each.id, force_send=True)
#                             #----------------------New Code For Payment Capture========================
#                             payfort_capture_obj = env['payfort.payment.capture']
#                             bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                             self.calculate_payfort_charges_value((paid_amount))
#                             partner = False
#                             payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                             if not payfort_capture_rec.id:
#                                 payfort_capture_data = {
#                                     'date' : current_date,
#                                     'partner': partner,
#                                     'pay_id' : post.get('fort_id') or '',
#                                     'reference_number' :  post.get('merchant_reference'),
#                                     'paid_amount' : paid_amount,
#                                     'bank_charges' : bank_charges,
#                                     'gross_transaction_value' : gross_transaction_value,
#                                     'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                     'transaction_charges' : transaction_charges,
#                                     'net_amount' : net_amount,
#                                 }
#                                 temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                             cr.commit()
#                             return request.render("website_student_enquiry.thankyou_reg_fee_paid", {
#                                 'pay_id': pay_id})
#                     else:
#                         return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
#                         })
#                         
#                         
#                 # invoice payment
#                 print invoice_ids,'==============invoice_ids'
#                 if len(invoice_ids) > 0:
#                     if post['status'] == '14':
#                         datestring = post['TRXDATE']
#                         # amount = float(post['amount'])
#                         tran_date = datestring
#                         reg_obj = env['registration']
#                         inv_id = ""
#                         c_amount = post['amount']
#                         c_amount = float(c_amount) / 100
#                         for inv_obj in invoice_ids:
#                             if inv_obj.state != 'open':
#                                 print '=======if'
#                                 # -----------------------------------------------------------------
#                                 #================= Written new function to calculate the correct amount=======
#                                 amount = inv_obj.residual
#                                 #================= Written new function to calculate the correct amount=======
#                                 journal_rec = env['account.journal'].sudo().browse(journal_id)
#                                 voucher_data = {
#                                     'period_id': inv_obj.period_id.id,
#                                     'account_id': journal_rec.default_debit_account_id.id,
#                                     'partner_id': inv_obj.partner_id.id,
#                                     'journal_id': journal_rec.id,
#                                     'currency_id': inv_obj.currency_id.id,
#                                     'reference': post['merchant_reference'],  # payplan.name +':'+salesname
#                                     'amount': inv_obj.residual,
#                                     'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
#                                     'state': 'draft',
#                                     'pay_now': 'pay_later',
#                                     'name': '',
#                                     'date': time.strftime('%Y-%m-%d'),
#                                     'company_id': 1,
#                                     'tax_id': False,
#                                     'payment_option': 'without_writeoff',
#                                     'comment': _('Write-Off'),
#                                     'payfort_payment_id' : post['fort_id'],
#                                     'payfort_pay_date' : tran_date,
#                                 }
#                                 voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
#                                                                                  ('payfort_payment_id' ,'=', post['fort_id'])])
#                                 if voucher_pool_exist.id:
#                                     
#                                     #----------------------New Code For Payment Capture========================
#                                     payfort_capture_obj = env['payfort.payment.capture']
#                                     bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                                     self.calculate_payfort_charges_value((inv_obj.residual))
#                                     if inv_obj.partner_id.id:
#                                         partner = inv_obj.partner_id.id
#                                     else:
#                                         partner = False
#                                     payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                                     if not payfort_capture_rec.id:
#                                         payfort_capture_data = {
#                                             'date' : current_date,
#                                             'partner': partner,
#                                             'pay_id' : post.get('fort_id') or '',
#                                             'reference_number' :  post.get('merchant_reference'),
#                                             'paid_amount' : inv_obj.residual,
#                                             'bank_charges' : bank_charges,
#                                             'gross_transaction_value' : gross_transaction_value,
#                                             'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                             'transaction_charges' : transaction_charges,
#                                             'net_amount' : net_amount,
#                                         }
#                                         temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                     cr.commit()
#                                     
#                                     #----------------------New Code For Payment Capture========================
#                                                 
#                                     return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                         'pay_id': post['fort_id']})
#                                 else:
#                                     voucher_id = voucher_pool.sudo().create(voucher_data)
#                                     #================= Commite current state For exception=======
#                                     cr.commit()
#                                     #================= Commite current state For exception=======
#                                     
#                                     # return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
#                                     #----------------------New Code For Payment Capture========================
#                                     payfort_capture_obj = env['payfort.payment.capture']
#                                     bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                                     self.calculate_payfort_charges_value((inv_obj.residual))
#                                     if inv_obj.partner_id.id:
#                                         partner = inv_obj.partner_id.id
#                                     else:
#                                         partner = False
#                                     payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                                     if not payfort_capture_rec.id:
#                                         payfort_capture_data = {
#                                             'date' : current_date,
#                                             'partner': partner,
#                                             'pay_id' : post.get('fort_id') or '',
#                                             'reference_number' :  post.get('merchant_reference'),
#                                             'paid_amount' : inv_obj.residual,
#                                             'bank_charges' : bank_charges,
#                                             'gross_transaction_value' : gross_transaction_value,
#                                             'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                             'transaction_charges' : transaction_charges,
#                                             'net_amount' : net_amount,
#                                         }
#                                         temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                     cr.commit()
#                                     
#                                     #----------------------New Code For Payment Capture========================
#                                 
#                                     voucher_id.button_proforma_voucher()
#                                 # payment date and payment id store in invoice
#                                 inv_obj.payfort_pay_date = tran_date
#                                 inv_obj.payfort_payment_id = post['fort_id']
#         
#                                 reg_ids = reg_obj.sudo().search([('student_id', '=', inv_obj.partner_id.id)])
#         
#                                 # code for sending fee receipt to student
#                                 if len(reg_ids) > 0:
#                                     for each in reg_ids:
#                                         each.fee_status = 'academy_fee_pay'
#                                         each.acd_pay_id = post['fort_id']
#                                         each.acd_trx_date = tran_date
#         #                                 email_server = env['ir.mail_server']
#         #                                 email_sender = email_server.sudo().search([])
#         #                                 ir_model_data = env['ir.model.data']
#         #                                 template_id = ir_model_data.get_object_reference(
#         #                                     'edsys_edu',
#         #                                     'email_template_academic_fee_receipt_paid')[1]
#         #                                 template_rec = env['email.template'].sudo().browse(template_id)
#         #                                 template_rec.sudo().write(
#         #                                     {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
#         #                                 template_rec.send_mail(voucher_id.id)
#                                 
#                                 return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                     'pay_id': post['fort_id']})
#                                 # --------------------------------------------------------------------
#         
#         
#                             else:
#                                 print '===============else'
#                                 #================= Written new function to calculate the correct amount=======
#                                 amount = inv_obj.residual
#                                 #================= Written new function to calculate the correct amount=======
#                                 journal_rec = env['account.journal'].sudo().browse(journal_id)
#                                 voucher_data = {
#                                     'period_id': inv_obj.period_id.id,
#                                     'account_id': journal_rec.default_debit_account_id.id,
#                                     'partner_id': inv_obj.partner_id.id,
#                                     'journal_id': journal_rec.id,
#                                     'currency_id': inv_obj.currency_id.id,
#                                     'reference': inv_obj.name,  # payplan.name +':'+salesname
#                                     'amount': inv_obj.residual,
#                                     'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
#                                     'state': 'draft',
#                                     'pay_now': 'pay_later',
#                                     'name': '',
#                                     'date': time.strftime('%Y-%m-%d'),
#                                     'company_id': 1,
#                                     'tax_id': False,
#                                     'payment_option': 'without_writeoff',
#                                     'comment': _('Write-Off'),
#                                     'payfort_payment_id' : post['fort_id'],
#                                     'payfort_pay_date' : tran_date,
#                                 }
#                                 voucher_pool_exist = voucher_pool.sudo().search([('partner_id' ,'=', inv_obj.partner_id.id),
#                                                                                  ('payfort_payment_id' ,'=', post['fort_id'])])
#                                 print '================1'
#                                 if voucher_pool_exist.id:
#                                     #----------------------New Code For Payment Capture========================
#                                     payfort_capture_obj = env['payfort.payment.capture']
#                                     bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                                     self.calculate_payfort_charges_value((inv_obj.residual))
#                                     if inv_obj.partner_id.id:
#                                         partner = inv_obj.partner_id.id
#                                     else:
#                                         partner = False
#                                     payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                                     if not payfort_capture_rec.id:
#                                         payfort_capture_data = {
#                                             'date' : current_date,
#                                             'partner': partner,
#                                             'pay_id' : post.get('fort_id') or '',
#                                             'reference_number' :  post.get('merchant_reference'),
#                                             'paid_amount' : inv_obj.residual,
#                                             'bank_charges' : bank_charges,
#                                             'gross_transaction_value' : gross_transaction_value,
#                                             'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                             'transaction_charges' : transaction_charges,
#                                             'net_amount' : net_amount,
#                                         }
#                                         temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                     print '===========================2'
#                                     cr.commit()
#                                     print '==========================3333'
#                                     #----------------------New Code For Payment Capture========================
#                                     return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                         'pay_id': post['fort_id']})
#                                 else:
#                                     print '=================4444'
#                                     voucher_id = voucher_pool.sudo().create(voucher_data)
#                                     #================= Commite current state For exception=======
#                                     cr.commit()
#                                     #================= Commite current state For exception=======
#                                     
#                                     date = time.strftime('%Y-%m-%d')
#                                     if voucher_id:
#                                         res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, journal_id,
#                                                                              inv_obj.amount_total,
#                                                                              inv_obj.currency_id.id, inv_obj.type, date)
#                                         advance_amount = 0.00
#                                         for line_data in res['value']['line_dr_ids']:
#                                             voucher_lines = {
#                                                 'move_line_id': line_data['move_line_id'],
#                                                 'name': line_data['name'],
#                                                 'amount_unreconciled': line_data['amount_unreconciled'],
#                                                 'type': line_data['type'],
#                                                 'amount_original': line_data['amount_original'],
#                                                 'account_id': line_data['account_id'],
#                                                 'voucher_id': voucher_id.id,
#                                                 'reconcile': True
#                                             }
#                                             advance_amount += line_data['amount_unreconciled']
#                                             voucher_line_pool.sudo().create(voucher_lines)
#                                             #================= Commite current state For exception=======
# #                                             cr.commit()
#                                             #================= Commite current state For exception=======
#                                         amount += advance_amount
#                                         for line_data in res['value']['line_cr_ids']:
#                                             # if not line_data['amount']:
#                                             #     continue
#                                             # name = line_data['name']
#                                             if line_data['name'] in [inv_obj.number]:
#                                                 if amount > 0:
#                                                     set_amount = line_data['amount_unreconciled']
#                                                     if amount <= set_amount:
#                                                         set_amount = amount
#                                                     reconcile = False
#                                                     voucher_lines = {
#                                                         'move_line_id': line_data['move_line_id'],
#                                                         'name': line_data['name'],
#                                                         'amount_unreconciled': line_data['amount_unreconciled'],
#                                                         'type': line_data['type'],
#                                                         'amount_original': line_data['amount_original'],
#                                                         'account_id': line_data['account_id'],
#                                                         'voucher_id': voucher_id.id,
#                                                         'reconcile': True
#                                                     }
#                                                     voucher_line_rec = voucher_line_pool.sudo().create(voucher_lines)
#                                                     #================= Commite current state For exception=======
# #                                                     cr.commit()
#                                                     #================= Commite current state For exception=======
#                                                     reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
#                                                     voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
#                                                     if voucher_line_rec.reconcile:
#                                                         amount_vals = voucher_line_rec.onchange_reconcile()
#                                                         voucher_line_rec.amount = amount_vals['value']['amount']
#                                                     else:
#                                                         voucher_line_rec.amount = set_amount
#                                                     amount -= set_amount
#                                         print '=================5555'
#                                         #----------------------New Code For Payment Capture========================
#                                         payfort_capture_obj = env['payfort.payment.capture']
#                                         bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                                         self.calculate_payfort_charges_value((inv_obj.residual))
#                                         if inv_obj.partner_id.id:
#                                             partner = inv_obj.partner_id.id
#                                         else:
#                                             partner = False
#                                         payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                                         if not payfort_capture_rec.id:
#                                             payfort_capture_data = {
#                                                 'date' : current_date,
#                                                 'partner': partner,
#                                                 'pay_id' : post.get('fort_id') or '',
#                                                 'reference_number' :  post.get('merchant_reference'),
#                                                 'paid_amount' : inv_obj.residual,
#                                                 'bank_charges' : bank_charges,
#                                                 'gross_transaction_value' : gross_transaction_value,
#                                                 'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                                 'transaction_charges' : transaction_charges,
#                                                 'net_amount' : net_amount,
#                                             }
#                                             temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                                             cr.commit()
#                                         print '=================6666'
#                                         #----------------------New Code For Payment Capture========================
#                                         # Add Journal Entries
#                                         voucher_id.button_proforma_voucher()
#                                         # payment date and payment id store in invoice
#                                         inv_obj.payfort_pay_date = tran_date
#                                         inv_obj.payfort_payment_id = post['fort_id']
#         
#                                         partner_id = inv_obj.partner_id
#                                         reg_ids = reg_obj.sudo().search([('student_id', '=', partner_id.id)])
#                                         print '=======================7777'
#                                         # code for sending fee receipt to student
#                                         if len(reg_ids) > 0:
#                                             for each in reg_ids:
#                                                 each.fee_status = 'academy_fee_pay'
#                                                 each.acd_pay_id = post['fort_id']
#                                                 each.acd_trx_date = tran_date
#                                                 email_server = env['ir.mail_server']
#                                                 email_sender = email_server.sudo().search([])
#                                                 ir_model_data = env['ir.model.data']
#                                                 template_id = ir_model_data.get_object_reference(
#                                                     'edsys_edu',
#                                                     'email_template_academic_fee_receipt_paid')[1]
#                                                 template_rec = env['email.template'].sudo().browse(template_id)
#                                                 template_rec.sudo().write(
#                                                     {'email_to': each.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
#                                                 template_rec.send_mail(voucher_id.id, force_send=True)
#                                                 print '=================8888'
#                                                 return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                                     'pay_id': post['fort_id']})
#                     else:
#                         return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
#                         })
#                 
#                     # for re-send academic link
#                 if len(voucher_rec) > 0:
#                     print voucher_rec,'===========voucher_rec'
#                     #=========================new code to collect payable voucher amount====================
#                     total_amount =0.0
#                     if voucher_rec.partner_id:
#                         voucher_datetime = datetime.strptime(voucher_rec.date, "%Y-%m-%d")
#                         voucher_date = voucher_datetime.date()
# 			            #voucher_date = voucher_rec.date
#                         account_invoice_obj = env['account.invoice']
#                         for parent_rec in voucher_rec.partner_id:
#                             student_id_list = []
#                             total_advance = 0.0
#                             parent_cedit = 0.00
#                             if parent_rec.chield1_ids:
#                                 for child_rec in parent_rec.chield1_ids:
#                                         if child_rec.active != False:
#                                             student_id_list.append(child_rec.id)
#                                 stud_rec = env['res.partner'].browse(student_id_list)
#                                 if len(stud_rec) > 0:
#                                     # check for parent advance payment#this is my logic
#                                     if parent_rec.credit :
#                                         parent_cedit += parent_rec.credit
#                                     total_amount += parent_cedit                    
#                 
#                                     for student_rec in stud_rec:
#                                         invoice_residual_amount = 0
#                                         
#                                         # COLLECT STUDENT ADVANCES
#                                         total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
#                                         advance_total_recivable = 0.0
#                                         if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
#                                             advance_total_recivable = 0.0
#                                         elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
#                                             advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
#                                         
#                                         #for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund')]):
#                                         for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund'),('date_invoice','<=',voucher_date)]):
#                                             #GET OPEN INVOICES
#                                             if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
#                                                 # CHECK FOR NEGATIVE AMOUNT
#                                                 if invoice_rec.amount_total < 0 : 
#                                                     invoice_residual_amount = -invoice_rec.residual
#                                                 else : 
#                                                     invoice_residual_amount += invoice_rec.residual
#                 #                                                     
#                                         #total_amount += student_rec.credit
#                                         total_amount += invoice_residual_amount
#                                         #Remove student advances
#                                         if student_rec.credit < 0:
#                                             total_amount += student_rec.credit
#                     #=========================new code to collect payable voucher amount====================
#                     
#                     if post['status']=='14':
#                         amount = post['amount']
#                         #=========================new code to collect payable voucher amount====================
#                         c_amount = float(amount) / 100
#                         #amount = total_amount
#                         #=========================new code to collect payable voucher amount====================
#                         
#                         self.resend_academic_fee_payment(voucher_rec=voucher_rec,
#                                                          amount=total_amount,
#                                                          env=env,
#                                                          pay_id = post['fort_id'])
#                         #----------------------New Code For Payment Capture========================
#                         payfort_capture_obj = env['payfort.payment.capture']
#                         bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                         self.calculate_payfort_charges_value((total_amount))
#                         if voucher_rec:
#                             partner = voucher_rec.partner_id.id
#                         else:
#                             partner = False
#                         payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                         if not payfort_capture_rec.id:
#                             payfort_capture_data = {
#                                 'date' : current_date,
#                                 'partner': partner,
#                                 'pay_id' : post.get('fort_id') or '',
#                                 'reference_number' :  post.get('merchant_reference'),
#                                 'paid_amount' : total_amount,
#                                 'bank_charges' : bank_charges,
#                                 'gross_transaction_value' : c_amount,
#                                 'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                 'transaction_charges' : transaction_charges,
#                                 'net_amount' : net_amount,
#                             }
#                             temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                         cr.commit()
#                         
#                         #----------------------New Code For Payment Capture========================
#                         return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                         'pay_id': post['fort_id']})
#                     else:
#                         return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
#                               })
#         
#                 # for next year advance fee payment
#                 if len(next_year_advance_fee_rec) > 0:
#                     print next_year_advance_fee_rec,'============next_year_advance_fee_rec'
#                     if post['status']=='14':
#                         order_id = post['merchant_reference']
#                         c_amount = post['amount']
#                         c_amount = float(c_amount) / 100
#                         original_amount = 0.00
#                         original_amount = next_year_advance_fee_rec.residual
#                         amount = original_amount
#                         payment_id = post['fort_id']
#                         voucher_obj = env['account.voucher']
#                         voucher_rec = voucher_obj.sudo().search([('payfort_payment_id','=',payment_id),('reference','=',order_id)],
#                                                          limit=1)
#                         if not voucher_rec.id:
#                             self.next_year_advance_payment(env=env,
#                                                            next_year_advance_fee_rec=next_year_advance_fee_rec,
#                                                            order_id=order_id,
#                                                            amount=amount,
#                                                            pay_id = payment_id)
#                             
#                             #----------------------New Code For Payment Capture========================
#                             payfort_capture_obj = env['payfort.payment.capture']
#                             bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                             self.calculate_payfort_charges_value((original_amount))
#                             if next_year_advance_fee_rec:
#                                 partner = next_year_advance_fee_rec.partner_id.id
#                             else:
#                                 partner = False
#                             payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                             if not payfort_capture_rec.id:
#                                 payfort_capture_data = {
#                                     'date' : current_date,
#                                     'partner': partner,
#                                     'pay_id' : post.get('fort_id') or '',
#                                     'reference_number' :  post.get('merchant_reference'),
#                                     'paid_amount' : original_amount,
#                                     'bank_charges' : bank_charges,
#                                     'gross_transaction_value' : gross_transaction_value,
#                                     'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                                     'transaction_charges' : transaction_charges,
#                                     'net_amount' : net_amount,
#                                 }
#                                 temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                             cr.commit()
#                             
#                             #----------------------New Code For Payment Capture========================
#         
#                             return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                             'pay_id':post['fort_id']})
#                         else:
#                             return request.render("website_student_enquiry.thankyou_acd_fee_paid", {
#                                             'pay_id':post['fort_id']})
#                     else:
#                         return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
		    
