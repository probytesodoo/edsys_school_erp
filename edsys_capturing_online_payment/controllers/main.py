from odoo import SUPERUSER_ID
from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from odoo.http import request,db_filter
import hashlib
from datetime import date
from odoo.addons.edsys_edu.controllers.main import payfort_payment_status as edsys_edu_show_acd_payment

class PayfortPaymentLinkRedirect(http.Controller):
    
    
    @http.route(['/redirect/payment/'], type='http', auth="public", website=True)
    def redirect_payment(self, **post):
        order_id = str(post.get('ORDERID'))
        total_amount = float(post.get('AMOUNT')) or 0.00
        requestParams = {
                                'AMOUNT' : total_amount,
                                'ORDERID' : order_id,
                        }

        return request.render("edsys_capturing_online_payment.payfort_submission_form",requestParams)
    

    @http.route(['/redirect/payfort'], type='http', auth="public", website=True,csrf=False)
    def redirect_payfort(self, **post):
        """
        create payfort payment link and
        redirect to Payfort Page.
        -------------------------------
        :return: redirect to payfort payment getway page.
        """
        #----------------new code---------------------
        currency = 'AED'
        #----------------new code---------------------
        env = request.env(user=SUPERUSER_ID)
        user_id = 1
        if user_id:
            res_user_obj = env['res.users']
            res_user_obj_rec = res_user_obj.sudo().search([('id', '=', user_id)],limit=1)
            #----------------new code---------------------
            currency = str(res_user_obj_rec.company_id.currency_id.name)
            #----------------new code---------------------
        payfort_conf_obj = env['payfort.config']
        payfort_conf_rec = payfort_conf_obj.sudo().search([('active', '=', 'True')],limit=1)
        if payfort_conf_rec.id:
            order_id = str(post.get('ORDERID'))
            total_amount = float(post.get('AMOUNT')) or 0.00
            payment_method = str(post.get('payment_method'))
            
            #------------------------get partner email------------------------------#
            reg_ids = env['registration'].sudo().search([('registration_number', '=', order_id)])
            invoice_ids = env['account.invoice'].sudo().search([('invoice_number', '=', order_id)],limit=1)
            voucher_rec = env['account.voucher'].sudo().search(
                [('payfort_type', '=', True), ('voucher_number', '=', order_id)],limit=1)
            next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', order_id)])
            re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('re_registration_number','=',order_id)]
                                                                                              , limit=1)
            tc_student_rec = env['trensfer.certificate'].sudo().search([('transfer_certificate_number', '=', order_id)],limit=1)
#                                                                                           limit=1)
            customer_email = False
            if len(reg_ids) > 0:
                customer_email = reg_ids.parent_email
            elif len(invoice_ids) > 0:
                customer_email = invoice_ids.partner_id.email
            elif len(voucher_rec) > 0:
                customer_email = voucher_rec.partner_id.parents_email
            elif len(next_year_advance_fee_rec) > 0:
                customer_email = next_year_advance_fee_rec.partner_id.email
       
            elif len(tc_student_rec) > 0:
                customer_email = tc_student_rec.name.email
            elif len(re_registration_parent_rec) > 0:
                customer_email = re_registration_parent_rec.name.parents_email
            #------------------------get partner email------------------------------#
            
            #------------------------calculate payfort charge-----------------------#
            amount = 0.00
            payfort_charge_amount = 0
            payfort_transaction_charge = 0
            payfort_url = payfort_conf_rec.payfort_url
            payfort_bank_charge = 0
            access_code = str(payfort_conf_rec.access_code)
            merchant_identifier = str(payfort_conf_rec.merchant_identifier)
            return_url = str(payfort_conf_rec.return_url)
            language = str(payfort_conf_rec.language)
            if payfort_conf_rec.id and payfort_conf_rec.charge > 0:
                payfort_charge_amount = (total_amount / 100 )   * payfort_conf_rec.charge
            if payfort_conf_rec.transaction_charg_amount > 0.00:
                payfort_transaction_charge = payfort_conf_rec.transaction_charg_amount
#             if payfort_conf_rec.id and payfort_conf_rec.bank_service_charge > 0:
#                 payfort_bank_charge = (total_amount / 100 )  * payfort_conf_rec.bank_service_charge
            total_payfort_charge = payfort_charge_amount + payfort_transaction_charge + payfort_bank_charge
            #------------------------calculate payfort charge-----------------------#
            
            #------------------------add payfort charge in amount-------------------#
            total_payable_amount = total_amount + total_payfort_charge
            total_net_amount = round(total_payable_amount)
            amount = int(total_net_amount * 100)
            #------------------------add payfort charge in amount-------------------#
            
            #----------------Redirection to sbcheckout page-------------------------#
            command = "PURCHASE"
            cart_details = '{"cart_items":[{"item_name":"Xbox360","item_description":"Xbox","item_quantity":"1","item_price":"300","item_image":"http://image.com"}],"sub_total":"300"}'
#                
            if payment_method == 'MASTERPASS':
                digital_wallet = payment_method
                message = 'TESTSHAINaccess_code=%samount=%scart_details=%scommand=%scurrency=%scustomer_email=%sdigital_wallet=%slanguage=%smerchant_identifier=%smerchant_reference=%sreturn_url=%sTESTSHAIN'%(access_code,amount,cart_details,command,currency,customer_email,digital_wallet,language,merchant_identifier,order_id,return_url)
                signature =  hashlib.sha256(message)
                return    """
                                                  <html>
                                                      <body>
                                                      <form action=%s method='post' id="payu" name="payu">
                                                          <input type="hidden" name="access_code" value="%s" />
                                                          <input type="hidden" name="amount" value="%s" />
                                                          <input type="hidden" name="cart_details" value='{"cart_items":[{"item_name":"Xbox360","item_description":"Xbox","item_quantity":"1","item_price":"300","item_image":"http://image.com"}],"sub_total":"300"}'/>
                                                          <input type="hidden" name="command" value="%s" />
                                                          <input type="hidden" name="currency" value="%s" />
                                                          <input type="hidden" name="customer_email" value ="%s" />
                                                          <input type="hidden" name="digital_wallet" value ="%s" />
                                                          <input type="hidden" name="language" value="%s" />
                                                          <input type="hidden" name="merchant_identifier" value="%s" />
                                                          <input type="hidden" name="merchant_reference" value="%s" />
                                                          <input type="hidden" name="return_url" value="%s" />
                                                          <input type="hidden" name="signature" value="%s" />
                                                      </form>
                                                      </body>
                                                      <script type='text/javascript'>
                                                       window.onload = function(){
                                                       document.forms['payu'].submit()
                                                      }
                                                      </script>
                                                  </html>
      
                                              """ % (payfort_url,access_code,amount,command,currency,customer_email,digital_wallet,language,merchant_identifier,order_id,return_url,signature.hexdigest())
                                              
            if payment_method == 'VISA_CHECKOUT' :
                digital_wallet = payment_method
                message = 'TESTSHAINaccess_code=%samount=%scommand=%scurrency=%scustomer_email=%sdigital_wallet=%slanguage=%smerchant_identifier=%smerchant_reference=%sreturn_url=%sTESTSHAIN'%(access_code,amount,command,currency,customer_email,digital_wallet,language,merchant_identifier,order_id,return_url)
                signature =  hashlib.sha256(message)
#                 cart_details = json.dumps(cart_details)
                return   """
                                                  <html>
                                                      <body>
                                                      <form action=%s method='post' id="payu" name="payu">
                                                          <input type="hidden" name="access_code" value="%s" />
                                                          <input type="hidden" name="amount" value="%s" />
                                                          <input type="hidden" name="command" value="%s" />
                                                          <input type="hidden" name="currency" value="%s" />
                                                          <input type="hidden" name="customer_email" value ="%s" />
                                                          <input type="hidden" name="digital_wallet" value ="%s" />
                                                          <input type="hidden" name="language" value="%s" />
                                                          <input type="hidden" name="merchant_identifier" value="%s" />
                                                          <input type="hidden" name="merchant_reference" value="%s" />
                                                          <input type="hidden" name="return_url" value="%s" />
                                                          <input type="hidden" name="signature" value="%s" />
                                                      </form>
                                                      </body>
                                                      <script type='text/javascript'>
                                                       window.onload = function(){
                                                       document.forms['payu'].submit()
                                                      }
                                                      </script>
                                                  </html>
      
                                              """ % (payfort_url,access_code,amount,command,currency,customer_email,digital_wallet,language,merchant_identifier,order_id,return_url,signature.hexdigest())
                                              
                                              
            if payment_method == 'CREDIT_CARD':
                message = 'TESTSHAINaccess_code=%samount=%scommand=%scurrency=%scustomer_email=%slanguage=%smerchant_identifier=%smerchant_reference=%sreturn_url=%sTESTSHAIN'%(access_code,amount,command,currency,customer_email,language,merchant_identifier,order_id,return_url)
                signature =  hashlib.sha256(message)
                return  """
                                                  <html>
                                                      <body>
                                                      <form action=%s method='post' id="payu" name="payu">
                                                          <input type="hidden" name="access_code" value="%s" />
                                                          <input type="hidden" name="amount" value="%s" />
                                                          <input type="hidden" name="command" value="%s" />
                                                          <input type="hidden" name="currency" value="%s" />
                                                          <input type="hidden" name="customer_email" value ="%s" />
                                                          <input type="hidden" name="language" value="%s" />
                                                          <input type="hidden" name="merchant_identifier" value="%s" />
                                                          <input type="hidden" name="merchant_reference" value="%s" />
                                                          <input type="hidden" name="return_url" value="%s" />
                                                          <input type="hidden" name="signature" value="%s" />
                                                      </form>
                                                      </body>
                                                      <script type='text/javascript'>
                                                       window.onload = function(){
                                                       document.forms['payu'].submit()
                                                      }
                                                      </script>
                                                  </html>
                                              """ % (payfort_url,access_code,amount,command,currency,customer_email,language,merchant_identifier,order_id,return_url,signature.hexdigest())
            #----------------Redirection to sbcheckout page-------------------------#

class ShowAcdPaymentInheritPayfortCapture(edsys_edu_show_acd_payment):

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
               
    def get_payment_amount(self,partner_id):
        env = request.env(user=SUPERUSER_ID)
        account_voucher_obj = env['account.voucher']
        account_invoice_obj = env['account.invoice']
        voucher_line_obj = env['account.voucher.line']
        total_amount =0.0
        if partner_id:
            for parent_rec in partner_id:
                chield_ids = parent_rec.chield1_ids
                table_data = ''
                student_id_list = []
                stud_advance_table = ''
                total_advance = 0.0
                parent_cedit = 0.00
                if chield_ids:
                    for chield_id in chield_ids:
                        student_id_list.append(chield_id.id)
                stud_rec = env['res.partner'].browse(student_id_list)
                if len(stud_rec) > 0:
                    # check for parent advance payment#this is my logic
                    if parent_rec.credit :
                        parent_cedit += parent_rec.credit

                    total_amount_table = 0.00
                    total_amount =0.0
                    move_ids_list = []
                    stud_lst_invoice = []
                    stud_balance=0.0
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
                         
                        stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                        
                        
                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund')]):
                            #GET OPEN INVOICES
                            if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
                                
                                
                                # CHECK FOR NEGATIVE AMOUNT
                                if invoice_rec.amount_total < 0 : 
                                    invoice_residual_amount = -invoice_rec.residual
                                
                                else : 
                                    invoice_residual_amount = invoice_rec.residual
                                      
                                #total_amount_table += invoice_rec.residual    
                                total_amount_table += invoice_residual_amount
                                table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(student_rec.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_residual_amount)
#                                                     
                        total_amount += student_rec.credit
        return total_amount
    
    
    @http.route([
    '/show_acd_payment'
    ], type='http', auth="public", website=True,csrf=False)
    def show_acd_payment(self, **post):
        """
        This method use to online payment by student/parent
        for Re-Registration
        ---------------------------------------------------
        :param post:
        :return:
        """
        res = {}
        #----------new code 20-mar-2017 payment declined------------
        response_code = ''
        #----------new code 20-mar-2017 payment declined------------
        env = request.env(user=SUPERUSER_ID)
        if 'response_code' in post:
            response_code = post['response_code']
            if response_code == '00066':
                return request.render("website_student_enquiry.thankyou_payment_link_expired", {
                    })
        
        #----------new code 20-mar-2017 payment declined------------
        if 'response_code' in post:
            response_code = post['response_code']
            if response_code == '00047':
                return request.render("website_student_enquiry.thankyou_payment_order_already_processed", {
                        })
                
        if 'response_code' in post:
            response_code = post['response_code']
            if response_code != '14000':
                return request.render("website_student_enquiry.thankyou_acd_fee_fail", {
                        })
        if 'response_code' in post:
            response_code = post['response_code']
            if response_code == '00066':
                return request.render("website_student_enquiry.thankyou_payment_link_expired", {
                    })
                
        if post.get('status') == '14':
            cr = env.cr
            env = request.env(user=SUPERUSER_ID)
            
            
            #======================new code for remove exception===================
            
            payfort_capture_obj = env['payfort.payment.capture']
            paid_amount = float(post.get('amount')) / 100
            paid_amount = self.get_orignal_amount(paid_amount)
            
            bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                self.calculate_payfort_charges_value(paid_amount)
            payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
            reg_ids = env['registration'].sudo().search([('registration_number', '=', post['merchant_reference'])])
            invoice_ids = env['account.invoice'].sudo().search([('invoice_number', '=', post['merchant_reference'])],limit=1)
            voucher_rec = env['account.voucher'].sudo().search(
                [('payfort_type', '=', True), ('voucher_number', '=', post['merchant_reference'])],limit=1)
            next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['merchant_reference'])])
            re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('re_registration_number','=',post['merchant_reference'])]
                                                                                              , limit=1)
            tc_student_rec = env['trensfer.certificate'].sudo().search([('transfer_certificate_number', '=', post['merchant_reference'])],limit=1)
            partner = False
            if len(reg_ids) > 0:
                partner = False
            elif len(invoice_ids) > 0:
                partner = invoice_ids.partner_id.id
            elif len(voucher_rec) > 0:
                partner = voucher_rec.partner_id.id
            elif len(next_year_advance_fee_rec) > 0:
                partner = next_year_advance_fee_rec.partner_id.id
            elif len(re_registration_parent_rec) > 0:
                partner = re_registration_parent_rec.name.id
            elif len(tc_student_rec) > 0:
                partner = tc_student_rec.name.id
            
            #======================END new code for remove exception===================
                
            try:
                res = super(ShowAcdPaymentInheritPayfortCapture,self).show_acd_payment(**post)
            except Exception as err_msg:
#                 payfort_error_capture_obj = env['payfort.error.capture']
                
                #======================new code for remove exception===================
                payfort_capture_rec = payfort_capture_obj.search([('pay_id','=',post.get('fort_id'))],limit=1)
                if not payfort_capture_rec:
                    payfort_capture_data = {
                        'date' : date.today(),
                        'partner':partner,
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
                    cr.commit()
                #======================new code for remove exception===================
                
                
                return request.render("edsys_capturing_online_payment.payfort_payment_error_templet", {
                    'payment_id':post['fort_id'],
                    'order_id':post['merchant_reference'],
                    'err_msg':err_msg,
                })
            except:
                import sys
                err_msg = sys.exc_info()[0]
                #======================new code for remove exception===================
                payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
                if not payfort_capture_rec:
                    payfort_capture_data = {
                        'date' : date.today(),
                        'partner':partner,
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
                    cr.commit()
                #======================new code for remove exception===================
                
                
                return request.render("edsys_capturing_online_payment.payfort_payment_error_templet", {
                    'payment_id':post['fort_id'],
                    'order_id':post['merchant_reference'],
                    'err_msg':err_msg,
                })
            payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
            if not payfort_capture_rec.id:
                payfort_capture_data = {
                    'date' : date.today(),
                    'partner':partner,
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
                cr.commit()
                
        return res

#             #======================new code for remove exception===================
#             
#             payfort_capture_obj = env['payfort.payment.capture']
#             paid_amount = float(post.get('amount')) / 100
#             paid_amount = self.get_orignal_amount(paid_amount)
#             
#             bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
#                 self.calculate_payfort_charges_value(paid_amount)
#             payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#             reg_ids = env['registration'].sudo().search([('registration_number', '=', post['merchant_reference'])])
#             invoice_ids = env['account.invoice'].sudo().search([('invoice_number', '=', post['merchant_reference'])],limit=1)
#             voucher_rec = env['account.voucher'].sudo().search(
#                 [('payfort_type', '=', True), ('voucher_number', '=', post['merchant_reference'])],limit=1)
#             next_year_advance_fee_rec = env['next.year.advance.fee'].sudo().search([('order_id', '=', post['merchant_reference'])])
#             re_registration_parent_rec = env['re.reg.waiting.responce.parents'].sudo().search([('re_registration_number','=',post['merchant_reference'])]
#                                                                                               , limit=1)
#             tc_student_rec = env['trensfer.certificate'].sudo().search([('transfer_certificate_number', '=', post['merchant_reference'])],limit=1)
#             partner = False
#             if len(reg_ids) > 0:
#                 partner = False
#             elif len(invoice_ids) > 0:
#                 partner = invoice_ids.partner_id.id
#             elif len(voucher_rec) > 0:
#                 partner = voucher_rec.partner_id.id
#             elif len(next_year_advance_fee_rec) > 0:
#                 partner = next_year_advance_fee_rec.partner_id.id
#             elif len(re_registration_parent_rec) > 0:
#                 partner = re_registration_parent_rec.name.id
#             elif len(tc_student_rec) > 0:
#                 partner = tc_student_rec.name.id
            
#             #======================END new code for remove exception===================
#                 
#             try:
#                 res = super(ShowAcdPaymentInheritPayfortCapture,self).show_acd_payment(**post)
#             except Exception as err_msg:
#                 return request.render("website_student_enquiry.thankyou_reg_fee_fail", {
#                         })
# #                 payfort_error_capture_obj = env['payfort.error.capture']
#                  
#                 #======================new code for remove exception===================
#                 payfort_capture_rec = payfort_capture_obj.search([('pay_id','=',post.get('fort_id'))],limit=1)
#                 if not payfort_capture_rec:
#                     payfort_capture_data = {
#                         'date' : date.today(),
#                         'partner':partner,
#                         'pay_id' : post.get('fort_id') or '',
#                         'reference_number' :  post.get('merchant_reference'),
#                         'paid_amount' : paid_amount,
#                         'bank_charges' : bank_charges,
#                         'gross_transaction_value' : gross_transaction_value,
#                         'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                         'transaction_charges' : transaction_charges,
#                         'net_amount' : net_amount,
#                     }
#                     temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                     cr.commit()
#                 #======================new code for remove exception===================
#                  
#                  
#                 return request.render("edsys_capturing_online_payment.payfort_payment_error_templet", {
#                     'payment_id':post['fort_id'],
#                     'order_id':post['merchant_reference'],
#                     'err_msg':err_msg,
#                 })
#             except:
#                 import sys
#                 err_msg = sys.exc_info()[0]
#                 #======================new code for remove exception===================
#                 payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#                 if not payfort_capture_rec:
#                     payfort_capture_data = {
#                         'date' : date.today(),
#                         'partner':partner,
#                         'pay_id' : post.get('fort_id') or '',
#                         'reference_number' :  post.get('merchant_reference'),
#                         'paid_amount' : paid_amount,
#                         'bank_charges' : bank_charges,
#                         'gross_transaction_value' : gross_transaction_value,
#                         'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                         'transaction_charges' : transaction_charges,
#                         'net_amount' : net_amount,
#                     }
#                     temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                     cr.commit()
#                 #======================new code for remove exception===================
#                  
#                  
#                 return request.render("edsys_capturing_online_payment.payfort_payment_error_templet", {
#                     'payment_id':post['fort_id'],
#                     'order_id':post['merchant_reference'],
#                     'err_msg':err_msg,
#                 })
#             payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id'))],limit=1)
#             if not payfort_capture_rec.id:
#                 payfort_capture_data = {
#                     'date' : date.today(),
#                     'partner':partner,
#                     'pay_id' : post.get('fort_id') or '',
#                     'reference_number' :  post.get('merchant_reference'),
#                     'paid_amount' : paid_amount,
#                     'bank_charges' : bank_charges,
#                     'gross_transaction_value' : gross_transaction_value,
#                     'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
#                     'transaction_charges' : transaction_charges,
#                     'net_amount' : net_amount,
#                 }
#                 temp = payfort_capture_obj.sudo().create(payfort_capture_data)
#                 cr.commit()
#                  
#         return res

        
