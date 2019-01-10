from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import date
import base64, re
import time
import odoo
from odoo import models, fields, api, _
from odoo.addons.edsys_edu.controllers.main import payfort_payment_status as edsys_edu_show_acd_payment

class payfort_payment_status_inherit(edsys_edu_show_acd_payment):
    
    
    def calculate_payfort_charges_value(self,paid_amount):
        """
        this method use to calculate payfort charges.
        ---------------------------------------------
        :param amount: get amount from payfort link
        :return: return orignal amount of payment.
        """
        env = request.env(user=SUPERUSER_ID)
        active_payforts_rec = env['payfort.config'].sudo().search([('active', '=', 'True')],limit=1)
        amount = float(paid_amount)
        bank_charges = 0.00
        transaction_charges = 0.00
        gross_transaction_value = 0.00
        net_amount = 0.00
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.charge > 0.00:
                bank_charges = (paid_amount * active_payforts_rec.charge)/100
            else:
                bank_charges = 0.00
            transaction_charges = active_payforts_rec.transaction_charg_amount
            gross_transaction_value = round(paid_amount + bank_charges + transaction_charges)
            if active_payforts_rec.bank_service_charge > 0.00:
                transaction_charges_deducted_by_bank = \
                    (gross_transaction_value * active_payforts_rec.bank_service_charge) / 100
            else:
                transaction_charges_deducted_by_bank = 0.00
            net_amount = gross_transaction_value - transaction_charges_deducted_by_bank
        else:
            bank_charges = 0.00
            transaction_charges = 0.00
            gross_transaction_value = paid_amount + bank_charges + transaction_charges
            transaction_charges_deducted_by_bank = 0.00
            net_amount = gross_transaction_value - transaction_charges_deducted_by_bank
            
        return bank_charges, transaction_charges, gross_transaction_value,\
               net_amount, transaction_charges_deducted_by_bank
    
               
    
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
    

    def create_attachment_re_reg_payment_receipt(self, voucher, re_regi):
        """
        this method is use for create receipt re-registration payment
        also store in back end.
        -------------------------------------------------------------
        :param voucher: voucher record set
        :param re_regi:re registration record set
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        attachment_obj = env['ir.attachment']
        result = False
        for record in voucher:
            ir_actions_report = env['ir.actions.report.xml']
            matching_report = ir_actions_report.search([('name', '=', 'Student Payment Receipt')])
            if matching_report:
                result, format = odoo.report.render_report(request.cr, env.uid, [record.id],
                                                              matching_report.report_name, {'model': 'account.payment'})
                eval_context = {'time': time, 'object': record}
                if not matching_report.attachment or not eval(matching_report.attachment, eval_context):
                    result = base64.b64encode(result)
                    file_name = record.name_get()[0][1]
                    file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                    file_name += ".pdf"
                    attachment_id = attachment_obj.create({
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': re_regi._name,
                        'res_id': re_regi.id,
                        'type': 'binary'
                    })


    def re_registration_parent_payment(self, env, re_reg_parent_rec, amount, pay_id, order_id):
        """
        when parent pay re-registration fee online.
        -----------------
        :param env:
        :param re_reg_parent_rec: re-registration parent payment
        :param amount: amount
        :param pay_id: payment id
        :param order_id:order id
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        account_payment_obj = self.env['account.payment']
        voucher_obj = env['account.voucher']
        currency_id = self._get_currency()
        c_date = time.strftime('%Y-%m-%d')
        t_date = date.today()
        # order_id = parent_re_reg_rec.code
        period_id = self._get_period().id
        journal_id = self.get_journal_from_payfort()
        account_id = env['account.journal'].sudo().browse(journal_id).default_debit_account_id.id
        total_amount = amount
        for student_re_reg_rec in re_reg_parent_rec.student_ids:
            if student_re_reg_rec.fee_status != 're_Paid' and total_amount > 0:
                student_data = '<table border="2"><tr><td><b>Student Name</b></td><td><b>Class-Sec</b></td><td><b>Re-Registrition Confirm</b></td><td><b>Amount Recived for Re-Registration</b></td></tr>'
                student_rec = student_re_reg_rec.name
                re_reg_advance_account = student_rec.re_reg_advance_account or False
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
#                         'journal_id': journal_id,
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
#                         'advance_account_id':re_reg_advance_account.id or student_rec.property_account_customer_advance.id or False,
#                         'payfort_payment_id' : pay_id,
#                         'payfort_pay_date' : t_date,
#                         're_reg_fee' : True,
#                     }

                    payment_vals ={
                               'partner_type' : 'customer',
                               'partner_id' : student_rec.id,
                               'journal_id' : journal_id,
                               'amount' : s_payable_amount,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
                    payment_rec = account_payment_obj.create(payment_vals)
                    payment_rec.post()
                    exist_payment = account_payment_obj.sudo().search([('partner_id','=',student_rec.id),
                                                        ('payfort_payment_id','=','payfort_payment_id')])
                    if not exist_payment.id:
                        s_payment_rec = account_payment_obj.create(payment_vals)

                        # update on re-registration student
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
#                         s_voucher_rec.button_proforma_voucher()

                        self.create_attachment_re_reg_payment_receipt(payment_rec,student_re_reg_rec)
                        #===================commented by shraddha because production server was creating 0 bytes pdf, so added send mail in more ref:send_for_re_registration.py ====================================
                        # # Send mail to Parent For Payment Receipt
                        # student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
                        #     student_re_reg_rec.name.name,student_re_reg_rec.next_year_course_id.name,s_payable_amount)
                        # email_server = env['ir.mail_server']
                        # email_sender = email_server.search([], limit=1)
                        # ir_model_data = env['ir.model.data']
                        # template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
                        # template_rec = env['email.template'].sudo().browse(template_id)
                        # body_html = template_rec.body_html
                        # body_dynamic_html = template_rec.body_html
                        # body_dynamic_html += '%s'%(student_data)
                        # template_rec.write({'email_to': student_re_reg_rec.name.parents1_id.parents_email,
                        #                     'email_from': email_sender.smtp_user,
                        #                     'email_cc': '',
                        #                     'body_html': body_dynamic_html})
                        # template_rec.send_mail(s_voucher_rec.id, force_send=False)
                        # template_rec.body_html = body_html
                        #=======================================================
        flag_fee_status = True
        for student_fee_status in re_reg_parent_rec.student_ids:
            if student_fee_status.fee_status == 're_unpaid':
                flag_fee_status = False
        if flag_fee_status == True:
            re_reg_parent_rec.come_to_confirm()
        


        if total_amount > 0.00:
            # parent pay amount in advance
            partner_rec = re_reg_parent_rec.name
            parent_voucher_data = {
                        'period_id': period_id,
                        'account_id': account_id,
                        'partner_id': partner_rec.id,
                        'journal_id': journal_id,
                        'currency_id': currency_id,
                        'reference': re_reg_parent_rec.code,
                        'amount': total_amount,
                        'type': 'receipt' or 'payment',
                        'state': 'draft',
                        'pay_now': 'pay_later',
                        'name': '',
                        'date': c_date,
                        'company_id': 1,
                        'tax_id': False,
                        'payment_option': 'without_writeoff',
                        'comment': _('Write-Off'),
                        'advance_account_id':partner_rec.property_account_customer_advance.id,
                        're_reg_fee' : True,
                        'payfort_payment_id' : pay_id,
                        'payfort_pay_date' : t_date,
                        # 'invoice_id':inv_obj.id,
                    }
            p_voucher_rec_exist = voucher_obj.sudo().search([('partner_id','=',partner_rec.id),('payfort_payment_id' ,'=', pay_id)])
            if not p_voucher_rec_exist.id:
                p_voucher_rec = voucher_obj.sudo().create(parent_voucher_data)

                # Add Journal Entries
                p_voucher_rec.button_proforma_voucher()

                # template_rec.write({
                #     'email_to': partner_rec.parents_email,
                #     'email_from': email_sender.smtp_user,
                #     'body_html': '<div><p>Dear, %s </p><br/>'
                #                      '<p>Thank you for completing the re-registration process by paying an amount of %s and'
                #                      ' confiriming a place for your child(ren) in the next academic year.'
                #                      ' Please find the receipt herewith attached for the payment made.</p>'
                #                      '<p>The amount paid towards re-registration is collected as advanced and will be adjusted in next year academic fee.</p>'
                #                      '<p>Thank you for your prompt response and confirming a seat for your child(ren) in the next academic year with us.'
                #                      ' We wish your child(ren) better prospects in the next grade and together we will ensure the best of learning for them.</p>'
                #                      
                # })
                # template_rec.send_mail(p_voucher_rec.id, force_send=False)


    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use to online payment by student/parent
        for Re-Registration
        ---------------------------------------------------
        :param post:
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        if post:
            cr = env.cr
            current_date = time.strftime('%Y-%m-%d')
            re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('re_registration_number','=',post['merchant_reference'])],
                                                                                              limit=1)
            #------------------new code-------------------------
            re_reg_amount = re_registration_parent_rec.residual
            #------------------new code-------------------------
            
            if len(re_registration_parent_rec) > 0:
                if post['status']=='14':
                    order_id = post['merchant_reference']
                    c_amount = post['amount']
                    c_amount = float(c_amount) / 100
                    payment_id = post['fort_id']
                    #------------------new code-------------------------
                    c_amount = re_reg_amount
                    #------------------new code-------------------------
                    
                    self.re_registration_parent_payment(env=env,
                                                        re_reg_parent_rec = re_registration_parent_rec,
                                                        amount=c_amount,
                                                        pay_id = payment_id,
                                                        order_id = order_id,
                                                        )
                    
                    #----------------------New Code For Payment Capture========================
                    payfort_capture_obj = env['payfort.payment.capture']
                    bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                        self.calculate_payfort_charges_value(re_reg_amount)
                    re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('re_registration_number','=',post['merchant_reference'])]
                                                                                              , limit=1)
                    partner = False
                    if len(re_registration_parent_rec) > 0:
                        partner = re_registration_parent_rec.name.id
                    payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id')),
                                                                  ('reference_number','=',post.get('merchant_reference'))],limit=1)
                    if not payfort_capture_rec.id:
                    
                        payfort_capture_data = {
                            'date' : current_date,
                            'partner':partner,
                            'pay_id' : post.get('fort_id') or '',
                            'reference_number' :  post.get('merchant_reference'),
                            'paid_amount' : re_reg_amount,
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
                    return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
            res = super(payfort_payment_status_inherit,self).show_acd_payment(**post)
            return res

class LinkReRegistration(http.Controller):

    def decode_base64(self,data):
        """
        Decode base64, padding being optional.
        ------------------------------------------------
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
        """
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += b'='* missing_padding
        try:
            res = base64.decodestring(data)
            if res:
                return res
        except:
            return ''

    @http.route([
        '/student/re_registration/request',
    ], type='http', auth="public", website=True)
    def render_re_registration_request(self, **post):
        """
        this method is used to call webpage for re-registraton,
        confirmation.
        parent book seat for next academic year in advance,
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                required data
        """
        
        child_rec_list_length = 0
        env = request.env(user=SUPERUSER_ID)
        if 'REREG' in post and post.get('REREG'):
            data = post.get('REREG')
            code_re_reg = self.decode_base64(data)
            env = request.env(context=dict(request.env.context, show_address=True,no_tag_br=True))
            parents_re_reg_obj = env['re.reg.waiting.responce.parents']
            student_re_reg_obj = env['re.reg.waiting.responce.student']
            parent_re_reg_rec = parents_re_reg_obj.sudo().search([('code','=',code_re_reg)],limit=1)
            student_re_reg_rec = student_re_reg_obj.sudo().search([('code','=',code_re_reg)],limit=1)
            if parent_re_reg_rec.id:
                child_rec_list = []
                for ch_rec in parent_re_reg_rec.student_ids:
                    if not ch_rec.confirm:
                        child_rec_list.append(ch_rec)
                child_rec_list_length = len(child_rec_list)
                
                return http.request.render("edsys_edu_re_registration.re_registration_request", {
                    'parent_rec': parent_re_reg_rec,
                    'children_rec_list': child_rec_list,
                    'child_rec_list_length':child_rec_list_length
                    })

            elif student_re_reg_rec.id:
                child_rec_list = [student_re_reg_rec]
                child_rec_list_length = len(child_rec_list)
              
                return http.request.render("edsys_edu_re_registration.re_registration_request", {
                    'parent_rec': student_re_reg_rec.re_reg_parents,
                    'children_rec_list': child_rec_list,
                    'child_rec_list_length':child_rec_list_length
                    })
        return http.request.render("edsys_edu_re_registration.re_registration_request", {
            })

    @http.route([
    '/student/re_registration/responce',
    ], type='http', auth="public", website=True,csrf=False)
    def render_student_re_reg_responce(self, **post):
        """
        this method is use for getting response of parent
        for conformation of re-registration process.
        :param post:
        :return:
        """
        if post:
            env = request.env(user=SUPERUSER_ID)
            for key,child_code in post.items():
                if key != 'parent_code':
                    student_re_reg_obj = env['re.reg.waiting.responce.student']
                    ch_code = str(child_code[:-2])
                    student_rec = student_re_reg_obj.sudo().search([('code', '=', ch_code)],limit=1)
                    if child_code[-2:]=='01':
                        student_rec.sudo().write({'confirm':True,'response':True,'confirmation_date':date.today()})
                    elif child_code[-2:]=='00':
                        student_rec.sudo().write({'confirm':False,'response':True,})
                        
            parents_re_reg_obj = env['re.reg.waiting.responce.parents']
            parent_rec = parents_re_reg_obj.sudo().search([('code', '=', post.get('parent_code'))],limit=1)
            parent_rec.come_to_awaiting_fee()

            return http.request.render("edsys_edu_re_registration.re_registration_request_thankyou",{})
