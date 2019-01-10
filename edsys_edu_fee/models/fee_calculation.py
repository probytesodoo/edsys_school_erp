import time
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import hashlib
import odoo
import time,re
import base64

class Fee_Payment_Line(models.Model):
    """
    Fee Payment Lines
    """
    _name = 'fee.payment.line'
    _description = 'Fee Payment Line'

    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]
    account_id = fields.Many2one('account.account',string='Account')
    student_id=fields.Many2one('res.partner','Student Name',required=True)
    fee_payment_id=fields.Many2one('fee.payment','Payment ID')
    total_fee=fields.Float('Total Fees')
    date=fields.Date('Date')
    month_id = fields.Many2one('fee.month','Month Ref',store=True)
    month = fields.Selection(List_Of_Month, string='Month')
    year = fields.Char(string="year")

    @api.onchange('month_id')
    def get_year_month(self):
        if self.month_id:
            self.month = self.month_id.name
            self.year = self.month_id.year

class Fee_Payment(models.Model):
    """
    Fee Payment
    """
    _name = 'fee.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Fee Payment'

    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]

    name = fields.Char('Name')
    code = fields.Char('Code')
    course_id= fields.Many2one('course', string='Class', required=True)
    academic_year_id=fields.Many2one('batch','Academic Year' ,required=True)
    fee_payment_line_ids = fields.One2many('fee.payment.line','fee_payment_id','Payment Lines')
    month = fields.Many2one('fee.month', string='Month')
    year = fields.Char('Year', related='month.year')
    fields_readonly = fields.Boolean('make fields Readonly')
    state = fields.Selection([('draft','Draft'),('genarated','Generated')], track_visibility='onchange')
    section_ids = fields.Many2many('section','payment_section_rel','section_id', 'payment_id', string='Section')
    
    @api.onchange('course_id') 
    def onchange_course_id(self):
        res = {}
        if self.course_id: 
            res['domain'] = {'section_ids': [('course_id', '=', self.course_id.name)]}
        return res

    @api.model
    def create(self,vals):
        recort_exist=self.search([('course_id','=',vals['course_id']),('academic_year_id','=',vals['academic_year_id']),('month','=',vals['month'])])
        if recort_exist.id:
            raise except_orm(_('Warning!'),
                    _("Record is already created for same Month,Year and Class!"))
 
        return super(Fee_Payment,self).create(vals)

    @api.multi
    def unlink(self):
        for record in self:
            if record.state == 'genarated':
                raise except_orm(_('Warning!'),
                    _("You can't detete record because Alredy Generated Fee Payment!"))
        return super(Fee_Payment,self).unlink()

    @api.multi
    def write(self,vals):
        if 'course_id' in vals and vals['course_id']:
            raise except_orm(_('Warning!'),
                    _("You can not Update Data direcaly."))
        if vals.get('course_id') or vals.get('academic_year_id') or vals.get('month'):
            if not vals.get('course_id'):
                course_id = self.course_id.id
            else:
                course_id = vals.get('course_id')
            if not vals.get('academic_year_id'):
                academic_year_id = self.academic_year_id.id
            else:
                academic_year_id = vals.get('academic_year_id')
            if not vals.get('month'):
                month = self.month.id
            else:
                month = vals.get('month')
            recort_exist=self.search([('course_id','=',course_id),
                                      ('academic_year_id','=',academic_year_id),
                                      ('month','=',month)])
            if recort_exist.id:
                raise except_orm(_('Warning!'),
                        _("Record is already created for same Month,Year and Class!"))
        return super(Fee_Payment,self).write(vals)

    # @api.depends('course_id','academic_year_id')
    @api.onchange('month','course_id','academic_year_id')
    def name_code_generate(self):
        name = 'Fee Calculation'
        if self.course_id and self.academic_year_id and self.month:
            name = str(self.course_id.name) + '/' +\
                   str(self.month.name)+ '/' + \
                   str(self.month.year)+ '/' + ' Fee Calculation'
        self.name = name
        self.code = name

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
#             SHA_key = active_payforts.sha_in_key
#             PSP_ID = active_payforts.psp_id
#             string_input = 'AMOUNT=%s' % (
#             total_amount) + SHA_key + 'CURRENCY=AED' + SHA_key + 'LANGUAGE=EN_US' + SHA_key + 'ORDERID=%s' % (
#             invoice_number) + SHA_key + 'PSPID=%s'%(PSP_ID) + SHA_key
#             ss = 'AMOUNT=%s&CURRENCY=AED&LANGUAGE=EN_US&ORDERID=%s&PSPID=%s' % (total_amount, invoice_number, PSP_ID)
# 
#             m = hashlib.sha1()
#             m.update(string_input)
#             hashkey = m.hexdigest()
#             hashkey = hashkey.upper()
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,invoice_rec.invoice_number)
            # send mail to every student whos pay fee this month
            attachment_obj = self.env['ir.attachment']
            result = False
            for record in invoice_rec:
                ir_actions_report = self.env['ir.actions.report.xml']
                matching_report = ir_actions_report.search([('name', '=', 'Invoices')])
                if matching_report:
                    result, format = odoo.report.render_report(self._cr, self._uid, [record.id],
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
            body_dynamic_html = template_rec.body_html + '<p>The total fee amount for the month of %s is AED %s.'%(month_value,invoice_rec.amount_total)
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

    @api.model
    def get_person_age(self,date_birth, date_today):

        """
        At top level there are three possibilities : Age can be in days or months or years.
        For age to be in years there are two cases: Year difference is one or Year difference is more than 1
        For age to be in months there are two cases: Year difference is 0 or 1
        For age to be in days there are 4 possibilities: Year difference is 1(20-dec-2012 - 2-jan-2013),
        """
        years_diff = date_today.year - date_birth.year

        months_diff = 0
        if date_today.month >= date_birth.month:
            months_diff = date_today.month - date_birth.month
        else:
            years_diff -= 1
            months_diff = 12 + (date_today.month - date_birth.month)

        days_diff = 0
        if date_today.day >= date_birth.day:
            days_diff = date_today.day - date_birth.day
        else:
            months_diff -= 1
            days_diff = 31 + (date_today.day - date_birth.day)

        if months_diff < 0:
            months_diff = 11
            years_diff -= 1

        age = years_diff
        age_dict = {
            'years' : years_diff,
            'months' : months_diff,
            'days' : days_diff
        }
        return age_dict

    @api.model
    def months_between(self,start_date,end_date):
        months = []
        month_year = []
        cursor = start_date

        while cursor <= end_date:
            if cursor.month not in months:
                months.append(cursor.month)
                month_year.append((int(cursor.month),int(cursor.year)))
            cursor += timedelta(weeks=1)
        return month_year
    
    
    @api.multi
    def generate_fee_payment(self):
        print'============generate fee payment================='
        """
        this method use to monthly fee calculation(including discount),
        --> calculate monthly total amount of fee pay to student,
            and display in student monthaly pay line,(current form)
        --> also calculate student remaining payment in student
            fee pay detail,(student form)
        --> also create invoice of student with different payment
            by student(account)
        --> send mail to student for pay fee from payfort.
        --------------------------------------------------------
        @param self : object pointer
        """
        main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
                                                                   ('leave_month','=',False)])
        leave_month = []
        for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),('leave_month','=',True)]):
            leave_month.append((int(l_month.name),int(l_month.year)))
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
            if self.section_ids :
                stud_ids = student_obj.search([('is_parent', '=', False),
                                               ('is_student', '=', True),
                                               ('active', '=', True),
                                               ('student_section_id', 'in', section_id_list),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id),
                                               '|', ('waiting_approval', '=', True)])
            else :
                stud_ids = student_obj.search([('is_parent', '=', False),
                                               ('is_student', '=', True),
                                               ('active', '=', True),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id),
                                               '|', ('waiting_approval', '=', True)])
            for stud_id in stud_ids:
                month_diff = main_month_diff
                joining_date = datetime.strptime(stud_id.admission_date,"%Y-%m-%d").date()
                start_date = datetime.strptime(self.academic_year_id.start_date,"%Y-%m-%d").date()
                get_unpaid_diff = self.get_person_age(start_date,joining_date)
                month_in_stj = self.months_between(start_date,joining_date)
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
                if stud_id.id:
                    fee_month_amount = 0.00
                    total_discount = 0.00
                    fee_line_lst = []
                    invoice_dic={}

                    for fee_amount in stud_id.student_fee_line:
                        per_month_year_fee = 0.0
                        dis_amount = 0.00
                        if fee_amount.fee_pay_type.name == 'year':
                            exist_month = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
                            if exist_month == 0:
                                all_amount = stud_id.student_fee_line.search([('name','=',fee_amount.name.id),
                                                                              ('stud_id','=',stud_id.id)],limit=1)
                                per_month_year_fee = all_amount.amount
                                if fee_amount.discount > 0:
                                    dis_amount = (per_month_year_fee * fee_amount.discount)/100
                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income_id.id,
                                            'name' : fee_amount.name.name,
                                            'quantity' : 1.00,
                                            'price_unit' : round(per_month_year_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_year_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
                                                                    'discount_amount' : dis_amount,
                                                                    'month_id':month_year_obj.id})
                                else:
                                    fee_year_pay_value = {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': per_month_year_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : dis_amount,
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'quater':
                            if month_year_obj.qtr_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('qtr_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
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
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
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

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income_id.id,
                                            'name' : fee_amount.name.name,
                                            'quantity' : 1.00,
                                            'price_unit' : round(per_month_qtr_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_qtr_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_qtr_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                        if fee_amount.fee_pay_type.name == 'half_year':
                            if month_year_obj.quater_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_qtr_fee = all_amount.total_amount/2
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('quater_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
                                    if exist_month.id:
                                        count_month += 1
                                if count_month != 0:
                                    new_per_month_qtr_fee = per_month_qtr_fee * count_month

                                    if all_amount.cal_amount <= new_per_month_qtr_fee:
                                        cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                        if cal_alt_new > 0:
                                            per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                        else:
                                            per_month_qtr_fee = all_amount.total_amount/2
                                else:
                                    per_month_qtr_fee = all_amount.total_amount/2

                                fee_month_amount += per_month_qtr_fee

                                #discount calculation for half year
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
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
                                            dis_amount_half_month = (per_month_qtr_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_half_month + (dis_amount_half_month * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_qtr_fee * fee_amount.discount)/100

                                total_discount += dis_amount

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income_id.id,
                                            'name' : fee_amount.name.name,
                                            'quantity' : 1.00,
                                            'parent_id' : stud_id.parents1_id.id,
                                            'price_unit' : round(per_month_qtr_fee,2),
                                            'rem_amount' : round(per_month_qtr_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))

                                exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_qtr_pay_detail.id:
                                    if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
                                        exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_qtr_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }

                                    stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'alt_month':
                            if month_year_obj.alt_month == True:
                                all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                            ('student_id','=',stud_id.id)],limit=1,order="id desc")
                                per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                count_month = 0
                                for total_month_id in self.academic_year_id.month_ids.search([('alt_month','=',True),
                                                                                              ('batch_id','=',self.academic_year_id.id),
                                                                                              ('leave_month','=',False)]):
                                    exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
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
                                fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
                                                                                 ('student_id','=',stud_id.id)])
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
                                            'quantity' : 1.00,
                                            'price_unit' : round(per_month_alt_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'rem_amount' : round(per_month_alt_fee,2),
                                            'priority' : fee_amount.sequence,
                                        }))
                                exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                      ('student_id','=',stud_id.id)],limit=1)
                                if exist_alt_pay_detail.id:
                                    if exist_alt_pay_detail.month_id.id != month_year_obj.id:
                                        exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
                                                                    'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                    'month_id': month_year_obj.id,})
                                else:
                                    fee_alt_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month_year_obj.id,
                                                'fee_pay_type': fee_amount.fee_pay_type,
                                                'cal_amount': all_amount.cal_amount + round(per_month_alt_fee,2),
                                                'total_amount' : fee_amount.amount,
                                                'discount_amount' : all_amount.discount_amount + dis_amount
                                            }
                                    stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]

                        elif fee_amount.fee_pay_type.name == 'month':
                            amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                          ('student_id','=',stud_id.id)],limit=1)
                            # per month fee calculation
                            per_month_fee = amount_above.total_amount/(month_diff)
                            # already fee paided month
                            fee_paid_line = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
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
                                        dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
                                else:
                                    dis_amount = (per_month_fee * fee_amount.discount)/100

                            total_discount += dis_amount

                            fee_line_lst.append((0,0,
                                {
                                    'product_id' : fee_amount.name.id,
                                    'account_id' : fee_amount.name.property_account_income_id.id,
                                    'name' : fee_amount.name.name,
                                    'quantity' : 1.00,
                                    'price_unit' : round(per_month_fee,2),
                                    'parent_id' : stud_id.parents1_id.id,
                                    'rem_amount' : round(per_month_fee,2),
                                    'priority' : fee_amount.sequence,
                                }))

                            exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                   ('student_id','=',stud_id.id)], limit=1)
                            if exist_stud_pay_detail.id:
                                if exist_stud_pay_detail.month_id.id != month_year_obj.id:
                                    exist_stud_pay_detail.write({'cal_amount':amount_above.cal_amount + per_month_fee,
                                                                 'discount_amount':amount_above.discount_amount + dis_amount,
                                                                 'month_id': month_year_obj.id,})
                            else:
                                fee_pay_value =\
                                    {
                                        'name': fee_amount.name.id,
                                        'student_id': stud_id.id,
                                        'month_id': month_year_obj.id,
                                        'fee_pay_type': fee_amount.fee_pay_type,
                                        'cal_amount': amount_above.cal_amount + per_month_fee,
                                        'total_amount' : fee_amount.amount,
                                        'discount_amount' : amount_above.discount_amount + dis_amount
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
                            term_id=False
                            prev_term_seq=exist_stud_pay_detail.next_term.id

                            if prev_term_seq:
                                same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq)])

                            next_term=exist_stud_pay_detail.next_term.id
                            invoice_dic={}
                            if current_term.id:
                                start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
                                end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
                                if start_date.month == self.month.name:
                                    if int(start_date.year) == int(self.year):
                                        term_month = self.months_between(start_date,end_date)
                                        per_month_fee = (fee_amount.amount / month_diff) * len(term_month)
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
                                    else:
                                        per_month_fee=0
                                        term_id=False
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
                                dis_amount + pre_dis

                            total_discount += dis_amount
                            fee_month_amount += per_month_fee

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
                                            'month_id': month_year_obj.id,
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
                                        'parent_id' : stud_id.parents1_id.id,
                                        'quantity' : 1.00,
                                        'price_unit' : -round(dis_amount,2),
                                        'rem_amount' : -round(dis_amount,2),
                                        'priority' : 0,
                                        }))

                    # Monthaly Fee Pyment Generate Line
                    exist_fee_line = self.fee_payment_line_ids.search([('student_id','=',stud_id.id),
                                                                        ('month_id','=',self.month.id),
                                                                        ('year','=',self.year),
                                                                        ('fee_payment_id','=',self.id)])
                    if not exist_fee_line.id:
                        self.fee_payment_line_ids.create({
                            'student_id': stud_id.id,
                            'total_fee': fee_month_amount-total_discount,
                            'month_id': month_year_obj.id,
                            'month': month_year_obj.name,
                            'year': month_year_obj.year,
                            'fee_payment_id' : self.id,
                            })
                    # else:
                    #     exist_fee_line.write({
                    #         'total_fee': fee_month_amount-total_discount,
                    #     })

                    # Invoice Create
                    exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month_year_obj.id)])
                    if exist_invoice == 0 and len(fee_line_lst) > 0:
                        invoice_vals = {
                                'partner_id' : stud_id.id,
                                'month_id' : month_year_obj.id,
                                'account_id' : stud_id.property_account_receivable_id.id,
                                'invoice_line_ids' : fee_line_lst,
                                'month' : month_year_obj.name,
                                'year' : month_year_obj.year,
                                'batch_id' : self.academic_year_id.id,
                            }
                        invoice_id = invoice_obj.create(invoice_vals)

                        if invoice_dic:
                            invoice_id.write(invoice_dic)

                        # Invoice validate
                        invoice_id.action_invoice_open()

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

                    fee_status = stud_id.payment_status.search([('month_id','=',month_year_obj.id),
                                                                ('student_id','=',stud_id.id)])
                    if not fee_status.id:
                        status_val = {
                            'month_id': month_year_obj.id,
                            'paid': False,
                        }
                        stud_id.payment_status = [(0,0,status_val)]
            self.state = 'genarated'
        else:
            raise except_orm(_('Warning !'),
                    _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                             % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))

#===============================================================================
#     @api.multi
#     def generate_fee_payment(self):
#         """
#         this method use to monthly fee calculation(including discount),
#         --> calculate monthly total amount of fee pay to student,
#             and display in student monthaly pay line,(current form)
#         --> also calculate student remaining payment in student
#             fee pay detail,(student form)
#         --> also create invoice of student with different payment
#             by student(account)
#         --> send mail to student for pay fee from payfort.
#         --------------------------------------------------------
#         @param self : object pointer
#         """
#         main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
#                                                                    ('leave_month','=',False)])
#         leave_month = []
#         for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),('leave_month','=',True)]):
#             leave_month.append((int(l_month.name),int(l_month.year)))
#         invoice_obj = self.env['account.invoice']
#         student_obj = self.env['res.partner']
#         month_year_obj = self.month
# 
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
#                 joining_date = datetime.strptime(stud_id.admission_date,"%Y-%m-%d").date()
#                 start_date = datetime.strptime(self.academic_year_id.start_date,"%Y-%m-%d").date()
#                 get_unpaid_diff = self.get_person_age(start_date,joining_date)
#                 month_in_stj = self.months_between(start_date,joining_date)
#                 student_total_receivable = stud_id.credit
#                 parent_total_receivable = 0.00
#                 if stud_id.parents1_id.id:
#                     parent_total_receivable = stud_id.parents1_id.credit
#                     for parent_advance_dict in parents_advance_change:
#                         if stud_id.parents1_id.id in parent_advance_dict:
#                             parent_total_receivable = parent_advance_dict[stud_id.parents1_id.id]
#                 unpaid_month = 0
#                 if get_unpaid_diff.get('months') > 0:
#                     unpaid_month = get_unpaid_diff.get('months')
#                     if len(month_in_stj) > 0 and len(leave_month) > 0:
#                         for leave_month_year in leave_month:
#                             if leave_month_year in month_in_stj:
#                                 unpaid_month -= 1
# 
#                 month_diff -= unpaid_month
#                 if stud_id.id:
#                     fee_month_amount = 0.00
#                     total_discount = 0.00
#                     fee_line_lst = []
#                     invoice_dic={}
# 
#                     for fee_amount in stud_id.student_fee_line:
#                         per_month_year_fee = 0.0
#                         dis_amount = 0.00
#                         if fee_amount.fee_pay_type.name == 'year':
#                             exist_month = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
#                             if exist_month == 0:
#                                 all_amount = stud_id.student_fee_line.search([('name','=',fee_amount.name.id),
#                                                                               ('stud_id','=',stud_id.id)],limit=1)
#                                 per_month_year_fee = all_amount.amount
#                                 if fee_amount.discount > 0:
#                                     dis_amount = (per_month_year_fee * fee_amount.discount)/100
#                                 fee_line_lst.append((0,0,
#                                         {
#                                             'product_id' : fee_amount.name.id,
#                                             'account_id' : fee_amount.name.property_account_income.id,
#                                             'name' : fee_amount.name.name,
#                                             'quantity' : 1.00,
#                                             'price_unit' : round(per_month_year_fee,2),
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'rem_amount' : round(per_month_year_fee,2),
#                                             'priority' : fee_amount.sequence,
#                                         }))
# 
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                       ('student_id','=',stud_id.id)],limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
#                                                                     'discount_amount' : dis_amount,
#                                                                     'month_id':month_year_obj.id})
#                                 else:
#                                     fee_year_pay_value = {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month_year_obj.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': per_month_year_fee,
#                                                 'total_amount' : fee_amount.amount,
#                                                 'discount_amount' : dis_amount,
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]
# 
#                         elif fee_amount.fee_pay_type.name == 'quater':
#                             if month_year_obj.qtr_month == True:
#                                 all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                             ('student_id','=',stud_id.id)],limit=1,order="id desc")
#                                 per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
#                                 count_month = 0
#                                 for total_month_id in self.academic_year_id.month_ids.search([('qtr_month','=',True),
#                                                                                               ('batch_id','=',self.academic_year_id.id),
#                                                                                               ('leave_month','=',False)]):
#                                     exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
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
#                                 fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
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
#                                 fee_line_lst.append((0,0,
#                                         {
#                                             'product_id' : fee_amount.name.id,
#                                             'account_id' : fee_amount.name.property_account_income.id,
#                                             'name' : fee_amount.name.name,
#                                             'quantity' : 1.00,
#                                             'price_unit' : round(per_month_qtr_fee,2),
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'rem_amount' : round(per_month_qtr_fee,2),
#                                             'priority' : fee_amount.sequence,
#                                         }))
# 
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                       ('student_id','=',stud_id.id)],limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                                     'discount_amount' : all_amount.discount_amount + dis_amount,
#                                                                     'month_id': month_year_obj.id,})
#                                 else:
#                                     fee_qtr_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month_year_obj.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                 'total_amount' : fee_amount.amount,
#                                                 'discount_amount' : all_amount.discount_amount + dis_amount
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
# 
#                         if fee_amount.fee_pay_type.name == 'half_year':
#                             if month_year_obj.quater_month == True:
#                                 all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                             ('student_id','=',stud_id.id)],limit=1,order="id desc")
#                                 per_month_qtr_fee = all_amount.total_amount/2
#                                 count_month = 0
#                                 for total_month_id in self.academic_year_id.month_ids.search([('quater_month','=',True),
#                                                                                               ('batch_id','=',self.academic_year_id.id),
#                                                                                               ('leave_month','=',False)]):
#                                     exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
#                                     if exist_month.id:
#                                         count_month += 1
#                                 if count_month != 0:
#                                     new_per_month_qtr_fee = per_month_qtr_fee * count_month
# 
#                                     if all_amount.cal_amount <= new_per_month_qtr_fee:
#                                         cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
#                                         if cal_alt_new > 0:
#                                             per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
#                                         else:
#                                             per_month_qtr_fee = all_amount.total_amount/2
#                                 else:
#                                     per_month_qtr_fee = all_amount.total_amount/2
# 
#                                 fee_month_amount += per_month_qtr_fee
# 
#                                 #discount calculation for half year
#                                 fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
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
#                                             dis_amount_half_month = (per_month_qtr_fee * fee_amount.discount)/100
#                                             dis_amount = dis_amount_half_month + (dis_amount_half_month * fee_paid_line)
#                                     else:
#                                         dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
# 
#                                 total_discount += dis_amount
# 
#                                 fee_line_lst.append((0,0,
#                                         {
#                                             'product_id' : fee_amount.name.id,
#                                             'account_id' : fee_amount.name.property_account_income.id,
#                                             'name' : fee_amount.name.name,
#                                             'quantity' : 1.00,
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'price_unit' : round(per_month_qtr_fee,2),
#                                             'rem_amount' : round(per_month_qtr_fee,2),
#                                             'priority' : fee_amount.sequence,
#                                         }))
# 
#                                 exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                       ('student_id','=',stud_id.id)],limit=1)
#                                 if exist_qtr_pay_detail.id:
#                                     if exist_qtr_pay_detail.month_id.id != month_year_obj.id:
#                                         exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                                     'discount_amount' : all_amount.discount_amount + dis_amount,
#                                                                     'month_id': month_year_obj.id,})
#                                 else:
#                                     fee_qtr_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month_year_obj.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
#                                                 'total_amount' : fee_amount.amount,
#                                                 'discount_amount' : all_amount.discount_amount + dis_amount
#                                             }
# 
#                                     stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
# 
#                         elif fee_amount.fee_pay_type.name == 'alt_month':
#                             if month_year_obj.alt_month == True:
#                                 all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                             ('student_id','=',stud_id.id)],limit=1,order="id desc")
#                                 per_month_alt_fee = all_amount.total_amount/(month_diff/2)
#                                 count_month = 0
#                                 for total_month_id in self.academic_year_id.month_ids.search([('alt_month','=',True),
#                                                                                               ('batch_id','=',self.academic_year_id.id),
#                                                                                               ('leave_month','=',False)]):
#                                     exist_month = stud_id.payment_status.search([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
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
#                                 fee_paid_line = stud_id.payment_status.search_count([('month_id','=',total_month_id.id),
#                                                                                  ('student_id','=',stud_id.id)])
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
#                                             'quantity' : 1.00,
#                                             'price_unit' : round(per_month_alt_fee,2),
#                                             'parent_id' : stud_id.parents1_id.id,
#                                             'rem_amount' : round(per_month_alt_fee,2),
#                                             'priority' : fee_amount.sequence,
#                                         }))
#                                 exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                       ('student_id','=',stud_id.id)],limit=1)
#                                 if exist_alt_pay_detail.id:
#                                     if exist_alt_pay_detail.month_id.id != month_year_obj.id:
#                                         exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
#                                                                     'discount_amount' : all_amount.discount_amount + dis_amount,
#                                                                     'month_id': month_year_obj.id,})
#                                 else:
#                                     fee_alt_pay_value =\
#                                             {
#                                                 'name': fee_amount.name.id,
#                                                 'student_id': stud_id.id,
#                                                 'month_id': month_year_obj.id,
#                                                 'fee_pay_type': fee_amount.fee_pay_type,
#                                                 'cal_amount': all_amount.cal_amount + round(per_month_alt_fee,2),
#                                                 'total_amount' : fee_amount.amount,
#                                                 'discount_amount' : all_amount.discount_amount + dis_amount
#                                             }
#                                     stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]
# 
#                         elif fee_amount.fee_pay_type.name == 'month':
#                             amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                           ('student_id','=',stud_id.id)],limit=1)
#                             # per month fee calculation
#                             per_month_fee = amount_above.total_amount/(month_diff)
#                             # already fee paided month
#                             fee_paid_line = stud_id.payment_status.search_count([('student_id','=',stud_id.id)])
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
# 
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
# 
#                             total_discount += dis_amount
# 
#                             fee_line_lst.append((0,0,
#                                 {
#                                     'product_id' : fee_amount.name.id,
#                                     'account_id' : fee_amount.name.property_account_income.id,
#                                     'name' : fee_amount.name.name,
#                                     'quantity' : 1.00,
#                                     'price_unit' : round(per_month_fee,2),
#                                     'parent_id' : stud_id.parents1_id.id,
#                                     'rem_amount' : round(per_month_fee,2),
#                                     'priority' : fee_amount.sequence,
#                                 }))
# 
#                             exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
#                                                                                    ('student_id','=',stud_id.id)], limit=1)
#                             if exist_stud_pay_detail.id:
#                                 if exist_stud_pay_detail.month_id.id != month_year_obj.id:
#                                     exist_stud_pay_detail.write({'cal_amount':amount_above.cal_amount + per_month_fee,
#                                                                  'discount_amount':amount_above.discount_amount + dis_amount,
#                                                                  'month_id': month_year_obj.id,})
#                             else:
#                                 fee_pay_value =\
#                                     {
#                                         'name': fee_amount.name.id,
#                                         'student_id': stud_id.id,
#                                         'month_id': month_year_obj.id,
#                                         'fee_pay_type': fee_amount.fee_pay_type,
#                                         'cal_amount': amount_above.cal_amount + per_month_fee,
#                                         'total_amount' : fee_amount.amount,
#                                         'discount_amount' : amount_above.discount_amount + dis_amount
#                                     }
# 
#                                 stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
# 
#                         # Term wise Fee Calculation
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
#                             term_id=False
#                             prev_term_seq=exist_stud_pay_detail.next_term.id
# 
#                             if prev_term_seq:
#                                 same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq)])
# 
#                             next_term=exist_stud_pay_detail.next_term.id
#                             invoice_dic={}
#                             if current_term.id:
#                                 start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
#                                 end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
#                                 if start_date.month == self.month.name:
#                                     if int(start_date.year) == int(self.year):
#                                         term_month = self.months_between(start_date,end_date)
#                                         per_month_fee = (fee_amount.amount / month_diff) * len(term_month)
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
# 
#                                             if list:
#                                                 list=sorted(list)
#                                                 next_term=list[0]
#                                     else:
#                                         per_month_fee=0
#                                         term_id=False
#                             # discount calculation
#                             if fee_amount.discount > 0:
#                                 pre_dis = 0.00
#                                 if amount_above.cal_amount > 0.00:
#                                     pre_dis = (amount_above.cal_amount * fee_amount.discount) / 100
#                                     if pre_dis != amount_above.discount_amount:
#                                         if pre_dis < amount_above.discount_amount:
#                                             pre_dis = pre_dis - amount_above.discount_amount
#                                         else:
#                                             pre_dis = pre_dis - amount_above.discount_amount
#                                 dis_amount = (per_month_fee * fee_amount.discount) / 100
#                                 dis_amount + pre_dis
# 
#                             total_discount += dis_amount
#                             fee_month_amount += per_month_fee
# 
#                             fee_line_lst.append((0,0,
#                                     {
#                                         'product_id' : fee_amount.name.id,
#                                         'account_id' : fee_amount.name.property_account_income.id,
#                                         'name' : fee_amount.name.name,
#                                         'quantity' : 1.00,
#                                         'price_unit' : round(per_month_fee,2),
#                                         'rem_amount' : round(per_month_fee,2),
#                                         'parent_id' : stud_id.parents1_id.id,
#                                         'priority' : fee_amount.sequence,
#                                     }))
# 
#                             fee_pay_value =\
#                                         {
#                                             'name': fee_amount.name.id,
#                                             'student_id': stud_id.id,
#                                             'month_id': month_year_obj.id,
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
#                                         'parent_id' : stud_id.parents1_id.id,
#                                         'quantity' : 1.00,
#                                         'price_unit' : -round(dis_amount,2),
#                                         'rem_amount' : -round(dis_amount,2),
#                                         'priority' : 0,
#                                         }))
# 
#                     # Monthaly Fee Pyment Generate Line
#                     exist_fee_line = self.fee_payment_line_ids.search([('student_id','=',stud_id.id),
#                                                                         ('month_id','=',self.month.id),
#                                                                         ('year','=',self.year),
#                                                                         ('fee_payment_id','=',self.id)])
#                     if not exist_fee_line.id:
#                         self.fee_payment_line_ids.create({
#                             'student_id': stud_id.id,
#                             'total_fee': fee_month_amount-total_discount,
#                             'month_id': month_year_obj.id,
#                             'month': month_year_obj.name,
#                             'year': month_year_obj.year,
#                             'fee_payment_id' : self.id,
#                             })
#                     # else:
#                     #     exist_fee_line.write({
#                     #         'total_fee': fee_month_amount-total_discount,
#                     #     })
# 
#                     # Invoice Create
#                     exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month_year_obj.id)])
#                     if exist_invoice == 0 and len(fee_line_lst) > 0:
#                         invoice_vals = {
#                                 'partner_id' : stud_id.id,
#                                 'month_id' : month_year_obj.id,
#                                 'account_id' : stud_id.property_account_receivable.id,
#                                 'invoice_line' : fee_line_lst,
#                                 'month' : month_year_obj.name,
#                                 'year' : month_year_obj.year,
#                                 'batch_id' : self.academic_year_id.id,
#                             }
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
#                     fee_status = stud_id.payment_status.search([('month_id','=',month_year_obj.id),
#                                                                 ('student_id','=',stud_id.id)])
#                     if not fee_status.id:
#                         status_val = {
#                             'month_id': month_year_obj.id,
#                             'paid': False,
#                         }
#                         stud_id.payment_status = [(0,0,status_val)]
#             self.state = 'genarated'
#         else:
#             raise except_orm(_('Warning !'),
#                     _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
#                              % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))
#===============================================================================