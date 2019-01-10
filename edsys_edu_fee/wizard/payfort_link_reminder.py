from odoo import models, fields, api, _
from odoo.exceptions import except_orm
import hashlib
import time
from datetime import date

class ResendPayfortLink(models.Model):

    _name='resend.payfort.wiz'

    class_id = fields.Many2one('course', "Class")
    student_section_id = fields.Many2one('section', 'Section')
    batch_id = fields.Many2one('batch', 'Academic Year')
    
    parent_ids = fields.Many2many('res.partner','resend_payfort','payfort_id','parent_id','Parent') 
    exclude_strike_off_student = fields.Boolean('Exclude striked off students',default=False)
    
    @api.onchange('exclude_strike_off_student')
    def onchange_exclude_strike_off_student(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.exclude_strike_off_student:
            if self.class_id or self.student_section_id or self.batch_id: 
                if self.class_id :
                    for class_id in self.class_id :
                        class_id_list.append(class_id.id)
                if self.student_section_id :
                    for section_id in self.student_section_id :
                        section_id_list.append(section_id.id)
                    
                
                if class_id_list and section_id_list and self.batch_id:
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id), ('chield1_ids.class_id', 'in', class_id_list), ('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                    
                elif class_id_list and section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif class_id_list and not section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif not class_id_list and section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                
                elif not class_id_list and not section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [ ('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.active','=', True )]}
                elif class_id_list and not section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif not class_id_list and section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                else :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
            else :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.active','=', True )]}
        else:
            if self.class_id or self.student_section_id or self.batch_id: 
                if self.class_id :
                    for class_id in self.class_id :
                        class_id_list.append(class_id.id)
                if self.student_section_id :
                    for section_id in self.student_section_id :
                        section_id_list.append(section_id.id)
                    
                
                if class_id_list and section_id_list and self.batch_id:
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id), ('chield1_ids.class_id', 'in', class_id_list), ('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                    
                elif class_id_list and section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif class_id_list and not section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif not class_id_list and section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                
                elif not class_id_list and not section_id_list and self.batch_id :
                    res['domain'] = {'parent_ids': [ ('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.active','=', True )]}
                elif class_id_list and not section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.class_id', 'in', class_id_list),('chield1_ids.active','=', True )]}
                elif not class_id_list and section_id_list and not self.batch_id :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.active','=', True )]}
                else :
                    res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
            else :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}       
        return res

    
    @api.onchange('class_id', 'student_section_id', 'batch_id')
    def onchange_class_ids(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.class_id or self.student_section_id or self.batch_id: 
            if self.class_id :
                for class_id in self.class_id :
                    class_id_list.append(class_id.id)
            if self.student_section_id :
                for section_id in self.student_section_id :
                    section_id_list.append(section_id.id)
                
            
            if class_id_list and section_id_list and self.batch_id:
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id), ('chield1_ids.class_id', 'in', class_id_list), ('chield1_ids.student_section_id', 'in', section_id_list)]}
                
            elif class_id_list and section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.class_id', 'in', class_id_list)]}
            elif class_id_list and not section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.class_id', 'in', class_id_list)]}
            elif not class_id_list and section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.student_section_id', 'in', section_id_list)]}
            
            elif not class_id_list and not section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [ ('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id)]}
            elif class_id_list and not section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.class_id', 'in', class_id_list)]}
            elif not class_id_list and section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list)]}
            else :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
        else :
            res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
            
        return res

    @api.model
    def _get_period(self):
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].search([])
        return periods and periods[0] or False

    @api.model
    def _make_journal_search(self,ttype):
        journal_pool = self.env['account.journal']
        return journal_pool.search([('type', '=', ttype)])

    @api.model
    def _get_journal(self):
        """
        get Payment Method
        -------------------
        :return:
        """
        active_payforts_rec = self.env['payfort.config'].sudo().search([('active', '=', 'True')])
        if len(active_payforts_rec) == 1:
            if active_payforts_rec.journal_id.id:
                return active_payforts_rec.journal_id
            else:
                raise except_orm(_('Warning!'),_("Please set payment method for Payfort ! "))
        else:
            raise except_orm(_('Warning!'),_("Please set Payfort Configration ! "))

    @api.model
    def _get_currency(self):
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
    def resend_mail_for_payfort_payment(self,parent,total_amount,order_id,table_date,advance_table,\
                                        voucher,advance_amt,invoice_amt):
        print '==========resend mail for payfort payment==========='
        
                                        
        active_payforts=self.env['payfort.config'].search([('active','=','True')])
        if not active_payforts:
            raise except_orm(_('Warning!'),
            _("Please create Payfort Details First!") )

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
            _("There should be only one payfort record!"))
        charge = 0.0
        payable_amount = total_amount
        if active_payforts.id:
            
            advance_amt += parent.advance_total_recivable + parent.re_reg_total_recivable
            parent_total_recivable = 0.0
            if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
                parent_total_recivable = 0.0
            elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
                parent_total_recivable = parent.advance_total_recivable  + parent.re_reg_total_recivable

             
            if (len(active_payforts) > 1):

                link= link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,voucher.voucher_number)

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
                body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
                body_dynamic_html += 'Total advances (if any):<br/>'
                body_dynamic_html += '<table border=%s>'%(2)
                body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
                body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
                body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
                body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                template_rec.write({'email_from': email_sender.smtp_user,
                                    'email_to': parent.parents_email,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(voucher.id)
                template_rec.body_html = body_html


        

    @api.multi
    def resend_payfort_link(self):
        print '============resend_payfort_link==============='
        account_voucher_obj = self.env['account.voucher']
        account_invoice_obj = self.env['account.invoice']
       
        if self.parent_ids:
            total_advance = 0.0
            for parent_rec in self.parent_ids:
                table_data = ''
                stud_advance_table = ''
                student_id_list = []
                stud_advance_table = ''
                total_advance = 0.0
                parent_cedit = 0.00
                if self.class_id and self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id and self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                elif self.class_id and not self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                    # stud_rec = parent_rec.chield1_ids.search([('class_id','=',self.class_id.id)])
                elif not self.class_id and self.student_section_id:
                    # stud_rec = parent_rec.chield1_ids.search([('student_section_id','=',self.student_section_id.id)])
                    for child_rec in parent_rec.chield1_ids:
                        if self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                else:
                    # stud_rec = parent_rec.chield1_ids
                    for child_rec in parent_rec.chield1_ids:
                        if child_rec.active != False:
                            student_id_list.append(child_rec.id)
                stud_rec = self.env['res.partner'].browse(student_id_list)
                if len(stud_rec) > 0:
                    total_amount = 0.00
                    advance_paid_amount = 0.00
                    total_invoice_amt = 0.0
                    move_ids_list = []
                    stud_lst_invoice = []
                    stud_balance=0.0
                    total_amount += parent_cedit                    

                    for student_rec in stud_rec:
                        total_advance += student_rec.advance_total_recivable
                        advance_total_recivable = 0.0
                        if student_rec.advance_total_recivable == False:
                            advance_total_recivable = 0.0
                        elif student_rec.advance_total_recivable > 0.0:
                            advance_total_recivable = student_rec.advance_total_recivable

                        stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                        # if not student_rec.property_account_customer_advance:
                        #     raise except_orm(_("Warning!"), _('Please define Advance Account for student %s') % student_rec.name)
                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id)]):
                            #GET OPEN INVOICES
                            if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
                                total_invoice_amt += invoice_rec.residual
                                total_amount += invoice_rec.residual
                                table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(student_rec.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)
                    if total_amount >= advance_paid_amount:
                        total_amount -= advance_paid_amount
                    period_rec = self._get_period()
                    journal_rec = self._get_journal()
                    curency_id = self._get_currency()
                    vouch_sequence = self.env['ir.sequence'].get('voucher.payfort') or '/'
                    account_config_settings_obj = self.env['account.config.settings']
                    account_config_settings_rec = account_config_settings_obj.search([])
                    if total_amount >= account_config_settings_rec.amount_configurable: 
		            if total_amount > 0.00:
		                voucher_data = {
		                    'period_id': period_rec.id,
		                    'journal_id': journal_rec.id,
		                    'account_id': journal_rec.default_debit_account_id.id,
		                    'partner_id': parent_rec.id,
		                    'currency_id': curency_id,
		                    'reference': parent_rec.name,
		                    'amount': 0.0,
		                    'type': 'receipt' or 'payment',
		                    'state': 'draft',
		                    'pay_now': 'pay_later',
		                    'name': '',
		                    'date': time.strftime('%Y-%m-%d'),
		                    'company_id': 1,
		                    'tax_id': False,
		                    'payment_option': 'without_writeoff',
		                    'comment': _('Write-Off'),
		                    'payfort_type': True,
		                    'payfort_link_order_id' : vouch_sequence,
				    'voucher_amount' : total_amount,
		                    # 'student_class' : self.class_id.id,
		                    # 'student_section' : self.student_section_id.id,
		                    }
		                voucher_rec = account_voucher_obj.create(voucher_data)

		                # SEND MAIL FOR PAY FORT
		self.resend_mail_for_payfort_payment(parent=parent_rec,total_amount=total_amount,order_id=vouch_sequence,\
		    table_date=table_data,advance_table=stud_advance_table,\
		    voucher=voucher_rec,advance_amt=total_advance,invoice_amt=total_invoice_amt)
