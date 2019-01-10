from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
# from datetime import date,datetime,timedelta
import base64
from datetime import datetime
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import logging
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo import models, fields, api, _
import logging
import werkzeug
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website.models.website import slug
# from odoo.addons.web.controllers.main import login_redirect
_logger = logging.getLogger(__name__)

class WebsiteEmployementForm(http.Controller):

    @http.route(['/new_employee',], type='http', auth="public", website=True)
    def new_employee(self,**post):
        env = request.env(user=SUPERUSER_ID)
        orm_country = env['res.country']
        orm_hr_job = env['hr.job']
        countries = orm_country.sudo().search([])
        hr_job_ids = orm_hr_job.sudo().search([])
        hr_web_data = {
                        'countries' : countries, 
                        'hr_job_ids' : hr_job_ids,
                       }
        return request.render("edsys_hrm.new_employement_form",hr_web_data)
    
    
    @http.route(['/employee/create_new_employee',], type='http', auth="public", website=True,csrf=False)
    def create_new_employee(self,**post):
        
        env = request.env(user=SUPERUSER_ID)
        offer_letter =  post.get('offer_letter') or None
        if offer_letter :
                offer_letter_encoded = base64.encodestring(offer_letter.read()),
            
        birthday = post.get('birthday') or None
        if birthday:
            birthday_datetime = datetime.strptime(str(birthday), "%d/%m/%Y")
        else :
            birthday_datetime = None
            
        date_of_interview = post.get('date_of_interview') or None
        if date_of_interview:
            date_of_interview_datetime = datetime.strptime(str(date_of_interview), "%d/%m/%Y")
        
        offer_letter_sent_date = post.get('offer_letter_sent_date') or None
        if offer_letter_sent_date:
            offer_letter_sent_datetime = datetime.strptime(str(offer_letter_sent_date), "%d/%m/%Y")
        
        joining_date = post.get('joining_date') or None
        if joining_date:
            joining_datetime = datetime.strptime(str(joining_date), "%d/%m/%Y")
            
        labour_card_exist = post.get('labour_card_exist') or None
        if labour_card_exist == 'yes' :
            permit_card_no = post.get('permit_card_no') or None
            permit_expiry_date = post.get('permit_expiry_date') or None
            if permit_expiry_date:
                permit_expiry_datetime = datetime.strptime(str(permit_expiry_date), "%d/%m/%Y")
        else :
            permit_card_no = False
            permit_expiry_date = False
            
        emirates_id_exist = post.get('emirates_id_exist') or None
        if emirates_id_exist == 'yes' :
            emirates_card_no = post.get('emirates_card_no') or None
            emirates_expiry_date = post.get('emirates_expiry_date') or None
            if emirates_expiry_date:
                emirates_expiry_datetime = datetime.strptime(str(emirates_expiry_date), "%d/%m/%Y")
        else :
            emirates_card_no = False
            emirates_expiry_date = False
                
            
        employee_data = {
                            'name': post.get('name') or None,
                            'middle_name': post.get('middle_name') or None, 
                            'last_name': post.get('last_name') or None, 
                            'email_id': post.get('email_id') or None, 
                            'contact_number1': post.get('contact_number1') or None,  
                            'isd_contact_number1': post.get('isd_contact_number1') or None,  
                            'contact_number2': post.get('contact_number2') or None,  
                            'isd_contact_number2': post.get('isd_contact_number2') or None,  
                            'contact_number3': post.get('contact_number3') or None,  
                            'isd_contact_number3': post.get('isd_contact_number3') or None,  
                            'country_id': post.get('nationality') or None, 
                            'job_id': post.get('job_id') or None, 
                            'date_of_interview': date_of_interview_datetime,
                            'offer_letter_sent_date': offer_letter_sent_datetime,
                            'joining_date': joining_datetime, 
                            'birthday': birthday_datetime, 
                            'is_existing_employee' : 'no',
                            #===================================================
                            # 'permit_card_no':post.get('permit_card_no') or None, 
                            # 'permit_expiry_date': post.get('permit_expiry_date') or None, 
                            # 'emirates_card_no': post.get('emirates_card_no') or None, 
                            # 'emirates_expiry_date': post.get('emirates_expiry_date') or None, 
                            #===================================================
                            'offer_letter' : offer_letter_encoded,
                            'passport_number': post.get('passport_number') or None, 
                            'visa_required': post.get('visa_required') or None, 
                            'accommodation': post.get('accommodation') or None, 
                            'medical_insurance': post.get('medical_insurance') or None, 
                            'health_card': post.get('health_card') or None, 
                            'remark': post.get('remark') or None, 
                            'identification_id': post.get('identification_id') or None, 
                            'labour_card_exist':labour_card_exist ,
                            'emirates_id_exist': emirates_id_exist ,
                            'employee_state' : 'new',
                            'active_employee' : False,
                        }
                
        employee_obj = env['hr.employee']
        employee_id = employee_obj.sudo().search([('email_id','=',post.get('email_id'))])
        if employee_id:
            return request.render("edsys_hrm.employee_duplicate_email",{})
#            raise except_orm(_('UserError'), _('Recursivity Detected.'))
        new_employee = employee_obj.sudo().create(employee_data)
         #Labour_card_details
        labour_card_details_obj = env['labour.card.details']
        labour_card_details = {}
        labour_card_exist = post.get('labour_card_exist') or None
        if labour_card_exist == 'yes' :
            if post.get('permit_card_no') or post.get('permit_expiry_date')  :
                labour_card_details = {
                                         'permit_card_no': permit_card_no, 
                                         'permit_expiry_date': permit_expiry_datetime, 
                                         'employee_id' : new_employee.id,
                                         'labour_card_status' : 'initiated',
                                         'confirm' : True,
                                         }
                
                labour_card_details_id  = env['labour.card.details'].sudo().create(labour_card_details)
        
        #Emirates Id details
        if post.get('emirates_card_no') or post.get('emirates_expiry_date')  :
            emirates_id_details_obj = env['emirates.id.details']
            emirates_id_details = {}
            emirates_id_exist = post.get('emirates_id_exist') or None
            if emirates_id_exist == 'yes' :
                emirates_id_details = {
                                         'emirates_card_no': emirates_card_no, 
                                         'emirates_expiry_date': emirates_expiry_datetime, 
                                         'employee_id' : new_employee.id,
                                         'emirates_id_status':'initiated',
                                         'confirm' : True,
                                         }
                emirates_id_details_id  = emirates_id_details_obj.sudo().create(emirates_id_details)
        
        return request.render("edsys_hrm.employee_complete_template",{})
    

            
    
    
    @http.route([
        '/employee/employment-form',
    ], type='http', auth="public", website=True)
    def render_employement_form(self, **post):
        """
        this method is used to Student email varification,
        if write email id then move to page that he is
        update his information and fill other details.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        
        employee_id = post.get('employee')
        env = request.env(context=dict(request.env.context))
        hr_emp_obj = env['hr.employee']
        ir_model_fields_obj = env['ir.model.fields']
        hr_emp_rec = hr_emp_obj.sudo().search([('id','=',employee_id)])
#         if hr_emp_rec.employment_form_filled == True:
#             return request.render("edsys_hrm.employement_link_expired_templet",{})
        orm_country = env['res.country']
        orm_currency = env['res.currency']
        state_orm = env['res.country.state']
        orm_visa_type = env['visa.type']
        orm_ir_attachment = env['ir.attachment']
        countries = orm_country.sudo().search([])
        currencies = orm_currency.sudo().search([])
        states = state_orm.sudo().search([])
        visa_type_ids = orm_visa_type.sudo().search([])
        resume_ids = orm_ir_attachment.sudo().search([('name','=','Resume'),('res_model','=', 'hr.employee'), ('res_id','=',hr_emp_rec.id)])
        if not resume_ids :
            resume_ids = False
        salary_certificate_ids = orm_ir_attachment.sudo().search([('name','=','Salary Certificate'),('res_model','=', 'hr.employee'), ('res_id','=',hr_emp_rec.id)])
        if not salary_certificate_ids :
            salary_certificate_ids = False
        passport_copy_ids = orm_ir_attachment.sudo().search([('name','=','Passport'),('res_model','=', 'hr.employee'), ('res_id','=',hr_emp_rec.id)])
        if not passport_copy_ids :
            passport_copy_ids = False
        relieving_letter_ids = orm_ir_attachment.sudo().search([('name','=','Relieving Letter'),('res_model','=', 'hr.employee'), ('res_id','=',hr_emp_rec.id)])
        if not relieving_letter_ids :
            relieving_letter_ids = False
        if hr_emp_rec.id :
            if hr_emp_rec.image_medium :
                image_medium =  True
            else :
                image_medium = False
            hr_web_data = {
                            'hr_emp_rec' : hr_emp_rec, 
                            'countries' : countries, 
                            'currencies' : currencies,
                            'states' : states,
                            'visa_type_ids' : visa_type_ids,
                            'resume_ids' : resume_ids,
                            'salary_certificate_ids' : salary_certificate_ids,
                            'relieving_letter_ids' : relieving_letter_ids,
                            'passport_copy_ids' : passport_copy_ids,
                            'image_medium' : image_medium,
                           }
            return request.render("edsys_hrm.website_epmloyement_application_form",hr_web_data)
        
    @http.route([
    '/otherinformation/thankyou',
    ], type='http', auth="public", website=True,csrf=False)
    def render_employee_other_info(self, **post):
        env = request.env(context=dict(request.env.context))
        ir_attachment = env['ir.attachment']
        #print post,'--------------post'
        
        employee_obj = env['hr.employee']
        if 'work_email' in post and post['work_email']:
            employee_id = employee_obj.sudo().search([('work_email','=',post.get('work_email'))])
        else :
            employee_id = employee_obj.sudo().search([('email_id','=',post.get('email_id'))])
        
        #check for visa_details_id
        if not employee_id.visa_details_id :
            uae_visa = post.get('uae_visa') or None
            if uae_visa == 'yes' :
                post_visa_issue_date = post.get('visa_issue_date') or None
                if post_visa_issue_date:
                    visa_issue_date = datetime.strptime(str(post_visa_issue_date), "%d/%m/%Y")
                else :
                    visa_issue_date = None
                post_visa_expiry_date = post.get('visa_expiry_date') or None
                if post_visa_expiry_date:
                    visa_expiry_date = datetime.strptime(str(post_visa_expiry_date), "%d/%m/%Y")
                else :
                    visa_expiry_date = None
                visa_type = post.get('visa_type') or None 
                visa_copy = post.get('visa_copy') or None
                visa_number = post.get('visa_number') or None
                sponsor_name = post.get('sponsor_name') or None
                sponsor_address = post.get('sponsor_address') or None
                # create visa details line
                visa_copy_filename = str(visa_copy.filename)
                old_visa_copy_filename = visa_copy_filename.split('.')[0]
                new_visa_copy_filename  =  visa_copy_filename.replace(old_visa_copy_filename, 'Visa')
                ir_attachment.sudo().create({'name': new_visa_copy_filename,
                                                   'datas_fname': visa_copy.filename,
                                                   'res_model': employee_id._name,
                                                   'res_id': employee_id.id,
                                                   'datas': base64.encodestring(visa_copy.read()),
                                                   })
                
                visa_type_id = env['visa.type'].sudo().search([('id','=',visa_type)])
                visa_details = {
                                     'visa_type': visa_type_id.id or None, 
                                     'visa_number': post.get('visa_number') or None, 
                                     'visa_issue_date' : visa_issue_date,  
                                     'visa_expiry_date' : visa_expiry_date,
                                     'sponsor_name' : post.get('sponsor_name') or None,
                                     'sponsor_address' : post.get('sponsor_address') or None,  
                                     'employee_id' : employee_id.id,
                                     'visa_details_status' : 'completed',
                                     'confirm' : True,
                                     'visa_attachment' : base64.encodestring(visa_copy.read()),
                                     'visa_file_name' : new_visa_copy_filename,
                                     }
                visa_details_id  = env['visa.details'].sudo().create(visa_details)
                
                
        labour_card_copy =  post.get('labour_card_copy') or None
        if labour_card_copy :
            labour_card_copy_filename = str(labour_card_copy.filename)
            old_labour_card_copy_filename = labour_card_copy_filename.split('.')[0]
            new_labour_card_copy_filename  =  labour_card_copy_filename.replace(old_labour_card_copy_filename, 'Labour Card')
            ir_attachment.sudo().create({'name': new_labour_card_copy_filename,
                                               'datas_fname': labour_card_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(labour_card_copy.read()),
                                               })
            
        #check for labour_card_details_id
        if not employee_id.labour_card_details_id :
            labour_card_exist = post.get('labour_card_exist') or None
            if labour_card_exist == 'yes' :
                permit_card_no = post.get('permit_card_no') or None
                post_permit_expiry_date = post.get('permit_expiry_date') or None
                if post_permit_expiry_date:
                    permit_expiry_date = datetime.strptime(str(post_permit_expiry_date), "%d/%m/%Y")
                else : 
                    permit_expiry_date = None
                # create labour card lines 
                labour_card_details = {
                                         'permit_card_no': permit_card_no, 
                                         'permit_expiry_date': permit_expiry_date, 
                                         'employee_id' : employee_id.id,
                                         'labour_card_status' : 'completed',
                                         'confirm' : True,
                                         'labour_card_file_name' : new_labour_card_copy_filename,
                                         'labour_card_attachment' : base64.encodestring(labour_card_copy.read()),
                                         }
                labour_card_details_id  = env['labour.card.details'].sudo().create(labour_card_details)
        
        emirates_id_copy =  post.get('emirates_id_copy') or None
        if emirates_id_copy :
            emirates_id_copy_filename = str(emirates_id_copy.filename)
            old_emirates_id_copy_filename = emirates_id_copy_filename.split('.')[0]
            new_emirates_id_copy_filename  =  emirates_id_copy_filename.replace(old_emirates_id_copy_filename, 'Emirates')
            ir_attachment.sudo().create({'name': new_emirates_id_copy_filename,
                                               'datas_fname': emirates_id_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(emirates_id_copy.read()),
                                               })
            
            
                 
        #check for emiratres_id_details_id
        if not employee_id.emiratres_id_details_id : 
            emirates_id_exist = post.get('emirates_id_exist') or None
            if emirates_id_exist == 'yes' :
                emirates_card_no = post.get('emirates_card_no') or None
                post_emirates_expiry_date = post.get('emirates_expiry_date') or None
                if post_emirates_expiry_date:
                    emirates_expiry_date = datetime.strptime(str(post_emirates_expiry_date), "%d/%m/%Y")
                else : 
                    emirates_expiry_date = None
                # create emirates lines
                emirates_id_details = {
                                         'emirates_card_no': emirates_card_no, 
                                         'emirates_expiry_date': emirates_expiry_date, 
                                         'employee_id' : employee_id.id,
                                         'emirates_id_status':'completed',
                                         'confirm' : True,
                                         'emirates_card_file_name' : new_emirates_id_copy_filename,
                                         'emirates_id_attachment' : base64.encodestring(emirates_id_copy.read()),
                                         }
                emirates_id_details_id  = env['emirates.id.details'].sudo().create(emirates_id_details)
        
        #check for document_issue_date
        if employee_id.document_issue_date :
            document_issue_date = employee_id.document_issue_date
        else : 
            post_document_issue_date = post.get('document_issue_date') or None
            if post_document_issue_date : 
                document_issue_date = datetime.strptime(str(post_document_issue_date), "%d/%m/%Y")
            else : 
                document_issue_date = None
                
        #check for document_expiry_date
        if employee_id.document_expiry_date :
            document_expiry_date = employee_id.document_expiry_date
        else : 
            post_document_expiry_date = post.get('document_expiry_date') or None
            if post_document_expiry_date : 
                document_expiry_date = datetime.strptime(str(post_document_expiry_date), "%d/%m/%Y")
            else : 
                document_expiry_date = None
            
            
        #check for passport_issue_date
        if employee_id.passport_issue_date :
            passport_issue_date = employee_id.passport_issue_date
        else : 
            post_passport_issue_date = post.get('passport_issue_date') or None
            if post_passport_issue_date : 
                passport_issue_date = datetime.strptime(str(post_passport_issue_date), "%d/%m/%Y")
            else : 
                passport_issue_date = None
            
        #check for passport_expiry_date
        if employee_id.passport_expiry_date :
            passport_expiry_date = employee_id.passport_expiry_date
        else : 
            post_passport_expiry_date = post.get('passport_expiry_date') or None
            if post_passport_expiry_date :
                passport_expiry_date = datetime.strptime(str(post_passport_expiry_date), "%d/%m/%Y")
            else : 
                passport_expiry_date =  None
            
        #check for passport_issue_place    
        if employee_id.passport_issue_place :
            passport_issue_place = employee_id.passport_issue_place
        else :
            passport_issue_place = post.get('passport_issue_place') or None
            
        
        #check for passport_number    
        if employee_id.passport_number :
            passport_number = employee_id.passport_number
        else :
            passport_number = post.get('passport_number') or None
        
        #check for photo
        if employee_id.image_medium : 
            image_medium = employee_id.image_medium
        else : 
            post_passport_size_photo = post.get('passport_size_photo') or None
            if post_passport_size_photo : 
                image_medium = base64.encodestring(post_passport_size_photo.read())
            else :
                image_medium = None
                
        #check for address 
        is_permanent_address_same = post.get('is_permanent_address_same')
        if  is_permanent_address_same == 'yes' :
            permnent_street = post.get('current_street') or None
            permnent_street2 = post.get('current_street2') or None
            permnent_nearest_landmark = post.get('current_nearest_landmark') or None
            permnent_city = post.get('current_city') or None
            permnent_state_id = post.get('current_state_id') or None
            permnent_zip = post.get('current_zip') or None
            permnent_country_id = post.get('current_country_id') or None
        else :
            permnent_street = post.get('permnent_street') or None
            permnent_street2 = post.get('permnent_street2') or None
            permnent_nearest_landmark = post.get('permnent_nearest_landmark') or None
            permnent_city = post.get('permnent_city') or None
            permnent_state_id = post.get('permnent_state_id') or None
            permnent_zip = post.get('permnent_zip') or None
            permnent_country_id = post.get('permnent_country_id') or None
            
            
        # personal details 
        if employee_id.name :
            name = employee_id.name
        else :
            name = post.get('name') or None
        
        if employee_id.middle_name :
            middle_name = employee_id.middle_name
        else :
            middle_name = post.get('middle_name') or None
        
        if employee_id.last_name :
            last_name = employee_id.last_name
        else :
            last_name = post.get('last_name') or None
        
        if employee_id.marital :
            marital = employee_id.marital
        else :
            marital = post.get('marital') or None
            
        #check for birthday
        if employee_id.birthday :
            birthday = employee_id.birthday
        else : 
            post_birthday = post.get('birthday') or None
            if post_birthday :
                birthday = datetime.strptime(str(post_birthday), "%d/%m/%Y")
            else :
                birthday = None
        
        if employee_id.currency :
            currency = employee_id.currency.id
        else :
            currency = post.get('currency') or None
        
        if employee_id.birth_country :
            birth_country = employee_id.birth_country.id
        else :
            birth_country = post.get('birth_country') or None
        
        if employee_id.birth_city :
            birth_city = employee_id.birth_city
        else :
            birth_city = post.get('birth_city') or None
            
            
        if employee_id.current_location :
            current_location = employee_id.current_location.id
        else :
            current_location = post.get('current_location') or None
        
        #other details
        if employee_id.attested_doc :
            attested_doc = employee_id.attested_doc
        else :
            attested_doc = post.get('attested_doc') or None
            
        if employee_id.medical_condition :
            medical_condition = employee_id.medical_condition
        else :
            medical_condition = post.get('medical_condition') or None
            
        if employee_id.contact_number1 :
            contact_number1 = employee_id.contact_number1
        else :
            contact_number1 = post.get('contact_number1') or None
            
        if employee_id.contact_number2 :
            contact_number2 = employee_id.contact_number2
        else :
            contact_number2 = post.get('contact_number2') or None
            
        if employee_id.contact_number3 :
            contact_number3 = employee_id.contact_number3
        else :
            contact_number3 = post.get('contact_number3') or None
            
        if employee_id.isd_contact_number1 :
            isd_contact_number1 = employee_id.isd_contact_number1
        else :
            isd_contact_number1 = post.get('isd_contact_number1') or None
            
        if employee_id.isd_contact_number2 :
            isd_contact_number2 = employee_id.isd_contact_number2
        else :
            isd_contact_number2 = post.get('isd_contact_number2') or None
            
        if employee_id.isd_contact_number3 :
            isd_contact_number3 = employee_id.isd_contact_number3
        else :
            isd_contact_number3 = post.get('isd_contact_number3') or None
            
        if employee_id.khda_moe_approval :
            khda_moe_approval = employee_id.khda_moe_approval
        else :
            khda_moe_approval = post.get('khda_moe_approval') or None
            
        if employee_id.grade :
            grade = employee_id.grade
        else :
            grade = post.get('grade') or None
            
        if employee_id.work_experience :
            work_experience = employee_id.work_experience
        else :
            work_experience = post.get('work_experience') or None
            
        if employee_id.working_with_other_org :
            working_with_other_org = employee_id.working_with_other_org
        else :
            working_with_other_org = post.get('working_with_other_org') or None
        
        if employee_id.country_id :
            nationality = employee_id.country_id.id
        else :
            nationality = post.get('nationality') or None
            
        if employee_id.notice_period :
            notice_period = employee_id.notice_period
        else :
            notice_period = post.get('notice_period') or None
            
        if employee_id.document_name :
            document_name = employee_id.document_name
        else :
            document_name = post.get('document_name') or None
            
        if employee_id.designation :
            designation = employee_id.designation
        else :
            designation = post.get('designation') or None

        if employee_id.please_specify :
            please_specify = employee_id.please_specify
        else :
            please_specify = post.get('please_specify') or None
            
        if employee_id.is_medical_condition_suffering :
            is_medical_condition_suffering = employee_id.is_medical_condition_suffering
        else :
            is_medical_condition_suffering = post.get('is_medical_condition_suffering') or None
        
        if employee_id.current_employer :
            current_employer = employee_id.current_employer
        else :
            current_employer = post.get('current_employer') or None
           
        if employee_id.is_highest_degree_certificate_attached :
            is_highest_degree_certificate_attached = employee_id.is_highest_degree_certificate_attached
        else :
            is_highest_degree_certificate_attached = post.get('is_highest_degree_certificate_attached') or None
            
        if employee_id.uae_visa :
            uae_visa = employee_id.uae_visa
        else :
            uae_visa = post.get('uae_visa') or None
            
        if employee_id.current_salary :
            current_salary = employee_id.current_salary
        else :
            current_salary = post.get('current_salary') or None
            
        if employee_id.is_highest_degree_certificate_attached :
            is_highest_degree_certificate_attached = employee_id.is_highest_degree_certificate_attached
        else :
            is_highest_degree_certificate_attached = post.get('is_highest_degree_certificate_attached') or None
            
        employee_data = {
                            #personal details
                            'name' : name,
                            'middle_name' : middle_name,
                            'last_name' : last_name,
                            'work_email' : post.get('work_email') or None,
                            'email_id' : post.get('email_id') or None,
                            'birthday' : birthday,
                            'marital' : marital,
                            'current_salary' : current_salary,
                            'currency' : currency,
                            'birth_country' : birth_country,
                            'birth_city' : birth_city,
                            'current_location' : current_location,
                            'contact_number1': contact_number1,
                            'contact_number2': contact_number2,
                            'contact_number3': contact_number3,
                            'isd_contact_number1': isd_contact_number1,
                            'isd_contact_number2': isd_contact_number2,
                            'isd_contact_number3': isd_contact_number3,
                            #passport details
                            'passport_issue_date' : passport_issue_date,
                            'passport_expiry_date' : passport_expiry_date,
                            'passport_issue_place' : passport_issue_place,
                            'passport_number': passport_number,
                            #other details
                            'is_permanent_address_same' : post.get('is_permanent_address_same'),
                            'is_highest_degree_certificate_attached' : is_highest_degree_certificate_attached,
                            'working_with_other_org' : working_with_other_org,
                            'current_employer' : current_employer,
                            'labour_card_exist' : post.get('labour_card_exist'),
                            'emirates_id_exist' : post.get('emirates_id_exist'),
                            'uae_visa' : uae_visa,
                            'attested_doc': attested_doc, 
                            'document_issue_date' : document_issue_date,
                            'document_expiry_date' : document_expiry_date,
                            'medical_condition' : medical_condition,
                            'khda_moe_approval': khda_moe_approval, 
                            'grade': grade,
                            'work_experience': work_experience,
                            'country_id': nationality, 
                            'notice_period': notice_period, 
                            'document_name': document_name,
                            'designation': designation,
                            'please_specify': please_specify,
                            'is_medical_condition_suffering': is_medical_condition_suffering,
                            'current_employer': current_employer,
                            'employment_form_filled' : True,
                            'last_update_date' : date.today().strftime('%Y-%m-%d'),
                            'employee_state' : 'validate',
                            'is_highest_degree_certificate_attached' : is_highest_degree_certificate_attached,
                            #photo details
                            'image_medium' : image_medium,
                            #permanent address
                            'permnent_street' : permnent_street,
                            'permnent_street2' : permnent_street2,
                            'permnent_nearest_landmark' : permnent_nearest_landmark,
                            'permnent_city' : permnent_city,
                            'permnent_state_id' : permnent_state_id,
                            'permnent_zip' : permnent_zip,
                            'permnent_country_id' : permnent_country_id,
                            #current address
                            'current_street' : post.get('current_street') or None,
                            'current_street2' : post.get('current_street2') or None,
                            'current_nearest_landmark' : post.get('current_nearest_landmark') or None,
                            'current_city' : post.get('current_city') or None,
                            'current_state_id' : post.get('current_state_id') or None,
                            'current_zip' : post.get('current_zip') or None,
                            'current_country_id' : post.get('current_country_id') or None,
                         }
        #print '---------------------------------employee_data---------', employee_data
        employee_id.sudo().write(employee_data)
        
        #-----------------------------------------START : Depenedant Details---------------------------------
        dependant_details = {}
        for i in range(5) :
            date_of_birth_dependent = post.get('date_of_birth_dependent%s'%str(i+1)) or None
            if date_of_birth_dependent:
                date_of_birth_dependent = datetime.strptime(str(date_of_birth_dependent), "%d/%m/%Y")
            dependant_details = {
                                 'full_name': post.get('full_name_dependent%s'%str(i+1)) or None, 
                                 'date_of_birth': date_of_birth_dependent,
                                 'relationship_with_dependant' : post.get('relationship_dependent%s'%str(i+1)) or None, 
                                 'employee_id' : employee_id.id,
                                 }
            if dependant_details['date_of_birth'] and  dependant_details['full_name'] and dependant_details['relationship_with_dependant'] :
                dependant_id  = env['dependant.obj'].sudo().create(dependant_details)
            
        #-----------------------------------------END : Depenedant Details---------------------------------
        
        #-------------------------------------------START : Employee Qualification-----------------------------
        employee_qualification_details = {}
        for i in range(4) :
            degree = post.get('degree%s'%str(i+1)) or None 
            university_name = post.get('university_name%s'%str(i+1)) or None
            year = post.get('year%s'%str(i+1)) or None
            employee_qualification_details = {
                                 'university_name': university_name, 
                                 'degree': degree, 
                                 'year': year, 
                                 'employee_id' : employee_id.id,
                                 }
            if university_name and degree and year :
                employee_qualification_id  = env['employee.qualification'].sudo().create(employee_qualification_details)
        #-------------------------------------------END : Employee Qualification-----------------------------
        
        #-------------------------------------START : Doc Attachment------------------------------------------
        
        
        passport_copy =  post.get('passport_copy') or None
        if passport_copy :
            passport_copy_filename = str(passport_copy.filename)
            old_passport_copy_filename = passport_copy_filename.split('.')[0]
            new_passport_copy_filename  =  passport_copy_filename.replace(old_passport_copy_filename, 'Passport')
            ir_attachment.sudo().create({'name': new_passport_copy_filename,
                                               'datas_fname': passport_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(passport_copy.read()),
                                               })
            
        certificates_copy =  post.get('certificates_copy') or None
        if certificates_copy :
            certificates_copy_filename = str(certificates_copy.filename)
            old_certificates_copy_filename = certificates_copy_filename.split('.')[0]
            new_certificates_copy_filename  =  certificates_copy_filename.replace(old_certificates_copy_filename, 'Certificates')
            ir_attachment.sudo().create({'name': new_certificates_copy_filename,
                                               'datas_fname': certificates_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(certificates_copy.read()),
                                               })
             
        relieveing_letter_copy =  post.get('relieveing_letter_copy') or None
        if relieveing_letter_copy :
            relieveing_letter_copy_filename = str(relieveing_letter_copy.filename)
            old_relieveing_letter_copy_filename = relieveing_letter_copy_filename.split('.')[0]
            new_relieveing_letter_copy_filename  =  relieveing_letter_copy_filename.replace(old_relieveing_letter_copy_filename, 'Relieving Letter')
            ir_attachment.sudo().create({'name': new_relieveing_letter_copy_filename,
                                               'datas_fname': relieveing_letter_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(relieveing_letter_copy.read()),
                                               })
                
        salary_certificate_copy =  post.get('salary_certificate_copy') or None
        if salary_certificate_copy :
            salary_certificate_copy_filename = str(salary_certificate_copy.filename)
            old_salary_certificate_copy_filename = salary_certificate_copy_filename.split('.')[0]
            new_salary_certificate_copy_filename  =  salary_certificate_copy_filename.replace(old_salary_certificate_copy_filename, 'Salary Certificate')
            ir_attachment.sudo().create({'name': new_salary_certificate_copy_filename,
                                               'datas_fname': salary_certificate_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(salary_certificate_copy.read()),
                                               })
            
        ##########ir attachment###resume_copy#######3
        resume_copy =  post.get('resume_copy') or None  
        if resume_copy : 
            resume_copy_filename = str(resume_copy.filename)
            old_resume_copy_filename = resume_copy_filename.split('.')[0]
            new_resume_copy_filename  =  resume_copy_filename.replace(old_resume_copy_filename, 'Resume')
            ir_attachment.sudo().create({'name': new_resume_copy_filename,
                                               'datas_fname': resume_copy.filename,
                                               'res_model': employee_id._name,
                                               'res_id': employee_id.id,
                                               'datas': base64.encodestring(resume_copy.read()),
                                               })
                
                
        certificates_copy1 =  post.get('certificates_copy1') or None  
        if certificates_copy1 : 
            certificate_name1 = post.get('certificate_name1') or None
            if certificate_name1:
                c_filename1 = str(certificates_copy1.filename)
                old_certificate_name1 = c_filename1.split('.')[0]
                new_certificate_name1 =  c_filename1.replace(old_certificate_name1, certificate_name1)
                temp = ir_attachment.sudo().create({
                                                        'name': new_certificate_name1,
                                                       'datas_fname': certificates_copy1.filename,
                                                       'res_model': employee_id._name,
                                                       'res_id': employee_id.id,
                                                       'datas': base64.encodestring(certificates_copy1.read()),
                                                       })

        certificates_copy2 =  post.get('certificates_copy2') or None
        if certificates_copy2 : 
            certificate_name2 = post.get('certificate_name2') or None 
            if certificate_name2: 
                c_filename2 = str(certificates_copy2.filename)
                old_certificate_name2 = c_filename2.split('.')[0]
                new_certificate_name2 =  c_filename1.replace(old_certificate_name2, certificate_name2)
                temp = ir_attachment.sudo().create({
                                                        'name': new_certificate_name2,
                                                       'datas_fname': certificates_copy2.filename,
                                                       'res_model': employee_id._name,
                                                       'res_id': employee_id.id,
                                                       'datas': base64.encodestring(certificates_copy2.read()),
                                                       })

        certificates_copy3 =  post.get('certificates_copy3') or None  
        if certificates_copy3 : 
            certificate_name3 = post.get('certificate_name3') or None  
            if certificate_name3 :
                c_filename3 = str(certificates_copy3.filename)
                old_certificate_name3 = c_filename3.split('.')[0]
                new_certificate_name3 =  c_filename3.replace(old_certificate_name3, certificate_name3)
                temp = ir_attachment.sudo().create({
                                                        'name': new_certificate_name3,
                                                       'datas_fname': certificates_copy3.filename,
                                                       'res_model': employee_id._name,
                                                       'res_id': employee_id.id,
                                                       'datas': base64.encodestring(certificates_copy3.read()),
                                                       })
            
        certificates_copy4 =  post.get('certificates_copy4') or None  
        if certificates_copy4 : 
            certificates_copy4 = post.get('certificate_name4') or None  
            if certificates_copy4 :
                c_filename4 = str(certificates_copy4.filename)
                old_certificate_name4 = c_filename4.split('.')[0]
                new_certificate_name4 =  c_filename4.replace(old_certificate_name4, certificate_name4)
                ir_attachment.sudo().create({
                                                       'name': new_certificate_name4,
                                                       'datas_fname': certificates_copy4.filename,
                                                       'res_model': employee_id._name,
                                                       'res_id': employee_id.id,
                                                       'datas': base64.encodestring(certificates_copy4.read()),
                                                       })
        
        #-------------------------------------END : Doc Attachment Completed------------------------------------------
        
        return request.render("edsys_hrm.employement_verification_template",{})
    
    
         
         