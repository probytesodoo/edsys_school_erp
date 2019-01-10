# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
import time
from odoo.exceptions import except_orm

class Student(models.Model):

    _inherit = 'res.partner'

    @api.depends('parent1_id')
    def get_sibling(self):
        """
        get sibling
        ------------------
        :return:
        """
        for stud_rec in self:
            sibling_list = []
            if stud_rec.parents1_id.id:
                for child_rec in stud_rec.parents1_id.chield1_ids:
                    if not child_rec.id == stud_rec.id:
                        sibling_list.append(child_rec.id)
            stud_rec.sibling_ids = [(6,0,sibling_list)]

    first_acd_year_of_child = fields.Many2one('batch', string='First Academic Year Of Child')
    parent1_id = fields.Char('Parent Code')
    sibling_info = fields.Char(string='Name and Grade of sibling, if any, studying in the School')
    student_id = fields.Char('Student ID') 
    reg_no = fields.Char('Registration Number')
    class_id = fields.Many2one('course',string="Class")
    year_id = fields.Many2one('batch',string='Year')
    is_parent = fields.Boolean('is Parents')
    is_student = fields.Boolean('is Student')
    chield1_ids = fields.One2many('res.partner','parents1_id','Child')
    mother_name = fields.Char('Mother name')
    parents_email = fields.Char('Father Email')
    mother_email = fields.Char('Mother Email')
    parent_profession = fields.Char()
    mother_profession = fields.Char()
    parent_contact = fields.Char('Father Contact')
    mother_contact = fields.Char('Mother Contact')
    student_fee_line = fields.Many2many('fees.line','student_id','fee_line_id',string='Student Fees')
    parents1_id = fields.Many2one('res.partner', string='Parents',domain=[('is_parent','=',True)])
#    student_name = fields.Char('Student Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    admission_date = fields.Date(string='Admission Date', track_visibility='onchange')
    batch_id = fields.Many2one('batch', string='Academic Year', track_visibility='onchange')
    course_id = fields.Many2one('course', string='Admission To Class', track_visibility='onchange')
    # standard_id = fields.Many2one('standard', 'Admitted Class')
    # category_id = fields.Many2one('category', string='Category')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender')
    emirati = fields.Selection([('y', 'Yes'), ('n', 'No')], string='Emirati')
    arab = fields.Selection([('arab', 'Arabs'), ('non_arab', 'Non Arabs')], string='Arab')
    religion_id = fields.Many2one('religion', string='Religion')
    birth_date = fields.Date(string='Birth Date')
    # birth_place = fields.Many2one('res.country.state', string='City')
    birth_place = fields.Char(string='City')
    birth_country = fields.Many2one('res.country', string='Birth Country')
    emirates_id = fields.Char('Emirates Id')
    passport_issue_date = fields.Date(string='Passport issue date')
    # student_id = fields.Char(sring='Student Id')
    title = fields.Many2one('res.partner.title', string='Title')
    date_of_joining = fields.Date('Date Of Joining', track_visibility='onchange')
    student_section_id = fields.Many2one('section', string='Admitted section')
    # application_number = fields.Char(size=16, string='Application Number')
    # application_date = fields.Datetime(string='Application Date')
    phone = fields.Char(size=16, string='Phone')
    mobile = fields.Char(size=16, string='Mobile')
    email = fields.Char(size=256, string='Email')
    prev_institute = fields.Char(size=256, string='Previous Institute')
    # prev_course = fields.Char(size=256, string='Previous Course')
    # prev_result = fields.Char(size=256, string='Previous Result')
    family_business = fields.Char(size=256, string='Family Business')
    family_income = fields.Float(string='Family Income')
    passport_no = fields.Char('Passport Number', size=128)
    place_of_issue = fields.Many2one('res.country', string='Place Of Issue')
    passport_expiry_date = fields.Date(string='Passport expiry date')
    visa_no = fields.Char('Visa Number', size=128)
    visa_issue_date = fields.Date(string='Visa issue date')
    visa_expiry_date = fields.Date(string='Visa expiry date')
    lang_id = fields.Many2one('res.lang', string='Languange')
    other_lang_id = fields.Many2one('res.lang', string='Other Languange')
    emergency_contact = fields.Char("Emergency Contact")
    prev_institute = fields.Char(size=256, string='Previous Institute')
    prev_grade = fields.Char(size=256, string='Grade Last attended')
    last_attendance = fields.Date(string='Last date of attendance')
    prev_academic_year = fields.Many2one('batch', string='Previous Academic Year')
    prev_academic_city = fields.Char(size=64, string='City')
    prev_academic_country = fields.Many2one('res.country', string='Country')
    tranfer_reason = fields.Text('Reason for Transfer')
    remarks = fields.Text('Remarks')
    about_us = fields.Selection(
        [('fb', 'facebook'), ('google', 'Google'), ('friend', 'Family & Friends'),
         ('sms_camp','SMS campaign'), ('np', 'Newspaper'),('visitnearbyarea','Visit to nearby area'),
         ('marketing_leaflet','Marketing Leaflet'),('other','Other')],
        string='Where did you first find out about us?')
    curriculum = fields.Char("Curriculum")
    t_c_number = fields.Char("TC Number")
    blood_group = fields.Char("Blood Group")
    s_height = fields.Char("Height(In Cm)")
    s_width = fields.Char("Weight(In Kg)")
    child_allergic = fields.Boolean("Is your child allergic to anything?")
    w_allergic = fields.Char("What is your child allergic to?")
    w_reaction = fields.Char("What is the reaction?")
    w_treatment = fields.Char('What is the treatment?')
    under_medication = fields.Boolean('Is your child currently under medication / treatment?')
    w_medication_mention = fields.Char('Please Mention')
    w_treatment_mention = fields.Char('What is the treatment?')
    transport_type = fields.Selection([('own', 'Own Transport'), ('school', 'School Transport')], 'Transport Type')
    bus_no = fields.Char('Bus No')
    pick_up = fields.Char('Pick up')
    droup_off_pick = fields.Char("Drop off points")
    transfer_certificate = fields.Binary('Transfer Certificate(Scanned copy)')
    s_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    s_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    passport_copy1 = fields.Binary('Passport Copy Page 1(Scanned copy)')
    passport_copy2 = fields.Binary('Passport Copy Page 2(Scanned copy)')
    parent_visa_copy = fields.Binary('Visa Copy(Scanned copy)')
    f_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    f_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    mother_visa_copy = fields.Binary('Visa Copy(Scanned copy)')
    m_emirates_copy1 = fields.Binary('Emirates Id Copy Page 1(Scanned copy)')
    m_emirates_copy2 = fields.Binary('Emirates Id Copy Page 2(Scanned copy)')
    medical_documents_file = fields.Binary("Medical documents/file")
    #sibling_ids = fields.One2many('sibling','student_id',string='Sibling')
    sibling_ids = fields.Many2many('res.partner',string='Sibling',compute='get_sibling')
    nationality = fields.Many2one('res.country',string="Nationality")
    parents_office_contact = fields.Char("Parents Office Contact")
    mother_office_contact = fields.Char("Mother Office Contact")
    parent_address = fields.Text("Parents Address")
    mother_address = fields.Text("Mother Address")
#    student_fee_line = fields.One2many('fees.line','stud_id','Fee Lines')
    student_fee_line = fields.One2many('fees.line','stud_id','Fee Lines', track_visibility='onchange')
    payble_fee_ids = fields.One2many('student.payble.fee','student_id',string="Payble Fee", track_visibility='onchange')
    paid_term_history_ids = fields.One2many('paid.term.history','student_id',sring="Piad Term History")
    payment_status = fields.One2many('student.fee.status','student_id',string='Fee Status', track_visibility='onchange')
    discount_on_fee = fields.Many2one('discount.category',string='Fee Discount', ondelete='cascade', track_visibility='onchange')
    waiting_approval = fields.Boolean('Waiting Ministry Approval')
    isd_code = fields.Char('ISD Code')
    about_us_other = fields.Char('Others')
    is_old_student = fields.Boolean('Old Student')
    old_id = fields.Char('Old Id')
    is_old_parent = fields.Boolean('Old Parents')
    stud_batch_shift = fields.Selection([('morning', 'Morning Batch'), ('clb', 'CLB Batch')],
                                        select=True, string='Batch Shift')
    khada_sis = fields.Char('KHDA/SIS')
    total_fee_amount_student = fields.Float(compute='count_total_fee_amount')

    _sql_constraints = [
        ('khada_sis_unique', 'unique(khada_sis)', 'KHDA/SIS must be unique per Student !')
        ]

    @api.multi
    def count_total_fee_amount(self):
        """
        count total fee amount
        ------------------------
        :return:
        """
        total_amount = 0.0
        for student_id in self:
            if student_id.student_fee_line:
                for fee_line in student_id.student_fee_line:
                    if fee_line.discount > 0.0:
                        total_amount += (fee_line.amount - (fee_line.amount * fee_line.discount/100))
                    else:
                        total_amount += fee_line.amount
                student_id.total_fee_amount_student = total_amount
    
    @api.onchange("country_id")
    def onchange_country_id_set_state(self):
        if self.country_id.id:
            state_rec = self.env['res.country.state'].search([('country_id','=',self.country_id.id)])
        else:
            state_rec = self.env['res.country.state'].search([])
        return {
                'domain': {
                      'state_id': [('id', 'in', state_rec.ids)],
                    }
                }


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # if self._context and self._context.get('active_ids'):

        if 'active_id' in self._context and self._context['active_id']:

            for record in self.env['res.partner'].browse(self._context.get('active_id')):
                mod_obj = self.env['ir.model.data']
                if view_type == 'form':
                    if record.is_student == True or record.is_parent == True:
                        vid = mod_obj.get_object_reference('edsys_edu', 'view_student_parent_form')
                        vid = vid and vid[1] or False,
                        view_id = vid
                        return super(Student, self).fields_view_get(
                            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        return super(Student, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

   
   
    @api.model
    def create(self,vals):
        """
        add unique student id when create student.
        --------------------------------------
        :param vals:
        :return:
        """
        if 'is_student' in vals and vals['is_student']:
            vals['student_id'] = self.env['ir.sequence'].get('res.partner')
        return super(Student, self).create(vals)

    @api.model
    def write_on_registration(self, vals):
        """
        student master data sink with registration table
        :param vals:
        :return:
        """
        if self.reg_no:
            registration_rec = self.env['registration'].search([('enquiry_no','=',self.reg_no)],limit=1)
            if registration_rec.id:
                registration_rec.write(vals)
                if vals.has_key('stud_batch_shift'):
                    registration_rec.batch_shift = vals['stud_batch_shift']
        return True

    @api.multi
    def write(self, vals):
        """
        overide write method,
        parent data synk with it's all child,
        student data synk with registration object.
        -------------------------------------------
        :param vals:
        :return:
        """
        for rec in self:
            #if rec.is_student:
                #rec.write_on_registration(vals)
            if rec.is_parent:
                child_vals = {}
                field_list = ['street','street2','city','state_id','zip','country_id','mother_name','parents_email',
                              'mother_email', 'parent_profession','mother_profession','parent_contact','mother_contact',
                              'property_account_customer_advance','property_account_receivable_id',
                              'property_account_payable','isd_code',]
                for key in field_list:
                    if vals.get(key):
                        child_vals.update({key : vals.get(key)})
                for child in rec.chield1_ids:
                    child.write(child_vals)
        return super(Student, self).write(vals)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            _name = ''
            f_name = str(record.name) if str(record.name) != 'False' else ""
            m_name = str(record.middle_name) if str(record.middle_name) != 'False' else ""
            l_name = str(record.last_name) if str(record.last_name) != 'False' else ""
            if record.is_parent == True:
                _name = '[ ' + str(record.parent1_id) + ' ]' + f_name + ' ' + m_name + ' ' + l_name
            elif record.is_student == True:
                _name = '[ ' + str(record.student_id) + ' ]' + f_name + ' ' + m_name + ' ' + l_name
            else:
                _name = str(record.name)
            res.append((record.id, _name))
        return res

# --------------------------------------------------------------------------------------

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
        if self._context is None: self._context = {}
        invoice_pool = self.env['account.invoice']
        journal_pool = self.env['account.journal']
        if self._context.get('invoice_id', False):
            invoice = invoice_pool.browse(self._context['invoice_id'])
            journal_id = journal_pool.search([('currency', '=', invoice.currency_id.id),
                                              ('company_id', '=', invoice.company_id.id)],
                                             limit=1)
            return journal_id and journal_id[0] or False
        if self._context.get('journal_id', False):
            return self._context.get('journal_id')
        if not self._context.get('journal_id', False) and self._context.get('search_default_journal_id', False):
            return self._context.get('search_default_journal_id')

        ttype = self._context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(ttype)
        return res and res[0] or False

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

    @api.multi
    def genarate_march_month_invoice_for_old_student(self):
        invoice_obj = self.env['account.invoice']
        for student_rec in self.search([('is_student','=',True)]):
            if student_rec.is_old_student:
                total_amount = 0.00
                for fee_line in student_rec.payble_fee_ids:
                    total_amount += fee_line.cal_amount
                if total_amount != 0:
                    if total_amount > 0:
                        # feee_dub_line = student_rec.payble_fee_ids[0]
                        fee_line_lst=[]

                        for feee_dub_line in student_rec.payble_fee_ids:
                            if feee_dub_line.cal_amount > 0.00:
                                set_amount = 0.00
                                if feee_dub_line.cal_amount < total_amount:
                                    set_amount = feee_dub_line.cal_amount
                                    total_amount -= set_amount
                                else:
                                    set_amount = total_amount
                                    total_amount = 0.00
                                if set_amount > 0.00:
                                    fee_line_lst.append((0,0,{
                                        'product_id' : feee_dub_line.name.id,
                                        'account_id' : feee_dub_line.name.property_account_income_id.id,
                                        'name' : feee_dub_line.name.name,
                                        'quantity' : 1.00,
                                        'price_unit' : set_amount,
                                        'priority' : 1,
                                        }))
                        invoice_vals = {
                            'partner_id' : student_rec.id,
                            'account_id' : student_rec.property_account_receivable_id.id,
                            'invoice_line_ids' : fee_line_lst,
                            'batch_id' : student_rec.batch_id.id,
                            'month_id' : 22,
                        }

                        invoice_obj.create(invoice_vals)
                    else:
                        account_voucher_obj = self.env['account.voucher']
                        period_rec = self._get_period()
                        journal_rec = self._get_journal()
                        curency_id = self._get_currency()
                        voucher_data = {
                            'period_id': period_rec.id,
                            'journal_id': journal_rec.id,
                            'account_id': journal_rec.default_debit_account_id.id,
                            'partner_id': student_rec.id,
                            'currency_id': curency_id,
                            'reference': student_rec.name,
                            'amount': abs(total_amount),
                            'type': 'receipt' or 'payment',
                            'state': 'draft',
                            'pay_now': 'pay_later',
                            'name': '',
                            'date': time.strftime('%Y-%m-%d'),
                            'company_id': 1,
                            'tax_id': False,
                            'payment_option': 'without_writeoff',
                            'comment': _('Write-Off'),
                            }
                        voucher_rec = account_voucher_obj.create(voucher_data)

# -----------------------------------------------------------------------------------------------------
    @api.multi
    def update_advance_account(self):
        fee_line_obj = self.env['fees.structure']
        student_obj = self.env['res.partner']
        st_ids=student_obj.search([('is_parent','=',True)])
        pt_ids=student_obj.search([('is_student','=',True)])
        for student_rec in st_ids:
            student_rec.property_account_customer_advance=678
        for st in pt_ids:
            st.property_account_customer_advance=678


    def get_fee_structure_all(self):
        fee_line_obj = self.env['fees.structure']
        student_obj = self.env['res.partner']

        for student_rec in student_obj.browse(4542):
            fee_lst = []
            fee_lst_detail = []
            for fee_criteria in fee_line_obj.search([
                        ('academic_year_id','=',student_rec.batch_id.id),
                        ('course_id','=',student_rec.course_id.id),
                        ('type','=','academic'),
                    ]):
                for fee_line in fee_criteria.fee_line_ids:
                    if fee_line.fee_pay_type.name != 'one':
                        fee_data = \
                            {
                                'name' : fee_line.name,
                                'amount' : int(fee_line.amount),
                                'type' : fee_line.type,
                                'fee_pay_type' : fee_line.fee_pay_type.id,
                                'sequence': fee_line.sequence,
                                'stud_id' : student_rec.id,
                            }
                        fee_detail={
                        'name' : fee_line.name,
                        'student_id': student_rec.id,
                        'fee_pay_type' : fee_line.fee_pay_type.id,
                        'cal_amount' : 0.00,
                        'rem_amount' : 0.00,
                        'total_amount' : int(fee_line.amount),
                        'discount_amount' : 0.00,
                        }
                        fee_lst.append((0,0,fee_data))
                        fee_lst_detail.append((0,0,fee_detail))
            if len(fee_lst) > 0:
                student_rec.student_fee_line = fee_lst
                student_rec.payble_fee_ids = fee_lst_detail

    @api.multi
    def update_fee_structure(self):
        # first all discount update with 0 value
        for feess in self.student_fee_line:
            feess.discount_amount = 0.0
            feess.discount = 0.0

        if self.discount_on_fee:
            # apply discount on fee structure
            for discount_fee_line in self.discount_on_fee.discount_category_line.search([
                ('discount_category_id','=',self.discount_on_fee.id)]):
                for fees in self.student_fee_line:
                    if fees.name.fees_discount:
                        if fees.name.fees_discount == discount_fee_line.product_id:
                            if discount_fee_line.discount_type == 'amount':
                                if discount_fee_line.discount_amount > 0.00 and fees.amount > 0.00:
                                    fees.discount_amount = discount_fee_line.discount_amount
                                    # fees.discount = (discount_fee_line.discount_amount * 100)/fees.amount
                            elif discount_fee_line.discount_type == 'persentage':
                                if discount_fee_line.discount_persentage > 0.00 and fees.amount > 0.00:
                                    fees.discount = discount_fee_line.discount_persentage
                                    
        #update NYAF
        reg_obj = self.env['registration']
        reg_rec = reg_obj.search([('enquiry_no','=',self.reg_no)])
        nyaf_obj = self.env['next.year.advance.fee']
        #nyaf_rec = nyaf_obj.search([('reg_id.enquiry_no','=', self.reg_no),('state','in',('fee_unpaid', 'fee_partial_paid'))])
        nyaf_rec = nyaf_obj.search([('reg_id.enquiry_no','=', self.reg_no),('state','in',('fee_unpaid', 'fee_partial_paid', 'fee_paid'))])
        if nyaf_rec :
            nyaf_updated_rec = reg_rec.send_payfort_acd_for_next_year()
            if nyaf_updated_rec.residual <= 0 :
                 reg_rec.next_year_advance_fee_id.state = 'fee_paid'
                 reg_rec.fee_status = 'academy_fee_pay'


class StudentPayableFee(models.Model):

    _name = 'student.payble.fee'

    @api.depends('total_amount','cal_amount','discount_amount')
    def _remaining_amount_cal(self):
        for rem in self:
            rem.rem_amount = rem.total_amount - (rem.cal_turm_amount+rem.discount_amount)

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

    month_id = fields.Many2one('fee.month',string='Month Ref',store=True)
    name = fields.Many2one('product.product',string='Name')
    month = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    year = fields.Char(string="year", related="month_id.year")
    fee_pay_type = fields.Many2one('fee.payment.type',string="Fee Payment Type")
    cal_amount = fields.Float(string="Calculated Amount")
    rem_amount = fields.Float(string='Remaining Amount',compute='_remaining_amount_cal')
    student_id = fields.Many2one('res.partner',string='Student')
    total_amount = fields.Float('Total Amount')
    cal_turm_amount = fields.Float('Paid')
    next_term = fields.Many2one('acd.term', string="Next Term")
    discount_amount = fields.Float(string="Discount Amount")
    is_next_half_year = fields.Boolean('Next Half Year')

class StudentFeeStatus(models.Model):

    _name = 'student.fee.status'

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

    month_id = fields.Many2one('fee.month', string='Month Ref',store=True)
    name = fields.Selection(List_Of_Month, string='Month')#, related='month_id.name')
    year = fields.Char(string="Year")#, related="month_id.year")
    paid = fields.Boolean('Paid')
    student_id = fields.Many2one('res.partner')
