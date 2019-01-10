# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
import datetime as d
from openerp import _
from openerp import api
from openerp import fields
from openerp import models
from openerp.exceptions import except_orm, Warning, RedirectWarning
import hashlib
import openerp
import time,re
import base64
import datetime as d


class Strike_off_Student(models.Model):

    _inherit = 'res.partner'

    last_attendance_date = fields.Date(string='Last Attendance Date')
    activate_date = fields.Date(string='Re-activate Date')
    strike_off = fields.Boolean(string='Strike-off', default=False)
    strike_off_date = fields.Date(string='Strike-off Date')
    remark = fields.Char(string="Strike-off Reason")

    @api.multi
    def strike_off_stud(self):
        strike_obj = self.env['strike.off.history']
        if not self.last_attendance_date:
            raise except_orm(_("Warning!"), _("Last attendance date can not be in future but can be today or in the past!"))
        elif self.last_attendance_date > fields.Date.today():
            raise except_orm(_("Warning!"), _('Last attendance date can not be in future but can be today or in the past!'))

        if not self.remark:
            raise except_orm(_("Warning!"), _("Please mention reason to strike-off this student"))

        self.active = False
        self.strike_off = True
        self.strike_off_date = fields.Date.today()
        exist_strike_rec = strike_obj.search([('student_id', '=', self.id)])
        if len(exist_strike_rec) > 0:
            exist_strike_rec.last_strike_off_date = self.strike_off_date
            exist_strike_rec.strike_history_line_ids.create({
                                'strike_history_id': exist_strike_rec.id,
                                'strike_off_date': self.strike_off_date,
                                'remark': self.remark
                                })
        else:
            create_student_rec = strike_obj.create({
                            'student_id': self.id,
                            'last_strike_off_date': self.strike_off_date,
                        })
            create_student_rec.strike_history_line_ids.create({
                            'strike_history_id': create_student_rec.id,
                            'strike_off_date': self.strike_off_date,
                            'remark': self.remark
                            })

    @api.multi
    def reactivate_stud(self):
        strike_obj = self.env['strike.off.history']
        strike_history_obj = self.env['strike.off.history.line']
        self.active = True
        self.strike_off = False
        self.activate_date = fields.Date.today()
        self.last_attendance_date = False
        self.remark = False
        strike_rec = strike_obj.search([('student_id', '=', self.id)])
        strike_history_rec = strike_history_obj.search([('strike_history_id', '=', strike_rec.id), ('activate_date', '=', False)])
        strike_history_rec.write({'activate_date': self.activate_date})

class Fee_Payment(models.Model):
    _inherit = 'fee.payment'

    @api.model
    def first_day_of_month(self,month,year):
        """
        getting first date of month
        -----------------------------------
        :param month:
        :param year:
        :return: first date of invoice
        """
        return date(year, month, 1)

    @api.model
    def last_day_of_month(self,date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - d.timedelta(days=1)


    @api.model
    def send_payforts_link(self, student_total_receivable,parent_total_receivable,student_rec, invoice_rec):
        """
        this method is use to send payfort link for online pay fee using payfort payment getway.
        ---------------------------------------------------------------------------------------
        :param student_total_receivable: student credit
        :param parent_total_receivable: parent credit
        :param student_rec: student record set
        :param invoice_rec: invoice record set
        :return:
        """
        month_value = str(dict(self.env['account.invoice'].fields_get(allfields=['month'])['month']['selection'])[invoice_rec.month])
        advance_paid_amount = 0.00
        if student_total_receivable < 0.00:
            advance_paid_amount += abs(student_total_receivable)
        return_parent = abs(parent_total_receivable)
        if parent_total_receivable < 0.00:
            if student_total_receivable > 0.00:
                if abs(parent_total_receivable) >= abs(student_total_receivable):
                    return_parent = return_parent - abs(student_total_receivable)
                else:
                    parent_total_receivable = 0.00
            advance_paid_amount += return_parent
        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'), _("There should be only one payfort record!"))

        if not active_payforts.id:
            raise except_orm(_('Warning!'), _("Please create Payfort Details First!"))

        payfort_amount = invoice_rec.residual
        if payfort_amount > advance_paid_amount:
            # if payfort amount greter then advance payment then mail send for payment
            # payfort_amount -= advance_paid_amount   //removed -it was deducting the advance twice from the invoiced amt aftr bulk reconciliation
            payable_amount = payfort_amount
#             if active_payforts.charge != 0.00:
#                 payfort_amount += (payfort_amount * active_payforts.charge) / 100
#             if active_payforts.transaction_charg_amount > 0.00:
#                 payfort_amount += active_payforts.transaction_charg_amount
#             payfort_amount = round(payfort_amount,2)
#             total_amount = str(int(payfort_amount * 100))
#             invoice_number = invoice_rec.number
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,invoice_rec.invoice_number)
            # send mail to every student whos pay fee this month
            attachment_obj = self.env['ir.attachment']
            result = False
            for record in invoice_rec:
                ir_actions_report = self.env['ir.actions.report.xml']
                matching_report = ir_actions_report.search([('name', '=', 'Invoices Attachment')])
                if matching_report:
                    result, format = openerp.report.render_report(self._cr, self._uid, [record.id],
                                                                  matching_report.report_name, {'model': 'account.invoice'})
                    eval_context = {'time': time, 'object': record}
                    if matching_report.attachment or not eval(matching_report.attachment, eval_context):
                        result = base64.b64encode(result)
                        file_name = record.name_get()[0][1]
                        file_name = re.sub(r'[^a-zA-Z0-9 ]', '_', file_name)
                        file_name += ".pdf"
                        attachment_id = attachment_obj.create({
                            'name': file_name,
                            'datas': result,
                            'datas_fname': file_name,
                            'res_model': invoice_rec._name,
                            'res_id': invoice_rec.id,
                            'type': 'binary'
                        })

            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([], limit=1)
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_monthly_fee_calculation')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            body_html = template_rec.body_html
            body_dynamic_html = template_rec.body_html + '<p>The total fee amount for the month of %s is AED %s.'%(month_value, invoice_rec.amount_total)
            body_dynamic_html += 'After adjusting your advances, the amount you have to pay is AED %s.'%(payable_amount)
            body_dynamic_html += ' The fee details are listed in the invoice attached </p>'
            body_dynamic_html += '<a href=%s><button>Click Here</button>For Online Payment</a></div>'%(link)
            template_rec.write({'email_to': student_rec.parents1_id.parents_email,
                                'email_from': email_sender.smtp_user,
                                'email_cc': '',
                                'body_html': body_dynamic_html})
            # Stop Email
            # template_rec.send_mail(invoice_rec.id)
            template_rec.body_html = body_html
        return parent_total_receivable

    @api.multi
    def striked_off_months(self, joining_date,start_date,end_date,last_date_of_month,month_year_obj):
        """
        find and return list of month in between student joining date
        or academic start date to month last date.
        -------------------------------------------------------------
        :param joining_date: date of joining
        :param start_date: academic year start date
        :param end_date: academic end date
        :param last_date_of_month: month last date
        :param month_year_obj: current month object
        :return:
        """
        fee_month_obj = self.env['fee.month']
        if start_date <= joining_date <= end_date:
            cal_date = joining_date
        else:
            cal_date = start_date
        after_joining_months = []
        cal_month = self.months_between(cal_date, last_date_of_month)
        for count_month in cal_month:
            month_data = fee_month_obj.search([('name', '=', count_month[0]),
                                               ('year', '=', count_month[1]),
                                               ('leave_month', '=', False),
                                               ('batch_id', '=', self.academic_year_id.id)])
            if len(month_data) > 1:
                raise except_orm(_("Warning!"), _("multiple month's found !"))
            if month_data.id:
                after_joining_months.append(month_data)
        if len(after_joining_months) > 0:
            return after_joining_months
        else:
            return month_year_obj
        
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
    def reconcile_exists_advance_payment(self, nyaf_rec):
            next_year_advance_obj = self.env['next.year.advance.fee']
            exists_invoices = False
            record = nyaf_rec
            if record.state == 'fee_paid':
                    invoice_obj = self.env['account.invoice']
                    voucher_obj = self.env['account.voucher']
                    voucher_line_obj = self.env['account.voucher.line']
                    fee_month_obj = self.env['fee.month']
                    admission_date=datetime.strptime(record.partner_id.admission_date, "%Y-%m-%d")
                    month_rec = fee_month_obj.search([('name','=', admission_date.month),('batch_id','=', record.batch_id.id)])
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
#                     inv_rec.signal_workflow('invoice_open')
                    inv_rec.action_invoice_open()
                    record.reg_id.invoice_id = inv_rec.id
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
                        #continue
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
                            # Loop through each document and Pay only selected documents and create a single receipt
                            if res :
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
            elif record.state == 'invoice_reconcile':
                raise except_orm(_('Warning!'),
                    _("This Record(%s) Already Reconcile") % (record.order_id))
            else:
                raise except_orm(_('Warning!'),
                    _("Without Advance payment you can't Reconcile record(%s)") % (record.order_id))
        
        
    @api.multi
    def generate_fee_payment(self):
        nyaf_obj = self.env['next.year.advance.fee']
        reconcile_nyaf_obj = self.env['reconsile.advance.fee']
        main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
                                                                        ('leave_month', '=', False)])
        leave_month = []
        for l_month in self.academic_year_id.month_ids.search([('batch_id', '=', self.academic_year_id.id),
                                                               ('leave_month', '=', True)]):
            leave_month.append((int(l_month.name), int(l_month.year)))
        invoice_obj = self.env['account.invoice']
        student_obj = self.env['res.partner']
        month_year_obj = self.month
        if self.month.leave_month == True:
            # get worning if try to calculate fee for leave month
            raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))

        self.fields_readonly=True
        parents_list = []
        parents_advance_change = []
        section_id_list = []
        for section_id in self.section_ids :
             section_id_list.append(section_id.id)
        if month_year_obj.id:
            if self.section_ids:
                stud_ids = student_obj.search([('is_parent', '=', False),
                                               ('is_student', '=', True),
                                               ('active', '=', True),
                                               ('student_section_id', 'in', section_id_list),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id),])
                                               #'|', ('ministry_approved', '=', True), ('waiting_approval', '=', True)])
            else :
                stud_ids = student_obj.search([('is_parent', '=', False),
                                               ('is_student', '=', True),
                                               ('active', '=', True),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id),])
                                               #'|', ('ministry_approved', '=', True), ('waiting_approval', '=', True)])
            for stud_id in stud_ids:
	        registration_obj = self.env['registration']
            	generate_invoice = False
                reg_rec = registration_obj.search([('enquiry_no','=',stud_id.reg_no)])
                if reg_rec :
                    if reg_rec.fee_status in ['academy_fee_partial_pay', 'academy_fee_pay']:
                        generate_invoice =  True
                else :
                    generate_invoice = True
                if generate_invoice :
		            month_diff = main_month_diff
		            joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
		            start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d").date()
		            end_date = datetime.strptime(self.academic_year_id.end_date, "%Y-%m-%d").date()
		            if start_date <= joining_date <= end_date:
		                cal_date = joining_date
		            else:
		                cal_date = start_date
		            get_unpaid_diff = self.get_person_age(start_date, cal_date)
		            month_in_stj = self.months_between(start_date, cal_date)
		            student_total_receivable = stud_id.credit
		            parent_total_receivable = 0.00
		            if stud_id.parents1_id.id:
		                parent_total_receivable = stud_id.parents1_id.credit
		                for parent_advance_dict in parents_advance_change:
		                    if stud_id.parents1_id.id in parent_advance_dict:
		                        parent_total_receivable = parent_advance_dict[stud_id.parents1_id.id]

		            unpaid_month = 0
		            if get_unpaid_diff.get('months') > 0:
		                unpaid_month = get_unpaid_diff.get('months')
		                if len(month_in_stj) > 0 and len(leave_month) > 0:
		                    for leave_month_year in leave_month:
		                        if leave_month_year in month_in_stj:
		                            unpaid_month -= 1

		            month_diff -= unpaid_month
		            first_date_of_month = self.first_day_of_month(int(month_year_obj.name), int(month_year_obj.year))
		            last_date_of_month = self.last_day_of_month(first_date_of_month)
		            if joining_date > last_date_of_month:
		                continue
		            if month_diff <= 0:
		                continue
		            # month_in_joining_end = self.months_between(joining_date, end_date)
		            months = self.striked_off_months(joining_date,start_date,end_date,last_date_of_month,month_year_obj)
		            for month in months:
		                alredy_month_exist = stud_id.payment_status.search([('student_id', '=', stud_id.id),
		                                                                    ('month_id','=',month.id)])
		                if alredy_month_exist.id:
		                    continue
		                nyaf_rec = nyaf_obj.search([('partner_id', '=', stud_id.id), ('state','=','fee_paid' )]) #next.year.advance.fee
		                print 'nyaf_rec :::::: ', nyaf_rec.total_amount
		                if nyaf_rec :
		                    self.reconcile_exists_advance_payment(nyaf_rec)
		                    print '==========backkkkkkkkkkkkkkkkk============='
		                    # Monthly Fee Payment Generate Line
		                    exist_month_rec = self.search([('course_id', '=', self.course_id.id),
		                                                   ('academic_year_id', '=', self.academic_year_id.id),
		                                                   ('month', '=', month.id)])
		                    if len(exist_month_rec)> 0:
		                        exist_fee_line = exist_month_rec.fee_payment_line_ids.search([('student_id', '=', stud_id.id),
		                                                                        ('month_id', '=', self.month.id),
		                                                                        ('year', '=', self.year)])
		                        if not exist_fee_line.id:
		                            exist_month_rec.fee_payment_line_ids.create({
		                                'student_id': stud_id.id,
		                                'total_fee': nyaf_rec.total_amount,#fee_month_amount-total_discount,
		                                'month_id': month.id,
		                                'month': month.name,
		                                'year': month.year,
		                                'fee_payment_id': exist_month_rec.id,
		                                })
		                    else:
		                        create_month_rec = self.create({
		                            'name': str(self.course_id.name)+'/' + str(month.name)+'/'+str(month.year)+'Fee Calculation',
		                            'code': str(self.course_id.name)+'/'+str(month.name)+'/'+str(month.year)+' Fee Calculation',
		                            'course_id': self.course_id.id,
		                            'academic_year_id': self.academic_year_id.id,
		                            'month': month.id,
		                        })
		                        create_month_rec.fee_payment_line_ids.create({
		                            'student_id': stud_id.id,
		                            'total_fee': nyaf_rec.total_amount, #fee_month_amount-total_discount,
		                            'month_id': month.id,
		                            'month': month.name,
		                            'year': month.year,
		                            'fee_payment_id': create_month_rec.id,
		                            })
		                elif stud_id.waiting_approval == True :
		                    print 'normal ay'
		                        #raise except_orm(_("Warning!"), _('stop'))
		                        
		                    fee_month_amount = 0.00
		                    total_discount = 0.00
		                    fee_line_lst = []
		                    invoice_dic = {}
		                    for fee_amount in stud_id.student_fee_line:
		                        per_month_year_fee = 0.0
		                        dis_amount = 0.00
		                        if fee_amount.fee_pay_type.name == 'year':
		                            exist_month = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),('month_id.batch_id','=',self.academic_year_id.id)])
		                            if exist_month == 0:
		                                all_amount = stud_id.student_fee_line.search([('name', '=', fee_amount.name.id),
		                                                                              ('stud_id', '=', stud_id.id)], limit=1)
		                                per_month_year_fee = all_amount.amount
		                                if fee_amount.discount > 0:
		                                    dis_amount = (per_month_year_fee * fee_amount.discount)/100
		                                fee_line_lst.append((0, 0,
		                                    {
		                                        'product_id': fee_amount.name.id,
		                                        'account_id': fee_amount.name.property_account_income_id.id,
		                                        'name': fee_amount.name.name,
		                                        'quantity': 1,
		                                        'price_unit': round(per_month_year_fee, 2),
		                                        'parent_id': stud_id.parents1_id.id,
		                                        'rem_amount': round(per_month_year_fee, 2),
		                                        'priority': fee_amount.sequence,
		                                    }))
		                                # student fee detail update
		                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                                      ('student_id', '=', stud_id.id)], limit=1)
		                                if exist_qtr_pay_detail.id:
		                                    # if exist_qtr_pay_detail.month_id.id != month.id:
		                                        exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
		                                                                    'discount_amount': dis_amount,
		                                                                    'month_id': month.id})
		                                else:
		                                    fee_year_pay_value = {
		                                                'name': fee_amount.name.id,
		                                                'student_id': stud_id.id,
		                                                'month_id': month.id,
		                                                'fee_pay_type': fee_amount.fee_pay_type,
		                                                'cal_amount': per_month_year_fee,
		                                                'total_amount': fee_amount.amount,
		                                                'discount_amount': dis_amount,
		                                            }
		                                    stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]
		
		                            fee_month_amount += per_month_year_fee
		
		                        elif fee_amount.fee_pay_type.name == 'quater':
		                            if month.qtr_month == True:
		                                all_amount = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                            ('student_id', '=', stud_id.id)], limit=1, order="id desc")
		                                per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
		                                count_month = 0
		                                for total_month_id in self.academic_year_id.month_ids.search([('qtr_month', '=', True),
		                                                                                              ('batch_id', '=', self.academic_year_id.id),
		                                                                                              ('leave_month', '=', False)]):
		                                    exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
		                                                                                 ('student_id', '=', stud_id.id)])
		                                    if exist_month.id:
		                                        count_month += 1
		
		                                if count_month != 0:
		                                    new_per_month_qtr_fee = per_month_qtr_fee * count_month
		                                    if all_amount.cal_amount <= new_per_month_qtr_fee:
		                                        cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
		                                        if cal_alt_new > 0:
		                                            per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
		                                        else:
		                                            per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
		                                else:
		                                    per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
		
		                                fee_month_amount += per_month_qtr_fee
		
		                                # discount calculation for quater month
		                                fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
		                                                                                 ('student_id', '=', stud_id.id)])
		                                if fee_amount.discount > 0:
		                                    if fee_paid_line > 0:
		                                        if amount_above.discount_amount > 0.0:
		                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
		                                            current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
		                                            if alredy_permonth_discount == current_month_disamount:
		                                                dis_amount = current_month_disamount
		                                            elif alredy_permonth_discount < current_month_disamount:
		                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
		                                                difference_discount = difference_discount_per_month * fee_paid_line
		                                                dis_amount = current_month_disamount + difference_discount
		                                            elif alredy_permonth_discount > current_month_disamount:
		                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
		                                                difference_discount = difference_discount_per_month * fee_paid_line
		                                                dis_amount = current_month_disamount - difference_discount
		                                        else:
		                                            dis_amount_quater = (per_month_qtr_fee * fee_amount.discount)/100
		                                            dis_amount = dis_amount_quater + (dis_amount_quater * fee_paid_line)
		                                    else:
		                                        dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
		                                total_discount += dis_amount
		
		                                fee_line_lst.append((0, 0,
		                                        {
		                                            'product_id': fee_amount.name.id,
		                                            'account_id': fee_amount.name.property_account_income_id.id,
		                                            'name': fee_amount.name.name,
		                                            'quantity': 1,
		                                            'price_unit': round(per_month_qtr_fee,2),
		                                            'parent_id': stud_id.parents1_id.id,
		                                            'rem_amount': round(per_month_qtr_fee,2),
		                                            'priority': fee_amount.sequence,
		                                        }))
		                                # student fee detail update
		                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
		                                                                                      ('student_id','=',stud_id.id)], limit=1)
		                                if exist_qtr_pay_detail.id:
		                                    # if exist_qtr_pay_detail.month_id.id != month.id:
		                                        exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
		                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
		                                                                    'month_id': month.id,})
		                                else:
		                                    fee_qtr_pay_value =\
		                                            {
		                                                'name': fee_amount.name.id,
		                                                'student_id': stud_id.id,
		                                                'month_id': month.id,
		                                                'fee_pay_type': fee_amount.fee_pay_type,
		                                                'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
		                                                'total_amount' : fee_amount.amount,
		                                                'discount_amount' : all_amount.discount_amount + dis_amount
		                                            }
		                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
		
		                        if fee_amount.fee_pay_type.name == 'half_year':
		                            if month.quater_month == True:
		                                fee_details_rec = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                            ('student_id', '=', stud_id.id)], limit=1,
		                                                                                order="id desc")
		                                amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
		                                                                          ('student_id','=',stud_id.id)])
		                                per_month_half_fee = 0.00
		                                joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
		                                total_month = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
		                                                                                 ('leave_month','=',False)])
		                                batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
		                                unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
		                                total_month_rec = total_month - unpaid_month_dic.get('months') or 0
		                                half_month_rec = self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
		                                                                                 ('leave_month','=',False),
		                                                                                 ('quater_month','=',True)])
		                                is_next_half_year = True
		                                if len(half_month_rec) == 2:
		                                    first_date_of_half = self.first_day_of_month(int(half_month_rec[0].name),
		                                                                                  int(half_month_rec[0].year))
		                                    second_date_of_half = self.first_day_of_month(int(half_month_rec[1].name),
		                                                                                  int(half_month_rec[1].year))
		                                    last_date_of_half = datetime.strptime(self.academic_year_id.end_date,"%Y-%m-%d").date()
		                                    if fee_details_rec.is_next_half_year:
		                                        if second_date_of_half > joining_date:
		                                            month_count = self.months_between(second_date_of_half,last_date_of_half)
		                                            is_next_half_year = False
		                                        else:
		                                            month_count = []
		                                    else:
		                                        if first_date_of_half <= joining_date < second_date_of_half:
		                                            month_count = self.months_between(joining_date,second_date_of_half)
		                                        elif second_date_of_half <= joining_date < last_date_of_half:
		                                            month_count = self.months_between(joining_date,last_date_of_half)
		                                    leave_month = []
		                                    for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
		                                                                                   ('leave_month','=',True)]):
		                                        leave_month.append((int(l_month.name),int(l_month.year)))
		                                    count_month = []
		                                    for month_year in month_count:
		                                        if month_year not in leave_month:
		                                            count_month.append(month_year)
		                                    if total_month_rec > 0 and len(count_month) > 0:
		                                        par_month_amount = fee_amount.amount / total_month_rec
		                                        per_month_half_fee = par_month_amount * len(count_month)
		                                    print 'per_month_half_fee ::::::::: ', per_month_half_fee
		
		#==================================================commented by shraddha for nyaf-- cz it looks same code as above=============================
		#                                     t_month_count = []
		#                                     print 'fee_details_rec.is_next_half_year ++++++++++++++++ : ', fee_details_rec.is_next_half_year
		#                                     if fee_details_rec.is_next_half_year:
		#                                         print 'first_date_of_half <= joining_date < second_date_of_half ---- ', first_date_of_half, joining_date, second_date_of_half
		#                                         print 'second_date_of_half <= joining_date < last_date_of_half -------- ', second_date_of_half, joining_date, last_date_of_half
		#                                         if first_date_of_half <= joining_date < second_date_of_half:
		#                                             t_month_count = self.months_between(joining_date,second_date_of_half)
		#                                         elif second_date_of_half <= joining_date < last_date_of_half:
		#                                             t_month_count = self.months_between(joining_date,last_date_of_half)
		#                                     t_leave_month = []
		#                                     for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
		#                                                                                    ('leave_month','=',True)]):
		#                                         t_leave_month.append((int(l_month.name),int(l_month.year)))
		# 
		#                                     t_count_month = []
		#                                     for month_year in t_month_count:
		#                                         if month_year not in t_leave_month:
		#                                             t_count_month.append(month_year)
		#                                     first_month_half_fee = 0.00
		#                                     print 'total_month_rec :::::::::: ', total_month_rec
		#                                     print 'len(t_count_month) :::::::::: ', len(t_count_month)
		#                                     print '=========================== ', total_month_rec > 0 and len(t_count_month) > 0
		#                                     if total_month_rec > 0 and len(t_count_month) > 0:
		#                                         par_month_amount = fee_amount.amount / total_month_rec
		#                                         first_month_half_fee = par_month_amount * len(t_count_month)
		#                                     print 'first_month_half_fee :::::: ', first_month_half_fee
		#                                     print 'amount_above.cal_amount ::: ',amount_above.cal_amount
		#                                     diff_half_amount = first_month_half_fee - amount_above.cal_amount
		#                                     print 'diff_half_amount ::::::::: ', diff_half_amount
		#                                     per_month_half_fee += diff_half_amount
		#                                     print 'per_month_half_fee+++++++++ ', per_month_half_fee
		#===============================================================================
		                                print 'per_month_half_fee+++++++++ ', per_month_half_fee
		                                fee_month_amount += per_month_half_fee
		                                #discount calculation for half year
		                                dis_amount = (per_month_half_fee * fee_amount.discount)/100
		
		                                total_discount += dis_amount
		
		                                fee_line_lst.append((0, 0,
		                                        {
		                                            'product_id': fee_amount.name.id,
		                                            'account_id': fee_amount.name.property_account_income_id.id,
		                                            'name': fee_amount.name.name,
		                                            'quantity': 1,
		                                            'parent_id': stud_id.parents1_id.id,
		                                            'price_unit': round(per_month_half_fee, 2),
		                                            'rem_amount': round(per_month_half_fee, 2),
		                                            'priority': fee_amount.sequence,
		                                        }))
		                                # Student fee detail update
		                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                                      ('student_id', '=', stud_id.id)], limit=1)
		                                if exist_qtr_pay_detail.id:
		                                    # if exist_qtr_pay_detail.month_id.id != month.id:
		                                        exist_qtr_pay_detail.write({'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
		                                                                    'discount_amount': fee_details_rec.discount_amount + dis_amount,
		                                                                    'month_id': month.id,
		                                                                    'is_next_half_year':is_next_half_year})
		                                else:
		                                    fee_qtr_pay_value =\
		                                            {
		                                                'name': fee_amount.name.id,
		                                                'student_id': stud_id.id,
		                                                'month_id': month.id,
		                                                'fee_pay_type': fee_amount.fee_pay_type,
		                                                'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
		                                                'total_amount': fee_amount.amount,
		                                                'discount_amount': fee_details_rec.discount_amount + dis_amount,
		                                                'is_next_half_year':is_next_half_year,
		                                            }
		                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
		                                #raise except_orm(_("Warning!"), _('stop'))
		                        elif fee_amount.fee_pay_type.name == 'alt_month':
		                            if month.alt_month == True:
		                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
		                                                                            ('student_id','=',stud_id.id)], limit=1, order="id desc")
		                                per_month_alt_fee = all_amount.total_amount/(month_diff/2)
		                                count_month = 0
		                                for total_month_id in self.academic_year_id.month_ids.search([('alt_month', '=', True),
		                                                                                              ('batch_id', '=', self.academic_year_id.id),
		                                                                                              ('leave_month', '=', False)]):
		                                    exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
		                                                                                 ('student_id', '=', stud_id.id)])
		                                    if exist_month.id:
		                                        count_month += 1
		                                if count_month != 0:
		                                    new_per_month_alt_fee = per_month_alt_fee * count_month
		                                    if all_amount.cal_amount <= new_per_month_alt_fee:
		                                        cal_alt_new = new_per_month_alt_fee - all_amount.cal_amount
		                                        if cal_alt_new > 0:
		                                            per_month_alt_fee = per_month_alt_fee + cal_alt_new
		                                        else:
		                                            per_month_alt_fee = all_amount.total_amount/(month_diff/2)
		                                else:
		                                    per_month_alt_fee = all_amount.total_amount/(month_diff/2)
		
		                                fee_month_amount += per_month_alt_fee
		
		                                # discount calculation for alt month
		                                fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
		                                                                                 ('student_id', '=', stud_id.id)])
		                                if fee_amount.discount > 0:
		                                    if fee_paid_line > 0:
		                                        if amount_above.discount_amount > 0.0:
		                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
		                                            current_month_disamount = (per_month_alt_fee * fee_amount.discount)/100
		                                            if alredy_permonth_discount == current_month_disamount:
		                                                dis_amount = current_month_disamount
		                                            elif alredy_permonth_discount < current_month_disamount:
		                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
		                                                difference_discount = difference_discount_per_month * fee_paid_line
		                                                dis_amount = current_month_disamount + difference_discount
		                                            elif alredy_permonth_discount > current_month_disamount:
		                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
		                                                difference_discount = difference_discount_per_month * fee_paid_line
		                                                dis_amount = current_month_disamount - difference_discount
		                                        else:
		                                            dis_amount_alt_month = (per_month_alt_fee * fee_amount.discount)/100
		                                            dis_amount = dis_amount_alt_month + (dis_amount_alt_month * fee_paid_line)
		                                    else:
		                                        dis_amount = (per_month_alt_fee * fee_amount.discount)/100
		
		                                total_discount += dis_amount
		
		                                fee_line_lst.append((0,0,
		                                        {
		                                            'product_id' : fee_amount.name.id,
		                                            'account_id' : fee_amount.name.property_account_income_id.id,
		                                            'name' : fee_amount.name.name,
		                                            'quantity' : 1,
		                                            'price_unit' : round(per_month_alt_fee,2),
		                                            'parent_id' : stud_id.parents1_id.id,
		                                            'rem_amount' : round(per_month_alt_fee,2),
		                                            'priority' : fee_amount.sequence,
		                                        }))
		                                # student fee detail update
		                                exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                                      ('student_id', '=', stud_id.id)], limit=1)
		                                if exist_alt_pay_detail.id:
		                                    # if exist_alt_pay_detail.month_id.id != month.id:
		                                        exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
		                                                                    'discount_amount': all_amount.discount_amount + dis_amount,
		                                                                    'month_id': month.id,})
		                                else:
		                                    fee_alt_pay_value =\
		                                            {
		                                                'name': fee_amount.name.id,
		                                                'student_id': stud_id.id,
		                                                'month_id': month.id,
		                                                'fee_pay_type': fee_amount.fee_pay_type,
		                                                'cal_amount': all_amount.cal_amount + round(per_month_alt_fee, 2),
		                                                'total_amount': fee_amount.amount,
		                                                'discount_amount': all_amount.discount_amount + dis_amount
		                                            }
		                                    stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]
		
		                        elif fee_amount.fee_pay_type.name == 'month':
		                            amount_above = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                          ('student_id', '=', stud_id.id)], limit=1)
		                            # per month fee calculation
		                            per_month_fee = amount_above.total_amount/(month_diff)
		                            # already fee paided month
		                            fee_paid_line = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),
		                                                                                 ('month_id.batch_id','=',self.academic_year_id.id)])
		                            if fee_paid_line > 0:
		                                new_rem_amount = per_month_fee * fee_paid_line
		                                if amount_above.cal_amount <= new_rem_amount:
		                                    cal_new = new_rem_amount - amount_above.cal_amount
		                                    if cal_new > 0:
		                                        per_month_fee = cal_new + per_month_fee
		                                    else:
		                                        per_month_fee = amount_above.total_amount/(month_diff)
		                            else:
		                                per_month_fee = amount_above.total_amount/(month_diff)
		                            fee_month_amount += per_month_fee
		                            # discount calculation for per month
		                            if fee_amount.discount > 0:
		                                if fee_paid_line > 0:
		                                    if amount_above.discount_amount > 0.0:
		                                        alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
		                                        current_month_disamount = (per_month_fee * fee_amount.discount)/100
		                                        if alredy_permonth_discount == current_month_disamount:
		                                            dis_amount = current_month_disamount
		                                        elif alredy_permonth_discount < current_month_disamount:
		                                            difference_discount_per_month = current_month_disamount - alredy_permonth_discount
		                                            difference_discount = difference_discount_per_month * fee_paid_line
		                                            dis_amount = current_month_disamount + difference_discount
		                                        elif alredy_permonth_discount > current_month_disamount:
		                                            difference_discount_per_month = alredy_permonth_discount - current_month_disamount
		                                            difference_discount = difference_discount_per_month * fee_paid_line
		                                            dis_amount = current_month_disamount - difference_discount
		                                    else:
		                                        dis_amount_month = (per_month_fee * fee_amount.discount)/100
		                                        dis_amount = (dis_amount_month * fee_paid_line)
		                                        #dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
		                                else:
		                                    dis_amount = (per_month_fee * fee_amount.discount)/100
		                            total_discount += dis_amount
		                            fee_line_lst.append((0, 0,
		                                {
		                                    'product_id': fee_amount.name.id,
		                                    'account_id': fee_amount.name.property_account_income_id.id,
		                                    'name': fee_amount.name.name,
		                                    'quantity': 1,
		                                    'price_unit': round(per_month_fee,2),
		                                    'parent_id': stud_id.parents1_id.id,
		                                    'rem_amount': round(per_month_fee,2),
		                                    'priority': fee_amount.sequence,
		                                }))
		                            # Student Fee Detail Update
		                            exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
		                                                                                   ('student_id', '=', stud_id.id)], limit=1)
		                            if exist_stud_pay_detail.id:
		                                # if exist_stud_pay_detail.month_id.id != month.id:
		                                    exist_stud_pay_detail.write({'cal_amount': amount_above.cal_amount + per_month_fee,
		                                                                 'discount_amount': amount_above.discount_amount + dis_amount,
		                                                                 'month_id': month.id})
		                            else:
		                                fee_pay_value =\
		                                    {
		                                        'name': fee_amount.name.id,
		                                        'student_id': stud_id.id,
		                                        'month_id': month.id,
		                                        'fee_pay_type': fee_amount.fee_pay_type,
		                                        'cal_amount': amount_above.cal_amount + per_month_fee,
		                                        'total_amount': fee_amount.amount,
		                                        'discount_amount': amount_above.discount_amount + dis_amount
		                                    }
		
		                                stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
		
		                        # Term wise Fee Calculation
		                        elif fee_amount.fee_pay_type.name == 'term':
		                            paid_term_obj = self.env['paid.term.history']
		                            terms=self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
		                            amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
		                                                                          ('student_id','=',stud_id.id)])
		                            current_term=amount_above.next_term
		                            exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
		                                                                                   ('student_id','=',stud_id.id)])
		
		                            per_month_fee=0
		                            dis_amount = 0
		                            term_id=False
		                            prev_term_seq=exist_stud_pay_detail.next_term.id
		
		                            if prev_term_seq:
		                                same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq),
		                                                                            ('batch_id','=',self.academic_year_id.id)])
		                            next_term=exist_stud_pay_detail.next_term.id
		                            invoice_dic={}
		                            if current_term.id:
		                                start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
		                                end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
		                                difference_amount = 0.00
		                                if start_date.month == month.name:
		                                    if int(start_date.year) == int(month.year):
		                                        term_month = self.months_between(start_date,end_date)
		                                        total_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
		                                                                        ('leave_month', '=', False)])
		                                        batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
		                                        joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
		                                        unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
		                                        t_month_diff = total_month_diff - unpaid_month_dic.get('months') or 0
		                                        if t_month_diff != 0 :
		                                            per_month_fee = (fee_amount.amount / t_month_diff) * len(term_month)
		                                        term_id=amount_above.next_term.id
		                                        prev_paid_rec=paid_term_obj.search([('student_id','=',stud_id.id),('term_id','=',term_id),('batch_id','=',self.academic_year_id.id)])
		                                        if not prev_paid_rec:
		                                            paid_term_obj.create({'student_id':stud_id.id,'term_id':term_id,'batch_id':self.academic_year_id.id})
		                                        if same_seq_terms.ids:
		                                            list=[]
		                                            for each in same_seq_terms:
		                                                if each in terms:
		                                                    list.append(each.id)
		#                                                    next_term=each.id
		                                            if list:
		                                                list=sorted(list)
		                                                next_term=list[0]
		
		                                        term_in_batch = self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
		                                        total_term_cal = 0.00
		                                        for term_rec in term_in_batch:
		                                            if term_rec.id == current_term.id:
		                                                break
		                                            term_start_date = datetime.strptime(term_rec.start_date, "%Y-%m-%d").date()
		                                            term_end_date = datetime.strptime(term_rec.end_date, "%Y-%m-%d").date()
		                                            # start with joining date in
		                                            if term_start_date <= joining_date <= term_end_date:
		                                                term_month = self.months_between(joining_date,term_end_date)
		                                                if t_month_diff != 0 :
		                                                    total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
		                                            elif joining_date <= term_end_date:
		                                                term_month = self.months_between(term_start_date,term_end_date)
		                                                if t_month_diff != 0 :
		                                                    total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
		                                        if total_term_cal > 0.00 and amount_above.cal_amount > 0.00:
		                                            difference_amount = total_term_cal - amount_above.cal_amount
		
		                                        per_month_fee += difference_amount
		
		                                        # discount calculation
		                                        if fee_amount.discount > 0:
		                                            pre_dis = 0.00
		                                            if amount_above.cal_amount > 0.00:
		                                                pre_dis = (amount_above.cal_amount * fee_amount.discount) / 100
		                                                if pre_dis != amount_above.discount_amount:
		                                                    if pre_dis < amount_above.discount_amount:
		                                                        pre_dis = pre_dis - amount_above.discount_amount
		                                                    else:
		                                                        pre_dis = pre_dis - amount_above.discount_amount
		                                            dis_amount = (per_month_fee * fee_amount.discount) / 100
		                                            #dis_amount += pre_dis
		                                    else:
		                                        per_month_fee=0
		                                        term_id=False
		
		                            total_discount += dis_amount
		                            fee_month_amount += per_month_fee
		                            if per_month_fee > 0.00:
		                                fee_line_lst.append((0,0,
		                                        {
		                                            'product_id' : fee_amount.name.id,
		                                            'account_id' : fee_amount.name.property_account_income_id.id,
		                                            'name' : fee_amount.name.name,
		                                            'quantity' : 1.00,
		                                            'price_unit' : round(per_month_fee,2),
		                                            'rem_amount' : round(per_month_fee,2),
		                                            'parent_id' : stud_id.parents1_id.id,
		                                            'priority' : fee_amount.sequence,
		                                        }))
		
		                            fee_pay_value =\
		                                        {
		                                            'name': fee_amount.name.id,
		                                            'student_id': stud_id.id,
		                                            'month_id': month.id,
		                                            'fee_pay_type': fee_amount.fee_pay_type.name,
		                                            'cal_amount': amount_above.cal_amount + per_month_fee,
		                                            'total_amount' : fee_amount.amount,
		                                            'next_term':next_term,
		                                            'discount_amount' : amount_above.discount_amount + dis_amount,
		                                        }
		                            invoice_dic.update({'term_id':term_id or "",})
		                            if not exist_stud_pay_detail.id:
		                                stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
		                            else:
		                                for val in exist_stud_pay_detail:
		                                    val.cal_amount=amount_above.cal_amount + per_month_fee
		                                    val.next_term=next_term
		                                    val.discount_amount = amount_above.discount_amount + dis_amount
		
		                        if fee_amount.discount > 0.00 and dis_amount != 0.00:
		                            if not fee_amount.name.fees_discount:
		                                raise except_orm(_("Warning!"), _('Please define Discount Fee For %s.')%(fee_amount.name.name))
		                            else:
		                                if not fee_amount.name.fees_discount.property_account_income_id.id:
		                                    raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_amount.name.fees_discount.name))
		                                else:
		                                    fee_line_lst.append((0,0,{
		                                        'product_id' : fee_amount.name.fees_discount.id,
		                                        'account_id' : fee_amount.name.fees_discount.property_account_income_id.id,
		                                        'name' : fee_amount.name.fees_discount.name,
		                                        'quantity' : 1.00,
		                                        'parent_id' : stud_id.parents1_id.id,
		                                        'price_unit' : -round(dis_amount,2),
		                                        'rem_amount' : -round(dis_amount,2),
		                                        'priority' : 0,
		                                        }))
		
		                    # Monthly Fee Payment Generate Line
		                    exist_month_rec = self.search([('course_id', '=', self.course_id.id),
		                                                   ('academic_year_id', '=', self.academic_year_id.id),
		                                                   ('month', '=', month.id)])
		                    if len(exist_month_rec)> 0:
		                        exist_fee_line = exist_month_rec.fee_payment_line_ids.search([('student_id', '=', stud_id.id),
		                                                                        ('month_id', '=', self.month.id),
		                                                                        ('year', '=', self.year)])
		                        if not exist_fee_line.id:
		                            exist_month_rec.fee_payment_line_ids.create({
		                                'student_id': stud_id.id,
		                                'total_fee': fee_month_amount-total_discount,
		                                'month_id': month.id,
		                                'month': month.name,
		                                'year': month.year,
		                                'fee_payment_id': exist_month_rec.id,
		                                })
		                    else:
		                        create_month_rec = self.create({
		                            'name': str(self.course_id.name)+'/' + str(month.name)+'/'+str(month.year)+'Fee Calculation',
		                            'code': str(self.course_id.name)+'/'+str(month.name)+'/'+str(month.year)+' Fee Calculation',
		                            'course_id': self.course_id.id,
		                            'academic_year_id': self.academic_year_id.id,
		                            'month': month.id,
		                        })
		                        create_month_rec.fee_payment_line_ids.create({
		                            'student_id': stud_id.id,
		                            'total_fee': fee_month_amount-total_discount,
		                            'month_id': month.id,
		                            'month': month.name,
		                            'year': month.year,
		                            'fee_payment_id': create_month_rec.id,
		                            })
		
		                    # Invoice Create
		                    exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month.id)])
		                    if exist_invoice == 0 and len(fee_line_lst) > 0:
		                        invoice_date = self.first_day_of_month(int(month.name), int(month.year))
		                        invoice_vals = {
		                            'partner_id' : stud_id.id,
		                            'month_id' : month.id,
		                            'account_id' : stud_id.property_account_receivable.id,
		                            'invoice_line_ids' : fee_line_lst,
		                            'month' : month.name,
		                            'year' : month.year,
		                            'batch_id' : self.academic_year_id.id,
		                            'date_invoice' : invoice_date,
		                        }
		                        invoice_id = invoice_obj.create(invoice_vals)
		
		                        if invoice_dic:
		                            invoice_id.write(invoice_dic)
		
		                        # Invoice validate
		                        invoice_id.signal_workflow('invoice_open')
		
		                        # send payfort link for online fee payment
		                        if invoice_id.id:
		                            parent_rem_advance = self.send_payforts_link(student_total_receivable=student_total_receivable,
		                                                    parent_total_receivable=parent_total_receivable,
		                                                    student_rec=stud_id,
		                                                    invoice_rec=invoice_id)
		                            if stud_id.parents1_id.id:
		                                if stud_id.parents1_id.id not in parents_list:
		                                    parents_list.append(stud_id.parents1_id.id)
		                                    parents_advance_change.append({stud_id.parents1_id.id:parent_rem_advance})

		                    fee_status = stud_id.payment_status.search([('month_id','=',month.id),
		                                                                ('student_id','=',stud_id.id)])
		                    if not fee_status.id:
		                        status_val = {
		                            'student_id':stud_id.id,
		                            'month_id': month.id,
		                            'paid': False,
		                        }
		                        print 'status_val ::::: ', status_val
		                        stud_id.payment_status.create(status_val)

            self.state = 'genarated'
        else:
            raise except_orm(_('Warning !'),
                    _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                             % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))



#===============================================================================
#     @api.multi
#     def generate_fee_payment(self):
#         main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
#                                                                         ('leave_month', '=', False)])
#         leave_month = []
#         for l_month in self.academic_year_id.month_ids.search([('batch_id', '=', self.academic_year_id.id),
#                                                                ('leave_month', '=', True)]):
#             leave_month.append((int(l_month.name), int(l_month.year)))
#         invoice_obj = self.env['account.invoice']
#         student_obj = self.env['res.partner']
#         month_year_obj = self.month
#         if self.month.leave_month == True:
#             # get worning if try to calculate fee for leave month
#             raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))
# 
#         self.fields_readonly=True
#         parents_list = []
#         parents_advance_change = []
#         if month_year_obj.id:
#             for stud_id in student_obj.search([('is_parent', '=', False),
#                                                ('is_student', '=', True),
#                                                ('active', '=', True),
#                                                ('course_id', '=', self.course_id.id),
#                                                ('batch_id', '=', self.academic_year_id.id),
#                                                '|', ('ministry_approved', '=', True), ('waiting_approval', '=', True)]):
#                 month_diff = main_month_diff
#                 joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
#                 start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d").date()
#                 end_date = datetime.strptime(self.academic_year_id.end_date, "%Y-%m-%d").date()
#                 if start_date <= joining_date <= end_date:
#                     cal_date = joining_date
#                 else:
#                     cal_date = start_date
#                 get_unpaid_diff = self.get_person_age(start_date, cal_date)
#                 month_in_stj = self.months_between(start_date, cal_date)
#                 student_total_receivable = stud_id.credit
#                 parent_total_receivable = 0.00
#                 if stud_id.parents1_id.id:
#                     parent_total_receivable = stud_id.parents1_id.credit
#                     for parent_advance_dict in parents_advance_change:
#                         if stud_id.parents1_id.id in parent_advance_dict:
#                             parent_total_receivable = parent_advance_dict[stud_id.parents1_id.id]
# 
#                 unpaid_month = 0
#                 if get_unpaid_diff.get('months') > 0:
#                     unpaid_month = get_unpaid_diff.get('months')
#                     if len(month_in_stj) > 0 and len(leave_month) > 0:
#                         for leave_month_year in leave_month:
#                             if leave_month_year in month_in_stj:
#                                 unpaid_month -= 1
# 
#                 month_diff -= unpaid_month
#                 first_date_of_month = self.first_day_of_month(int(month_year_obj.name), int(month_year_obj.year))
#                 last_date_of_month = self.last_day_of_month(first_date_of_month)
#                 if joining_date > last_date_of_month:
#                     continue
#                 if month_diff <= 0:
#                     continue
#                 # month_in_joining_end = self.months_between(joining_date, end_date)
#                 months = self.striked_off_months(joining_date,start_date,end_date,last_date_of_month,month_year_obj)
#                 for month in months:
#                     alredy_month_exist = stud_id.payment_status.search([('student_id', '=', stud_id.id),
#                                                                         ('month_id','=',month.id)])
#                     if alredy_month_exist.id:
#                         continue
#                     fee_month_amount = 0.00
#                     total_discount = 0.00
#                     fee_line_lst = []
#                     invoice_dic = {}
#                     for fee_amount in stud_id.student_fee_line:
#                         per_month_year_fee = 0.0
#                         dis_amount = 0.00
#                         if fee_amount.fee_pay_type.name == 'year':
#                             exist_month = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),('month_id.batch_id','=',self.academic_year_id.id)])
#                             if exist_month == 0:
#                                 all_amount = stud_id.student_fee_line.search([('name', '=', fee_amount.name.id),
#                                                                               ('stud_id', '=', stud_id.id)], limit=1)
#                                 per_month_year_fee = all_amount.amount
#                                 if fee_amount.discount > 0:
#                                     dis_amount = (per_month_year_fee * fee_amount.discount)/100
#                                 fee_line_lst.append((0, 0,
#                                     {
#                                         'product_id': fee_amount.name.id,
#                                         'account_id': fee_amount.name.property_account_income.id,
#                                         'name': fee_amount.name.name,
#                                         'quantity': 1,
#                                         'price_unit': round(per_month_year_fee, 2),
#                                         'parent_id': stud_id.parents1_id.id,
#                                         'rem_amount': round(per_month_year_fee, 2),
#                                         'priority': fee_amount.sequence,
#                                     }))
#                                 # student fee detail update
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                                       ('student_id', '=', stud_id.id)], limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     # if exist_qtr_pay_detail.month_id.id != month.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
#                                                                     'discount_amount': dis_amount,
#                                                                     'month_id': month.id})
#                                 else:
#                                     fee_year_pay_value = {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': per_month_year_fee,
#                                                 'total_amount': fee_amount.amount,
#                                                 'discount_amount': dis_amount,
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]
# 
#                             fee_month_amount += per_month_year_fee
# 
#                         elif fee_amount.fee_pay_type.name == 'quater':
#                             if month.qtr_month == True:
#                                 all_amount = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                             ('student_id', '=', stud_id.id)], limit=1, order="id desc")
#                                 per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
#                                 count_month = 0
#                                 for total_month_id in self.academic_year_id.month_ids.search([('qtr_month', '=', True),
#                                                                                               ('batch_id', '=', self.academic_year_id.id),
#                                                                                               ('leave_month', '=', False)]):
#                                     exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
#                                                                                  ('student_id', '=', stud_id.id)])
#                                     if exist_month.id:
#                                         count_month += 1
# 
#                                 if count_month != 0:
#                                     new_per_month_qtr_fee = per_month_qtr_fee * count_month
#                                     if all_amount.cal_amount <= new_per_month_qtr_fee:
#                                         cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
#                                         if cal_alt_new > 0:
#                                             per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
#                                         else:
#                                             per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
#                                 else:
#                                     per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
# 
#                                 fee_month_amount += per_month_qtr_fee
# 
#                                 # discount calculation for quater month
#                                 fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
#                                                                                  ('student_id', '=', stud_id.id)])
#                                 if fee_amount.discount > 0:
#                                     if fee_paid_line > 0:
#                                         if amount_above.discount_amount > 0.0:
#                                             alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
#                                             current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
#                                             if alredy_permonth_discount == current_month_disamount:
#                                                 dis_amount = current_month_disamount
#                                             elif alredy_permonth_discount < current_month_disamount:
#                                                 difference_discount_per_month = current_month_disamount - alredy_permonth_discount
#                                                 difference_discount = difference_discount_per_month * fee_paid_line
#                                                 dis_amount = current_month_disamount + difference_discount
#                                             elif alredy_permonth_discount > current_month_disamount:
#                                                 difference_discount_per_month = alredy_permonth_discount - current_month_disamount
#                                                 difference_discount = difference_discount_per_month * fee_paid_line
#                                                 dis_amount = current_month_disamount - difference_discount
#                                         else:
#                                             dis_amount_quater = (per_month_qtr_fee * fee_amount.discount)/100
#                                             dis_amount = dis_amount_quater + (dis_amount_quater * fee_paid_line)
#                                     else:
#                                         dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
#                                 total_discount += dis_amount
# 
#                                 fee_line_lst.append((0, 0,
#                                         {
#                                             'product_id': fee_amount.name.id,
#                                             'account_id': fee_amount.name.property_account_income.id,
#                                             'name': fee_amount.name.name,
#                                             'quantity': 1,
#                                             'price_unit': round(per_month_qtr_fee,2),
#                                             'parent_id': stud_id.parents1_id.id,
#                                             'rem_amount': round(per_month_qtr_fee,2),
#                                             'priority': fee_amount.sequence,
#                                         }))
#                                 # student fee detail update
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                       ('student_id','=',stud_id.id)], limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     # if exist_qtr_pay_detail.month_id.id != month.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                                     'discount_amount' : all_amount.discount_amount + dis_amount,
#                                                                     'month_id': month.id,})
#                                 else:
#                                     fee_qtr_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                 'total_amount' : fee_amount.amount,
#                                                 'discount_amount' : all_amount.discount_amount + dis_amount
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
# 
#                         if fee_amount.fee_pay_type.name == 'half_year':
#                             if month.quater_month == True:
#                                 fee_details_rec = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                             ('student_id', '=', stud_id.id)], limit=1,
#                                                                                 order="id desc")
#                                 amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                           ('student_id','=',stud_id.id)])
#                                 per_month_half_fee = 0.00
#                                 joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
#                                 total_month = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
#                                                                                  ('leave_month','=',False)])
#                                 batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
#                                 unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
#                                 total_month_rec = total_month - unpaid_month_dic.get('months') or 0
#                                 half_month_rec = self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
#                                                                                  ('leave_month','=',False),
#                                                                                  ('quater_month','=',True)])
#                                 is_next_half_year = True
#                                 if len(half_month_rec) == 2:
#                                     first_date_of_half = self.first_day_of_month(int(half_month_rec[0].name),
#                                                                                   int(half_month_rec[0].year))
#                                     second_date_of_half = self.first_day_of_month(int(half_month_rec[1].name),
#                                                                                   int(half_month_rec[1].year))
#                                     last_date_of_half = datetime.strptime(self.academic_year_id.end_date,"%Y-%m-%d").date()
#                                     if fee_details_rec.is_next_half_year:
#                                         if second_date_of_half > joining_date:
#                                             month_count = self.months_between(second_date_of_half,last_date_of_half)
#                                             is_next_half_year = False
#                                         else:
#                                             month_count = []
#                                     else:
#                                         if first_date_of_half <= joining_date < second_date_of_half:
#                                             month_count = self.months_between(joining_date,second_date_of_half)
#                                         elif second_date_of_half <= joining_date < last_date_of_half:
#                                             month_count = self.months_between(joining_date,last_date_of_half)
#                                     leave_month = []
#                                     for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
#                                                                                    ('leave_month','=',True)]):
#                                         leave_month.append((int(l_month.name),int(l_month.year)))
#                                     count_month = []
#                                     for month_year in month_count:
#                                         if month_year not in leave_month:
#                                             count_month.append(month_year)
#                                     if total_month_rec > 0 and len(count_month) > 0:
#                                         par_month_amount = fee_amount.amount / total_month_rec
#                                         per_month_half_fee = par_month_amount * len(count_month)
# 
#                                     t_month_count = []
#                                     if fee_details_rec.is_next_half_year:
#                                         if first_date_of_half <= joining_date < second_date_of_half:
#                                             t_month_count = self.months_between(joining_date,second_date_of_half)
#                                         elif second_date_of_half <= joining_date < last_date_of_half:
#                                             t_month_count = self.months_between(joining_date,last_date_of_half)
#                                     t_leave_month = []
#                                     for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
#                                                                                    ('leave_month','=',True)]):
#                                         t_leave_month.append((int(l_month.name),int(l_month.year)))
# 
#                                     t_count_month = []
#                                     for month_year in t_month_count:
#                                         if month_year not in t_leave_month:
#                                             t_count_month.append(month_year)
#                                     first_month_half_fee = 0.00
#                                     if total_month_rec > 0 and len(t_count_month) > 0:
#                                         par_month_amount = fee_amount.amount / total_month_rec
#                                         first_month_half_fee = par_month_amount * len(t_count_month)
#                                     diff_half_amount = first_month_half_fee - amount_above.cal_amount
#                                     per_month_half_fee += diff_half_amount
#                                 fee_month_amount += per_month_half_fee
#                                 #discount calculation for half year
#                                 dis_amount = (per_month_half_fee * fee_amount.discount)/100
# 
#                                 total_discount += dis_amount
# 
#                                 fee_line_lst.append((0, 0,
#                                         {
#                                             'product_id': fee_amount.name.id,
#                                             'account_id': fee_amount.name.property_account_income.id,
#                                             'name': fee_amount.name.name,
#                                             'quantity': 1,
#                                             'parent_id': stud_id.parents1_id.id,
#                                             'price_unit': round(per_month_half_fee, 2),
#                                             'rem_amount': round(per_month_half_fee, 2),
#                                             'priority': fee_amount.sequence,
#                                         }))
#                                 # Student fee detail update
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                                       ('student_id', '=', stud_id.id)], limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     # if exist_qtr_pay_detail.month_id.id != month.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
#                                                                     'discount_amount': fee_details_rec.discount_amount + dis_amount,
#                                                                     'month_id': month.id,
#                                                                     'is_next_half_year':is_next_half_year})
#                                 else:
#                                     fee_qtr_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
#                                                 'total_amount': fee_amount.amount,
#                                                 'discount_amount': fee_details_rec.discount_amount + dis_amount,
#                                                 'is_next_half_year':is_next_half_year,
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
# 
#                         elif fee_amount.fee_pay_type.name == 'alt_month':
#                             if month.alt_month == True:
#                                 all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                             ('student_id','=',stud_id.id)], limit=1, order="id desc")
#                                 per_month_alt_fee = all_amount.total_amount/(month_diff/2)
#                                 count_month = 0
#                                 for total_month_id in self.academic_year_id.month_ids.search([('alt_month', '=', True),
#                                                                                               ('batch_id', '=', self.academic_year_id.id),
#                                                                                               ('leave_month', '=', False)]):
#                                     exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
#                                                                                  ('student_id', '=', stud_id.id)])
#                                     if exist_month.id:
#                                         count_month += 1
#                                 if count_month != 0:
#                                     new_per_month_alt_fee = per_month_alt_fee * count_month
#                                     if all_amount.cal_amount <= new_per_month_alt_fee:
#                                         cal_alt_new = new_per_month_alt_fee - all_amount.cal_amount
#                                         if cal_alt_new > 0:
#                                             per_month_alt_fee = per_month_alt_fee + cal_alt_new
#                                         else:
#                                             per_month_alt_fee = all_amount.total_amount/(month_diff/2)
#                                 else:
#                                     per_month_alt_fee = all_amount.total_amount/(month_diff/2)
# 
#                                 fee_month_amount += per_month_alt_fee
# 
#                                 # discount calculation for alt month
#                                 fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
#                                                                                  ('student_id', '=', stud_id.id)])
#                                 if fee_amount.discount > 0:
#                                     if fee_paid_line > 0:
#                                         if amount_above.discount_amount > 0.0:
#                                             alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
#                                             current_month_disamount = (per_month_alt_fee * fee_amount.discount)/100
#                                             if alredy_permonth_discount == current_month_disamount:
#                                                 dis_amount = current_month_disamount
#                                             elif alredy_permonth_discount < current_month_disamount:
#                                                 difference_discount_per_month = current_month_disamount - alredy_permonth_discount
#                                                 difference_discount = difference_discount_per_month * fee_paid_line
#                                                 dis_amount = current_month_disamount + difference_discount
#                                             elif alredy_permonth_discount > current_month_disamount:
#                                                 difference_discount_per_month = alredy_permonth_discount - current_month_disamount
#                                                 difference_discount = difference_discount_per_month * fee_paid_line
#                                                 dis_amount = current_month_disamount - difference_discount
#                                         else:
#                                             dis_amount_alt_month = (per_month_alt_fee * fee_amount.discount)/100
#                                             dis_amount = dis_amount_alt_month + (dis_amount_alt_month * fee_paid_line)
#                                     else:
#                                         dis_amount = (per_month_alt_fee * fee_amount.discount)/100
# 
#                                 total_discount += dis_amount
# 
#                                 fee_line_lst.append((0,0,
#                                         {
#                                             'product_id' : fee_amount.name.id,
#                                             'account_id' : fee_amount.name.property_account_income.id,
#                                             'name' : fee_amount.name.name,
#                                             'quantity' : 1,
#                                             'price_unit' : round(per_month_alt_fee,2),
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'rem_amount' : round(per_month_alt_fee,2),
#                                             'priority' : fee_amount.sequence,
#                                         }))
#                                 # student fee detail update
#                                 exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                                       ('student_id', '=', stud_id.id)], limit=1)
#                                 if exist_alt_pay_detail.id:
#                                     # if exist_alt_pay_detail.month_id.id != month.id:
#                                         exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
#                                                                     'discount_amount': all_amount.discount_amount + dis_amount,
#                                                                     'month_id': month.id,})
#                                 else:
#                                     fee_alt_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': all_amount.cal_amount + round(per_month_alt_fee, 2),
#                                                 'total_amount': fee_amount.amount,
#                                                 'discount_amount': all_amount.discount_amount + dis_amount
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]
# 
#                         elif fee_amount.fee_pay_type.name == 'month':
#                             amount_above = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                           ('student_id', '=', stud_id.id)], limit=1)
#                             # per month fee calculation
#                             per_month_fee = amount_above.total_amount/(month_diff)
#                             # already fee paided month
#                             fee_paid_line = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),
#                                                                                  ('month_id.batch_id','=',self.academic_year_id.id)])
#                             if fee_paid_line > 0:
#                                 new_rem_amount = per_month_fee * fee_paid_line
#                                 if amount_above.cal_amount <= new_rem_amount:
#                                     cal_new = new_rem_amount - amount_above.cal_amount
#                                     if cal_new > 0:
#                                         per_month_fee = cal_new + per_month_fee
#                                     else:
#                                         per_month_fee = amount_above.total_amount/(month_diff)
#                             else:
#                                 per_month_fee = amount_above.total_amount/(month_diff)
#                             fee_month_amount += per_month_fee
#                             # discount calculation for per month
#                             if fee_amount.discount > 0:
#                                 if fee_paid_line > 0:
#                                     if amount_above.discount_amount > 0.0:
#                                         alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
#                                         current_month_disamount = (per_month_fee * fee_amount.discount)/100
#                                         if alredy_permonth_discount == current_month_disamount:
#                                             dis_amount = current_month_disamount
#                                         elif alredy_permonth_discount < current_month_disamount:
#                                             difference_discount_per_month = current_month_disamount - alredy_permonth_discount
#                                             difference_discount = difference_discount_per_month * fee_paid_line
#                                             dis_amount = current_month_disamount + difference_discount
#                                         elif alredy_permonth_discount > current_month_disamount:
#                                             difference_discount_per_month = alredy_permonth_discount - current_month_disamount
#                                             difference_discount = difference_discount_per_month * fee_paid_line
#                                             dis_amount = current_month_disamount - difference_discount
#                                     else:
#                                         dis_amount_month = (per_month_fee * fee_amount.discount)/100
#                                         dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
#                                 else:
#                                     dis_amount = (per_month_fee * fee_amount.discount)/100
#                             total_discount += dis_amount
#                             fee_line_lst.append((0, 0,
#                                 {
#                                     'product_id': fee_amount.name.id,
#                                     'account_id': fee_amount.name.property_account_income.id,
#                                     'name': fee_amount.name.name,
#                                     'quantity': 1,
#                                     'price_unit': round(per_month_fee,2),
#                                     'parent_id': stud_id.parents1_id.id,
#                                     'rem_amount': round(per_month_fee,2),
#                                     'priority': fee_amount.sequence,
#                                 }))
#                             # Student Fee Detail Update
#                             exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
#                                                                                    ('student_id', '=', stud_id.id)], limit=1)
#                             if exist_stud_pay_detail.id:
#                                 # if exist_stud_pay_detail.month_id.id != month.id:
#                                     exist_stud_pay_detail.write({'cal_amount': amount_above.cal_amount + per_month_fee,
#                                                                  'discount_amount': amount_above.discount_amount + dis_amount,
#                                                                  'month_id': month.id})
#                             else:
#                                 fee_pay_value =\
#                                     {
#                                         'name': fee_amount.name.id,
#                                         'student_id': stud_id.id,
#                                         'month_id': month.id,
#                                         'fee_pay_type': fee_amount.fee_pay_type,
#                                         'cal_amount': amount_above.cal_amount + per_month_fee,
#                                         'total_amount': fee_amount.amount,
#                                         'discount_amount': amount_above.discount_amount + dis_amount
#                                     }
# 
#                                 stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
# 
#                         # Term Wise Fee Calculations
#                         elif fee_amount.fee_pay_type.name == 'term':
#                             paid_term_obj = self.env['paid.term.history']
#                             terms=self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
#                             amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                           ('student_id','=',stud_id.id)])
#                             current_term=amount_above.next_term
#                             exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                    ('student_id','=',stud_id.id)])
# 
#                             per_month_fee=0
#                             dis_amount = 0
#                             term_id=False
#                             prev_term_seq=exist_stud_pay_detail.next_term.id
# 
#                             if prev_term_seq:
#                                 same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq),
#                                                                             ('batch_id','=',self.academic_year_id.id)])
#                             next_term=exist_stud_pay_detail.next_term.id
#                             invoice_dic={}
#                             if current_term.id:
#                                 start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
#                                 end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
#                                 difference_amount = 0.00
#                                 if start_date.month == month.name:
#                                     if int(start_date.year) == int(month.year):
#                                         term_month = self.months_between(start_date,end_date)
#                                         total_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
#                                                                         ('leave_month', '=', False)])
#                                         batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
#                                         joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
#                                         unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
#                                         t_month_diff = total_month_diff - unpaid_month_dic.get('months') or 0
#                                         per_month_fee = (fee_amount.amount / t_month_diff) * len(term_month)
#                                         term_id=amount_above.next_term.id
#                                         prev_paid_rec=paid_term_obj.search([('student_id','=',stud_id.id),('term_id','=',term_id),('batch_id','=',self.academic_year_id.id)])
#                                         if not prev_paid_rec:
#                                             paid_term_obj.create({'student_id':stud_id.id,'term_id':term_id,'batch_id':self.academic_year_id.id})
#                                         if same_seq_terms.ids:
#                                             list=[]
#                                             for each in same_seq_terms:
#                                                 if each in terms:
#                                                     list.append(each.id)
# #                                                    next_term=each.id
#                                             if list:
#                                                 list=sorted(list)
#                                                 next_term=list[0]
# 
#                                         term_in_batch = self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
#                                         total_term_cal = 0.00
#                                         for term_rec in term_in_batch:
#                                             if term_rec.id == current_term.id:
#                                                 break
#                                             term_start_date = datetime.strptime(term_rec.start_date, "%Y-%m-%d").date()
#                                             term_end_date = datetime.strptime(term_rec.end_date, "%Y-%m-%d").date()
#                                             # start with joining date in
#                                             if term_start_date <= joining_date <= term_end_date:
#                                                 term_month = self.months_between(joining_date,term_end_date)
#                                                 total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
#                                             elif joining_date <= term_end_date:
#                                                 term_month = self.months_between(term_start_date,term_end_date)
#                                                 total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
#                                         if total_term_cal > 0.00 and amount_above.cal_amount > 0.00:
#                                             difference_amount = total_term_cal - amount_above.cal_amount
# 
#                                         per_month_fee += difference_amount
# 
#                                         # discount calculation
#                                         if fee_amount.discount > 0:
#                                             pre_dis = 0.00
#                                             if amount_above.cal_amount > 0.00:
#                                                 pre_dis = (amount_above.cal_amount * fee_amount.discount) / 100
#                                                 if pre_dis != amount_above.discount_amount:
#                                                     if pre_dis < amount_above.discount_amount:
#                                                         pre_dis = pre_dis - amount_above.discount_amount
#                                                     else:
#                                                         pre_dis = pre_dis - amount_above.discount_amount
#                                             dis_amount = (per_month_fee * fee_amount.discount) / 100
#                                             dis_amount += pre_dis
#                                     else:
#                                         per_month_fee=0
#                                         term_id=False
# 
#                             total_discount += dis_amount
#                             fee_month_amount += per_month_fee
#                             if per_month_fee > 0.00:
#                                 fee_line_lst.append((0,0,
#                                         {
#                                             'product_id' : fee_amount.name.id,
#                                             'account_id' : fee_amount.name.property_account_income.id,
#                                             'name' : fee_amount.name.name,
#                                             'quantity' : 1.00,
#                                             'price_unit' : round(per_month_fee,2),
#                                             'rem_amount' : round(per_month_fee,2),
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'priority' : fee_amount.sequence,
#                                         }))
# 
#                             fee_pay_value =\
#                                         {
#                                             'name': fee_amount.name.id,
#                                             'student_id': stud_id.id,
#                                             'month_id': month.id,
#                                             'fee_pay_type': fee_amount.fee_pay_type.name,
#                                             'cal_amount': amount_above.cal_amount + per_month_fee,
#                                             'total_amount' : fee_amount.amount,
#                                             'next_term':next_term,
#                                             'discount_amount' : amount_above.discount_amount + dis_amount,
#                                         }
#                             invoice_dic.update({'term_id':term_id or "",})
#                             if not exist_stud_pay_detail.id:
#                                 stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
#                             else:
#                                 for val in exist_stud_pay_detail:
#                                     val.cal_amount=amount_above.cal_amount + per_month_fee
#                                     val.next_term=next_term
#                                     val.discount_amount = amount_above.discount_amount + dis_amount
# 
#                         if fee_amount.discount > 0.00 and dis_amount != 0.00:
#                             if not fee_amount.name.fees_discount:
#                                 raise except_orm(_("Warning!"), _('Please define Discount Fee For %s.')%(fee_amount.name.name))
#                             else:
#                                 if not fee_amount.name.fees_discount.property_account_income.id:
#                                     raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_amount.name.fees_discount.name))
#                                 else:
#                                     fee_line_lst.append((0,0,{
#                                         'product_id' : fee_amount.name.fees_discount.id,
#                                         'account_id' : fee_amount.name.fees_discount.property_account_income.id,
#                                         'name' : fee_amount.name.fees_discount.name,
#                                         'quantity' : 1.00,
#                                         'parent_id' : stud_id.parents1_id.id,
#                                         'price_unit' : -round(dis_amount,2),
#                                         'rem_amount' : -round(dis_amount,2),
#                                         'priority' : 0,
#                                         }))
# 
#                     # Monthly Fee Payment Generate Line
#                     exist_month_rec = self.search([('course_id', '=', self.course_id.id),
#                                                    ('academic_year_id', '=', self.academic_year_id.id),
#                                                    ('month', '=', month.id)])
#                     if len(exist_month_rec)> 0:
#                         exist_fee_line = exist_month_rec.fee_payment_line_ids.search([('student_id', '=', stud_id.id),
#                                                                         ('month_id', '=', self.month.id),
#                                                                         ('year', '=', self.year)])
#                         if not exist_fee_line.id:
#                             exist_month_rec.fee_payment_line_ids.create({
#                                 'student_id': stud_id.id,
#                                 'total_fee': fee_month_amount-total_discount,
#                                 'month_id': month.id,
#                                 'month': month.name,
#                                 'year': month.year,
#                                 'fee_payment_id': exist_month_rec.id,
#                                 })
#                     else:
#                         create_month_rec = self.create({
#                             'name': str(self.course_id.name)+'/' + str(month.name)+'/'+str(month.year)+'Fee Calculation',
#                             'code': str(self.course_id.name)+'/'+str(month.name)+'/'+str(month.year)+' Fee Calculation',
#                             'course_id': self.course_id.id,
#                             'academic_year_id': self.academic_year_id.id,
#                             'month': month.id,
#                         })
#                         create_month_rec.fee_payment_line_ids.create({
#                             'student_id': stud_id.id,
#                             'total_fee': fee_month_amount-total_discount,
#                             'month_id': month.id,
#                             'month': month.name,
#                             'year': month.year,
#                             'fee_payment_id': create_month_rec.id,
#                             })
# 
#                     # Invoice Create
#                     exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month.id)])
#                     if exist_invoice == 0 and len(fee_line_lst) > 0:
#                         invoice_date = self.first_day_of_month(int(month.name), int(month.year))
#                         invoice_vals = {
#                             'partner_id' : stud_id.id,
#                             'month_id' : month.id,
#                             'account_id' : stud_id.property_account_receivable.id,
#                             'invoice_line' : fee_line_lst,
#                             'month' : month.name,
#                             'year' : month.year,
#                             'batch_id' : self.academic_year_id.id,
#                             'date_invoice' : invoice_date,
#                         }
#                         invoice_id = invoice_obj.create(invoice_vals)
# 
#                         if invoice_dic:
#                             invoice_id.write(invoice_dic)
# 
#                         # Invoice validate
#                         invoice_id.signal_workflow('invoice_open')
# 
#                         # send payfort link for online fee payment
#                         if invoice_id.id:
#                             parent_rem_advance = self.send_payforts_link(student_total_receivable=student_total_receivable,
#                                                     parent_total_receivable=parent_total_receivable,
#                                                     student_rec=stud_id,
#                                                     invoice_rec=invoice_id)
#                             if stud_id.parents1_id.id:
#                                 if stud_id.parents1_id.id not in parents_list:
#                                     parents_list.append(stud_id.parents1_id.id)
#                                     parents_advance_change.append({stud_id.parents1_id.id:parent_rem_advance})
# 
#                     fee_status = stud_id.payment_status.search([('month_id','=',month.id),
#                                                                 ('student_id','=',stud_id.id)])
#                     if not fee_status.id:
#                         status_val = {
#                             'student_id':stud_id.id,
#                             'month_id': month.id,
#                             'paid': False,
#                         }
#                         stud_id.payment_status.create(status_val)
# 
#             self.state = 'genarated'
#         else:
#             raise except_orm(_('Warning !'),
#                     _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
#                              % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))
#===============================================================================


