# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from odoo import SUPERUSER_ID
import re
import new
import base64
from odoo import api, tools
# from odoo.osv import osv
from lxml import etree
import calendar
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class visa_type(models.Model):
    
    _name = "visa.type"
    
    name = fields.Char('Visa Type' )
    visible_to_pro = fields.Boolean('Visible to PRO' )
    
 

class hr_employee(models.Model):
    _inherit = "hr.employee"


    @api.one
    @api.onchange('company_id')
    def _onchange_company_inherit(self):
        address = self.company_id.partner_id.address_get(['default'])
        self.address_id = address['default'] if address else False

    
    @api.multi
    def get_current_user(self):
        user_obj = self.env['res.users']
        user_value = user_obj.browse(self.env.user.id)
        current_user = False
        for group in user_value.groups_id :
            if group.name == 'PRO User' or group.name == 'HR User' or group.name == 'Admin' or group.name == 'Admin Manager' :
                current_user = group.name
        for employee_id in self:
            employee_id.current_user = current_user
        
        
        
        
    @api.one
    def get_days_since_joining(self):
        if self.first_day_office and self.probation_period :
            today_date = datetime.datetime.strptime(str(datetime.datetime.now().date()), DATE_FORMAT)
            first_day_office = datetime.datetime.strptime(self.first_day_office, DATE_FORMAT)
            days_since_joining = (today_date - first_day_office).days
            for employee_id in self:
                if days_since_joining < int(self.probation_period) :
                    employee_id.show_message = True
                else : 
                    employee_id.show_message = False
                employee_id.days_since_joining = days_since_joining
        
        
    
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(hr_employee, self).fields_view_get(view_id=view_id, view_type=view_type,toolbar=toolbar, submenu=submenu)
        if view_id:
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        if view_type != 'search' and self.env.uid != SUPERUSER_ID:
            # Check if user is in group that allow creation
            group_pro_user_rb = self.env.user.has_group('edsys_hrm.group_pro_user_rb')
            group_admin_manager_user_rb = self.env.user.has_group('edsys_hrm.group_admin_manager_user_rb')
            if group_pro_user_rb or group_admin_manager_user_rb :
                root = etree.fromstring(res['arch'])
                root.set('create', 'false')
                res['arch'] = etree.tostring(root)
        return res
    
    # def _check_email_get(self):
    #
    #     for rule in self.browse():
    #         cur_rec_ids = self.search([])
    #         if cur_rec_ids:
    #             for cur_rec_id in cur_rec_ids:
    #                 if id[0] == cur_rec_id:
    #                     continue
    #                 cur_rec = self.browse(cur_rec_id)
    #                 if cur_rec:
    #                     if rule.work_email and cur_rec.email_id:
    #                         if rule.work_email == cur_rec.email_id:
    #                             return False
        
        
    
    # Personal Information Field
    current_user =fields.Char('User', compute='get_current_user')
    job_id = fields.Many2one("hr.job", 'Job Title', ondelete='restrict')
    category_ids_ids = fields.Many2many('hr.employee.category', 'employee_category_rel', 'emp_id', 'category_id', string='Tags')
    employee_name = fields.Char('Employee Name',compute='employee_full_name')
    employee_code = fields.Char('Employee Code', readonly="1")
    identification_id = fields.Char('Candidate Profile Number', size=240 )
    otherid = fields.Char('Other Id')
    middle_name = fields.Char('Middle Name', size=15 )
    last_name = fields.Char('Last Name', size=15)
    contact_number1 = fields.Char('Contact Number 1', size=15,required=True)
    contact_number2 = fields.Char('Emergency contact number')
    contact_number3 = fields.Char('Home country contact number')
    isd_contact_number1 = fields.Char('ISD Contact Number 1', size=4,required=True)
    isd_contact_number2 = fields.Char('ISD Emergency contact number', size=4 )
    isd_contact_number3 = fields.Char('ISD Home country contact number', size=4)
    email_id = fields.Char('Personal Email ID')
    current_street = fields.Char('Street' )
    current_street2 = fields.Char('Street2' )
    current_zip = fields.Char('Zip', size=24, change_default=True )
    current_city = fields.Char('City' )
    current_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict' )
    current_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict' )
    is_permanent_address_same = fields.Selection([('yes','YES' ),('no','NO')],'Is Permanent address same as Current??')
    permnent_street = fields.Char('Street' )
    permnent_street2 = fields.Char('Street2' )
    permnent_zip = fields.Char('Zip', size=24, change_default=True )
    permnent_city = fields.Char('City' )
    permnent_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict' )
    permnent_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict' )
    birth_city = fields.Char('Birth City' )
    birth_country = fields.Many2one('res.country', 'Birth Country', ondelete='restrict' )
    current_nearest_landmark = fields.Char('Nearest Landmark' )
    permnent_nearest_landmark = fields.Char('Nearest Landmark' )
    employee_state = fields.Selection([('new','New' ),('validate','Validate'),('on_board','On Board'),('probation','Probation'),('employee','Employee'),('off_boarding','Off Boarding'),('off_boarding_confirmation','Off Boarding Confirmation'),('ex_employee','Ex Employee')],'State',default='new')
    is_existing_employee = fields.Selection([('yes','YES' ),('no','NO')],'Existing Employee?', default='no')
    # Admin Section
    medical_insurance_card_expiry_date = fields.Date('Medical Card Expiry Date ')
    health_card_expiry_date = fields.Date('Health Card Expiry Date')
    medical_insurance_card_number = fields.Char('Medical Insurance Card Number' )
    health_card_number = fields.Char('Health Card Number' )
    pro_visa_uid = fields.Char('Visa UID' )
    
    # HR Setting Field
    date_of_interview = fields.Date('Date Of Interview',required=True)
    joining_date = fields.Date('Expected Date Of Joining',required=True)
    offer_letter = fields.Binary('offer Letter')
    offer_letter_sent_date = fields.Date('Offer Letter Sent Date  ',required=True)
    visa_required = fields.Selection([('yes','YES' ),('no','NO')],'Employer Visa Required', default='no')
    labour_card_exist = fields.Selection([('yes','YES' ),('no','NO')],'Labour Card')
    emirates_id_exist = fields.Selection([('yes','YES' ),('no','NO')],'Emirates ID')
    accommodation = fields.Selection([('yes','YES' ),('no','NO')],'Employer Accommodation' , default='no')
    health_card = fields.Selection([('yes','YES' ),('no','NO')],'Health Card Required' ,default='no')
    medical_insurance = fields.Selection([('yes','YES' ),('no','NO')],'Medical Insurance Required' ,default='no')
    remark = fields.Char('Remarks')
    employment_form_filled = fields.Boolean('Employment Form Filled',default=False)
    last_update_date = fields.Date('Last Update Date')
    employment_application_form_link = fields.Char('Additional Information Form Link',readonly=True )
    terminated_resigned_selection = fields.Selection([('applicable','Applicable' ),('not_applicable','Not Applicable')],'Terminated/Resigned Selection')
    terminated_resigned = fields.Selection([('terminated','Terminated' ),('resigned','Resigned')],'Terminated/Resigned ?')
    terminated_remark = fields.Char('Remarks')
    resignation_date = fields.Date('Resignation Date')
    last_working_day = fields.Date('Last Working Day')
    renew_labour_card = fields.Selection([('yes','YES' ),('no','NO')],'Renew Labour Card', default='no')
    renew_emirates_card = fields.Selection([('yes','YES' ),('no','NO')],'Renew Emirates Card', default='no')
    admin_person =fields.Many2one('hr.employee','Admin',domain=[('job_id','=','Admin'),('active_employee','=',True)])
    hr_person =fields.Many2one('hr.employee','HR' ,domain=[('job_id','=','HR'),('active_employee','=',True)])
    it_person =fields.Many2one('hr.employee','IT Person',domain=[('department_id','=','IT')])
    
    # Applicant Passport Details
    passport_number = fields.Char('Passport Number' )
    passport_issue_date = fields.Date('Date Of Issue ',    )
    passport_expiry_date = fields.Date('Date Of Expiry  ',   )
    passport_issue_place  = fields.Char('Place Of Issue' )
    
    # Applicant Visa Details
    uae_visa = fields.Selection([('yes','YES' ),('no','NO')],'UAE Visa')
   
    
    # PRO Activities
    remark = fields.Selection([('no_document_received','No documents received' ),('awaiting_hr_confirmation','Awaiting HR confirmation' )],'Remarks' )
    pro_visa_details_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Visa Details Status' )
    pro_visa_type = fields.Many2one('visa.type', string='Visa Type',domain=[('visible_to_pro','=',True)])
    pro_visa_number = fields.Char('Visa Number' )
    hr_name = fields.Char('HR Name')
    hr_email = fields.Char('HR Email')
    pro_visa_issue_date = fields.Date('Date Of Issue  ',   )
    pro_visa_expiry_date = fields.Date('Date Of Expiry  ',  ) 
    pro_visa_remark = fields.Char('Remark')
    pro_sponsor_name = fields.Char('Sponsor Name')
    pro_relation_with_emp = fields.Char('Relation with employee')
    pro_sponsor_visa_number = fields.Char('Sponsor Visa Number')
    pro_sponsor_visa_start_date = fields.Date('Sponsor Visa start Date  ')
    pro_sponsor_visa_expiry_date = fields.Date('Sponsor Visa Expiry Date  ')
    pro_labour_card_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Labour Card Status' )
    pro_labour_card_no = fields.Char('Labour Card / Permit Card No.' )
    pro_labour_card_remark = fields.Char('Remark')
    pro_labour_card_start_date = fields.Date('Labour Card valid from date  ',  )
    pro_permit_expiry_date = fields.Date('Expiry Date Of Labour Card  ',   )
    pro_emirates_id_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Emirates Id Status' )
    pro_emirates_card_no = fields.Char('Emirates Card No.' )
    pro_emirates_start_date = fields.Date('Emirates ID valid from Date  ',  )
    pro_emirates_expiry_date = fields.Date('Expiry Date Of Emirates ID Card  ',   )
    pro_emirates_remark = fields.Char('Remark')
    labour_noc = fields.Selection([('yes','YES' ),('no','NO')],'Labour NOC required' ,default='no')
    khda_noc = fields.Selection([('yes','YES' ),('no','NO')],'KHDA NOC required' ,default='no')
    labour_noc_submitted = fields.Boolean('Labour NOC Submitted ')
    khda_noc_submitted = fields.Boolean('KHDA NOC Submitted')
    
    pro_visa_attachment = fields.Binary(string='Visa Attachment' )
    pro_labour_card_attachment = fields.Binary(string='Labour Card Attachment' )
    pro_emirates_card_attachment = fields.Binary(string='Emirates Card Attachment' )
    
    pro_labour_card_file_name =fields.Char('Labour Card Attachment Name')
    pro_emirates_card_file_name =fields.Char('Emirates Card Attachment Name' )
    pro_visa_file_name =fields.Char('Visa Attachment Name')
    
    
    #Visa Details
    visa_details_id = fields.One2many('visa.details','employee_id','Visa Details' )
    
    # Employee Qualification
    employee_qualification_id =fields.One2many('employee.qualification','employee_id','Employee Qualification' )
    
    # Other Information
    current_employer = fields.Selection([('yes','YES' ),('no','NO')],'Have you completed 2 years with your current employer? (Applicable only for those working in the UAE)')
    emiratres_id_details_id = fields.One2many('emirates.id.details','employee_id','Emirates Id Details' )
    labour_card_details_id = fields.One2many('labour.card.details','employee_id','Labour Card Details' )
    designation = fields.Char('Designation' )
    grade = fields.Char('Grade And Level' )
    work_experience =fields.Char('Work Experience' )
    current_location =fields.Many2one('res.country','Current Location' )
    current_salary = fields.Char('Current Salary' )
    currency = fields.Many2one('res.currency','Currency' )
    notice_period = fields.Selection([('immediate','Immediate' ),('one_months','1 month' ),('two_months','2 months' ),('three_months','3 months')],'Notice Period')
    khda_moe_approval = fields.Selection([('yes','YES' ),('no','NO')],'KHDA/MoE Approval and/Or Certificate Of Equivalancy Exist?')
    document_name = fields.Char('Name Of The Document' )
    attested_doc = fields.Selection([('yes','YES' ),('no','NO')],'Is The Document Attested?')
    document_issue_date = fields.Date('Document Issue Date  ',   )
    document_expiry_date = fields.Date('Document Expiry Date  ' ,  )
    is_medical_condition_suffering = fields.Selection([('yes','YES' ),('no','NO')],'Is Medical Condition Suffering')
    medical_condition = fields.Char('Medical Condition' )
    marital = fields.Selection([('unmarried','Unmarried' ),('married','Married' ),('divorced','Divorced' ),('separated','Separated' ),('widowed','Widowed' ),('other','Other')], 'Marital Status' )
    please_specify = fields.Char('Please Specify' )
    working_with_other_org = fields.Selection([('yes','YES' ),('no','NO')],'Are you working for a freezone / Government / Semi-Government / Hospitality / Banking Service Provider? :' )
    labour_card_status = fields.Selection([('Initiated','Initiated' ),('In progress','In progress' ),('Completed','Completed' ),('Not required','Not required' )],'Labour Card Status' )
    labour_card_start_date = fields.Date('Labour Card valid from date  ',  )
    emirates_start_date = fields.Date('Emirates ID valid from Date  ',  )
    is_highest_degree_certificate_attached = fields.Selection([('yes','YES' ),('no','NO')],'Is your highest degree certificate attested' )
    
    # Admin Document
    admin_attchment_ids = fields.One2many('admin.attachement', 'employee_id', 'Attachments' )
    
    # Dependant Details
    dependant_ids = fields.One2many('dependant.obj', 'employee_id', 'Attachments' )
    
    
    # Required Flag
    off_boarding = fields.Boolean(string="Off-Boarding",default=False)
    off_boarding_confirmation = fields.Boolean(string="Off-Boarding Confirmation",default=False)
    ex_employee = fields.Boolean(string="Ex-Employee",default=False)
    first_day_office = fields.Date('First Day In Office  ',   )
    active_employee = fields.Boolean(string="Active",default=False)
    pro_activities = fields.Boolean('PRO Record',default=False)
    
    #probation period
    probation_period = fields.Char('Probation Period In Days')
    confirmation_date = fields.Date('Confirmation Date')
    days_since_joining = fields.Integer('Days since joining', compute='get_days_since_joining')
    show_message = fields.Boolean('Show message', compute='get_days_since_joining')
    probation_completion_date = fields.Date('Probation Completion Date')
    
    _sql_constraints = [
        ('login_key123', 'UNIQUE (email_id)',  'You can not have two users with the same email id !'),
        ('login_key2', 'UNIQUE (work_email)',  'You can not have two users with the same email id !'),
    ]
    
    # _constraints = [
    #     (_check_email_get, 'You can not have two users with the same email id !', ['email_id', 'work_email']),
    # ]



    @api.model_cr
    def init(self):

        hr_job_id = self.env['hr.job'].search([('name', '=', 'HR')])
        if not hr_job_id :
            self.env.cr.execute(""" INSERT INTO hr_job (name, state) VALUES ('HR', 'open') """)
        
        admin_job_id = self.env['hr.job'].search([('name', '=', 'Admin')])
        if not admin_job_id :
            self.env.cr.execute(""" INSERT INTO hr_job (name, state) VALUES ('Admin', 'open') """)
            
        admin_manager_job_id = self.env['hr.job'].search([('name', '=', 'Admin Manager')])
        if not admin_manager_job_id :
            self.env.cr.execute(""" INSERT INTO hr_job (name, state) VALUES ('Admin Manager', 'open') """)
            
        it_department_id = self.env['hr.department'].search([('name', '=', 'IT')])
        if not it_department_id :
            self.env.cr.execute(""" INSERT INTO hr_department (name) VALUES ('IT') """)
        
        employer_visa_id = self.env['visa.type'].search([('name', '=', 'Employer Visa')])
        if not employer_visa_id :
            self.env.cr.execute(""" INSERT INTO visa_type (name, visible_to_pro) VALUES ('Employer Visa', True) """)
        
        residance_visa_id = self.env['visa.type'].search([('name', '=', 'Residance Visa')])
        if not residance_visa_id :
            self.env.cr.execute(""" INSERT INTO visa_type (name, visible_to_pro) VALUES ('Residance Visa', True) """)
         
        tourist_visa_id = self.env['visa.type'].search([('name', '=', 'Tourist Visa')])
        if not tourist_visa_id :
            self.env.cr.execute(""" INSERT INTO visa_type (name, visible_to_pro) VALUES ('Tourist Visa', False) """)
         
                  
    @api.multi
    def send_employement_form(self):
        for hr_rec in self :
            if hr_rec.active_employee:
                if not hr_rec.work_email:
                    raise except_orm(_('Warning!'), _('Please specify work email of existing employee.'))
                else :
                    email_to = hr_rec.work_email
            else : 
                if not hr_rec.email_id :
                    raise except_orm(_('Warning!'), _('Please specify personal email of new employee.'))
                else :
                    email_to = hr_rec.email_id
            hr_rec.employment_application_form_link = '/employee/employment-form?employee=%s'%(hr_rec.id)
             
            if  hr_rec.is_existing_employee == 'no':
                raise except_orm(_('Warning!'), _('For Candidate please use resend application form'))
                
            # send mail to employee to fill the information
                    
            if  hr_rec.is_existing_employee == 'yes':
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])[0]
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_existing_employee')[1]
                template_rec = self.env['email.template'].browse(template_id)
                temp = template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
                template_rec.send_mail(hr_rec.id, force_send=True)
            
        return True
     
    def on_change_probation_period(self,probation_period,first_day_office):
        vals = {}
        if probation_period and not first_day_office :
            raise except_orm(_('Warning!'),
                             _("Please enter First day in office"))
        if probation_period and first_day_office:
           first_day_office = datetime.datetime.strptime(first_day_office, DATE_FORMAT)
           probation_completion_date = first_day_office + datetime.timedelta(days= int(probation_period))
           vals['probation_completion_date'] = probation_completion_date
           
           today_date = datetime.datetime.strptime(str(datetime.datetime.now().date()), DATE_FORMAT)
           days_since_joining = (today_date - first_day_office).days
           vals['days_since_joining'] = days_since_joining
        return  {'value' : vals}
            
            
            
    def onchange_department_id(self,department_id):
        value = {'parent_id': False}
        if department_id:
            department = self.env['hr.department'].browse(department_id)
            value['parent_id'] = department.manager_id.id
            value['admin_person'] = department.admin_person.id
            value['hr_person'] = department.hr_person.id
            value['it_person'] = department.it_person.id
        return {'value': value}
    
    
            
    def Validatemobile(self,mobile):
        p = re.compile('^\d{8,10}$')
        if p.match(mobile) != None:
            return True
        else:
            raise except_orm(_('Warning!'),
                    _("Please Enter Valid Mobile Number: (%s)") % (mobile,))
            

    def Validateisd(self, isd):
        length_isd = len(isd)
        if length_isd < 3 and length_isd > 4:
            raise except_orm(_('Warning!'),
                    _("Please Enter Valid ISD Number: (%s)") % (isd,))
        else:
            return True
            
    
    def onchange_pro_permit_expiry_date(self,cr,uid,ids,pro_labour_card_start_date,pro_permit_expiry_date):
        if pro_permit_expiry_date:
            if pro_permit_expiry_date  < pro_labour_card_start_date:
                raise except_orm(_('Warning!'),_("Please select date after Labour Card valid from date (%s)") % (pro_labour_card_start_date,))
            
            
    @api.multi
    def employee_full_name(self):
        for employee_id in self:
            name = ''
            middle_name = ''
            last_name = ''
            if employee_id.name:
                name = employee_id.name
            if employee_id.middle_name:
                middle_name = employee_id.middle_name
            if employee_id.last_name:
                last_name = employee_id.last_name
            employee_id.employee_name = name  + ' '+  middle_name + ' ' + last_name
    
    def send_mail_to_admin(self):
            if self.admin_person.work_email:
                admin_person = self.admin_person.work_email
            else:
                admin_person = self.admin_person.email_id
            # send mail to IT Department and CC to HR and Admin
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_hrm', 'hr_email_template')[1]
            template_rec = self.env['email.template'].browse(template_id)
            template_rec.write({'email_to' : admin_person,'email_from':email_sender.smtp_user})
            template_rec.send_mail(self.id, force_send=True)
    
    
    def  ValidateEmail(self,email_id):
        if email_id:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email_id) != None:
                return True
            else:
                raise except_orm(_('Warning!'),_('Invalid Email', 'Please enter a valid email address'))
        
    def  ValidateWorkEmail(self,work_email):
        if work_email:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", work_email) != None:
                return True
            else:
                raise except_orm(_('Warning!'),_('Please enter a valid email address'))
        
    
    def on_change_is_permanent_address_same(self,is_permanent_address_same,current_street,current_street2,current_nearest_landmark,current_city,current_state_id,current_zip,current_country_id):
        values = {}
        work_email = ''
        if is_permanent_address_same == 'yes':
            values = {
                      'permnent_street' : current_street,
                      'permnent_street2' : current_street2,
                      'permnent_nearest_landmark' : current_nearest_landmark,
                      'permnent_city' : current_city,
                      'permnent_state_id' : current_state_id,
                      'permnent_zip' : current_zip,
                      'permnent_country_id' : current_country_id,
                      }
        else:
            values = {
                      'permnent_street' : False,
                      'permnent_street2' : False,
                      'permnent_nearest_landmark' : False,
                      'permnent_city' : False,
                      'permnent_state_id' : False,
                      'permnent_zip' : False,
                      'permnent_country_id' : False,
                      }
        return  {'value' : values}
                    
        
    def on_change_resignation_date(self):
        values = {}
        if self.resignation_date:
            converted_resignation_date = datetime.datetime.strptime(str(self.resignation_date), DATE_FORMAT)
            month = converted_resignation_date.month - 1 + 2
            year = int(converted_resignation_date.year + month / 12 )
            month = month % 12 + 1
            day = min(converted_resignation_date.day,calendar.monthrange(year,month)[1])
            last_working_day = datetime.datetime.strptime(str(datetime.date(year,month,day)), DATE_FORMAT)
            values = {
                      'last_working_day' : last_working_day,
                      }
            return  {'value' : values}
         
    @api.model
    def create(self, vals):
        email_to = ''
	employee_code = False
        vals_write = {}
        if 'uae_visa' in vals and vals['uae_visa'] == 'yes':
            if vals['visa_details_id'] == []  :
                raise except_orm(_('Warning!'),_("If you have UAE Visa then you must have to enter the respective details under 'History Details' tab."))
        if vals['is_existing_employee'] == 'yes' :
            vals['employee_state'] = 'employee'
            vals['active_employee'] = True
	    obj_ir_sequence = self.env['ir.sequence']
            ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Employee Code')])
            if ir_sequence_ids:
                employee_code = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
            else:
                sequence_vals = {
                                    'name' : 'Employee Code',
                                    'prefix' : 4,
                                    'padding' : 4,
                                    'number_next_actual' : 1,
                                    'number_increment' : 1,
                                    'implementation_standard' : 'standard',
                                 }
                ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
                employee_code = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
            vals['employee_code'] = employee_code
        if 'first_day_office' in vals and vals['first_day_office']:
            vals['active_employee'] = True
            vals['employee_state'] = 'employee'
        if 'contact_number1' in vals and vals['contact_number1']:
            self.Validatemobile(vals['contact_number1'])
        if 'contact_number2' in vals and vals['contact_number2']:
            self.Validatemobile(vals['contact_number2']) 
        if 'contact_number3' in vals and vals['contact_number3']:
            self.Validatemobile(vals['contact_number3']) 
            
        if 'isd_contact_number1' in vals and vals['isd_contact_number1']:
            self.Validateisd(vals['isd_contact_number1']) 
        if 'isd_contact_number2' in vals and vals['isd_contact_number2']:
            self.Validateisd(vals['isd_contact_number2']) 
        if 'isd_contact_number3' in vals and vals['isd_contact_number3']:
            self.Validateisd(vals['isd_contact_number3']) 
            
        if 'offer_letter_sent_date' in vals and vals['offer_letter_sent_date']:
            offer_letter_sent_date = vals['offer_letter_sent_date']
            date_of_interview = vals['date_of_interview']
            if offer_letter_sent_date < date_of_interview:
                raise except_orm(_('Warning!'),_("Please select offer letter date after date of interview (%s)") % (date_of_interview,))
            
        if 'joining_date' in vals and vals['joining_date']:
            joining_date = vals['joining_date']
            offer_letter_sent_date = vals['offer_letter_sent_date']
            if joining_date < offer_letter_sent_date:
                raise except_orm(_('Warning!'),_("Please select joining date after offer letter sent date (%s)") % (offer_letter_sent_date,))
        
        if 'passport_expiry_date' in vals and vals['passport_expiry_date']:
            passport_expiry_date = vals['passport_expiry_date']
            passport_issue_date = vals['passport_issue_date']
            if passport_expiry_date < passport_issue_date:
                raise except_orm(_('Warning!'),_("Please select passport expiry date after passport issue date (%s)") % (passport_issue_date,))
        
        if 'visa_details_id' in vals and vals['visa_details_id']:
            visa_details_id = vals['visa_details_id']
            visa_expiry_date = visa_details_id[0][2]['visa_expiry_date']
            visa_issue_date = visa_details_id[0][2]['visa_issue_date']
            vals['visa_details_id'][0][2]['confirm'] = True
            if visa_expiry_date < visa_issue_date:
                raise except_orm(_('Warning!'),_("Please select visa expiry date after visa issue date (%s)") % (visa_issue_date,))
         
        if 'labour_card_exist' in vals:
            labour_card_exist = vals['labour_card_exist']
            if labour_card_exist == 'yes':
                if 'labour_card_details_id' in vals :
                    if vals['labour_card_details_id'] == []:
                             raise except_orm(_('Warning!'),_("Please enter Labour card details under 'History Details' tab"))
                    else :
                        vals['labour_card_details_id'][0][2]['confirm'] = True
                        
        if 'labour_id_exist' in vals:
            labour_id_exist = vals['labour_id_exist']
            if labour_id_exist == 'yes':
                if 'emiratres_id_details_id' in vals :
                    if vals['emiratres_id_details_id'] == []:
                        raise except_orm(_('Warning!'),_("Please enter Emirates id details under 'History Details' tab"))
                    else :
                        vals['emiratres_id_details_id'][0][2]['confirm'] = True
            
        res = super(hr_employee, self).create(vals)
        
        if 'active_employee' in vals and vals['active_employee']:
            active_employee = vals['active_employee']
            if active_employee : 
                if 'work_email' in vals:
                    work_email = vals['work_email']
                    if not work_email :
                        raise except_orm(_('Warning!'), _('Please specify work email of existing employee.'))
                    else :
                        email_to = work_email
                 
        else : 
            if not vals['email_id'] :
                raise except_orm(_('Warning!'), _('Please specify personal email of new employee.'))
            
            if 'email_id' in vals and vals['email_id']:
                email_to = vals['email_id']
                
        vals_write['employment_application_form_link'] = '/employee/employment-form?employee=%s'%(res.id)
        res.write(vals_write)
        # send mail to employee to fill the information
        if vals['is_existing_employee'] == 'no' :
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_employement_form')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            temp = template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
            template_rec.send_mail(res.id, force_send=True)
        return res
    
    
    
    @api.multi
    def write(self, vals):
        if 'pro_activities' in vals and vals['pro_activities']:
                pro_activities = vals['pro_activities']
        else :
            pro_activities = self.pro_activities
        if pro_activities == True :
            if 'pro_visa_details_status' in vals and vals['pro_visa_details_status']:
                if vals['pro_visa_details_status'] == 'cancelled' :
                    raise except_orm(_('Warning!'),_("You can not cancel Visa of new employee"))
            if 'pro_labour_card_status' in vals and vals['pro_labour_card_status']:
                if vals['pro_labour_card_status'] == 'cancelled' :
                    raise except_orm(_('Warning!'),_("You can not cancel Labour Card of new employee"))
            if 'pro_emirates_id_status' in vals and vals['pro_emirates_id_status']:
                if vals['pro_emirates_id_status'] == 'cancelled' :
                    raise except_orm(_('Warning!'),_("You can not cancel Emirates of new employee"))
            
        ir_attachment = self.env['ir.attachment']
        if 'pro_visa_file_name' in vals and vals['pro_visa_file_name']:
            if not 'pro_visa_attachment' in vals :
                raise except_orm(_('Warning!'),_("Please attach visa copy"))
        
        if 'pro_emirates_card_file_name' in vals and vals['pro_emirates_card_file_name']:
            if not 'pro_emirates_card_attachment' in vals :
                raise except_orm(_('Warning!'),_("Please attach Emirates Card copy"))
            
        if 'pro_labour_card_file_name' in vals and vals['pro_labour_card_file_name']:
            if not 'pro_labour_card_attachment' in vals :
                raise except_orm(_('Warning!'),_("Please attach Labour Card copy"))
            
        if 'labour_card_details_id' in vals :
            if type(vals['labour_card_details_id'][0][2]) is dict :
                vals['labour_card_details_id'][0][2]['confirm'] = True
        if 'emiratres_id_details_id' in vals :
            if type(vals['emiratres_id_details_id'][0][2]) is dict :
                vals['emiratres_id_details_id'][0][2]['confirm'] = True
        if 'is_existing_employee' in vals and vals['is_existing_employee'] :
            if vals['is_existing_employee'] == 'yes' :
                vals['employee_state'] = 'employee'
                vals['active_employee'] = True
            
        if 'contact_number1' in vals and vals['contact_number1']:
            self.Validatemobile(vals['contact_number1']) 
        if 'contact_number2' in vals and vals['contact_number2']:
            self.Validatemobile(vals['contact_number2']) 
        if 'contact_number3' in vals and vals['contact_number3']:
            self.Validatemobile(vals['contact_number3']) 
            
        if 'isd_contact_number1' in vals and vals['isd_contact_number1']:
            self.Validateisd(vals['isd_contact_number1']) 
        if 'isd_contact_number2' in vals and vals['isd_contact_number2']:
            self.Validateisd(vals['isd_contact_number2']) 
        if 'isd_contact_number3' in vals and vals['isd_contact_number3']:
            self.Validateisd(vals['isd_contact_number3']) 
            
        if 'health_card' in vals and vals['health_card']:
            if vals['health_card'] == 'yes':
                self.send_mail_to_admin()
                
        if 'renew_labour_card' in vals and vals['renew_labour_card']:
            if vals['renew_labour_card'] == 'yes':
                vals['pro_activities'] = True
            
        if 'renew_emirates_card' in vals and vals['renew_emirates_card']:
            if vals['renew_emirates_card'] == 'yes':
                vals['pro_activities'] = True
                
        if 'medical_insurance' in vals and vals['medical_insurance']:
            if vals['medical_insurance'] == 'yes':
                self.send_mail_to_admin()
        
        if 'date_of_interview' in vals and vals['date_of_interview']:
            date_of_interview = vals['date_of_interview']
        else:
            date_of_interview = self.date_of_interview
            
        if 'offer_letter_sent_date' in vals and vals['offer_letter_sent_date']:
            offer_letter_sent_date = vals['offer_letter_sent_date']
        else:
            offer_letter_sent_date = self.offer_letter_sent_date
            
        if 'joining_date' in vals and vals['joining_date']:
            joining_date = vals['joining_date']
        else:
            joining_date = self.joining_date
            
        if offer_letter_sent_date < date_of_interview:
            raise except_orm(_('Warning!'),_("Please select offer letter date after date of interview (%s)") % (date_of_interview,))
        
        if joining_date < offer_letter_sent_date:
            raise except_orm(_('Warning!'),_("Please select joining date after offer letter sent date (%s)") % (offer_letter_sent_date,))
            
        if 'passport_expiry_date' in vals and vals['passport_expiry_date']:
            passport_expiry_date = vals['passport_expiry_date']
        else:
            passport_expiry_date = self.passport_expiry_date
          
        if 'passport_issue_date' in vals and vals['passport_issue_date']:  
            passport_issue_date = vals['passport_issue_date']
        else:
            passport_issue_date = self.passport_issue_date
            
        if passport_expiry_date < passport_expiry_date:
            raise except_orm(_('Warning!'),_("Please select passport expiry date after passport issue date (%s)") % (passport_issue_date,))
        
        if 'visa_details_id' in vals and vals['visa_details_id']:
            if vals['visa_details_id'][0] :
                if type(vals['visa_details_id'][0][2]) is dict :
                    if 'visa_issue_date' in vals['visa_details_id'][0][2]:
                        vals['visa_details_id'][0][2]['confirm'] = True
                        visa_issue_date = vals['visa_details_id'][0][2]['visa_issue_date']
                    else:
                        visa_issue_date = self.visa_details_id.visa_issue_date
                    if 'visa_expiry_date' in vals['visa_details_id'][0][2] :
                        visa_expiry_date = vals['visa_details_id'][0][2]['visa_expiry_date']
                    else:
                        visa_expiry_date = self.visa_details_id.visa_expiry_date
                 
                    if visa_expiry_date < visa_issue_date:
                        raise except_orm(_('Warning!'),_("Please select visa expiry date after visa issue date (%s)") % (visa_issue_date,))
            
        if 'active_employee' in vals and vals['active_employee']:
            active_employee = vals['active_employee']
            if active_employee:
                name = ''
                middle_name = ''
                last_name = ''
        #visa_attachment = None
        if 'visa_details_id' in vals:
            if vals['visa_details_id'][0] :
                if type(vals['visa_details_id'][0][2]) is dict :
                    vals['visa_details_id'][0][2]['visa_flag'] = True    
                    vals['visa_details_id'][0][2]['visa_attachment'] = None 
            
        #labour_card_attachment = None
        if 'labour_card_details_id' in vals:
            if vals['labour_card_details_id'][0] :
                if type(vals['labour_card_details_id'][0][2]) is dict :
                    #labour_card_attachment = vals['labour_card_details_id'][0][2]['labour_card_attachment']
                    vals['labour_card_details_id'][0][2]['labour_card_attachment'] = None
                    vals['labour_card_details_id'][0][2]['labour_flag'] = True     
               
        #emirates_id_attachment = None 
        if 'emiratres_id_details_id' in vals:
            if vals['emiratres_id_details_id'][0] :
                if type(vals['emiratres_id_details_id'][0][2]) is dict :
                    #emirates_id_attachment = vals['emiratres_id_details_id'][0][2]['emirates_id_attachment']    
                    vals['emiratres_id_details_id'][0][2]['emirates_id_attachment']  = None
                    vals['emiratres_id_details_id'][0][2]['emirates_flag'] = True 
        
        if 'pro_visa_attachment' in vals:
            pro_visa_attachment = vals['pro_visa_attachment']
            if pro_visa_attachment :
                ir_attachment.sudo().create({'name': vals['pro_visa_file_name'],
                                                       'res_model':  'hr.employee',
                                                       'res_id': self.id,
                                                       'datas': pro_visa_attachment,
                                                       'type': 'binary',
                                                        'datas_fname': vals['pro_visa_file_name'],
                                                       })
                vals['pro_visa_attachment'] = None
        
            
        if 'pro_labour_card_attachment' in vals:
            pro_labour_card_attachment = vals['pro_labour_card_attachment']    
            print 'pro_labour_card_attachment : ', pro_labour_card_attachment
            print 'pro_labour_card_file_name : ', vals['pro_labour_card_file_name']
            if pro_labour_card_attachment :
                ir_attachment.sudo().create({
                                                'name': vals['pro_labour_card_file_name'],
                                               'res_model':  'hr.employee',
                                               'res_id': self.id,
                                               'datas': pro_labour_card_attachment,
                                               'type': 'binary',
                                               'datas_fname': vals['pro_labour_card_file_name'],
                                           })
                vals['pro_labour_card_attachment'] = None
        
        if 'pro_emirates_card_attachment' in vals:
            pro_emirates_card_attachment = vals['pro_emirates_card_attachment']    
        
            if pro_emirates_card_attachment :
                ir_attachment.sudo().create({
                                                'name': vals['pro_emirates_card_file_name'],
                                                'res_model':  'hr.employee',
                                                'res_id': self.id,
                                                'datas': pro_emirates_card_attachment,
                                                'type': 'binary',
                                                'datas_fname': vals['pro_emirates_card_file_name'],
                                                   })
                vals['pro_emirates_card_attachment']  = None
            
        return super(hr_employee, self).write(vals)
    
    @api.multi
    def resend_employement_application_form(self):
        if self.active_employee:
            email_id = self.work_email
        else:
            email_id = self.email_id
             
        employment_application_form_link = self.employment_application_form_link
        self.employment_application_form_link = '/employee/employment-form?employee=%s'%(self.id)
        # send mail to employee to fill the information
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_employement_form')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        template_rec.write({'email_to' : email_id,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        return True
         
    @api.multi
    def on_boarding_employee_comfirmation(self):
        print'===========on_boarding_employee_comfirmation==============='
        self.ensure_one()
        first_day_office = datetime.datetime.strptime(self.first_day_office, DATE_FORMAT)
        probation_period = int(self.probation_period)
        probation_completion_date = first_day_office + datetime.timedelta(days=probation_period)
        if probation_period > 0 :
            self.employee_state = 'probation'
            self.probation_completion_date = probation_completion_date
        else :
            self.employee_state = 'employee'
            self.probation_completion_date = first_day_office
        self.active_employee = True
        
        employee_code = ''
        obj_ir_sequence = self.env['ir.sequence']
        print obj_ir_sequence,'======================obj_ir_sequence'
        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Employee Code')])
        print ir_sequence_ids,'======================ir_sequence_ids==========='
        if ir_sequence_ids:
            employee_code = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
            print obj_ir_sequence.next_by_code('ir_sequence_ids.id'),'---------------------------obj_ir_sequence.next_by_code'
            print employee_code,'================employee_code============='
        else:
            sequence_vals = {
                                'name' : 'Employee Code',
                                'prefix' : 4,
                                'padding' : 4,
                                'number_next_actual' : 1,
                                'number_increment' : 1,
                                'implementation_standard' : 'standard',
                             }
            ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
            employee_code = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
        self.employee_code = employee_code
        print self.employee_code,'=====================self.employee_code==self.employee_code'
#         raise except_orm(_("Warning!"), _('stop'))
        return True
    
    
    
    @api.multi
    def probation_completed(self):
        self.employee_state = 'employee'
        self.confirmation_date = datetime.datetime.now().strftime(DATE_FORMAT)
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('edsys_hrm', 'probation_complete_email_template_edi')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'hr.employee',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    @api.multi
    def off_boarding_employee_comfirmation(self):
        email_id= ''
        current_date = datetime.datetime.now().date()
        d1 = datetime.datetime.strptime(str(current_date), DATE_FORMAT)
        d2 = datetime.datetime.strptime(self.last_working_day, DATE_FORMAT)
        d3 = (d2 - d1).days
        if d3 <= 0:
            if self.active_employee:
                email_id = self.work_email
            else:
                email_id = self.email_id
                
                
            self.hr_name = self.hr_person.name
            self.hr_email = self.hr_person.work_email
            hr_person = self.hr_person.work_email
            admin_person = self.admin_person.work_email
            it_person = self.it_person.work_email
            # send mail to IT Department and CC to HR and Admin
            if not hr_person : 
                email_cc = admin_person
            if not admin_person : 
                email_cc = hr_person
            if hr_person and admin_person :
                email_cc = hr_person + ',' + admin_person
            # send mail to employee to fill the information
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_hrm', 'off_boarding_template')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_cc' : email_cc,'email_to' : it_person,'email_from':email_sender.smtp_user})    
            template_rec.send_mail(self.id, force_send=True)
            self.employee_state = 'ex_employee'
            self.active_employee = False
            self.off_boarding = False
            return True
        else:
            raise except_orm(_('Warning!'), _('You can not confirm before last working day'))
        
    @api.one
    def submit_pro_activities_form(self):
	if not self.pro_visa_details_status or not self.pro_labour_card_status or not self.pro_emirates_id_status :
            raise except_orm(_('Warning!'),_("Please fill Visa / Emirates / Labourd card status"))
        ir_attchment_obj = self.env['ir.attachment']
        if self.pro_visa_details_status == 'completed' :
            if not self.pro_visa_file_name :
                raise except_orm(_('Warning!'),_("Please attach Visa documents"))
            
        if self.pro_labour_card_status == 'completed' :
            if not self.pro_labour_card_file_name :
                raise except_orm(_('Warning!'),_("Please attach Labour Card documents"))
            
        if self.pro_emirates_id_status == 'completed' :
            if not self.pro_emirates_card_file_name :
                raise except_orm(_('Warning!'),_("Please attach Emirates ID documents"))
            
        pro_user_list = []
        self.pro_activities = False
        if self.emiratres_id_details_id :
            self.emiratres_id_details_id[0].renew_done = True
        if self.visa_details_id :
            self.visa_details_id[0].renew_done = True
        if self.labour_card_details_id :
            self.labour_card_details_id[0].renew_done = True
        emirates_id_details_vals = {
                                        'emirates_id_status':self.pro_emirates_id_status,
                                        'emirates_card_no':self.pro_emirates_card_no,
                                        'emirates_start_date' : self.pro_emirates_start_date,
                                        'emirates_expiry_date' : self.pro_emirates_expiry_date,
                                        'employee_id' : self.id,
                                        'employee_code' : self.employee_code, 
                                        'confirm' : True,
                                        'emirates_card_file_name' : self.pro_emirates_card_file_name,
                                       # 'emirates_id_attachment' : self.pro_emirates_id_attachment,
                                    }
        self.env['emirates.id.details'].create(emirates_id_details_vals)
        
        visa_details_vals = {
                                    'visa_details_status':self.pro_visa_details_status ,
                                    'visa_type':self.pro_visa_type.id ,
                                    'visa_number' : self.pro_visa_number ,
                                    'visa_issue_date' : self.pro_visa_issue_date,
                                    'visa_expiry_date':self.pro_visa_expiry_date,
                                    'sponsor_name' : self.pro_sponsor_name,
                                    'relation_with_emp' : self.pro_relation_with_emp,
                                    'sponsor_visa_number':self.pro_sponsor_visa_number,
                                    'sponsor_visa_start_date' : self.pro_sponsor_visa_start_date,
                                    'sponsor_visa_expiry_date' : self.pro_sponsor_visa_expiry_date,
                                    'employee_id' : self.id,
                                    'employee_code' : self.employee_code,
                                    'confirm' : True,
                                    'visa_file_name' : self.pro_visa_file_name,
                                   # 'visa_attachment' : self.pro_visa_attachment,
                                }
        self.env['visa.details'].create(visa_details_vals)
        
        labour_card_details_vals = {
                                        'labour_card_status':self.pro_labour_card_status,
                                        'permit_card_no' : self.pro_labour_card_no,
                                        'permit_issue_date' : self.pro_labour_card_start_date,
                                        'permit_expiry_date' : self.pro_permit_expiry_date,
                                        'employee_id' : self.id,
                                        'employee_code' : self.employee_code,
                                        'confirm' : True,
                                        'labour_card_file_name' : self.pro_labour_card_file_name,
                                      #  'labour_card_attachment' : self.pro_labour_card_attachment,
                                    }
        self.env['labour.card.details'].create(labour_card_details_vals)
            
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'probation_pro_details_submitted_edi')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        if self.active_employee :
            employee_email = self.work_email
        else :
            employee_email = self.email_id
        hr_email = self.hr_person.work_email
        
        #pro email
        res_groups_obj = self.env['res.groups']
        res_groups_ids = res_groups_obj.search([('name','=','PRO User')])
        if res_groups_ids :
            res_groups_id = res_groups_ids[0]
            for user in res_groups_id.users :
                pro_user_list = user.login + ','
        email_to = hr_email
        if pro_user_list :
            email_cc = pro_user_list + employee_email
        else :
            email_cc = employee_email
        template_rec.write({'email_to' : email_to,'email_cc' : email_cc,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        return True
        
    @api.one    
    def validate_employee(self):
        ir_attchment_obj = self.env['ir.attachment']
        ir_attchment_ids =  ir_attchment_obj.search([('res_model','=','hr.employee'),('res_id','=',self.id)])
        if self.uae_visa == 'yes' and self.labour_card_exist == 'yes' and self.emirates_id_exist == 'yes':
            if len(ir_attchment_ids) < 5:
                raise except_orm(_('Warning!'),_("Please attach Visa, Emirates and Labour card documents"))
        
        if self.uae_visa == 'yes' and self.labour_card_exist == 'no' and self.emirates_id_exist == 'no':
            if len(ir_attchment_ids) < 3:
                raise except_orm(_('Warning!'),_("Please attach Visa documents"))
            
        if self.uae_visa == 'no' and self.labour_card_exist == 'no' and self.emirates_id_exist == 'yes':
            if len(ir_attchment_ids) < 3:
                raise except_orm(_('Warning!'),_("Please attach Emirates documents"))
            
        if self.uae_visa == 'no' and self.labour_card_exist == 'yes' and self.emirates_id_exist == 'no':
            if len(ir_attchment_ids) < 3:
                raise except_orm(_('Warning!'),_("Please attach Labour card documents"))
            
        if self.uae_visa == 'yes' and self.labour_card_exist == 'yes' and self.emirates_id_exist == 'no':
            if len(ir_attchment_ids) < 4:
                raise except_orm(_('Warning!'),_("Please attach Visa and Labour card documents"))
            
        if self.uae_visa == 'yes' and self.labour_card_exist == 'no' and self.emirates_id_exist == 'yes':
            if len(ir_attchment_ids) < 4:
                raise except_orm(_('Warning!'),_("Please attach Visa and Emirates Id documents"))
            
        if self.uae_visa == 'no' and self.labour_card_exist == 'yes' and self.emirates_id_exist == 'yes':
            if len(ir_attchment_ids) < 4:
                raise except_orm(_('Warning!'),_("Please attach Labour Card and Emirates Id documents"))
                
        if self.active_employee :
            if self.work_email :
                self.employee_state = 'employee'
                self.pro_activities = False
            else :
                raise except_orm(_('Warning!'), _('You should enter work email of employee'))
        else :
            self.employee_state = 'on_board'
            self.pro_activities = True
            res_groups_obj = self.env['res.groups']
            res_groups_ids = res_groups_obj.search([('name','=','PRO User')])
            if res_groups_ids :
                res_groups_id = res_groups_ids[0]
                for user in res_groups_id.users :
                    # send mail to  PRO saying a new record has been moved to PRO activities tab
                    email_server=self.env['ir.mail_server']
                    email_sender=email_server.search([])[0]
                    ir_model_data = self.env['ir.model.data']
                    template_id = ir_model_data.get_object_reference('edsys_hrm', 'hr_email_template')[1]
                    template_rec = self.env['email.template'].browse(template_id)
                    template_rec.write({'email_to' : user.login,'email_from':email_sender.smtp_user})
                    template_rec.send_mail(self.id, force_send=True)

        self.hr_name = self.hr_person.name
        self.hr_email = self.hr_person.work_email
        hr_person = self.hr_person.work_email
        admin_person = self.admin_person.work_email
        it_person = self.it_person.work_email
        
        # send mail to IT Department and CC to HR and Admin
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'hr_email_template')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        
        if not hr_person : 
            email_cc = admin_person
        if not admin_person : 
            email_cc = hr_person
        if hr_person and admin_person :
            email_cc = hr_person + ',' + admin_person
        template_rec.write({'email_cc' : email_cc,'email_to' : it_person,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        return True
    
    @api.one    
    def off_boarding_employee(self):
        self.employee_state = 'off_boarding'
        return True
    
    @api.one    
    def cancel_offboarding(self):
        self.employee_state = 'employee'
        return True
       
class employee_qualification(models.Model):
    _name = "employee.qualification"

    university_name = fields.Char('University', size=240)
    degree = fields.Selection([('graduation','Graduation' ),('post_graduation','Post Graduation')],'Grade')
    year = fields.Char('Year', size=15 )
    employee_id =fields.Many2one('hr.employee','HR Employee' )
    
 
class admin_attachement(models.Model):
     
    _name = "admin.attachement"
 
    name =fields.Char('Attachment Name', size=56 )
    filename =fields.Char('Attachment Name', size=56 )
    file =fields.Binary(string='File Name' )
    date =fields.Date('Date Created',  )
    employee_id = fields.Many2one('hr.employee', 'HR Employee' )
    
class dependant_obj(models.Model):
    
    _name = "dependant.obj"

    full_name =fields.Char('Full Name', size=56 )
    date_of_birth =fields.Date('Date Of Birth', size=56 ,  )
    relationship_with_dependant =fields.Selection([('spouse','Spouse' ),('children','Children' ),('parents','Parents' ),('parents_in_law','Parents in law' ),('brother','Brother' ),('sister','Sister')],'Relationship With Dependant')
    employee_id =fields.Many2one('hr.employee','HR Employee' )   
    
    
class hr_department(models.Model):


    _inherit = "hr.department"
    
    admin_person =fields.Many2one('hr.employee','Admin',domain=[('job_id','=','Admin'),('active_employee','=',True)])
    hr_person =fields.Many2one('hr.employee','HR' ,domain=[('job_id','=','HR'),('active_employee','=',True)])
    it_person =fields.Many2one('hr.employee','IT Person',domain=[('department_id','=','IT')])
    
