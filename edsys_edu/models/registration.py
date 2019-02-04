# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import hashlib
import re
import urllib
from validate_email import validate_email
from num2words import num2words
import pytz
import base64

class state_history(models.Model):
    _name = 'state.history'
    reg_id=fields.Many2one('registration',string ='reg ID')
    state_name=fields.Char(string='State Name',size=126)

class Registration(models.Model):
    _name = 'registration'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Registration"
    _order = "application_date desc"

    @api.multi
    def amount_to_text(self, amount):
        """
        this method is use to convert
        datatype int to char
        :param amount: amount
        :return:
        """
        amount_in_text= num2words(amount)
        amount_upper=amount_in_text.upper()
        return amount_upper

    @api.onchange('admission_date','batch_id')
    def admission_date_change(self):
        """
            this method used to check admition date
            greter then current date.
            ------------------------------------------
            @param self : object pointer
            @worning : if date less then current date
        """
        if self.admission_date and self.batch_id:
            admition_date=datetime.strptime(self.admission_date, "%Y-%m-%d")
            year_start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d")
            year_end_date = datetime.strptime(self.batch_id.end_date,"%Y-%m-%d")
            if admition_date < year_start_date:
                raise except_orm(_('Warning!'),
                        _("Admission Date should be Equal to or After Start of Academic year!"))
            elif admition_date > year_end_date:
                raise except_orm(_('Warning!'),
                        _("Admission Date should be Equal to or Before End of Academic year!"))

            for month_year in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),('leave_month','=',True)]):
                if int(month_year.name) == int(admition_date.month) and int(month_year.year) == int(admition_date.year):
                    raise except_orm(_('Warning!'),
                        _("Admission Date should not be in Leave month !"))
    # @api.onchange('entrance_exam_date')
    # def enterance_exam_date_old_4july2016(self):
    #     """
    #     add validation on enterance exam.
    #     ---------------------------------
    #     :return:
    #     """
    #     if self.entrance_exam_date:
    #         comp_date= datetime.strptime(self.entrance_exam_date.split(' ')[0], "%Y-%m-%d")
    #         date_status = self.compare_with_current_date(comp_date)
    #         if date_status == False:
    #             raise except_orm(_('Warning!'),
    #                     _("Enterance Exam date can not be before Application Date!"))

    # @api.model
    # def compare_with_current_date_old_4july2016(self,selected_date):
    #     """
    #         this method used to check selected date,
    #         greter then current date,
    #         ------------------------------------------
    #         @param self : object pointer
    #         @return : True if current date lessthen selected_date
    #                   else return False
    #     """
    #     if selected_date:
    #         current_date=date.today()
    #         current_date=datetime.strptime(str(current_date), "%Y-%m-%d")
    #         if selected_date < current_date:
    #             return False
    #         else:
    #             return True


#     @api.onchange('entrance_exam_date')
#     def enterance_exam_date(self):
#         """
#         add validation on enterance exam.
#         ---------------------------------
#         :return:
#         """
#         if self.entrance_exam_date:
#             # ODOO DATE + 5:30 HOURS
#             comp_date= datetime.strptime(self.entrance_exam_date, "%Y-%m-%d %H:%M:%S")+timedelta(hours=5,minutes=30)
#             date_status = self.compare_with_current_date(comp_date)
#             if date_status == False:
#                 raise except_orm(_('Warning!'),
#                         _("Entrance Exam Date should be current date or future date."))

    @api.model
    def compare_with_current_date(self,selected_date):
        """
            this method used to check selected date,
            greter then current date,
            ------------------------------------------
            @param self : object pointer
            @return : True if current date lessthen selected_date
                      else return False
        """
        if selected_date:
            current_date = datetime.now() + timedelta(hours=5,minutes=30)
            s_date = datetime.strptime(str(selected_date).split(' ')[0],"%Y-%m-%d").date()
            c_date = datetime.strptime(str(current_date).split(' ')[0],"%Y-%m-%d").date()
            if s_date < c_date:
                return False
            else:
                return True

                
    def get_person_age(self,date_birth, date_today):

        """
        At top level there are three possibilities : Age can be in days or months or years.
        For age to be in years there are two cases: Year difference is one or Year difference is more than 1
        For age to be in months there are two cases: Year difference is 0 or 1
        For age to be in days there are 4 possibilities: Year difference is 1(20-dec-2012 - 2-jan-2013),
        ----------------------------------------------------------------------------------------------------
        :param date_birth: Birth Date
        :param date_today: Current Date
        :return: Dictonary
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

    @api.onchange('birth_date','course_id','batch_id')
    def age_criteria_cal(self):
        """
        This method is used to calculate age from birthday
        and check age criteria
        example : age criteria for TIA dubai
        |-----------------------------------------------------------------------------------|
        |   CLASS   |  MIN AGE  | MAX AGE | effective_date |     Remarks                    |
        ====================================================================================|
        |    KG 1   |     4     |    5    |   06/01/2015   | student age must be in beetween|
        |           |           |         |                | minimum age to maximum age as  |
        |           |           |         |                | otherwise not eligible for     |
        |           |           |         |                | admission                      |
        |-----------------------------------------------------------------------------------|
        @param self : object pointer
        """

        if self.birth_date and self.course_id and self.batch_id:
            date_birth = datetime.strptime(self.birth_date,"%Y-%m-%d").date()
            effective_date= datetime.strptime(self.batch_id.effective_date,"%Y-%m-%d").date()
            age_dict = self.get_person_age(date_birth,effective_date)
            min_age=self.course_id.min_age
            max_age=self.course_id.max_age

            if age_dict['years'] < min_age or age_dict['years'] > max_age:
                self.birth_date = False
                raise except_orm(_('Warning!'),
                    _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                 (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))
            if age_dict['years'] == max_age:
                if age_dict['months'] > 0 or age_dict['days'] > 0:
                    raise except_orm(_('Warning!'),
                    _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                 (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))

    def change_colore_on_kanban(self):
        """
        change color index base on fee status
        ----------------------------------------
        :return: index of color for kanban view
        """
        for record in self:
            color = 0
            if record.fee_status == 'reg_fee_unpaid':
                color = 0
            elif record.fee_status == 'reg_fee_pay':
                color = 5
            elif record.fee_status == 'academy_fee_unpaid':
                color = 0
            elif record.fee_status == 'academy_fee_partial_pay':
                color = 3
            elif record.fee_status == 'academy_fee_pay':
                color = 5
            else:
                color = 0
            record.color = color

    @api.multi
    def count_total_fee_amount(self):
        """
        count total fee amount
        ------------------------
        :return:
        """
        total_amount = 0.0
        if self.student_fee_line:
            for fee_line in self.student_fee_line:
                if fee_line.discount > 0.0:
                    total_amount += (fee_line.amount - (fee_line.amount * fee_line.discount/100))
                else:
                    total_amount += fee_line.amount
        self.total_fee_amount = total_amount
        
        
    @api.one
    def get_dubai_exam_date_formate(self):
        if self.entrance_exam_date : 
            convetred_date = datetime.strptime(self.entrance_exam_date, "%Y-%m-%d %H:%M:%S")
            added_hour_date = str(convetred_date + timedelta(hours=4))
            date_now = added_hour_date.split(" ")[0]
            time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
            self.dubai_exam_date_formate = str(date_now) + " " + str(time_now)

    first_acd_year_of_child = fields.Many2one('batch', string='First Academic Year Of Child')
    enquiry_no = fields.Char(sring='Enquiry Form No', readonly='1')
    registration_number = fields.Char('Registration Number')
    sibling_info = fields.Char(string='Name and Grade of sibling, if any, studying in the School')
#    registration_id = fields.Char(string='Registration No')
    title = fields.Many2one('res.partner.title',  string='Title')
    name = fields.Char(string='First Name', required=True)
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    image = fields.Binary()
    date_of_joining = fields.Date('Date Of Joining')
    course_id = fields.Many2one('course',  string='Admission To Class', required=True, track_visibility='onchange')
    batch_id = fields.Many2one('batch',  string='Academic Year')
    
    # standard_id = fields.Many2one('standard', 'Admitted Class')
    student_section_id = fields.Many2one('section', string='Admitted section')
    # application_number = fields.Char(size=16, string='Application Number', readonly='1')
    admission_date = fields.Date(string='Joining Date')
    application_date = fields.Datetime(string='Application Date')
    birth_date = fields.Date(string='Birth Date', required=True)
    # birth_place = fields.Many2one('res.country.state', string='City')
    birth_place = fields.Char(string='Place of Birth')
    birth_country = fields.Many2one('res.country', string='Birth Country')
    emirates_id = fields.Char('Emirates Id', size=64)
    street = fields.Char(size=256, string='Street')
    street2 = fields.Char(size=256, string='Street2')
    phone = fields.Char(size=16, string='Phone')
    mobile = fields.Char(size=16, string='Mobile',required=True)
    email = fields.Char(size=256, string='Email',required=True)
    city = fields.Char(size=64, string='City')
    zip = fields.Char(size=8, string='Zip')
    state_id = fields.Many2one('res.country.state', string='States')
    country_id = fields.Many2one('res.country', string='Country')

#    state = fields.Selection([('enquiry', 'Enquiry'), ('reg', 'Registration'), 
#                              ('pending', 'Decsion pending'),('awaiting_fee', 'Awaiting Fee'), 
#                              ('waiting_list', 'Waiting List'), ('rejected', 'Rejected'), 
#                              ('ministry_approval', 'Ministry Approval'), ('done', 'Done'), ('cancel', 'Cancel')],
#                              select=True, string='Stage', default='enquiry')
    STATES=[('enquiry', 'Enquiry'), ('reg', 'Registration'), 
                              ('pending', 'Decision pending'),('awaiting_fee', 'Awaiting Fee'), 
                              ('waiting_list', 'Waiting List'), ('rejected', 'Rejected'), 
                              ('done', 'Done')]
    state = fields.Selection(STATES, select=True, string='Stage', default='enquiry', track_visibility='onchange')
    state_dropdown = fields.Selection([('enquiry', 'Enquiry'), ('reg', 'Registration'), \
                              ('pending', 'Decision Pending'),('awaiting_fee', 'Awaiting Fee'), \
                              ('waiting_list', 'Waiting List'),
                              ('done', 'Done')], string='Stage', track_visibility='onchange')
    state_hide = fields.Char(invisible=1)
    state_hide_ids = fields.One2many('state.history','reg_id',string='Hide state')
    prev_institute = fields.Char(size=256, string='Previous Institute')
    prev_course = fields.Char(size=256, string='Previous Course')
    prev_result = fields.Char(size=256, string='Previous Result')
    family_business = fields.Char(size=256, string='Family Business')
    family_income = fields.Float(string='Family Income')
    religion_id = fields.Many2one('religion', string='Religion', ondelete="cascade")
    # category_id = fields.Many2one('category', string='Category')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender', required=True)
    passport_no = fields.Char('Passport Number', size=128)
    place_of_issue = fields.Many2one('res.country', string='Place Of Issue')
    passport_issue_date = fields.Date(string='Passport issue date')
    passport_expiry_date = fields.Date(string='Passport expiry date')
    visa_no = fields.Char('Visa Number', size=128)
    visa_issue_date = fields.Date(string='Visa issue date')
    visa_expiry_date = fields.Date(string='Visa expiry date')
    emirati = fields.Selection([('y', 'Yes'), ('n', 'No')], string='Emirati')
    arab = fields.Selection([('arab', 'Arabs'), ('non_arab', 'Non Arabs')], string='Arab')
    lang_id = fields.Many2one('res.lang',  string='Languange')
    other_lang_id = fields.Many2one('res.lang',  string='Other Languange')
    parent_name = fields.Char(size=256, string='Father Name',required=True)
    parent_email = fields.Char(string='Parent Email',)
    parent_profession = fields.Char(size=256, string='Profession')
    parent_contact = fields.Char(size=256, string='Father Contact')
    parent_office_contact = fields.Char(size=256, string="Office Tel. No")
    #parent_residential_address = fields.Text(string="Residential Address",)
    mother_name = fields.Char(size=256, string='Mother Name')
    mother_contact = fields.Char(size=256, string='Mother Contact')
    mother_profession = fields.Char(size=256, string='Mother Profession')
    mother_email = fields.Char(string="Mother Email")
    #mother_residential_address = fields.Char(string="Parent Residential Address")
    emergency_contact = fields.Char("Emergency Contact")
    prev_institute = fields.Char(size=256, string='Previous Institute')
    prev_grade = fields.Char(size=256, string='Grade Last attended')
    last_attendance = fields.Date(string='Last date of attendance')
    prev_academic_year = fields.Many2one('batch', string='Previous Academic Year')
    prev_academic_city = fields.Char(size=64, string='City/Country')
    prev_academic_country = fields.Many2one('res.country', string='Country')
    tranfer_reason = fields.Text('Reason for Transfer')
    remarks = fields.Text('Remarks')
    about_us = fields.Selection(
        [('fb', 'facebook'), ('google', 'Google'), ('friend', 'Family & Friends'),
         ('sms_camp','SMS campaign'), ('np', 'Newspaper'),('visitnearbyarea','Visit to nearby area'),
         ('marketing_leaflet','Marketing Leaflet'),('other','Other')],
        string='Where did you first find out about us?')
    validated = fields.Boolean(string='Validated')
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
#    sibling_ids = fields.One2many('sibling','reg_id',string='Sibling')
    sibling_ids = fields.Many2many('res.partner',string='Sibling', related='student_id.sibling_ids')
    # nationality = fields.Many2one('nationality',string="Nationality")
    nationality_id = fields.Many2one('res.country',string="Nationality")
    reg_fee_line = fields.One2many('fees.line','reg_id','Fee Lines')
    student_fee_line = fields.One2many('fees.line','reg_form_id','Fee Lines')
    fee_status = fields.Selection(
        [('reg_fee_unpaid','Registration Fee Unpaid'),('reg_fee_pay','Registration Fee Paid'),
         ('academy_fee_unpaid','Academic Fee Unpaid'),('academy_fee_partial_pay','Academic Fee Partially Paid'),
         ('academy_fee_pay','Academic Fee Paid')], string="Fee Payment status")
    entrance_exam_date = fields.Datetime('Entrance Exam Date')
    color = fields.Integer('Color Index',compute="change_colore_on_kanban")
    reg_pay_link = fields.Char("PayFort Payment", readonly='1')
    sen = fields.Boolean(string = 'SEN')
    eal = fields.Boolean(string = 'EAL')
    efl = fields.Boolean(string = 'EFL')
    student_id = fields.Many2one('res.partner',string="Student Name")
    pay_id=fields.Char(string=" Payfort Payment ID", readonly="1")
    trx_date=fields.Date(string="Payment Date", readonly="1")
    acd_pay_link=fields.Char(string="Academic fee payment Link",size=126)
    acd_pay_id=fields.Char(string=" Payfort Payment ID",readonly="1")
    acd_trx_date=fields.Date(string="Payment Date",readonly="1")
    add_form_filled = fields.Boolean(string="Additional Form Filled")
    add_form_link = fields.Char(string="Additional Form Link")
    reject_reason = fields.Char(string="Reject Reason",size=126)
    fee_structure_confirm = fields.Boolean(string="Fee structure Confirm")
    test_completed = fields.Selection([('yes','YES'),('no','NO')],string="Test Completed")
    current_date_time = fields.Char(string="Created At",readonly="1")
    reg_fee_receipt = fields.Many2one('account.move',string='Registration Fee Receipt')
    invoice_id=fields.Many2one('account.invoice', string='Invoice')
    paid_amount = fields.Float(strin="You have to pay this amount")
    reg_fee_receipt = fields.Many2one('account.move',string='Registration Fee Receipt')
    remaining_form_link = fields.Char('Other Form Fillup')
    current_date_for_link = fields.Char('Current Date')
    discount_on_fee = fields.Many2one('discount.category',string='Fee Discount')
    dubai_exam_date_formate = fields.Char('Exam date', compute='get_dubai_exam_date_formate')
    total_fee_amount = fields.Float(compute='count_total_fee_amount')
    reg_amount=fields.Float(string="Registration Fee")
    complete_parent_contract = fields.Boolean('Complete Parent Contract')
    fee_structure_done = fields.Boolean('Fee Structure Confirm/Reset')
    with_out_reg_fee = fields.Boolean("Do not Collect Registration Fee")
    remark_for_reg_fee = fields.Char('Remark')
    confirm_fee_date = fields.Date(string="Fee Confirmed Date")
    online_reg_pay_link = fields.Char('Online Registration Payment Link')
    next_year_advance_fee_id = fields.Many2one('next.year.advance.fee',string='Next Year Advance Fee', ondelete='cascade')
    isd_code = fields.Char('ISD Code')
    about_us_other = fields.Char('Others')
    mother_office_contact = fields.Char('Mother Office Contact')
    batch_shift = fields.Selection([('morning', 'Morning Batch'), ('clb', 'CLB Batch')],
                               select=True, string='Batch Shift', default='morning')
    khada_sis = fields.Char('KHDA/SIS')
    user_id = fields.Many2one('res.users')
    total_fee_amount = fields.Float(compute='count_total_fee_amount')

    _defaults={
    'test_completed':'no',
    'paid_amount':0.00,
    'user_id': lambda obj, cr, uid, context: uid,
    }
    
    _sql_constraints = [
        ('khada_sis_unique_reg', 'unique(khada_sis)', 'KHDA/SIS must be unique per Student !')
        ]

#     @api.multi
#     def count_total_fee_amount(self):
#         """
#         count total fee amount
#         ------------------------
#         :return:
#         """
#         total_amount = 0.0
#         if self.student_fee_line:
#             for fee_line in self.student_fee_line:
#                 if fee_line.discount > 0.0:
#                     total_amount += (fee_line.amount - (fee_line.amount * fee_line.discount/100))
#                 else:
#                     total_amount += fee_line.amount
#         self.total_fee_amount = total_amount

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
    def state_groups(self, present_ids, domain, **kwargs):
            folded={}
            for e in  self.STATES:
                if e[0] not in present_ids:
                    folded.update({e[0]:1})
            return self.STATES[:], folded

    _group_by_full = {
        'state': state_groups
    }

    @api.multi
    def name_get(self):
        """
        This method is use for get dynamic name of registration object.
        :return:list of touple, touple contain id of record and display name
        """
        res = []
        for record in self:
            _name = '[ ' + str(record.enquiry_no) + ' ]' + str(record.name)
            res.append((record.id,_name))
        return res

    # def _read_group_fill_results(self):
    #     """
    #     The method seems to support grouping using m2o fields only,
    #     while we want to group by a simple status field.
    #     Hence the code below - it replaces simple status values
    #     with (value, name) tuples.
    #     """

    #     if groupby == 'state':
    #         STATES_DICT = dict(self.STATES)
    #         for result in read_group_result:
    #             state = result['state']
    #             result['state'] = (state, STATES_DICT.get(state))
    #     return super(Registration, self)._read_group_fill_results()

    def Validatemobile(self, mobile):
        """
        this method use for mobile number validation.
        ---------------------------------------------
        :param mobile:
        :return:
        """
        # p = re.compile('^\d{8,10}$')
        p = re.compile(r'(^[+0-9]{1,3})*([0-9]{8,10}$)')
        if p.match(mobile) != None:
            return True
        else:
            raise except_orm(_('Warning!'),
                    _("Please Enter Valid Mobile Number: (%s)") % (mobile,))

    def ValidateEmail(self, email):
        """
        validation on Email id
        :param email: email address
        :return:
        """
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
        else:
            raise except_orm(_('Warning!'),
                    _("Please Enter Valid Email Address : (%s)") % (email,))

    @api.onchange('eal')
    def eal_efl(self):
        if self.eal == True:
            self.efl = False

    @api.onchange('efl')
    def efl_eal(self):
        if self.efl == True:
            self.eal = False

    @api.onchange("batch_id") 
    def change_batch_id(self):
        res={}
        course_ids=self.batch_id.course_ids.ids
        return {
                'domain': {
                      'course_id': [('id', 'in', course_ids)],
                    }
                }

    @api.onchange('passport_issue_date','passport_expiry_date')
    def cheque_passport_start(self):
        """
        add validation on passoprt date.
        -------------------------------
        :return:
        """
        if self.passport_issue_date and self.passport_expiry_date:
            s_date = datetime.strptime(self.passport_issue_date,"%Y-%m-%d")
            e_date = datetime.strptime(self.passport_expiry_date,"%Y-%m-%d")
            if s_date > e_date:
                raise except_orm(_('Warning!'),
                    _("Passport Expiry date should be after the Passport issue date !"))

    @api.onchange('visa_issue_date','visa_expiry_date')
    def cheque_visa_start(self):
        """
        add validation on visa date.
        ----------------------------
        :return:
        """
        if self.visa_issue_date and self.visa_expiry_date:
            s_date = datetime.strptime(self.visa_issue_date,"%Y-%m-%d")
            e_date = datetime.strptime(self.visa_expiry_date,"%Y-%m-%d")
            if s_date > e_date:
                raise except_orm(_('Warning!'),
                    _(" visa Expiry date should be after the visa issue date !"))

    @api.multi
    def state_sent(self):
        """
            this method is call from we reject form,
            It change stage from reject to other stage.
            ------------------------------------------
            @param self : object pointer
            @param vals : dictonary
            @return : call super method of create
        """

#       ************************for inquiry state***************************
        if self.state_hide == 'enquiry' and self.state_dropdown == 'enquiry':
            self.state = 'enquiry'
            
        elif self.state_hide == 'enquiry' and self.state_dropdown == 'reg':
            self.validate_enquiry()
            self.state='reg'
          
        elif self.state_hide == 'enquiry' and self.state_dropdown in ['pending','awaiting_fee','waiting_list','done']:
            raise except_orm(_('Warning!'),
                    _("You cant go from Rejected to %s state!") % (self.state_dropdown,))

  #     **************************for reg state****************************
        elif self.state_hide == 'reg' and self.state_dropdown == 'enquiry':
            self.fee_status = 'reg_fee_unpaid'
            self.state = 'enquiry'
          
        elif self.state_hide == 'reg' and self.state_dropdown == 'reg':
            # if self.with_out_reg_fee != True:
            #     self.fee_status = 'reg_fee_unpaid'
            #     self.state = 'enquiry'
            #     self.validate_enquiry()
            # else:
            #     self.fee_status = 'reg_fee_pay'
                self.state='reg'
            
        elif self.state_hide == 'reg' and self.state_dropdown in ['pending','awaiting_fee','waiting_list','done']:
            raise except_orm(_('Warning!'),
                    _("You cant go from Rejected to %s state!") % (self.state_dropdown,))

    #    ***************************for pending state**************************
        elif self.state_hide == 'pending' and self.state_dropdown == 'enquiry':
            self.state = 'enquiry'
        elif self.state_hide == 'pending' and self.state_dropdown == 'reg':
            self.state='reg'
        elif self.state_hide == 'pending' and self.state_dropdown == 'pending':
            self.state='pending'
        elif self.state_hide == 'pending' and self.state_dropdown in ['awaiting_fee','waiting_list','done']:
            raise except_orm(_('Warning!'),
                    _("You cant go from Rejected to %s state!") % (self.state_dropdown,))

        # ***********************for awaiting fee**********************************
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'enquiry':
            self.state = 'enquiry'
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'reg':
            self.state = 'reg'
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'pending':
            self.state='pending'
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'awaiting_fee':
            self.student_id.active=True
            self.state='awaiting_fee'
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'waiting_list':
            self.state='waiting_list'
            
        elif self.state_hide == 'awaiting_fee' and self.state_dropdown == 'done':
             raise except_orm(_('Warning!'),
                    _("You cant go from Rejected to %s state!") % (self.state_dropdown,))

         # ***********************for awaiting List**************************
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'enquiry':
            self.state = 'enquiry'
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'reg':
            self.state='reg'
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'pending':
            self.state='pending'
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'awaiting_fee':
            self.come_to_waitting_fee()
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'waiting_list':
            self.state='waiting_list'
        elif self.state_hide == 'waiting_list' and self.state_dropdown == 'done':
             raise except_orm(_('Warning!'),
                    _("You cant go from Rejected to %s state!") % (self.state_dropdown,))

    @api.model
    def create(self, vals):
        #print '==================create==============='
        """
        this method is overide create method.
        this method also check age age criteria and
        assign unique enquiry number as per enquiry.
        ------------------------------------------
        @param self : object pointer
        @param vals : dictonary
        @return : call super method of create
        """
#         registration_number = ''
#         registration_number = self.env['ir.sequence'].get('registration') or '/'
#         vals['registration_number'] = registration_number
        registration_number = ''
        obj_ir_sequence = self.env['ir.sequence']
        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Registration Number Sequence')])
        if ir_sequence_ids:
            registration_number = obj_ir_sequence.next_by_code('registration')
           # print registration_number,'--------------------------registration_number'
        else:
            sequence_vals = {
                                'name' : 'Registration Number Sequence',
                                'prefix' : 20,
                                'padding' : 7,
                                'number_next_actual' : 1,
                                'number_increment' : 1,
                                'implementation_standard' : 'standard',
                             }
            ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
            registration_number = obj_ir_sequence.next_by_code('ir_sequence_ids')
#         dyanamic_registration_number = random.randrange(1000, 1000000, 1)
        vals['registration_number'] = registration_number
        
        email=vals.get('email',False)
        parent_email = vals.get('parent_email',False)
        name=vals['name'].title()
        vals['name']=name
        parent_name=vals['parent_name'].title()
        vals['parent_name']=parent_name
        if email and not parent_email:
            self.ValidateEmail(vals['email'])
            vals['parent_email']=email

        email=vals.get('parent_email',False)
        if email:
            self.ValidateEmail(vals['parent_email'])    
        email=vals.get('mother_email',False)
        if email:
            self.ValidateEmail(vals['mother_email'])    
        if 'parent_contact' in vals and vals['parent_contact']:
            self.Validatemobile(vals['parent_contact']) 
        if 'mobile' in vals and vals['mobile']:
            self.Validatemobile(vals['mobile'])
            
        if 'entrance_exam_date' in vals and vals['entrance_exam_date']:
            entrance_exam_date = vals['entrance_exam_date']
#             convetred_date = datetime.strptime(vals['entrance_exam_date'], "%Y-%m-%d %H:%M:%S")
#             added_hour_date = str(convetred_date + timedelta(hours=4))
#             date_now = added_hour_date.split(" ")[0]
#             time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
#             vals['dubai_exam_date_formate'] = str(date_now) + " " + str(time_now)

        if 'passport_issue_date' in vals and 'passport_expiry_date' in vals:
            if vals['passport_issue_date'] and vals['passport_expiry_date']:
                s_date = datetime.strptime(vals['passport_issue_date'],"%Y-%m-%d")
                e_date = datetime.strptime(vals['passport_expiry_date'],"%Y-%m-%d")
                if s_date > e_date:
                    raise except_orm(_('Warning!'),
                        _(" Passport Expiry date should be after the Passport issue date !!"))

        if 'visa_issue_date' in vals and 'visa_expiry_date' in vals:
            if vals['visa_issue_date'] and vals['visa_expiry_date']:
                s_date = datetime.strptime(vals['visa_issue_date'],"%Y-%m-%d")
                e_date = datetime.strptime(vals['visa_expiry_date'],"%Y-%m-%d")
                if s_date > e_date:
                    raise except_orm(_('Warning!'),
                        _("Visa Expiry date should be after the Visa issue date !!"))

        if vals['birth_date'] and vals['course_id'] and vals['batch_id']:
            course_brw = self.env['course'].browse(vals['course_id'])
            batch_brw = self.env['batch'].browse(vals['batch_id'])
            date_birth = datetime.strptime(vals['birth_date'],"%Y-%m-%d")
            effective_date= datetime.strptime(batch_brw.effective_date,"%Y-%m-%d")
            min_age=course_brw.min_age
            max_age=course_brw.max_age
            age_dict = self.get_person_age(date_birth,effective_date)
            if age_dict['years'] < min_age or age_dict['years'] > max_age:
                vals['birth_date'] = False
                raise except_orm(_('Warning!'),
                    _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                 (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))
            if (age_dict['years'] == max_age) and (age_dict['months'] > 0 or age_dict['days'] > 0):
                    raise except_orm(_('Warning!'),
                    _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                 (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))
            else:
                sequence_no = self.env['ir.sequence'].get('enquiry.form') or '/'
                batch_id = self.env['batch'].browse(vals['batch_id'])
                course_id = self.env['course'].browse(vals['course_id'])
                start_date = datetime.strptime(batch_id.start_date,"%Y-%m-%d")
                vals['enquiry_no'] = str(start_date.year) + "/" + course_id.name + "/" + sequence_no
                vals['application_date'] = datetime.now()
                fee_structure=self.env['fees.structure'].search([('type','=','reg'),('course_id','=',vals['course_id']),('academic_year_id','=',vals['batch_id'])])
                if not fee_structure:
                    raise except_orm(_('Warning!'),
                        _("please Define Registration fee !"))
                amount=0
                if fee_structure:
                    for each in fee_structure.fee_line_ids:
                        amount=each.amount
                vals['reg_amount']=amount

                c_date_time = str(datetime.now(pytz.timezone('Asia/Dubai'))).split(".")[0]
                date_now = c_date_time.split(" ")[0].split('-')[2] + '-' + c_date_time.split(" ")[0].split('-')[1] +\
                '-' + c_date_time.split(" ")[0].split('-')[0]
                time_now = datetime.strptime(c_date_time.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
                vals['current_date_time'] = date_now + " " + time_now
                res = super(Registration, self).create(vals)

                # sending email
                ir_model_data = self.env['ir.model.data']
                email_server= self.env['ir.mail_server']
                email_sender=email_server.search([])[0]
                template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_validate')[1]
                template_rec = self.env['mail.template'].sudo().browse(template_id)
                template_rec.write({'email_to' : res.parent_email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                template_rec.send_mail(res.id)
                return res

    @api.multi
    def write(self, vals):
        """
        this method is overide write method.
        this method also check age criteria
        ------------------------------------------
        @param self : object pointer
        @param vals : dictonary
        @return : call super method of create
        """

	student_id = False
        if 'student_id' in vals and vals.has_key('student_id'):
            student_id = vals['student_id']
            if self.state == 'awaiting_fee':
                if self.fee_status == 'academy_fee_unpaid':
                    student_id.student_state = 'academic_fee_unpaid'
        else : 
            student_id = self.student_id
        if student_id :
            if 'state' in vals and vals.has_key('state'):
                state = vals['state']
            else :
                state = self.state
                
            if state == 'awaiting_fee' :
                if 'fee_status' in vals and vals.has_key('fee_status'):
                    fee_status = vals['fee_status'] 
                else :
                    fee_status = self.fee_status
                    
                if fee_status == 'academy_fee_unpaid':
                    student_id.student_state = 'academic_fee_unpaid'
                if fee_status == 'academy_fee_partial_pay':
                    student_id.student_state = 'academic_fee_partially_paid'
                if fee_status == 'academy_fee_pay':
                    student_id.student_state = 'academic_fee_paid'
                    
            if state == 'done':
                student_id.student_state = 'confirmed_student'

        # SYNC KHDA/SIS NUMBER TO STUDENT MASTER
        admition_date =  False
        if vals.get('khada_sis') : 
            if not self.student_id :
                raise except_orm(_('Error!'),
                        _("Student Id Mapping Not Found\nContact Odoo Team!"))
            self.env.cr.execute('''update res_partner set khada_sis=%s where id=%s''',(vals.get('khada_sis'),self.student_id.id))

        if 'name' in vals and vals['name']:
            name=vals['name'].title()
            vals['name']=name
        if 'parent_name' in vals and vals['parent_name']:
            parent_name=vals['parent_name'].title()
            vals['parent_name']=parent_name

        if 'parent_contact' in vals and vals['parent_contact']:
            self.Validatemobile(vals['parent_contact'])
        if 'mobile' in vals and vals['mobile']:
            self.Validatemobile(vals['mobile'])
            
        if 'application_date' in vals and vals['application_date']:
            application_date = vals['application_date']
        else :
            application_date = self.application_date
            
        if 'entrance_exam_date' in vals and vals['entrance_exam_date']:
            entrance_exam_date = vals['entrance_exam_date']
#             convetred_date = datetime.strptime(vals['entrance_exam_date'], "%Y-%m-%d %H:%M:%S")
#             added_hour_date = str(convetred_date + timedelta(hours=4))
#             date_now = added_hour_date.split(" ")[0]
#             time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
#             vals['dubai_exam_date_formate'] = str(date_now) + " " + str(time_now)
        else :
            entrance_exam_date = self.entrance_exam_date

        if 'admission_date' in vals and vals['admission_date']:
            admition_date=datetime.strptime(vals['admission_date'], "%Y-%m-%d")
        elif self.admission_date :
            admition_date=datetime.strptime(self.admission_date, "%Y-%m-%d")
        if self.batch_id and self.batch_id.start_date :
            year_start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d")
        if application_date :
            application_date = datetime.strptime(application_date,"%Y-%m-%d %H:%M:%S").date()
            app_date=datetime.strftime(application_date,"%Y-%m-%d")
            app_date=datetime.strptime(app_date,"%Y-%m-%d")
        if entrance_exam_date :
            entrance_date = datetime.strptime(entrance_exam_date,"%Y-%m-%d %H:%M:%S").date()
            ent_date=datetime.strftime(entrance_date,"%Y-%m-%d")
            ent_date=datetime.strptime(ent_date,"%Y-%m-%d")
            
            
            if admition_date and year_start_date :
                if admition_date < year_start_date:
                    raise except_orm(_('Warning!'),
                            _("Admission Date should be Equal to or After Start of Academic year!"))
            if admition_date and app_date:
                if admition_date < app_date:
                    raise except_orm(_('Warning!'),
                            _("Admission Date should be Equal to or After Application Date!"))
            if admition_date and ent_date:
                if admition_date < ent_date:
                    raise except_orm(_('Warning!'),
                            _("Admission Date should be Equal to or After Entrance exam date!"))

#         if 'entrance_exam_date' in vals and vals['entrance_exam_date'] :
#             #comp_date= datetime.strptime(vals['entrance_exam_date'].split(' ')[0], "%Y-%m-%d")
#             # ODOO DATE + 5:30 HOURS # NEW LOGIC BY SHASHANK
#             comp_date= datetime.strptime(vals['entrance_exam_date'], "%Y-%m-%d %H:%M:%S")+timedelta(hours=5,minutes=30)
#                         
#             date_status = self.compare_with_current_date(comp_date)
#             if date_status == False:
#                 raise except_orm(_('Warning!'),
#                         _("Entrance Exam Date should be current date or future date"))
#             convetred_date = datetime.strptime(vals['entrance_exam_date'], "%Y-%m-%d %H:%M:%S")
#             added_hour_date = str(convetred_date + timedelta(hours=4))
#             date_now = added_hour_date.split(" ")[0]
#             time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
#             date_now = str(date_now).split('-')[2]+'-'+str(date_now).split('-')[1]+'-'+str(date_now).split('-')[0]
#             vals['dubai_exam_date_formate'] = str(date_now) + " " + str(time_now)

        email=vals.get('email',False)
        if email:
            self.ValidateEmail(vals['email'])
            self.parent_email=email

        email=vals.get('parent_email',False)
        if email:
            self.ValidateEmail(vals['parent_email'])    
        email=vals.get('mother_email',False)
        if email:
            self.ValidateEmail(vals['mother_email'])

#         if 'entrance_exam_date' in vals and vals['entrance_exam_date']:
#             convetred_date = datetime.strptime(vals['entrance_exam_date'], "%Y-%m-%d %H:%M:%S")
#             added_hour_date = str(convetred_date + timedelta(hours=4))
#             date_now = added_hour_date.split(" ")[0]
#             time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
#             vals['dubai_exam_date_formate'] = str(date_now) + " " + str(time_now)

        if 'passport_issue_date' in vals and 'passport_expiry_date' in vals:
            if vals['passport_issue_date'] and vals['passport_expiry_date']:
                s_date = datetime.strptime(vals['passport_issue_date'],"%Y-%m-%d")
                e_date = datetime.strptime(vals['passport_expiry_date'],"%Y-%m-%d")
                if s_date > e_date:
                    raise except_orm(_('Warning!'),
                        _(" Passport Expiry date should be after the Passport issue date !!"))

        if 'visa_issue_date' in vals and 'visa_expiry_date' in vals:
            if vals['visa_issue_date'] and vals['visa_expiry_date']:
                s_date = datetime.strptime(vals['visa_issue_date'],"%Y-%m-%d")
                e_date = datetime.strptime(vals['visa_expiry_date'],"%Y-%m-%d")
                if s_date > e_date:
                    raise except_orm(_('Warning!'),
                        _("Visa Expiry date should be after the Visa issue date !!"))

        if 'birth_date' in vals or 'course_id' in vals or 'batch_id' in vals:
            if 'birth_date' not in vals:
                vals['birth_date']=self.birth_date
            if 'course_id' not in vals:  
                vals['course_id']=self.course_id.id
            if 'batch_id'not in vals:
                vals['batch_id']=self.batch_id.id

            if vals['birth_date'] and vals['course_id'] and vals['batch_id']:
                course_brw = self.env['course'].browse(vals['course_id'])
                batch_brw = self.env['batch'].browse(vals['batch_id'])

                date_birth = datetime.strptime(vals['birth_date'],"%Y-%m-%d")
                effective_date= datetime.strptime(batch_brw.effective_date,"%Y-%m-%d")   
                min_age=course_brw.min_age
                max_age=course_brw.max_age

                age_dict = self.get_person_age(date_birth,effective_date)

                if age_dict['years'] < min_age or age_dict['years'] > max_age:
                    self.birth_date = False
                    raise except_orm(_('Warning!'),
                        _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                     (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))
                if age_dict['years'] == max_age:
                    if age_dict['months'] > 0 or age_dict['days'] > 0:
                        raise except_orm(_('Warning!'),
                        _("Student age must be in between %s and %s years! \n Now your age is %s year, %s month, %s days.") %
                                     (min_age,max_age,age_dict['years'],age_dict['months'],age_dict['days']))

        return super(Registration, self).write(vals)

    @api.multi
    def mannual_fee_wizard(self):
        
        view = self.env.ref('edsys_edu.show_fee_wiz_view')
        return {
            'name': _('Manual Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'show.fee.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }

    @api.multi
    def validate_enquiry(self):
        """
        this method is validate enquiry of
        student, also define to student how many
        registration fee pay for registration and
        state change from enqiry to registration.
        ------------------------------------------
        @param self : object pointer
        """
        if self.with_out_reg_fee != True:
            if self.batch_id and self.course_id:
                fee_line_obj = self.env['fees.structure']
                fee_data = {}
                fee_lst = []
                for fee_criteria in fee_line_obj.search([
                    ('academic_year_id','=',self.batch_id.id),
                    ('course_id','=',self.course_id.id),
                    ('type','=','reg')
                ]):
                    for fee_line in fee_criteria.fee_line_ids:
                        if fee_line.fee_pay_type.name == 'one':
                            fee_data = \
                                {
                                    'name' : fee_line.name,
                                    'amount' : fee_line.amount,
                                    'type' : fee_line.type,
                                    'fee_pay_type' : fee_line.fee_pay_type.id,
                                    'reg_id':self.id
                                }
                            fee_lst.append((0,0,fee_data))
                if len(fee_lst) == 0:
                    raise except_orm(_('Warning!'),
                    _(" Registration Fee is Not Define !"))
                else:
                    self.reg_fee_line = fee_lst
                    self.send_payfort_reg_pay_link()
                    self.state = 'reg'
                    self.fee_status = 'reg_fee_unpaid'
                    return True
        else:
            self.state = 'reg'
            self.fee_status = 'reg_fee_pay'
        raise except_orm(_("Warning!"), _('stop'))
    @api.multi
    def reg_to_decision_pending(self):
        """
        this method is define fee pay to
        student for admition in school also change
        stage registration to decisition pending.
        ------------------------------------------
        @param self : object pointer
        """
        if not self.entrance_exam_date:
            raise except_orm(_('Warning!'),
                    _("Please Fill The Entrance Exam Date !"))
        flag="0"
        for each in self.state_hide_ids:
            if each.state_name=='pending' or each.state_name=='awaiting_fee' or each.state_name=='waiting_list':
                flag="1"
        if flag=="1":
            self.state = 'pending'
            return True
        else:
            mail_obj=self.env['mail.mail']
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_exam_email')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
            template_rec.send_mail(self.id, force_send=True)
            self.state = 'pending'
            self.fee_status = 'academy_fee_unpaid'
            return True
            
    @api.multi
    def send_mail_for_extra_form_fillup(self):
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_confirmation')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
            template_rec.send_mail(self.id)
            self.add_form_link='successfully send to Student'
        
    @api.multi
    def confirm_payment(self):
        if self.add_form_link != '' and self.add_form_filled==True:
            self.state='done'
        else:
            raise except_orm(_('Warning!'),
                    _(" Additional Form is not filled up !"))
        return True

    @api.multi
    def decision_to_waitting_list(self):
#         """
#         this method change state from decisition
#          pending to waiting list.
#         ------------------------------------------
#         @param self : object pointer
#         """
        if self.state_hide=='' or self.state_hide=='enquiry' or self.state_hide=='reg' or self.state_hide=='pending': 
#             mail_obj=self.env['mail.mail']
#             email_server=self.env['ir.mail_server']
#             email_sender=email_server.search([])
#             ir_model_data = self.env['ir.model.data']
#             template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_waiting_list')[1]
#             template_rec = self.env['email.template'].browse(template_id)
#             template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
#             template_rec.send_mail(self.id, force_send=True)
            self.state = 'waiting_list'
        else:
#             email_server=self.env['ir.mail_server']
#             email_sender=email_server.search([])
#             ir_model_data = self.env['ir.model.data']
#             template_id = ir_model_data.get_object_reference('edsys_edu',
#                                                              'email_template_student_decisition_to_waiting_list')[1]
#             template_rec = self.env['email.template'].browse(template_id)
#             template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
#             template_rec.send_mail(self.id, force_send=True)
            self.state = 'waiting_list'

    @api.multi
    def waitting_fee_to_waitting_list(self):
        """
        this method change state from waiting fee
        to waiting list.
        ------------------------------------------
        @param self : object pointer
        """
        self.state = 'waiting_list'

    @api.multi
    def come_to_waitting_fee(self):
        """
        this method create new student and itd parent,
        student duplicate not created, check with email.
        parent duplicate nt created, check with email.
        maintain parent child.
        update in account journal entry for reg fee.
        ------------------------------------------
        @param self : object pointer
        """
        flag="0"
        for each in self.state_hide_ids:
            if each.state_name=='awaiting_fee':
                flag="1"
        if flag=="1":
            self.state = 'awaiting_fee'

            self.student_id.active=True
            
            return True
        else:
#        if self.state_hide=='' or self.state_hide=='enquiry' or self.state_hide=='reg' or self.state_hide=='pending' or self.state_hide=='waiting_list':

            if self.batch_id and self.course_id:
                fee_line_obj = self.env['fees.structure']
                fee_data = {}
                fee_lst = []
                for fee_criteria in fee_line_obj.search([
                    ('academic_year_id','=',self.batch_id.id),
                    ('course_id','=',self.course_id.id),
                    ('type','=','academic'),
                ]):
                    for fee_line in fee_criteria.fee_line_ids:
                        fee_data = \
                            {
                                'name' : fee_line.name,
                                'amount' : int(fee_line.amount),
                                'type' : fee_line.type,
                                'fee_pay_type' : fee_line.fee_pay_type.id,
                                'reg_form_id':self.id,
                                'sequence': fee_line.sequence,
                            }
                        fee_lst.append((0,0,fee_data))

                if len(fee_lst) == 0:
                    raise except_orm(_('Warning!'),
                    _(" Fee Structure is Not Define !"))
                else:
                    for std_fee_line in self.student_fee_line:
                        self.student_fee_line = [(2,std_fee_line.id)]
                    self.student_fee_line = fee_lst
            student_parent_obj = self.env['res.partner']
            account_obj = self.env['account.account']
            student_receive_acc = account_obj.search([('code','=','110410')])
            student_payable_acc = account_obj.search([('code','=','2010001')])
            student_advance_acc = account_obj.search([('code','=','210601')])
            if not student_receive_acc.id:
                raise except_orm(_("Warning!"), _('Please define account receivable for student'))
            if not student_payable_acc.id:
                raise except_orm(_("Warning!"), _('Please define account payable for student'))
            if not student_advance_acc.id:
                raise except_orm(_("Warning!"), _('Please define Advance Account for Student/Parent'))
            exist_parent = ''
            for parent in student_parent_obj.search([('is_parent','=',True),('parents_email','=',self.parent_email)]):
                exist_parent = parent
            if exist_parent and exist_parent.id:
                stud_parent_id = exist_parent
            else:
                parent_data = \
                    {
                        'parent1_id' : self.env['ir.sequence'].get('partner.form'),
                        'name' : self.parent_name or "",
                        'is_parent' : True,
                        'street' : self.street or "",
                        'street2' : self.street2 or "",
                        'city' : self.city or "",
                        'state_id' : self.state_id.id or "",
                        'zip' : self.zip or "",
                        'country_id' : self.country_id.id or "",
                        'mother_name' : self.mother_name or "",
                        'parents_email' : self.parent_email or "",
                        'mother_email' : self.mother_email or "",
                        'parent_profession' : self.parent_profession or "",
                        'mother_profession' : self.mother_profession or "",
                        'parent_contact' : self.parent_contact or "",
                        'mother_contact' : self.mother_contact or "",
                        'property_account_customer_advance':student_advance_acc.id,
                        'property_account_receivable_id':student_receive_acc.id,
                        'property_account_payable':student_payable_acc.id,
                        'isd_code' : self.isd_code,
                    }
                stud_parent_id = student_parent_obj.create(parent_data)

            exist_student= student_parent_obj.search([('is_parent','=',False),('reg_no','=',self.enquiry_no)])
            if exist_student.id:
                raise except_orm(_("Warning!"), _('Student already exist with same Enquiry No'))
            else:
                student_date = \
                    {
			'first_acd_year_of_child' : self.first_acd_year_of_child.id,
                        'parents1_id' : stud_parent_id.id or "",
                        'name' : self.name or "",
                        'image' : self.image or "",
                        'middle_name' : self.middle_name or "",
                        'last_name' : self.last_name or "",
                        'is_parent' : False,
                        'is_student': True,
                        'admission_date' : self.admission_date or False,
                        'nationality' : self.nationality_id.id or "",
                        'batch_id' : self.batch_id.id or "",
                        'course_id' : self.course_id.id or "",
                        # 'standard_id' : self.standard_id.id or "",
                        # 'category_id' : self.category_id.id or "",
                        'gender' : self.gender or "",
                        'emirati' : self.emirati or "",
                        'arab' : self.arab or "",
                        'religion_id' : self.religion_id.id or "",
                        'birth_date' : self.birth_date or False,
                        'birth_place' : self.birth_place or "",
                        'birth_country' : self.birth_country.id or "",
                        'emirates_id' : self.emirates_id or "",
                        'passport_no' : self.passport_no or "",
                        'title' : self.title.id or "",
                        'date_of_joining' : date.today() or False,
                        'student_section_id' : self.student_section_id.id or "",
                        'place_of_issue' : self.place_of_issue.id or "",
                        'passport_issue_date' : self.passport_issue_date or False,
                        'passport_expiry_date' : self.passport_expiry_date or False,
                        'visa_no' : self.visa_no or "",
                        'street' : self.street or "",
                        'street2' : self.street2 or "",
                        'city' : self.city or "",
                        'state_id' : self.state_id.id or "",
                        'zip' : self.zip or "",
                        'country_id' : self.country_id.id or "",
                        'phone' : self.phone or "",
                        'mobile' : self.mobile or "",
                        'email' : self.email or "",
                        'prev_institute' : self.prev_institute or "",
                    #     'prev_course' : self.prev_course or "",
                    #     'prev_result' : self.prev_result or "",
                        'family_business' : self.family_business or "",
                        'family_income' : self.family_income or "",
                    #     'place_of_issue' : self.place_of_issue or "",
                        'passport_expiry_date' : self.passport_expiry_date or False,
                        'visa_issue_date' : self.visa_issue_date or False,
                        'visa_expiry_date' : self.visa_expiry_date or False,
                        'lang_id' : self.lang_id.id or "",
                        'other_lang_id' : self.other_lang_id.id or "",
                        'emergency_contact' : self.emergency_contact or "",
                        'prev_institute' : self.prev_institute or "",
                        'prev_grade' : self.prev_grade or "",
                        'last_attendance' : self.last_attendance or False,
                        'prev_academic_year' : self.prev_academic_year.id or "",
                        'prev_academic_city' : self.prev_academic_city or "",
                        'prev_academic_country' : self.prev_academic_country.id or "",
                        'tranfer_reason' : self.tranfer_reason or "",
                        'remarks' : self.remarks or "",
                        'about_us' : self.about_us or "",
                        'curriculum' : self.curriculum or "",
                        't_c_number' : self.t_c_number or "",
                        'blood_group' : self.blood_group or "",
                        's_height' : self.s_height or "",
                        's_width' : self.s_width or "",
                        'child_allergic' : self.child_allergic or "",
                        'w_allergic' : self.w_allergic or "",
                        'w_reaction' : self.w_reaction or "",
                        'w_treatment' : self.w_treatment or "",
                        'under_medication' : self.under_medication or "",
                        'w_medication_mention' : self.w_medication_mention or "",
                        'w_treatment_mention' : self.w_treatment_mention or "",
                        'transport_type' : self.transport_type or "",
                        'bus_no' : self.bus_no or "",
                        'pick_up' : self.pick_up or "",
                        'droup_off_pick' : self.droup_off_pick or "",
                        # 'student_fee_line':[(6,0,self.student_fee_line.ids)],
                        'reg_no':self.enquiry_no,
                        'class_id':self.course_id.id,
                        'year_id':self.batch_id.id,
                        'property_account_customer_advance':student_advance_acc.id,
                        'property_account_receivable_id':student_receive_acc.id,
                        'property_account_payable':student_payable_acc.id,
                        'isd_code' : self.isd_code,
                        'about_us_other' : self.about_us_other,
                        'stud_batch_shift' : self.batch_shift or "",
                    }

                std_create = student_parent_obj.create(student_date)
                self.student_id=std_create.id

                # student Fee structure
                if std_create.id:
                    for fee_of_stud in self.student_fee_line:
                        fee_of_stud.stud_id = std_create.id
                    #for sibling_rec in self.sibling_ids:
                        #sibling_rec.student_id = std_create.id

                account_move_obj = self.env['account.move']
                for acc_move in account_move_obj.search([('ref','=',self.enquiry_no)]):
                    for jonral in acc_move.line_ids:
                        jonral.write({'partner_id':std_create.id})
                mail_obj=self.env['mail.mail']
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_awaitting_fee')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                template_rec.send_mail(self.id, force_send=True)
                self.state = 'awaiting_fee'


    @api.multi
    def create_pdc_detail(self,add_jounral,amount,bank_name=False,chk_num=False,sdate=False,exdate=False,party_name=False):
        pdc_obj = self.env['pdc.detail']
        vals={
            'name':chk_num,
            'amount':amount,
            'journal_id':add_jounral.journal_id and add_jounral.journal_id.id or False,
            'journal_entry_id':add_jounral.id,
            'cheque_start_date':sdate,
            'cheque_expiry_date':exdate,
            'bank_name':bank_name,
            'party_name':party_name,
            'period_id':add_jounral.period_id and add_jounral.period_id.id or False ,
            'state':'draft',
            'chk_fee_type':'reg',
            'enquiry_no':self.enquiry_no
                }

        pdc_obj.create(vals)
        return True

    @api.multi
    def reg_pay_manually(self,journal_id,bank_name=False,chk_num=False,sdate=False,exdate=False,cheque_pay=False,party_name=False):
        """
        this method used when student pay registration fee.
        the fee amount get from fee structure.
        fee entry define in account journal entry.
        ------------------------------------------
        @param self : object pointer
        """

        if self.state == 'reg':
            jounral_dict1 = {}
            jounral_dict2 = {}
            account_move_obj = self.env['account.move']
            account_id = self.env['account.account'].search([('code', '=', '402050')], limit=1)
        
            if not account_id.id:
                raise except_orm(_('Warning!'),
                    _("Registration Fees account not found."))

            exist_stu_fee = account_move_obj.search_count([('ref', '=', self.enquiry_no)])
            if exist_stu_fee == 0:
                amount = 0.0
                for student_fee_rec in self.reg_fee_line:
                    if student_fee_rec.amount:
                        amount = student_fee_rec.amount
                        full_name = str(self.name or '') + ' ' +  str(self.middle_name or '') + ' ' + str(self.last_name or '')
                        jounral_dict1.update({'name':full_name, 'debit':student_fee_rec.amount, 'credit':0.00,'account_id':account_id.id})
                        jounral_dict2.update({'name':full_name, 'credit':student_fee_rec.amount, 'debit':0.00, 'account_id':account_id.id})
                jounral_data = {'journal_id':journal_id,
                                'line_ids':[(0,0,jounral_dict1),(0,0,jounral_dict2)],
                                'ref':self.enquiry_no,
                                'cheque_pay':cheque_pay,
                                'bank_name':bank_name}
                if sdate != False and exdate != False:
                    jounral_data.update({
                        'cheque_date': sdate,
                        'cheque_expiry_date': exdate,
                    })
                    
                add_jounral = account_move_obj.create(jounral_data)
                
                if add_jounral.id:
                    self.fee_status = 'reg_fee_pay'
                    self.trx_date = datetime.now()
                    # if add_jounral.journal_id.is_cheque == False:
                    #     add_jounral.button_validate()
                    self.reg_fee_receipt = add_jounral.id
                if amount > 0.0 and add_jounral.journal_id.is_cheque :
                    self.create_pdc_detail(add_jounral,amount,bank_name=bank_name,chk_num=chk_num,sdate=sdate,exdate=exdate,party_name=party_name)                    
            else:
                self.fee_status = 'reg_fee_pay'
                self.trx_date = datetime.now()
            mail_obj = self.env['mail.mail']
            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_registration_receipt')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
            template_rec.send_mail(self.id, force_send=True)
        return True

    @api.model
    def count_month(self,s_date,e_date):
        """
        this method used to count the number of
        month in between two date.
        ------------------------------------------
        @param self : object pointer
        @param s_date : starting date
        @param e_date : ending date
        @return : it return integer number
        """
        s_year = int(s_date.split('-')[0])
        s_month = int(s_date.split('-')[1])
        s_day = int(s_date.split('-')[2])
        e_year = int(e_date.split('-')[0])
        e_month = int(e_date.split('-')[1])
        e_day = int(e_date.split('-')[2])

        def diff_month(d1, d2):
            return (d1.year - d2.year)*12 + d1.month - d2.month

        return diff_month(datetime(e_year,e_month,e_day), datetime(s_year,s_month,s_day))

    @api.model
    def student_fee_detail_update_dict(self,fee_pay_type,cal_amount,total_amount,discount_amount):
        student_detail ={
            'fee_pay_type' : fee_pay_type,
            'cal_amount' : cal_amount,
            'total_amount' : total_amount,
            'discount_amount' : discount_amount,
            }
        return student_detail

    @api.model
    def invoice_dict_create(self,product_id,account_id,name,quantity,price_unit,rem_amount,parent_id,priority):
        invoice_line_data = {
            'product_id' : product_id,
            'account_id' : account_id,
            'name' : name,
            'quantity' : quantity,
            'price_unit' : price_unit,
            'rem_amount': rem_amount,
            'parent_id' : parent_id,
            'priority' : priority,
            }
        return invoice_line_data

    @api.model
    def acd_manually_fee_calculation(self,cal_type,pay_amount,discount,month_diff=0,no_of_month=0):
        if pay_amount == 0.00:
                raise except_orm(_("Warning!"), _("You can't define Fee with 0.00 amount."))
        else:
            dis_amount = 0.00
            month_amount = 0
            if cal_type in ['year','one']:
                if discount > 0.00:
                    dis_amount = (pay_amount * discount) / 100
                return pay_amount, dis_amount
            elif cal_type == 'half_year':
                half_amount = 0.00
                if month_diff > 0 and no_of_month > 0:
                    par_month_amount = pay_amount / month_diff
                    half_amount = par_month_amount * no_of_month
                if discount > 0.00 and half_amount > 0.00:
                    dis_amount = (half_amount * discount) / 100
                return half_amount,dis_amount
            elif cal_type == 'quater':
                if month_diff >= 3:
                    qtr_amount = pay_amount / (month_diff/3)
                else:
                    qtr_amount = pay_amount
                if discount > 0.00:
                    dis_amount = (qtr_amount * discount) / 100
                return qtr_amount, dis_amount
            elif cal_type == 'alt_month':
                if month_diff >= 2:
                    alt_amount = pay_amount / (month_diff/2)
                else:
                    alt_amount = pay_amount
                if discount > 0.00:
                    dis_amount = (alt_amount * discount) / 100
                return alt_amount, dis_amount
            elif cal_type == 'month':
                if pay_amount > 0:
                    month_amount = pay_amount / (month_diff)
                if discount > 0.00:
                    dis_amount = (month_amount * discount) / 100
                return month_amount, dis_amount
            elif cal_type == 'term':
                term_amount = pay_amount / (month_diff)
                if no_of_month > 0:
                    term_amount = term_amount * no_of_month
                if discount > 0.00:
                    dis_amount = (term_amount * discount) / 100
                return term_amount, dis_amount
        return cal_type

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

    @api.multi
    def reg_pay_acd_manually(self,flag):
        """
        this method used when student pay Academy fee manualy.
        after fee pay fee status will be changed as
        academy fee unpaid to fee paid.
        ------------------------------------------
        @param self : object pointer
        """
        if self.fee_structure_confirm!=True:
             raise except_orm(_("Warning!"), _('Please Confirm the fee structure before paying fee'))
        stud_payble_obj = self.env['student.payble.fee']
        paid_term_obj=self.env['paid.term.history']
        invoice_obj = self.env['account.invoice']
        fee_payment_line_obj = self.env['fee.payment']
        month_diff = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),('leave_month','=',False)])
        joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
        start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d").date()
        get_unpaid_diff = self.get_person_age(start_date,joining_date)
        leave_month = []
        for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),('leave_month','=',True)]):
            leave_month.append((int(l_month.name),int(l_month.year)))
        month_in_stj = self.months_between(start_date,joining_date)
        unpaid_month = 0
        if get_unpaid_diff.get('months') > 0:
            unpaid_month = get_unpaid_diff.get('months')
            if len(month_in_stj) > 0 and len(leave_month) > 0:
                for leave_month_year in leave_month:
                        if leave_month_year in month_in_stj:
                            unpaid_month -= 1
        month_diff -= unpaid_month
        # month_rec = self.batch_id.month_ids[0]
        month_rec = self.batch_id.month_ids.search([('name','=',joining_date.month),('year','=',str(joining_date.year))],limit=1)
        if not month_rec.id:
            raise except_orm(_("Warning!"), _('Month not found'))

        if self.student_id:
            fee_line_lst = []
            fee_pay_line_val = {}
            invoice_dic = {}
            total_amount = 0.00
            total_discount = 0.00
            for fee_structure_rec in self.student_id.student_fee_line:
                dis_amount = 0.00
                # print ('ffffffffffffffffff',fee_structure_rec.name.name)
                if not fee_structure_rec.name.property_account_income_id.id:
                    raise except_orm(_("Warning!"), _('Please define property income account for fees %s') % fee_structure_rec.name.name)
                val = {}
                val.update({
                    'name': fee_structure_rec.name.id,
                    'student_id': self.student_id.id,
                    'month_id' : month_rec.id,
                    })
                if fee_structure_rec.name.is_admission_fee == True:
                    adm_amount = fee_structure_rec.amount or 0.00
                    on_discount = fee_structure_rec.discount or 0.00
                    admision_pay,dis_amount = self.acd_manually_fee_calculation(cal_type = fee_structure_rec.fee_pay_type.name,
                                                                             pay_amount=adm_amount,
                                                                             discount=on_discount)

                    student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                           cal_amount=admision_pay,
                                                                           total_amount=fee_structure_rec.amount,
                                                                           discount_amount=dis_amount)
                    val.update(student_fee_dict)
                    total_amount += admision_pay
                    invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                 account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                 name=fee_structure_rec.name.name,
                                                                 quantity=1.00,
                                                                 price_unit=round(admision_pay,2),
                                                                 rem_amount=round(admision_pay,2),
                                                                 parent_id=self.student_id.parents1_id.id,
                                                                 priority=fee_structure_rec.sequence)
                    fee_line_lst.append((0,0,invoice_line_dict))
                else:
                    if fee_structure_rec.fee_pay_type.name == 'year' or fee_structure_rec.fee_pay_type.name == 'one':
                        year_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        yeary_pay,dis_amount = self.acd_manually_fee_calculation(cal_type=fee_structure_rec.fee_pay_type.name,
                                                                                 pay_amount=year_amount,
                                                                                 discount=on_discount)

                        total_discount += dis_amount
                        student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                               cal_amount=yeary_pay,
                                                                               total_amount=fee_structure_rec.amount,
                                                                               discount_amount=dis_amount)
                        val.update(student_fee_dict)

                        total_amount += yeary_pay
                        invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                     account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                     name=fee_structure_rec.name.name,
                                                                     quantity=1.00,
                                                                     price_unit=round(yeary_pay,2),
                                                                     rem_amount=round(yeary_pay,2),
                                                                     parent_id=self.student_id.parents1_id.id,
                                                                     priority=fee_structure_rec.sequence)
                        fee_line_lst.append((0,0,invoice_line_dict))
                    elif fee_structure_rec.fee_pay_type.name == 'half_year':
                        is_next_half_year = False
                        joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
                        batch_start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d").date()
                        total_month = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),
                                                                         ('leave_month','=',False)])
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
                                is_next_half_year = True
                            elif second_date_of_half <= joining_date < last_date_of_half:
                                month_count = self.months_between(joining_date,last_date_of_half)
                        leave_month = []
                        for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),
                                                                       ('leave_month','=',True)]):
                            leave_month.append((int(l_month.name),int(l_month.year)))
                        count_month = []
                        if month_count :
                            for month_year in month_count:
                                if month_year not in leave_month:
                                    count_month.append(month_year)

                        half_year_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        half_pay,dis_amount = self.acd_manually_fee_calculation(cal_type='half_year',
                                                                                pay_amount=half_year_amount,
                                                                                discount=on_discount,
                                                                                month_diff=total_month_rec,
                                                                                no_of_month=len(count_month))
                        student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                               cal_amount=half_pay,
                                                                               total_amount=half_year_amount,
                                                                               discount_amount=dis_amount)
                        total_discount += dis_amount
                        student_fee_dict.update({'is_next_half_year': is_next_half_year})
                        val.update(student_fee_dict)
                        total_amount += half_pay
                        invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                     account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                     name=fee_structure_rec.name.name,
                                                                     quantity=1.00,
                                                                     price_unit=round(half_pay,2),
                                                                     rem_amount=round(half_pay,2),
                                                                     parent_id=self.student_id.parents1_id.id,
                                                                     priority=fee_structure_rec.sequence)

                        fee_line_lst.append((0,0,invoice_line_dict))
                    elif fee_structure_rec.fee_pay_type.name == 'quater':
                        quter_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        quaterly_pay,dis_amount = self.acd_manually_fee_calculation(cal_type='quater',
                                                                                    pay_amount=quter_amount,
                                                                                    discount=on_discount,
                                                                                    month_diff=month_diff)
                        total_discount += dis_amount
                        student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                               cal_amount=quaterly_pay,
                                                                               total_amount=quter_amount,
                                                                               discount_amount=dis_amount)
                        val.update(student_fee_dict)
                        total_amount += quaterly_pay
                        invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                     account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                     name=fee_structure_rec.name.name,
                                                                     quantity=1.00,
                                                                     price_unit=round(quaterly_pay,2),
                                                                     rem_amount=round(quaterly_pay,2),
                                                                     parent_id=self.student_id.parents1_id.id,
                                                                     priority=fee_structure_rec.sequence)
                        fee_line_lst.append((0,0,invoice_line_dict))
                    elif fee_structure_rec.fee_pay_type.name == 'alt_month':
                        alt_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        alterly_pay,dis_amount = self.acd_manually_fee_calculation(cal_type='alt_month',
                                                                                    pay_amount=alt_amount,
                                                                                    discount=on_discount,
                                                                                    month_diff=month_diff)
                        total_discount += dis_amount
                        student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                               cal_amount=alterly_pay,
                                                                               total_amount=alt_amount,
                                                                               discount_amount=dis_amount)
                        val.update(student_fee_dict)

                        total_amount += alterly_pay

                        invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                     account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                     name=fee_structure_rec.name.name,
                                                                     quantity=1.00,
                                                                     price_unit=round(alterly_pay,2),
                                                                     rem_amount=round(alterly_pay,2),
                                                                     parent_id=self.student_id.parents1_id.id,
                                                                     priority=fee_structure_rec.sequence)
                        fee_line_lst.append((0,0,invoice_line_dict))
                    elif fee_structure_rec.fee_pay_type.name == 'month':
                        month_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        monthly_pay,dis_amount = self.acd_manually_fee_calculation(cal_type='month',
                                                                                   pay_amount=month_amount,
                                                                                   discount=on_discount,
                                                                                   month_diff=month_diff)

                        total_discount += dis_amount
                        student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                               cal_amount=monthly_pay,
                                                                               total_amount=month_amount,
                                                                               discount_amount=dis_amount)
                        val.update(student_fee_dict)

                        total_amount += monthly_pay

                        invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                     account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                     name=fee_structure_rec.name.name,
                                                                     quantity=1.00,
                                                                     price_unit=round(monthly_pay,2),
                                                                     rem_amount=round(monthly_pay,2),
                                                                     parent_id=self.student_id.parents1_id.id,
                                                                     priority=fee_structure_rec.sequence)

                        fee_line_lst.append((0,0,invoice_line_dict))

                    elif fee_structure_rec.fee_pay_type.name == 'term':
                        terms = self.env['acd.term'].search([('batch_id','=',self.batch_id.id)])
                        if len(terms) == 0:
                            raise except_orm(_("Warning!"), _('Please define Term for Academic year %s !')%(self.batch_id.name))
                        term_amount = fee_structure_rec.amount or 0.00
                        on_discount = fee_structure_rec.discount or 0.00
                        term_count = 0
                        c_term = False
                        next_term = False
                        for terms_rec in terms:
                            if self.admission_date and terms_rec.start_date and terms_rec.end_date:
                                joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
                                term_sdate = datetime.strptime(terms_rec.start_date,"%Y-%m-%d").date()
                                term_edate = datetime.strptime(terms_rec.end_date,"%Y-%m-%d").date()
                                if term_sdate <= joining_date < term_edate:
                                    no_of_month = self.months_between(term_sdate,term_edate)
                                    total_month = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),('leave_month','=',False)])
                                    unpaid_month_dic = self.get_person_age(term_sdate,joining_date)
                                    month_diff_term = total_month - unpaid_month_dic.get('months') or 0
                                    term_pay, dis_amount = self.acd_manually_fee_calculation(cal_type='term',
                                                                                     pay_amount=term_amount,
                                                                                     discount=on_discount,
                                                                                     month_diff=month_diff_term,
                                                                                     no_of_month=len(no_of_month))
                                    c_term = terms_rec
                                    unpaid_month_dic = self.get_person_age(term_sdate,joining_date)
                                    total_month_dic = self.get_person_age(term_sdate,term_edate)
                                    if unpaid_month_dic.get('months') > 0 and total_month_dic.get('months') > 0:
                                        unpaid_month = unpaid_month_dic.get('months')
                                        paid_month = len(no_of_month) - unpaid_month
                                        term_pay = (fee_structure_rec.amount / month_diff_term) * paid_month
                                        if on_discount > 0.00:
                                            dis_amount = (term_pay * on_discount) / 100
                                else:
                                    term_count +=1
                        # if term_count > 0:
                        #     if term_count < len(terms)-1:
                        #         next_term = terms[term_count+1]
                        #     else:
                        #         next_term = False
                        if c_term:
                            for_next_term = self.env['acd.term'].search([('id', '>', c_term.id),
                                                                         ('seq','>',c_term.seq),
                                                                         ('batch_id','=',self.batch_id.id)])
                            for term_rec in for_next_term:
                                if term_rec.seq == c_term.seq+1:
                                    next_term = term_rec
                        term_pay = round(term_pay,2)
                        val.update({
                            'fee_pay_type' : fee_structure_rec.fee_pay_type.id,
                            'cal_amount' : term_pay,
                            'rem_amount' : fee_structure_rec.amount - term_pay,
                            'total_amount' : fee_structure_rec.amount,
                            'discount_amount' : dis_amount,
                        })
                        if next_term:
                            val.update({
                                'next_term': next_term.id or '',
                        })

                        total_amount += term_pay
                        if term_pay > 0.00:
                            invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.id,
                                                                         account_id=fee_structure_rec.name.property_account_income_id.id,
                                                                         name=fee_structure_rec.name.name,
                                                                         quantity=1.00,
                                                                         price_unit=round(term_pay,2),
                                                                         rem_amount=round(term_pay,2),
                                                                         parent_id=self.student_id.parents1_id.id,
                                                                         priority=fee_structure_rec.sequence)
                            fee_line_lst.append((0,0,invoice_line_dict))

                        invoice_dic={
                            'batch_id':self.batch_id.id,
                            'term_id':terms[term_count].id
                            }

                        prev_paid_rec=paid_term_obj.search([('student_id','=',self.student_id.id),('term_id','=',terms[term_count].id),('batch_id','=',self.batch_id.id)])
                        if not prev_paid_rec:
                            paid_term_obj.create({'student_id':self.student_id.id,'term_id':terms[term_count].id,'batch_id':self.batch_id.id})

                if fee_structure_rec.discount > 0.00 and dis_amount != 0.00:
                    if not fee_structure_rec.name.fees_discount:
                        raise except_orm(_("Warning!"), _('Please define Discount Fees for %s.')%(fee_structure_rec.name.name))
                    else:
                        if not fee_structure_rec.name.fees_discount.property_account_income_id.id:
                            raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_structure_rec.name.fees_discount.name))
                        else:
                            invoice_line_dict = self.invoice_dict_create(product_id=fee_structure_rec.name.fees_discount.id,
                                                                         account_id=fee_structure_rec.name.fees_discount.property_account_income_id.id,
                                                                         name="Discount",
                                                                         quantity=1.00,
                                                                         price_unit= -round(dis_amount,2),
                                                                         rem_amount= -round(dis_amount,2),
                                                                         parent_id=self.student_id.parents1_id.id,
                                                                         priority=0)
                            fee_line_lst.append((0,0,invoice_line_dict))

                #Student Fee Payment Detail Entry
                stud_payble_rec = stud_payble_obj.search_count([('month_id','=',month_rec.id),
                                                                ('name','=',fee_structure_rec.name.id),
                                                                ('fee_pay_type','=',fee_structure_rec.fee_pay_type.id),
                                                                ('student_id','=',self.student_id.id)])

                if stud_payble_rec == 0:
                    stud_payble_obj.create(val)

                # Student Fee Stutas
                fee_status = self.student_id.payment_status.search([('month_id','=',month_rec.id),
                                                                ('student_id','=',self.student_id.id)])
                if not fee_status.id:
                    status_val = {
                        'month_id': month_rec.id,
                        'paid': False,
                    }
                    self.student_id.payment_status = [(0,0,status_val)]
            total_amount -= total_discount
            #create master Fee line
            if total_amount > 0.0:
                fee_pay_line_val.update\
                    ({
                    'student_id' : self.student_id.id,
                    'month_id' : month_rec.id,
                    'total_fee' : total_amount,
                    'month' : month_rec.name,
                    'year' : month_rec.year,
                    })

           # code to search fee payment exist for current month,class and academic yaer
            fee_ids=fee_payment_line_obj.search([('course_id','=',self.course_id.id),
                                                ('academic_year_id','=',self.batch_id.id),
                                                ('month','=',month_rec.id)])
            if not fee_ids.id:
                fee_id=fee_payment_line_obj.create({
                                            'name':str(self.course_id.name) +'/'+str(month_rec.name)+'/'+str(month_rec.year)+' Fee Calculation',
                                            'code':str(self.course_id.name) +'/'+str(month_rec.name)+'/'+str(month_rec.year)+' Fee Calculation',
                                            'course_id':self.course_id.id,
                                            'academic_year_id':self.batch_id.id,
                                            'year':month_rec.year,
                                            'fee_payment_line_ids':[(0,0,fee_pay_line_val)],
                                            'month':month_rec.id,
                                            'fields_readonly':True
                                                })
                fee_ids=[fee_ids]
            else:
                for fee_pay_rec in fee_ids:
                    if fee_pay_rec.id:
                        exist_fee_pay_line = fee_pay_rec.fee_payment_line_ids.search_count([('student_id','=',self.student_id.id),
                                                                                             ('month_id','=',month_rec.id)])
                        if exist_fee_pay_line == 0:
                            fee_pay_rec.fee_payment_line_ids = [(0,0,fee_pay_line_val)]

            # create invoice entry
            if self.invoice_id.id:
                exist_invoice = self.invoice_id
            else:
                exist_invoice = invoice_obj.search([('partner_id','=',self.student_id.id),('month_id','=',month_rec.id)],limit=1)
            if not self.student_id.property_account_receivable_id.id:
                raise except_orm(_("Warning!"), _('Please define account receivable for student'))
            if not exist_invoice.id:
                invoice_date = self.admission_date
                invoice_vals={
                            'partner_id' : self.student_id.id,
                            'month_id' : month_rec.id,
                            'account_id' : self.student_id.property_account_receivable_id.id,
                            'invoice_line_ids' : fee_line_lst,
                            'month' : month_rec.name,
                            'year' : month_rec.year,
                            'batch_id' : self.batch_id.id,
                            'date_invoice' : invoice_date,
                        }
                invoice_id=invoice_obj.create(invoice_vals)
                if invoice_dic:
                    invoice_id.write(invoice_dic)

                # validating invoice
                invoice_id.signal_workflow('invoice_open')
                self.invoice_id=invoice_id.id

                return invoice_id
            else:
                if self.invoice_id:
                    invoice_id = self.invoice_id
                else:
                    invoice_id = invoice_obj.search([('partner_id','=',self.student_id.id),('month_id','=',month_rec.id)])
                if flag == True and invoice_id.state != 'paid':
                    return invoice_id
                raise except_orm(_("Warning!"), _('You have already paid your academic fee'))
        else:
             raise except_orm(_("Warning!"), _('Student Not Found'))

    @api.multi
    def reminder_for_additional_form(self):
        self.current_date_for_link = base64.b64encode(str(date.today()))
        mail_obj=self.env['mail.mail']
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_reminder_for_extra_form_fillup')[1]
        template_rec = self.env['email.template'].browse(template_id)
        template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
        template_rec.send_mail(self.id, force_send=True)

    @api.multi
    def send_payfort_reg_pay_link(self):
        """
        this method used when student registration
        fee pay type is  pay fort.
        ------------------------------------------
        @param self : object pointer
        """
        enquiry_no = self.enquiry_no
        registration_number = self.registration_number
        amount = 0.0
        final_amount = 0
        if not self.reg_fee_line:
            raise except_orm(_('Warning!'),
                             _("please fill Student Registration Fee Structure"))
        # elif self.env['account.journal'].search_count([('name','=','Online Payment'),
        #                                                ('type','=','bank')]) == 0:
        #     raise except_orm(_('Warning!'),
        #             _("please mention journals with name 'Online Payment' and payment type is 'Bank and Checks'. "))
        #
        elif self.env['account.account'].search_count([('code', '=', '402050')]) == 0:
            raise except_orm(_('Warning!'),
                             _("Registration Fees account not found."))

        else:
            pay_able_amount = 0.00
            for each in self.reg_fee_line:
                amount = each.amount

                active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])
                if not active_payforts:
                    raise except_orm(_('Warning!'),
                                     _("Please create Payfort Details First!"))

                if len(active_payforts) > 1:
                    raise except_orm(_('Warning!'),
                                     _("There should be only one payfort record!"))
                pay_able_amount += amount
            final_amount = pay_able_amount

        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])
        if not active_payforts:
                    raise except_orm(_('Warning!'),
                                     _("Please create Payfort Details First!"))
                    
        if (len(active_payforts)) > 1:
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s&EMAIL=%s'%(final_amount,registration_number,self.email)
            self.online_reg_pay_link = link

            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_registration_fee_payment_link')[1]
            template_rec = self.env['email.template'].browse(template_id)
            body_html = template_rec.body_html
            body_dynamic_html = template_rec.body_html + 'You are requested to pay the (non-refundable) Registration Fee of AED %s.<br/>' \
                                                 '<p><a href=%s><button>Click Here</button> to pay Registration Fee</a></p></div>'%(final_amount,link)
            template_rec.write({'email_to': self.email,
                                'email_from': email_sender.smtp_user,
                                'email_cc': '',
                                'body_html': body_dynamic_html})
            template_rec.send_mail(self.id)
            template_rec.body_html = body_html

        self.reg_pay_link = 'PayFort Payment Link Successfully Send To Parents'

    @api.multi
    def send_payfort_acd_pay_link(self):
        """
        this method used to send payfort link for
        online payment of student acd fee.
        ------------------------------------------
        @param self : object pointer
        @net_amount : calculated amount
        @dis_amount : discount amount on calculated amount
        @total_net_amount : total calculated amount - total discount
        """
        amount_on_link = 0.00
        if self._context.has_key('flag') and self._context.get('flag') == True:
            if self.fee_structure_confirm != True:
                raise except_orm(_("Warning!"), _('Please Confirm the fee structure before sending payment link.'))
            if self.invoice_id:
                order_id = self.invoice_id.invoice_number
                amount_on_link = self.invoice_id.residual
            elif self.next_year_advance_fee_id:
                order_id = self.next_year_advance_fee_id.order_id
                amount_on_link = self.next_year_advance_fee_id.residual
        else:
        # if flag != True:
            if self.batch_id.current_academic == True:
                get_record = self.reg_pay_acd_manually(True)
                self.invoice_id = get_record.id
                order_id = get_record.invoice_number
            else:
                get_record = self.send_payfort_acd_for_next_year()
                self.next_year_advance_fee_id = get_record.id
                order_id = get_record.order_id

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
                        if month_count :
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
                                unpaid_month_dic = self.get_person_age(default_turm_start_date,joining_date)
                                t_month_diff = total_month_diff - unpaid_month_dic.get('months') or 0
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
                active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])
                if not active_payforts:
                    raise except_orm(_('Warning!'),
                                     _("Please create Payfort Details First!"))

                if len(active_payforts) > 1:
                    raise except_orm(_('Warning!'),
                                     _("There should be only one payfort record!"))

        cal_total_net_amount = total_net_amount
        if amount_on_link > 0.00:
            total_net_amount = amount_on_link
            cal_total_net_amount = amount_on_link
        

        link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_net_amount,order_id)

        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_payment_link')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        body_html = template_rec.body_html
        body_dynamic_html = template_rec.body_html + '<p>The Fee structure for %s is:</p><br/>'%(self.name)
        body_dynamic_html += '<table border=%s>'%(2)
        body_dynamic_html += '<tr><td>Name</td><td>Amount</td><td>Type</td><td>Discount %% </td><td>Discount Amount</td><td>Net Amount</td></tr>%s</table>'%(data)
        body_dynamic_html += '<p>Total amount you have to pay this month is AED %s </p>'%(round(cal_total_net_amount, 2))
        body_dynamic_html += '<p><a href=%s><button>Click Here</button></a> to pay the Fee online</a></p></div>'%(link)
        template_rec.write({'email_to': self.email,
                            'email_from': email_sender.smtp_user,
                            'email_cc': '',
                            'body_html': body_dynamic_html})
        template_rec.send_mail(self.id)
        template_rec.body_html = body_html
        self.acd_pay_link = "PayFort Payment Link Successfully Send To Parents"

    @api.multi
    def send_payfort_acd_for_next_year(self):
        """
        This method is use when enquiry for next year.
        --------------------------------------------
        :return: It return record set.
        """
        next_year_advance_fee_obj = self.env['next.year.advance.fee']
        month_diff = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),('leave_month','=',False)])
        joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
        start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d").date()
        get_unpaid_diff = self.get_person_age(start_date,joining_date)
        stud_payble_obj = self.env['student.payble.fee']
        leave_month = []
        for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),('leave_month','=',True)]):
            leave_month.append((int(l_month.name),int(l_month.year)))
        month_in_stj = self.months_between(start_date,joining_date)
        unpaid_month = 0
        if get_unpaid_diff.get('months') > 0 and get_unpaid_diff.get('years') >= 0:
            unpaid_month = get_unpaid_diff.get('months')
            if len(month_in_stj) > 0 and len(leave_month) > 0:
                for leave_month_year in leave_month:
                        if leave_month_year in month_in_stj:
                            unpaid_month -= 1
        month_diff -= unpaid_month
        next_year_advance_fee_line_data = []
        if not self.student_id.property_account_customer_advance.id:
            raise except_orm(_('Warning!'),
                    _("Please define student Advance Payment Account!"))

        for fee_structure_rec in self.student_id.student_fee_line:
            amount = fee_structure_rec.amount or 0.00
            discount = fee_structure_rec.discount or 0.00
            next_term = False
            if fee_structure_rec.fee_pay_type.name not in ['term','half_year']:
                pay_amount,dis_amount = self.acd_manually_fee_calculation(cal_type=fee_structure_rec.fee_pay_type.name,
                                                                          pay_amount=amount, discount=discount,
                                                                          month_diff=month_diff)
            elif fee_structure_rec.fee_pay_type.name == 'half_year':
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
                    elif joining_date > first_date_of_half:
                        month_count = self.months_between(first_date_of_half,second_date_of_half)
                leave_month = []
                for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),
                                                               ('leave_month','=',True)]):
                    leave_month.append((int(l_month.name),int(l_month.year)))
                count_month = []
                for month_year in month_count:
                    if month_year not in leave_month:
                        count_month.append(month_year)

                half_year_amount = fee_structure_rec.amount or 0.00
                on_discount = fee_structure_rec.discount or 0.00
                pay_amount,dis_amount = self.acd_manually_fee_calculation(cal_type='half_year',
                                                                        pay_amount=half_year_amount,
                                                                        discount=on_discount,
                                                                        month_diff=total_month_rec,
                                                                        no_of_month=len(count_month))
            elif fee_structure_rec.fee_pay_type.name == 'term':
                terms = self.env['acd.term'].search([('batch_id', '=', self.batch_id.id)])
                if len(terms) == 0:
                    raise except_orm(_("Warning!"), _('Please define Term for Academic year %s !')%(self.batch_id.name))
                if len(terms) > 0:
                    term_list = []
                    for_next_term = self.env['acd.term'].search([('id', '>', terms[0].id)])
                    for term_rec in for_next_term:
                        term_list.append(term_rec.id)
                    if term_list:
                        term_list= sorted(term_list)
                        next_term = term_list[0]
                    no_of_month = 0
                    joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
                    term_start_date = datetime.strptime(terms[0].start_date,"%Y-%m-%d").date()
                    term_end_date = datetime.strptime(terms[0].end_date,"%Y-%m-%d").date()
                    if term_start_date <= joining_date < term_end_date:
                        no_of_month = self.months_between(joining_date,term_end_date)
                    else:
                        no_of_month = self.months_between(term_start_date,term_end_date)
                    total_month = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),
                                                                            ('leave_month','=',False)])
                    unpaid_month_dic = self.get_person_age(term_start_date,joining_date)
                    month_diff_term = total_month - unpaid_month_dic.get('months') or 0
                    pay_amount,dis_amount = self.acd_manually_fee_calculation(cal_type= fee_structure_rec.fee_pay_type.name,
                                                                          pay_amount= amount, discount=discount,
                                                                          month_diff= month_diff_term,
                                                                          no_of_month = len(no_of_month))
                else:
                    raise except_orm(_('Warning!'),
                        _("Please define Term for next Academic Year!"))
            next_year_advance_fee_line_data.append((0,0,{
                'name' : fee_structure_rec.name.id,
                'description' : fee_structure_rec.name.name,
                'account_id' : self.student_id.property_account_customer_advance.id,
                'priority' : fee_structure_rec.sequence,
                'amount' : pay_amount,
                'rem_amount' : pay_amount,
            }))
            if fee_structure_rec.discount > 0.00 and dis_amount > 0.00:
                if not fee_structure_rec.name.fees_discount:
                    raise except_orm(_("Warning!"), _('Please define Discount Fees for %s.')%(fee_structure_rec.name.name))
                else:
                    if not fee_structure_rec.name.fees_discount.property_account_income_id.id:
                        raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_structure_rec.name.fees_discount.name))
                    else:
                        next_year_advance_fee_line_data.append((0,0,{
                            'name' : fee_structure_rec.name.fees_discount.id,
                            'description' : fee_structure_rec.name.fees_discount.name,
                            'account_id' : self.student_id.property_account_customer_advance.id,
                            'priority' : 0,
                            'amount' : -round(dis_amount,2),
                            'rem_amount' : -round(dis_amount,2),
                        }))

            val = {}
            month_rec = self.batch_id.month_ids[0]
            val.update({
                'name': fee_structure_rec.name.id,
                'student_id': self.student_id.id,
                'month_id' : month_rec.id,
                })
            student_fee_dict = self.student_fee_detail_update_dict(fee_pay_type=fee_structure_rec.fee_pay_type.id,
                                                                   cal_amount=pay_amount,
                                                                   total_amount=fee_structure_rec.amount,
                                                                   discount_amount=dis_amount)
            val.update(student_fee_dict)
            val.update({'next_term':next_term})
            if fee_structure_rec.fee_pay_type.name == 'half_year':
                val.update({'is_next_half_year':True})
            stud_payble_rec = stud_payble_obj.search_count([('month_id','=',month_rec.id),
                                                ('name','=',fee_structure_rec.name.id),
                                                ('fee_pay_type','=',fee_structure_rec.fee_pay_type.id),
                                                ('student_id','=',self.student_id.id)])
            if stud_payble_rec == 0:
                stud_payble_obj.create(val)

        #check if NYAF already exists and state in unpaid or partially paid... if yes then update else create new
        #next_year_advance_fee_id = next_year_advance_fee_obj.search([('partner_id','=', self.student_id.id),('reg_id', '=', self.id),('batch_id', '=', self.batch_id.id),('state','in', ('fee_unpaid','fee_partial_paid'))])
        next_year_advance_fee_id = next_year_advance_fee_obj.search([('partner_id','=', self.student_id.id),('reg_id', '=', self.id),('batch_id', '=', self.batch_id.id),('state','in', ('fee_unpaid','fee_partial_paid','fee_paid'))])
        if next_year_advance_fee_id :
            for next_year_advance_fee_line_id in next_year_advance_fee_id.next_year_advance_fee_line_ids :
                if next_year_advance_fee_line_id.amount < 0:
                    next_year_advance_fee_line_id.unlink()
                else :
                    for next_year_advance_fee_line in next_year_advance_fee_line_data :
                        if next_year_advance_fee_line_id.name.id == next_year_advance_fee_line[2]['name'] :
                                next_year_advance_fee_line_id.amount = next_year_advance_fee_line[2]['amount']
                                next_year_advance_fee_line_id.rem_amount = next_year_advance_fee_line[2]['rem_amount']
                
            for next_year_advance_fee_line in next_year_advance_fee_line_data :
                if next_year_advance_fee_line[2]['amount'] < 0 :
                    next_year_advance_fee_id.write({'next_year_advance_fee_line_ids' : [next_year_advance_fee_line]})
            return next_year_advance_fee_id
        else : 
            next_year_advance_fee_data = {
                'partner_id' : self.student_id.id,
                'reg_id' : self.id,
                'enq_date' : self.application_date,
                'order_id' : '/',
                'batch_id' : self.batch_id.id,
                'state' : 'fee_unpaid',
                'next_year_advance_fee_line_ids' : next_year_advance_fee_line_data,
            }
            new_obj = next_year_advance_fee_obj.create(next_year_advance_fee_data)
            return new_obj


    @api.multi
    def online_registration_fee_payment(self):
        """
        :return:redirect to online reg fee payment
        """
        if not self.online_reg_pay_link:
            raise except_orm(_('Warning!'),_("Online Payment Link not Generated"))
        else:
            online_link = self.online_reg_pay_link
            return {
                    "type": "ir.actions.act_url",
                    "url": online_link,
                    "target": "new",
                    }

    @api.multi
    def online_academic_fee_payment(self):
        """
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
            order_id = self.invoice_id.invoice_number
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_amount,order_id)
            return {
                "type": "ir.actions.act_url",
                "url": link,
                "target": "new",
                }

    @api.multi
    def mini_app_to_done(self,args):
        """
        this method used to go to student form
        ------------------------------------------
        @param self : object pointer
        """
        res_id=self.student_id.id
        vid = False
        mod_obj = self.pool.get('ir.model.data')
        if self.complete_parent_contract != True:
            raise except_orm(_('Warning!'),
                        _("Please Complete Parent Contract."))
        if not self.khada_sis:
            raise except_orm(_('Warning!'),
                        _("Please fill KHADA/SIS."))
        vid = self.env['ir.model.data'].get_object_reference('edsys_edu', 'view_student_parent_form')
        vid = vid and vid[1] or False,
        self.state = 'done'
        # send mail to student/parent to inform for ministral approval
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_for_ministral_approval')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
        template_rec.send_mail(self.id, force_send=True)

        return {
           'type': 'ir.actions.act_window',
           'name': _('Student'),
           'res_model': 'res.partner',
           'res_id': res_id,
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': vid,
           'target': 'current',
           'nodestroy': True,
        }

    @api.multi
    def decision_reject_state(self):
        """
        this method used when students is rejected.
        ------------------------------------------
        @param self : object pointer
        """
        mail_obj=self.env['mail.mail']
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_student_rejected')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        template_rec.write({'email_to' : self.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
        #template_rec.send_mail(self.id, force_send=True)
        self.write({'state_hide_ids': [(0,0, {'reg_id': self.id, 'state_name': self.state})],
                    'state_hide': self.state,
                    'state_dropdown': self.state})
        self.state = 'rejected'
        # self.state_dropdown = self.state

    @api.multi
    def reject_state(self):
        """
        this method used when students is rejected.
        ------------------------------------------
        @param self : object pointer
        """
        if self.state == 'awaiting_fee':
            self.student_id.active = False
        self.write({'state_hide_ids': [(0, 0, {'reg_id': self.id, 'state_name': self.state})],
                    'state_hide': self.state})
        self.state_dropdown = self.state
        self.state = 'rejected'

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
    def confirm_fee_structure(self):
        if not self.admission_date:
            raise except_orm(_('Warning!'),_("Please fill joining date."))
        if self.fee_structure_done == True:
            raise except_orm(_('Warning!'),_("Fee structure Already confirm."))
        else:
            # update fee structure based on joining date
            joining_date = datetime.strptime(self.admission_date,"%Y-%m-%d").date()
            start_date = datetime.strptime(self.batch_id.start_date,"%Y-%m-%d").date()
            total_month = self.batch_id.month_ids.search_count([('batch_id','=',self.batch_id.id),('leave_month','=',False)])
            leave_month = []
            for l_month in self.batch_id.month_ids.search([('batch_id','=',self.batch_id.id),('leave_month','=',True)]):
                leave_month.append((int(l_month.name),int(l_month.year)))
            month_in_stj = self.months_between(start_date,joining_date)
            get_unpaid_diff = self.get_person_age(start_date,joining_date)
            if get_unpaid_diff.get('months') > 0 or get_unpaid_diff.get('days') > 0:
                unpaid_month = get_unpaid_diff.get('months')
                # if get_unpaid_diff.get('days') > 0:
                #     unpaid_month += 1
                if len(month_in_stj) > 0 and len(leave_month) > 0:
                    for leave_month_year in leave_month:
                        if leave_month_year in month_in_stj:
                            unpaid_month -= 1
                if unpaid_month > 0.00 and total_month > 0.00:
                    # not pay amount because joining date is late,
                    for fee_line in self.student_fee_line:
                        if fee_line.fee_pay_type.name not in ['one'] and fee_line.name.is_admission_fee != True:
                            total_amount = float(fee_line.amount)
                            unpaid_amount = (total_amount * unpaid_month) / total_month
                            total_amount -= round(unpaid_amount,2)
                            fee_line.write({'amount':total_amount,
                                            'update_amount':0.00})

	    self.student_id.admission_date = self.admission_date
            # discount apply in fee structure
            if self.discount_on_fee.id:
                self.student_id.discount_on_fee = self.discount_on_fee.id
                self.student_id.update_fee_structure()
            self.fee_structure_done = True




    @api.multi
    def reverse_fee_structure(self):
        if self.fee_structure_done == False:
            raise except_orm(_('Warning!'),_("Fee structure Already Reverse."))
        else:
            fee_line_obj = self.env['fees.structure']
            for fee_criteria in fee_line_obj.search([
                    ('academic_year_id','=',self.batch_id.id),
                    ('course_id','=',self.course_id.id),
                    ('type','=','academic')]):
                for fee_line in fee_criteria.fee_line_ids:
                    for stud_fee_rec in self.student_fee_line:
                        if stud_fee_rec.name == fee_line.name:
                            stud_fee_rec.write({'amount':fee_line.amount,
                                                'update_amount':0.00,'discount':0.00
                                                })
            self.fee_structure_done = False

    @api.multi
    def confirm_done_fee_structure(self):
        """
        finaly Done fee structure with all fee calculation,
        ---------------------------------------------------
        """
        self.fee_structure_confirm = True
        # send mail for link to pay acd fee online
        self.send_payfort_acd_pay_link()
        self.current_date_for_link = base64.b64encode(str(date.today()))
        # send mail for extra form fillup and genarate link for same,
        self.send_mail_for_extra_form_fillup()
        dumy_date = base64.b64encode('0000-00-00')
        self.remaining_form_link = '/student/verification?ENQUIRY=%s&DATE=%s'%(self.enquiry_no,dumy_date)
        self.confirm_fee_date = datetime.now()


class account_invoice_line(models.Model):

    _inherit = 'account.invoice.line'

    parent_id = fields.Many2one('res.partner',string="Parent ID")

class Account_Move(models.Model):

    _inherit = 'account.move'

    cheque_pay = fields.Boolean('Cheque')
    cheque_date = fields.Date('Cheque Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
