from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import base64
from odoo import models, fields, api, _
import time
from odoo.addons.edsys_edu.controllers.main import payfort_payment_status as edsys_edu_show_acd_payment

class payfort_payment_status_inherit_transfer(edsys_edu_show_acd_payment):
    
    
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
            gross_transaction_value = round( paid_amount + bank_charges + transaction_charges)
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
        

    @http.route([
        '/show_acd_payment'
    ], type='http', auth="public", website=True)
    def show_acd_payment(self, **post):
        """
        This method use to online payment by student/parent
        for TC Fee and outstading balance..
        ---------------------------------------------------
        :param post:
        :return:
        """
        env = request.env(user=SUPERUSER_ID)
        current_date = time.strftime('%Y-%m-%d')
        #==============Define cursor to commit ======================
        cr = env.cr
        #==============Define cursor to commit ======================
        if post:
            tc_student_rec = env['trensfer.certificate'].sudo().search([('transfer_certificate_number', '=', post['merchant_reference'])],limit=1)
            tc_amount = tc_student_rec.total_receivables_amount
            if len(tc_student_rec) > 0:
                if post['status'] == '14':
                    voucher_obj = env['account.voucher']
                    voucher_line_obj = env['account.voucher.line']
                    period_rec = self._get_period()
                    payment_id = post['fort_id']
                    curency_id = self._get_currency()
                    amount = post['amount']
                    transaction_amount = float(post['amount'])/ 100
                    amount = float(amount) / 100
                    amount = tc_amount
                    paid_amount = self.get_orignal_amount_new(transaction_amount,tc_amount)
                    current_date = time.strftime('%Y-%m-%d')
                    order_id = post['merchant_reference']
                    voucher_rec = voucher_obj.search([('payfort_payment_id', '=', payment_id),('reference', '=', order_id)],
                                                     limit=1)
                    journal_id = self.get_journal_from_payfort()
                    if not voucher_rec.id:
                        voucher_data = {
                            'period_id': period_rec.id,
                            'account_id': env['account.journal'].browse(journal_id).default_debit_account_id.id,
                            'partner_id': tc_student_rec.name.id,
                            'journal_id': journal_id,
                            'currency_id': curency_id,
                            'reference': order_id,
                            'amount': amount,
                            'type': 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': current_date,
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            'payfort_payment_id': payment_id,
                            'payfort_pay_date': current_date,
                        }
                        voucher_rec = voucher_obj.sudo().create(voucher_data)
                        cr.commit()
                        res = voucher_rec.onchange_partner_id(self,voucher_rec.partner_id.id, journal_id,
                                              amount,
                                              voucher_rec.type, current_date)
                        advance_amount = 0.00
                        for line_data in res['value']['line_dr_ids']:
                            voucher_lines = {
                                'move_line_id': line_data['move_line_id'],
                                'name': line_data['name'],
                                'amount_unreconciled': line_data['amount_unreconciled'],
                                'type': line_data['type'],
                                'amount_original': line_data['amount_original'],
                                'account_id': line_data['account_id'],
                                'voucher_id': voucher_rec.id,
                                'reconcile': True
                            }
                            advance_amount += line_data['amount_unreconciled']
                            voucher_line_obj.sudo().create(voucher_lines)
                            cr.commit()
                        amount += advance_amount
                        for line_data in res['value']['line_cr_ids']:
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
                                    'voucher_id': voucher_rec.id,
                                    'reconcile': True
                                }
                                voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
                                reconsile_vals = voucher_line_rec.onchange_amount(set_amount,line_data['amount_unreconciled'])
                                if reconsile_vals['value']:
                                    voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
                                    if voucher_line_rec.reconcile:
                                        voucher_line_rec.amount_unreconciled = set_amount
                                        voucher_line_rec.amount = set_amount
                                    else:
                                        voucher_line_rec.amount = set_amount
                                amount -= set_amount
    
                        # Validate voucher (Add Journal Entries)
                        voucher_rec.proforma_voucher()
                        tc_student_rec.send_fee_receipt_mail(voucher_rec)
                        
                        #----------------------New Code For Payment Capture========================
                        payfort_capture_obj = env['payfort.payment.capture']
                        bank_charges, transaction_charges, gross_transaction_value, net_amount, transaction_charges_deducted_by_bank =\
                            self.calculate_payfort_charges_value(tc_amount)
                        tc_student_rec = env['trensfer.certificate'].sudo().search([('transfer_certificate_number', '=', post['merchant_reference'])],limit=1)
                        partner = False
                        if len(tc_student_rec) > 0:
                            partner = tc_student_rec.name.id
                        payfort_capture_rec = payfort_capture_obj.sudo().search([('pay_id','=',post.get('fort_id')),
                                                                      ('reference_number','=',post.get('merchant_reference'))],limit=1)
                        if not payfort_capture_rec.id:
                        
                            payfort_capture_data = {
                                'date' : current_date,
                                'partner':partner,
                                'pay_id' : post.get('fort_id') or '',
                                'reference_number' :  post.get('merchant_reference'),
                                'paid_amount' : tc_amount,
                                'bank_charges' : bank_charges,
                                'gross_transaction_value' : gross_transaction_value,
                                'transaction_charges_deducted_by_bank' : transaction_charges_deducted_by_bank,
                                'transaction_charges' : transaction_charges,
                                'net_amount' : net_amount,
                            }
                            temp = payfort_capture_obj.sudo().create(payfort_capture_data)
                        cr.commit()
                        #----------------------New Code For Payment Capture========================
                        return request.render("website_student_enquiry.thankyou_acd_fee_paid", {'pay_id':post['fort_id']})
                    else:
                        return request.render("website_student_enquiry.thankyou_acd_fee_paid", {'pay_id':post['fort_id']})

        else:                
            return request.render("website_student_enquiry.thankyou_acd_fee_fail", {})
        res = super(payfort_payment_status_inherit_transfer,self).show_acd_payment(**post)
        return res

class TrensferCertificateController(http.Controller):

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
        '/student/tc/request',
    ], type='http', auth="public", website=True,csrf=False)
    def render_tc_request(self, **post):
        """
        this method is used to call webpage for TC Form.
        When students leave the school, it is through the TC process.
        then this process must be required.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                required data
        """
        env = request.env(user=SUPERUSER_ID)
        if 'TCCODE' in post and post.get('TCCODE'):
            data = post.get('TCCODE')
            tc_code = self.decode_base64(data)
            env = request.env(context=dict(request.env.context, show_address=True,no_tag_br=True))
            tc_object = env['trensfer.certificate']
            tc_stud_record = tc_object.sudo().search([('code','=',tc_code)],limit=1)
            if tc_stud_record.id and tc_stud_record.tc_form_filled != True:
                return http.request.render("edsys_transfer_certificate.tc_form_request", {
                    'tc_stud_rec' : tc_stud_record
                    })
            else:
                return http.request.render("edsys_transfer_certificate.tc_request_fail", {})
        else:
            return http.request.render("edsys_transfer_certificate.tc_request_fail", {})

    @http.route([
    '/student/tc/responce',
    ], type='http', auth="public", website=True,csrf=False)
    def render_student_tc_form_responce(self, **post):
        """
        this method is use for getting responce from parent
        for conformation of tc form.
        :param post:
        :return:
        """
        if post and 'TCCODE' in post and post.get('TCCODE'):
            env = request.env(user=SUPERUSER_ID)
            tc_object = env['trensfer.certificate']
            tc_stud_record = tc_object.sudo().search([('id','=',post.get('TCCODE'))],limit=1)
            if tc_stud_record.id:
                tc_type = ''
                if 'select_type_tc' in post and post.get('select_type_tc'):
                    tc_type = post.get('select_type_tc')
                tc_stud_record.sudo().write({'tc_form_filled' : True,
                                             'new_school_name': post.get('new_school_name'),
                                             'reason_for_leaving':post.get('reason_leaving'),
                                             'tc_type':tc_type})
                if tc_stud_record.tc_form_filled == True:
                    tc_stud_record.sudo().come_to_fee_balance_review()
                return http.request.render("edsys_transfer_certificate.tc_request_success", {})
            else:
                return http.request.render("edsys_transfer_certificate.tc_request_fail", {})

