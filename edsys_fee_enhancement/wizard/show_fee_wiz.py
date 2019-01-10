from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import except_orm, Warning, RedirectWarning

class show_fee_wiz(models.TransientModel):
    _inherit = 'show.fee.wiz'
    
    
    @api.model
    def default_get(self, fields):
        total_amount = 0.00
        dis_amount = 0.00
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
                    if brw_reg.fee_computation_ids :
                        res['total_fee'] = brw_reg.fee_computation_ids[0].invoice_amount
                        res['total_remaining'] = brw_reg.fee_computation_ids[0].invoice_amount
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



    @api.multi
    def submit_fee_enhancement(self):
        print'==================submit fee enhancement==================='
        """
        this method is used to manualy subbimit fee.
        -------------------------------------------------
        :return:
        """
        active_id=self._context['active_id']
        brw_reg=self.env['registration'].browse(active_id)
        bankname = self.bank_name
        sdate = self.cheque_start_date or False
        exdate = self.cheque_expiry_date or False
        chk_num=self.chk_num or False
        party_name=self.party_name or False
        if brw_reg.state=='reg':
            journal_id=self.journal_id.id
            brw_reg.reg_pay_manually(journal_id,bank_name=bankname,chk_num=chk_num,
                    sdate=sdate,exdate=exdate,cheque_pay=self.journal_id.is_cheque,party_name=party_name)

        if brw_reg.state=='awaiting_fee':
            account_payment_obj = self.env['account.payment']
            voucher_pool = self.env['account.voucher']
            voucher_line_pool = self.env['account.voucher.line']
            inv_obj = brw_reg.invoice_id
            if not inv_obj :
                #create voucher with advance payment
                currency_id = self._get_currency()
                partner_rec = brw_reg.student_id
                date = time.strftime('%Y-%m-%d')
                period_id = self._get_period().id
                account_id = self.journal_id.default_debit_account_id.id
                total_amount = self.total_fee
                brw_reg.paid_amount= brw_reg.paid_amount+self.total_fee
                if brw_reg.next_year_advance_fee_id :
                    order_id = brw_reg.next_year_advance_fee_id.order_id
                else :
                    order_id = brw_reg.enquiry_no
                if not partner_rec.property_account_customer_advance:
                    raise except_orm(_('Warning!'),
                        _("Please define advance account of student %s!")%(partner_rec.name))
#                 voucher_data = {
#                         'period_id': period_id,
#                         'account_id': account_id,
#                         'partner_id': partner_rec.id,
#                         'journal_id': self.journal_id.id,
#                         'currency_id': currency_id,
#                         'reference': order_id,
#                         'amount': total_amount,
#                         'type': 'receipt',
#                         'state': 'draft',
#                         'pay_now': 'pay_later',
#                         'name': '',
#                         'date': time.strftime('%Y-%m-%d'),
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
#                         'advance_account_id':partner_rec.property_account_customer_advance.id,
#                         # 'invoice_id':inv_obj.id,
#                     }
#                 
                
                payment_vals ={
                               'period_id': period_id,
                               # 'account_id': partner_rec.property_account_customer_advance.id,
                               'partner_type' : 'customer',
                               'partner_id' : partner_rec.id,
                               'journal_id' : self.journal_id.id,
                               # 'reference': order_id,
                               'amount' : total_amount,
                               'payment_method_id' : 1,
                                'advance_account_id':partner_rec.property_account_customer_advance.id,

                                'payment_type' : 'inbound',
                               }
                payment_rec = account_payment_obj.create(payment_vals)
                payment_rec.post_new()
#                 voucher_id = voucher_pool.create(voucher_data)

                # Add Journal Entries
#                 voucher_id.proforma_voucher()
                if brw_reg.paid_amount >=  brw_reg.fee_computation_ids[0].invoice_amount:
                    brw_reg.fee_status = 'academy_fee_pay'
                else :
                    brw_reg.fee_status = 'academy_fee_partial_pay'
                    
                if brw_reg.next_year_advance_fee_id :
                    brw_reg.next_year_advance_fee_id.total_paid_amount += total_amount
                    if round(brw_reg.next_year_advance_fee_id.total_amount, 2) <= round(brw_reg.next_year_advance_fee_id.total_paid_amount, 2):
                        brw_reg.next_year_advance_fee_id.state = 'fee_paid'
                        #brw_reg.fee_status = 'academy_fee_pay'
                    elif round(brw_reg.next_year_advance_fee_id.total_paid_amount,2) < round(brw_reg.next_year_advance_fee_id.total_amount, 2) and brw_reg.next_year_advance_fee_id.total_paid_amount != 0.00:
                        brw_reg.next_year_advance_fee_id.state = 'fee_partial_paid'
                        #brw_reg.fee_status = 'academy_fee_partial_pay'
                    brw_reg.next_year_advance_fee_id.payment_ids = [(4, payment_rec.id)]
                    brw_reg.next_year_advance_fee_id.journal_ids = [(4, self.journal_id.id)]
                    brw_reg.next_year_advance_fee_id.journal_id = self.journal_id.id

                # send mail for advance payment recipt
                mail_obj = self.env['mail.mail']
                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([])
                ir_model_data = self.env['ir.model.data']
                if total_amount >= brw_reg.fee_computation_ids[0].invoice_amount :
                    template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                else :
                    template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_open')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                template_rec.write({'email_to': brw_reg.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
                template_rec.send_mail(payment_rec.id, force_send=True)
            # else :
            #     if inv_obj.state=='open':
#                     voucher_data = {
#                            'period_id': inv_obj.period_id.id,
#                            'account_id': self.journal_id.default_debit_account_id.id,
#                            'partner_id': inv_obj.partner_id.id,
#                            'journal_id': self.journal_id.id,
#                            'currency_id': inv_obj.currency_id.id,
#                            'reference': inv_obj.name,
#                            'amount': self.total_fee,
#                            'type': inv_obj.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
#                            'state': 'draft',
#                            'pay_now': 'pay_later',
#                            'name': '',
#                            'date': time.strftime('%Y-%m-%d'),
#                            'company_id': 1,
#                            'tax_id': False,
#                            # 'payment_option': 'without_writeoff',
#                            # 'comment': _('Write-Off'),
#                            'cheque_start_date':self.cheque_start_date or False,
#                            'cheque_expiry_date':self.cheque_expiry_date or False,
#                            'bank_name':self.bank_name or "",
#                            'cheque':self.cheque,
#                            'party_name' :self.party_name or "",
#                            'chk_num':self.chk_num or "",
#                            'invoice_id':inv_obj.id,
#                            }
#                      
#                     payment_vals ={
#                                 'account_id': partner_rec.property_account_customer_advance.id,
#
#                                 'period_id': inv_obj.period_id.id,
#                                'partner_type' : 'customer',
#                                'partner_id' : partner_rec.id,
#                                'journal_id' : self.journal_id.id,
#                                'amount' : total_amount,
#                                'payment_method_id' : 1,
#                                'payment_type' : 'inbound',
#                                'invoice_id':inv_obj.id,
#                                }
#                 payment_rec = account_payment_obj.create(payment_vals)
#                 payment_rec.post()
#                      

                # create voucher
#                 voucher_id = voucher_pool.create(voucher_data)
#                 print voucher_id,'======================voucher_id'
#                 date = time.strftime('%Y-%m-%d')
#                 if payment_rec:
#                     res = voucher_id.onchange_partner_id(inv_obj.partner_id.id, self.journal_id.id, self.total_fee, inv_obj.currency_id.id, inv_obj.type,date)
#                     print res,'===================================res=======enhanemnt '
#                     total_amount = self.total_fee
#                     if self.total_fee >= inv_obj.residual:
#                         total_amount = inv_obj.residual
                    #Loop through each document and Pay only selected documents and create a single receipt
#                     for line_data in res['value']['line_cr_ids']:
#                         if not line_data['amount']:
#                             continue
#                         name = line_data['name']
# 
#                         if line_data['name'] in [inv_obj.number]:
#                             if not line_data['amount']:
#                                 continue
#                             voucher_lines = {
#                                 'move_line_id': line_data['move_line_id'],
#                                 'amount': total_amount,
#                                 'name': line_data['name'],
#                                 'amount_unreconciled': line_data['amount_unreconciled'],
#                                 'type': line_data['type'],
#                                 'amount_original': line_data['amount_original'],
#                                 'account_id': line_data['account_id'],
#                                 'voucher_id': voucher_id.id,
#                             }
#                             voucher_line_pool.create(voucher_lines)
# 
#                     for line_data in res['value']['line_dr_ids']:
#                         if not line_data['amount']:
#                             continue
#                         if line_data['name'] in [inv_obj.number]:
#                             if not line_data['amount']:
#                                 continue
#                         payment_lines = {
#                                 'move_line_id': line_data['move_line_id'],
#                                 'amount': total_amount,
#                                 'name': line_data['name'],
#                                 'amount_unreconciled': line_data['amount_unreconciled'],
#                                 'type': line_data['type'],
#                                 'amount_original': line_data['amount_original'],
#                                 'account_id': line_data['account_id'],
#                                 'voucher_id': voucher_id.id,
#                             }
#                         payment_line_id = voucher_line_pool.create(voucher_lines)
                    #Add Journal Entries
                    # payment_rec.proforma_voucher()
                    # brw_reg.paid_amount= brw_reg.paid_amount+self.total_fee
                    # send mail for advance payment recipt
                    # mail_obj = self.env['mail.mail']
                    # email_server = self.env['ir.mail_server']
                    # email_sender = email_server.search([])
                    # ir_model_data = self.env['ir.model.data']
                    # if inv_obj.state=='paid':
                    #     template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                    # else :
                    #     template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_open')[1]
                    # template_rec = self.env['mail.template'].browse(template_id)
                    # template_rec.send_mail(payment_rec.id, force_send=True)
                
        #raise except_orm(_("Warning!"), _('stop'))

class account_payment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post_new(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry_new(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

    def _create_payment_entry_new(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """

        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))


        account_move_obj = self.env['account.move']
        account_id = self.env['account.account'].search([('code', '=', '210601')], limit=1)

        counterpart_aml_dict.update({'account_id': account_id.id})

        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)


        self.invoice_ids.register_payment(counterpart_aml)

        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move



