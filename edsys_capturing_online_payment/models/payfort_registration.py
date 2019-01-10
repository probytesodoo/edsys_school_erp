# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date,datetime,timedelta

class RegistrationInheritPayfort(models.Model):

    _inherit = 'registration'

    @api.multi
    def send_payfort_reg_pay_link(self):
        """
        this method used to send registration
        fee payment link to the parent,
        @overide method send_payfort_reg_pay_link for update
        payment amount with curent payfort service charges.
        -----------------------------------------------------
        @param self : object pointer
        @overide method : send_payfort_reg_pay_link
        """
        enquiry_no = self.enquiry_no
        registration_number = self.registration_number
        amount = 0.0
        if not self.reg_fee_line:
            raise except_orm(_('Warning!'),
                             _("please fill Student Registration Fee Structure"))
        elif self.env['account.account'].search_count([('code', '=', '402050')]) == 0:
            raise except_orm(_('Warning!'),
                             _("Registration Fees account not found."))
        else:
            for each in self.reg_fee_line:
                amount += each.amount
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(amount,registration_number)
            self.online_reg_pay_link = link
            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_registration_fee_payment_link')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            body_html = template_rec.body_html
            body_dynamic_html = template_rec.body_html + 'You are requested to pay the (non-refundable) Registration Fee of AED %s.<br/>' \
                                                 '<p><a href=%s><button>Click Here</button> to pay Registration Fee</a></p></div>'%(amount,link)
            template_rec.write({'email_to': self.email,
                                'email_from': email_sender.smtp_user,
                                'email_cc': '',
                                'body_html': body_dynamic_html})
            template_rec.send_mail(self.id, force_send=True)
            template_rec.body_html = body_html
        self.reg_pay_link = 'PayFort Payment Link Successfully Send To Parents'

    @api.multi
    def send_payfort_acd_pay_link(self):
        """
        this method used to send payfort link academic fee payment online,
        @overide method send_payfort_acd_pay_link for update payment
        amount with curent payfort service charges.
        -----------------------------------------------------------------
        @param self : object pointer
        @net_amount : calculated amount
            @dis_amount : discount amount on calculated amount
        @total_net_amount : total calculated amount - total discount
        """
        amount_on_link = 0.00
        month_count = False
        invoice_number = ''
        order_id = False
        #===================new code for payment amount==================
        payable_amount = 0.00
        #===================new code for payment amount==================
        if self._context.has_key('flag') and self._context.get('flag') == True:
            if self.fee_structure_confirm != True:
                raise except_orm(_("Warning!"), _('Please Confirm the fee structure before sending payment link.'))
            if self.invoice_id:
                order_id = self.invoice_id.number
                amount_on_link = self.invoice_id.residual
            elif self.next_year_advance_fee_id:
                order_id = self.next_year_advance_fee_id.order_id
                amount_on_link = self.next_year_advance_fee_id.residual
        else:
            if self.batch_id.current_academic == True:
                get_record = self.reg_pay_acd_manually(True)
                self.invoice_id = get_record.id
                order_id = get_record.number
            else:
                get_record = self.send_payfort_acd_for_next_year()
                self.next_year_advance_fee_id = get_record.id
                order_id = get_record.order_id

        #===================new code for payment amount==================
        if self.invoice_id:
            payable_amount = self.invoice_id.residual
        #===================new code for payment amount==================
        month_diff = self.batch_id.month_ids.search_count(
            [('batch_id', '=', self.batch_id.id), ('leave_month', '=', False)])

        joining_date = datetime.strptime(self.admission_date, "%Y-%m-%d").date()
        start_date = datetime.strptime(self.batch_id.start_date, "%Y-%m-%d").date()
        get_unpaid_diff = self.get_person_age(start_date, joining_date)

        leave_month = []
        for l_month in self.batch_id.month_ids.search(
                [('batch_id', '=', self.batch_id.id), ('leave_month', '=', True)]):
            leave_month.append((int(l_month.name), int(l_month.year)))
        month_in_stj = self.months_between(start_date, joining_date)
        unpaid_month = 0
        if get_unpaid_diff.get('months') > 0:
            unpaid_month = get_unpaid_diff.get('months')
            if len(month_in_stj) > 0 and len(leave_month) > 0:
                for leave_month_year in leave_month:
                    if leave_month_year in month_in_stj:
                        unpaid_month -= 1
        month_diff -= unpaid_month

        if not self.student_fee_line:
            raise except_orm(_('Warning!'), _("Please fill Student Academic Fee Structure"))
        else:
            data = ''
            total_net_amount = 0.0
            for each in self.student_fee_line:
                data = data + '<tr>'
                net_amount = 0.00
                dis_amount = 0.00
                fee_type = ''
                if each.name.is_admission_fee == True:
                    fee_type = each.fee_pay_type.name
                    Adm_amount = each.amount / (1)
                    data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                        each.name.name, round(Adm_amount, 2), fee_type, 0.00, 0.00)
                    net_amount = round(Adm_amount, 2)
                    total_net_amount += net_amount
                else:
                    if each.fee_pay_type.name == 'month':
                        fee_type = 'Monthly'
                        month_amount = each.amount / month_diff
                        if each.discount > 0.00:
                            dis_amount = (month_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(month_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(month_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                    elif each.fee_pay_type.name == 'alt_month':
                        fee_type = 'Alternate Month'
                        alt_amount = each.amount / (month_diff / 2)
                        if each.discount > 0.00:
                            dis_amount = (alt_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(alt_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(alt_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                    elif each.fee_pay_type.name == 'quater':
                        fee_type = 'Quarterly'
                        qtr_amount = each.amount / (month_diff / 3)
                        if each.discount > 0.00:
                            dis_amount = (qtr_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(qtr_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(qtr_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                    elif each.fee_pay_type.name == 'year' or each.fee_pay_type.name == 'one':
                        if each.fee_pay_type.name == 'year':
                            fee_type = 'Yearly'
                        else:
                            fee_type = 'One Time'
                        yer_amount = each.amount / (1)
                        if each.discount > 0.00:
                            dis_amount = (yer_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(yer_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(yer_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                    elif each.fee_pay_type.name == 'half_year':
                        fee_type = 'Half Year'
                        joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
                        total_month = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),
                                                                         ('leave_month','=',False)])
                        batch_start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d").date()
                        unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
                        total_month_rec = total_month - unpaid_month_dic.get('months') or 0
                        half_month_rec = self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),
                                                                         ('leave_month','=',False),
                                                                         ('quater_month','=',True)])
                        if len(half_month_rec) == 2:
                            first_date_of_half = self.first_day_of_month(int(half_month_rec[0].name),
                                                                          int(half_month_rec[0].year))
                            second_date_of_half = self.first_day_of_month(int(half_month_rec[1].name),
                                                                          int(half_month_rec[1].year))
                            last_date_of_half = datetime.strptime(self.batch_id.end_date,"%Y-%m-%d").date()
                            if first_date_of_half <= joining_date < second_date_of_half:
                                month_count = self.months_between(joining_date,second_date_of_half)
                            elif second_date_of_half <= joining_date < last_date_of_half:
                                month_count = self.months_between(joining_date,last_date_of_half)
                        leave_month = []
                        for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),
                                                                       ('leave_month','=',True)]):
                            leave_month.append((int(l_month.name),int(l_month.year)))
                        count_month = []
                        for month_year in month_count:
                            if month_year not in leave_month:
                                count_month.append(month_year)
                        half_amount = 0.00
                        if total_month_rec > 0 and len(count_month) > 0:
                            par_month_amount = each.amount / total_month_rec
                            half_amount = par_month_amount * len(count_month)
                        if each.discount > 0.00:
                            dis_amount = (half_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(half_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(half_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                    elif each.fee_pay_type.name == 'term':
                        fee_type = 'Term Wise'
                        terms = self.env['acd.term'].search([('batch_id', '=', self.batch_id.id)])
                        term_amount = 0.00
                        if len(terms) > 1:
                            default_turm = terms[0]
                            joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
                            for term_rec in terms:
                                term_start_date = datetime.strptime(term_rec.start_date,"%Y-%m-%d").date()
                                term_end_date = datetime.strptime(term_rec.end_date,"%Y-%m-%d").date()
                                if term_start_date <= joining_date < term_end_date:
                                    default_turm = term_rec
                            if default_turm.id:
                                default_turm_start_date = datetime.strptime(default_turm.start_date,"%Y-%m-%d").date()
                                default_turm_end_date = datetime.strptime(default_turm.end_date,"%Y-%m-%d").date()
                                no_of_month = self.months_between(default_turm_start_date, default_turm_end_date)
                                total_month_diff = self.batch_id.month_ids.search_count(
                                    [('batch_id', '=', self.batch_id.id), ('leave_month', '=', False)])
                                unpaid_month = self.get_person_age(default_turm_start_date,joining_date)
                                t_month_diff = total_month_diff - unpaid_month.get('months') or 0
                                term_amount = (each.amount / t_month_diff) * len(no_of_month)
                                unpaid_month_dic = self.get_person_age(default_turm_start_date,joining_date)
                                total_month_dic = self.get_person_age(default_turm_start_date,default_turm_end_date)
                                if unpaid_month_dic.get('months') > 0 and total_month_dic.get('months') > 0:
                                    unpaid_month = unpaid_month_dic.get('months')
                                    paid_month = len(no_of_month) - unpaid_month
                                    term_amount = (each.amount / t_month_diff) * paid_month
                        if each.discount > 0.00 and term_amount > 0.00:
                            dis_amount = (term_amount * each.discount) / 100
                        data += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (
                            each.name.name, round(term_amount, 2), fee_type, each.discount, round(dis_amount, 2))
                        net_amount = round(term_amount, 2) - round(dis_amount, 2)
                        total_net_amount += net_amount
                data += '<td>%s</td></tr>' % (net_amount)
        cal_total_net_amount = total_net_amount

        if amount_on_link > 0.00:
            cal_total_net_amount = amount_on_link
            
        if self.student_id:
            obj_account_invoice = self.env['account.invoice']
            account_invoice_ids = obj_account_invoice.search([('partner_id','=',self.student_id.id),('state','=','open')])
            if account_invoice_ids:
                invoice_number = account_invoice_ids.invoice_number
                if invoice_number:
                    #===============send payable amount =======================
                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,invoice_number)
                    #===============send payable amount =======================
                else :
                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(cal_total_net_amount,order_id)
            else :
                link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(cal_total_net_amount,order_id)
        else:
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(cal_total_net_amount,order_id)
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_payment_link')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        body_html = template_rec.body_html
        body_dynamic_html = template_rec.body_html + '<p>The Fee structure for %s is:</p><br/>'%(self.name)
        body_dynamic_html += '<table border=%s>'%(2)
        body_dynamic_html += '<tr><td>Name</td><td>Amount</td><td>Type</td><td>Discount %% </td><td>Discount Amount</td><td>Net Amount</td></tr>%s</table>'%(data)
#         body_dynamic_html += '<p>Total amount you have to pay this month is AED %s </p>'%(round(cal_total_net_amount, 2))
        if invoice_number:
            body_dynamic_html += '<p>Total amount you have to pay this term is AED %s </p>'%(round(payable_amount))
        else:
            body_dynamic_html += '<p>Total amount you have to pay this term is AED %s </p>'%(round(cal_total_net_amount))
        body_dynamic_html += '<p><a href=%s><button>Click Here</button></a> to pay the Fee online</a></p></div>'%(link)
        template_rec.write({'email_to': self.email,
                            'email_from': email_sender.smtp_user,
                            'email_cc': '',
                            'body_html': body_dynamic_html})
        template_rec.send_mail(self.id, force_send=True)
        template_rec.body_html = body_html
        self.acd_pay_link = "PayFort Payment Link Successfully Send To Parents"

    @api.multi
    def online_academic_fee_payment(self):
        """
        redirect to payfort payment getway for
        online fee payment,
        -------------------------------------------
        @overide method : online_academic_fee_payment
        :return : Redirect to online acd fee payment
        """
        active_payforts=self.env['payfort.config'].search([('active','=','True')])
        if not active_payforts.id:
            raise except_orm(_('Warning!'),
            _("Please create Payfort Details First!") )

        if len(active_payforts) >1:
            raise except_orm(_('Warning!'),
            _("There should be only one payfort record!"))

        if self.invoice_id.id and self.invoice_id.state != 'paid':
            total_amount = self.invoice_id.residual
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_amount,self.invoice_id.invoice_number)
            return {
                "type": "ir.actions.act_url",
                "url": link,
                "target": "new",
                }