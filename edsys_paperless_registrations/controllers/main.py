from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import base64
from datetime import date,datetime,timedelta
from odoo import models, fields, api, _
import time
from odoo.addons.website_student_enquiry.controllers.main import WebsiteStudentEnquiry as StudentEnquiry

class WebsiteStudentPaperLess(StudentEnquiry):

    @http.route([
        '/student/verification',
    ], type='http', auth="public", website=True, csrf=False)
    def render_student_verification(self, **post):
        """
        inherit render_student_verification method,
        student additional form should student admission form.
        ------------------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : booleab(True)
        @return :
        """
        if 'DATE' in post and post['DATE']:
            data = post['DATE']
            link_date = self.decode_base64(data)
            if link_date == '':
                return request.render("website_student_enquiry.student_link_expired_templet",{})
            if 'ENQUIRY' in post and post['ENQUIRY']:
                eq_no = str(post['ENQUIRY'])
                env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
                reg_obj = env['registration']
                reg_rec = reg_obj.sudo().search([('enquiry_no','=',eq_no)],limit=1)
                if reg_rec.id:
                    if reg_rec.add_form_filled != True:
                        if link_date != '0000-00-00':
                            s_date = datetime.strptime(link_date, '%Y-%m-%d').date()
                            l_date = s_date + timedelta(days=10)
                            c_date = date.today()
                            if s_date <= c_date < l_date:
                                if 'ENQUIRY' in post and post['ENQUIRY']:
                                    student_obj = env['res.partner']
                                    student_rec = student_obj.sudo().search(['|',('active','=',True),
                                                                             ('strike_off','=',True),
                                                                             ('is_student','=',True),
                                                                             ('reg_no','=',eq_no)],limit=1)
                                    if student_rec.id:
                                        e_student_id = base64.b64encode(str(student_rec.id))
                                        return request.redirect(
                                            "/student/verification/pagecode?student_id=%s" % (e_student_id))
                            else:
                                return request.render("website_student_enquiry.student_link_expired_templet",{})
                        else:
                            if 'ENQUIRY' in post and post['ENQUIRY']:
                                eq_no = str(post['ENQUIRY'])
                                env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
                                student_obj = env['res.partner']
                                student_rec = student_obj.sudo().search(['|',('active','=',True),
                                                                         ('strike_off','=',True),
                                                                         ('is_student','=',True),
                                                                         ('reg_no','=',eq_no)],limit=1)
                                if student_rec.id:
                                    e_student_id = base64.b64encode(str(student_rec.id))
                                    return request.redirect(
                                        "/student/verification/pagecode?student_id=%s" % (e_student_id))
                    else:
                        return request.render("website_student_enquiry.student_link_expired_templet",{})

    @http.route([
        '/student/verification/pagecode',
    ], type='http', auth="public", website=True, csrf=False)
    def render_student_pagecode(self, **post):
        """
        this method should be redirect particuler page
        with proper data.
        ----------------------------------------------
        :param post:
        :return:
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        print env
        student_obj = env['res.partner']
        country_obj = env['res.country']
        religion_obj = env['religion']
        language_obj = env['res.lang']
        batch_obj = env['batch']
        country_rec_list = []
        religion_rec_list = []
        language_rec_list = []
        for country_rec in country_obj.sudo().search([]):
            country_rec_list.append(country_rec)
        for reg_rec in religion_obj.sudo().search([]):
            religion_rec_list.append(reg_rec)
        for lang_rec in language_obj.sudo().search([]):
            language_rec_list.append(lang_rec)
        if post.get('student_id') and not post.get('page_code'):
            student_id = self.decode_base64(post.get('student_id'))
            student_rec = student_obj.sudo().browse(int(student_id))
            if not student_rec.default_page:
                return request.render("edsys_paperless_registrations.student_other_information",{
                                      'student_rec' : student_rec,
                                      'page_code' : '0',
                                    })
            if not student_rec.is_fill_page1:
                lang_spoken_at_home_list = []
                for lang_rec in student_rec.lang_spoken_at_home:
                    lang_spoken_at_home_list.append(lang_rec.id)
                return request.render("edsys_paperless_registrations.student_other_information_page1",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'religion_rec_list' : religion_rec_list,
                    'language_rec_list' : language_rec_list,
                    'lang_spoken_at_home_list' : lang_spoken_at_home_list,
                    'page_code' : '1',
                })
            if not student_rec.is_fill_page2:
                return request.render("edsys_paperless_registrations.student_other_information_page2",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'page_code' : '2',
                })
            if not student_rec.is_fill_page3:
                course_rec_list = []
                for batch_rec in batch_obj.sudo().search([('id','=',student_rec.batch_id.id)]):
                    for class_rec in batch_rec.course_ids:
                        course_rec_list.append(class_rec)
                return request.render("edsys_paperless_registrations.student_other_information_page3",{
                    'student_rec' : student_rec,
                    'language_rec_list' : language_rec_list,
                    'course_rec_list' : course_rec_list,
                    'page_code' : '3',
                })
            if not student_rec.is_fill_page4:
                return request.render("edsys_paperless_registrations.student_other_information_page4",{
                    'student_rec' : student_rec,
                    'page_code' : '4',
                })
            if not student_rec.is_fill_page5:
                return request.render("edsys_paperless_registrations.student_other_information_page5",{
                    'student_rec' : student_rec,
                    'page_code' : '5',
                })
            if not student_rec.is_fill_page6:
                return request.render("edsys_paperless_registrations.student_other_information_page6",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'page_code' : '6',
                })
        if post.get('student_id') and post.get('page_code'):
            student_id = self.decode_base64(post.get('student_id'))
            student_rec = student_obj.sudo().browse(int(student_id))
            page_code = self.decode_base64(post.get('page_code'))
            if post.get('page_code') and int(page_code) == 0:
                return request.render("edsys_paperless_registrations.student_other_information",{
                                      'student_rec' : student_rec,
                                      'page_code' : '0',
                                    })
            if post.get('page_code') and int(page_code) == 1:
                lang_spoken_at_home_list = []
                for lang_rec in student_rec.lang_spoken_at_home:
                    lang_spoken_at_home_list.append(lang_rec.id)
                return request.render("edsys_paperless_registrations.student_other_information_page1",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'religion_rec_list' : religion_rec_list,
                    'language_rec_list' : language_rec_list,
                    'lang_spoken_at_home_list' : lang_spoken_at_home_list,
                    'page_code' : '1',
                })
            if post.get('page_code') and int(page_code) == 2:
                return request.render("edsys_paperless_registrations.student_other_information_page2",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'page_code' : '2',
                })
            if post.get('page_code') and int(page_code) == 3:
                course_rec_list = []
                for batch_rec in batch_obj.sudo().search([('id','=',student_rec.batch_id.id)]):
                    for class_rec in batch_rec.course_ids:
                        course_rec_list.append(class_rec)
                return request.render("edsys_paperless_registrations.student_other_information_page3",{
                    'student_rec' : student_rec,
                    'language_rec_list' : language_rec_list,
                    'course_rec_list' : course_rec_list,
                    'page_code' : '3',
                })
            if post.get('page_code') and int(page_code) == 4:
                return request.render("edsys_paperless_registrations.student_other_information_page4",{
                    'student_rec' : student_rec,
                    'page_code' : '4',
                })
            if post.get('page_code') and int(page_code) == 5:
                return request.render("edsys_paperless_registrations.student_other_information_page5",{
                    'student_rec' : student_rec,
                    'page_code' : '5',
                })
            if post.get('page_code') and int(page_code) == 6:
                return request.render("edsys_paperless_registrations.student_other_information_page6",{
                    'student_rec' : student_rec,
                    'country_rec_list' : country_rec_list,
                    'page_code' : '6',
                })

    @http.route([
    '/student/verification/previous',
    ], type='http', auth="public", website=True)
    def render_previous_page(self, **post):
        """
        this method is use to move privious page,
        -----------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return :
        """
        if post.get('page_code') and post.get('student_id'):
            e_page_code = base64.b64encode(str(post.get('page_code')))
            e_student_id = base64.b64encode(str(post.get('student_id')))
            return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page_default',
    ], type='http', auth="public", website=True, csrf=False)
    def render_page_default(self, **post):
        print '===============post'
        """
        this method use to save default form data in
        database, and redirect to next page,
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        attach_obj = env['ir.attachment']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            parent_data = {
                'parents_email' : post.get('Father_Email') or '',
                'parents_office_contact' : post.get('office_no') or '',
                'street' : post.get('parents_address') or '',
                'mother_profession' : post.get('mother_profession') or '',
                'mother_contact' : post.get('mother_mobile_no') or '',
                'mother_office_contact' : post.get('mother_tel_no') or '',
                'mother_email' : post.get('mother_email') or '',
                'mother_address' : post.get('mother_address') or '',
                'emergency_contact' : post.get('emergency_mobile_no') or '',
            }
            for document,values in {'f_visa_copy1':'parent_visa_copy','f_emirates_copy1':'f_emirates_copy1',
                                    'f_emirates_copy2':'f_emirates_copy2','m_visa_copy1':'mother_visa_copy',
                                    'm_emirates_copy1':'m_emirates_copy1','m_emirates_copy2':'m_emirates_copy2'}.items():
                if post.get(document):
                    parent_data.update({values:base64.encodestring(post[document].read())})
            child_allergic = False
            under_medication = False
            if post.get('allergic') == 'y':
                child_allergic = True
            if post.get('under_medication') == 'y':
                under_medication = True
            student_data = {
                'emirati' : post.get('Emirati') or '',
                'arab' : post.get('Arab_v') or '',
                'emirates_id' : post.get('Emirates_id') or '',
                'blood_group' : post.get('Blood_Group') or '',
                's_height' : post.get('S_Height') or '',
                's_width' : post.get('S_Width') or '',
                'child_allergic' : child_allergic or False,
                'w_allergic' : post.get('yes_allergic') or '',
                'w_reaction' : post.get('reaction') or '',
                'w_treatment' : post.get('treatment') or '',
                'under_medication' : under_medication or False,
                'mention' : post.get('w_medication_mention') or '',
                'w_treatment_mention' : post.get('w_treatment') or '',
                'isd_code' : post.get('Isd_Code') or '',
                'mobile' : post.get('S_Mobile') or '',
                'transport_type' : post.get('transport_type') or '',
                'pick_up' : post.get('pick_up') or '',
                'droup_off_pick' : post.get('droup_off') or '',
            }
            for sdocument,svalues in {'transfer_certi':'transfer_certificate','s_emirates_copy1':'s_emirates_copy1',
                                      's_emirates_copy2':'s_emirates_copy2','s_pass_copy1':'passport_copy1',
                                      's_pass_copy2':'passport_copy2','s_visa':'medical_documents_file'}.items():
                if post.get(sdocument):
                    student_data.update({svalues:base64.encodestring(post[sdocument].read())})

            student_rec.sudo().write(student_data)
	    reg_obj = env['registration']            
	    reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)            
	    reg_rec.sudo().write(student_data)
            student_rec.parents1_id.sudo().write(parent_data)
            for get_file in ['transfer_certi','s_visa','s_emirates_copy1','s_emirates_copy2','s_pass_copy1','s_pass_copy2']:
                attachment_value = {}
                if get_file in post and post[get_file]:
                    attachment_value = {
                        'type':'binary',
                        'name': post[get_file].filename,
                        'res_name': 'demo01',
                        'res_model': 'res.partner',
                        # 'res_id': stud_rec.id,
                        'datas': base64.encodestring(post[get_file].read()),
                        'datas_fname': post[get_file].filename,
                    }
                    attach_obj.sudo().create(attachment_value)

            for get_f_file in ['f_visa_copy1','f_emirates_copy1','f_emirates_copy2','m_visa_copy1','m_emirates_copy1','m_emirates_copy2']:
                attachment_value = {}
                if 'get_f_file' in post and post['get_f_file']:
                    res_name = ""
                    if get_f_file in ['f_visa_copy1','f_emirates_copy1','f_emirates_copy2']:
                        res_name = student_rec.parents1_id.name
                    else:
                        res_name = student_rec.parents1_id.mother_name

                    attachment_value = {
                        'type':'binary',
                        'name': post[get_file].filename,
                        'res_name': res_name,
                        'res_model': 'res.partner',
                        # 'res_id': stud_rec.parents1_id.id,
                        'datas': base64.encodestring(post[get_file].read()),
                        'datas_fname': post[get_file].filename,
                    }
                    attach_obj.sudo().create(attachment_value)
        e_page_code = base64.b64encode('1')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page1',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page1(self, **post):
        """
        this method use to save first form data in
        database, and redirect to next page,
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            image = ''
            if post.get('Student_Photo'):
                image = base64.encodestring(post.get('Student_Photo').read()) or ''
            else:
                image = student_rec.image
            lang_spoken_home_ids = []
            if post.get('id_Lang_Spoken_Home_value') != '':
                for lang_id in post.get('id_Lang_Spoken_Home_value').split(','):
                    lang_spoken_home_ids.append(lang_id)
            # import ipdb;ipdb.set_trace()
            student_data = {
                'image' : image or '',
                'name':post.get('First_Name') or '',
                'middle_name':post.get('Middle_Name') or '',
                'last_name':post.get('Last_Name') or '',
                'birth_place':post.get('Place_of_Birth') or '',
                'gender':post.get('Gender') or 'm',
                'nationality' : post.get('Nationality') or '',
                'religion_id': post.get('Religion') or '',
                'lang_id' : post.get('Mother_Tongue') or '',
                'passport_no' : post.get('Passport_No') or '',
                'place_of_issue' : post.get('Pass_Place_of_issue') or '',
                'passport_issue_date' : post.get('Pass_Date_of_issue') or False,
                'passport_expiry_date' : post.get('Pass_Date_of_Expiry') or False,
                'visa_no' : post.get('Visa_Number') or '',
                'visa_issue_date' : post.get('Visa_Date_of_Issue') or False,
                'visa_expiry_date' : post.get('Visa_Date_of_Exp') or False,
                'emirates_id' : post.get('Emirates_Id') or '',
                'email' : post.get('S_Email') or '',
                'street' : post.get('Residential_Address') or '',
                'postal_address' : post.get('Postal_Address') or '',
                'mobile' : post.get('S_Mobile') or '',
                'student_is_living_with' : post.get('Student_is_Living_With') or '',
                # 'language_spoken_at_home' : [(6,0,lang_spoken_home_ids)],
                'english_is_spoken_at_home' : post.get('Eng_Spik_Home') or '',
                'english_written' : post.get('Written'),
                'english_spoken' : post.get('Spoken'),
                'english_reading' : post.get('Reading'),
            }
            student_rec.sudo().write(student_data)
	    reg_obj = env['registration']            
	    reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)            
	    reg_rec.sudo().write(student_data)
            student_rec.lang_spoken_at_home = [(6, 0, lang_spoken_home_ids)]

        e_page_code = base64.b64encode('2')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page2',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page2(self, **post):
        """
        this method store data from current(2) page,
        and redirect to page next page(3)
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return :
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            parent_data = {
                'name' : post.get('Father_name') or '',
                'father_nationality' : post.get('Father_Nationality') or '',
                'father_passport' : post.get('Father_Passport') or '',
                'father_emirates_id' : post.get('Father_Emirates_Id') or '',
                'parent_profession' : post.get('Father_Designation') or '',
                'parent_address' : post.get('Parent_Address') or '',
                'parents_office_contact' : post.get('Parents_Office_Contact') or '',
                'parent_contact' : post.get('Parent_Contact') or '',
                'parents_email' : post.get('Parents_Email') or '',
                'mother_name' : post.get('Mother_Name') or '',
                'mother_nationality' : post.get('Mother_Nationality') or '',
                'mother_passport' : post.get('Mother_Passport') or '',
                'mother_emirates_id' : post.get('Mother_Emirates_Id') or '',
                'mother_profession' : post.get('Mother_Designation') or '',
                'mother_address' : post.get('Mother_Address') or '',
                'mother_office_contact' : post.get('Mother_Office_Contact') or '',
                'mother_contact' : post.get('Mother_Contact') or '',
                'mother_email' : post.get('Mother_Email') or '',
                'spe_contribution' : post.get('Special_Contribution') or '',
                'special_contribution_any_other' : post.get('Special_Contribution_Any_Other') or '',
            }
            student_rec.parents1_id.sudo().write(parent_data)
        e_page_code = base64.b64encode('3')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page3',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page3(self, **post):
        """
        this method store data from current(3) page,
        and redirect to page next page(4)
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return :
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            Special_Learning_Disability_Details = False
            if post.get('Special_Learning_Disability'):
                Special_Learning_Disability_Details = post.get('Special_Learning_Disability_Details')
            student_data = {
                'prev_institute': post.get('Current_School_Name') or '',
                'prev_academic_city': post.get('Prev_Academic_City') or '',
                'curriculum': post.get('Curriculum') or '',
                'medium_of_instruction': post.get('Medium_of_Instruction') or '',
                'last_attendance': post.get('Last_Attendance_Date') or False,
                'tranfer_reason': post.get('Reason_for_Transfer') or '',
                'received_double_promotion': post.get('Received_Double_Promotion') or '',
                'identified_gifted_or_talented': post.get('Identified_Gifted_or_Talented') or '',
                'has_child_detained': post.get('Has_Child_Detained') or '',
                'child_received_academic_distinction': post.get('Child_Received_Academic_Distinction') or '',
                'child_received_academic_distinction_details': post.get(
                    'Child_Received_Academic_Distinction_Details') or '',
                'has_suspended_expelled_by_school' : post.get('Has_Suspended_Expelled_by_School') or '',
                'has_suspended_expelled_by_school_details' : post.get('Has_Suspended_Expelled_by_School_Details') or '',
                'child_associated_with_awareness' : post.get('Child_Associated_with_Awareness') or '',
                'child_associated_with_awareness_details' : post.get('Child_Associated_with_Awareness_Details') or '',
                'member_of_environment_protection' : post.get('Member_of_Environment_Protection') or '',
                'member_of_environment_protection_details' : post.get('Member_of_Environment_Protection_Details') or '',
                'leadership_positions_in_school' : post.get('Leadership_Positions_in_School') or '',
                'leadership_positions_in_school_details' : post.get('Leadership_Positions_in_School_Details') or '',
                'special_education_programme' : post.get('Special_Education_Programme') or '',
                'special_education_programme_details' : post.get('Special_Education_Programme_Details') or '',
                'special_learning_disability' : post.get('Special_Learning_Disability') or False,
                'special_learning_disability_details' : Special_Learning_Disability_Details or False,
                'has_other_than_english_languages' : post.get('Has_Other_than_English_Languages') or '',
                'other_than_english_languages' : post.get('Other_than_English_Languages') or '',
                'other_lang_id' : post.get('Optional_Lang') or '',
                'has_child_detained_grade' : post.get('Has_Child_Detained_Grade') or '',
            }
            student_rec.sudo().write(student_data)
	    reg_obj = env['registration']            
	    reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)            
	    reg_rec.sudo().write(student_data)
        e_page_code = base64.b64encode('4')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    def get_check_box_value(self,get_check):
        """
        get and verify check box value and
        return Boolean
        ----------------------------------
        :param get_check: get checkbox
                value from webform
        :return: return boolean value
        """
        if get_check == 'on':
            return True
        else:
            return False


    @http.route([
    '/otherinformation/page4',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page4(self, **post):
        """
        this method store data from current(4) page,
        and redirect to page next page(5)
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return :
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            student_data = {
                'hobbies_interests': post.get('Hobbies_Interests') or '',
                'has_play_any_musical_instrument': post.get('Has_Play_any_Musical_Instrument') or '',
                'musical_instrument_details': post.get('Musical_Instrument_Details') or '',
                'has_formal_training_in_music': post.get('Has_Formal_Training_in_Music') or '',
                'training_in_music_details': post.get('Training_in_Music_Details') or '',
                'sport_child_play': post.get('Sport_Child_Play') or '',
                'has_training_or_interest_art': post.get('Has_Training_or_Interest_Art') or '',
                'has_training_or_interest_art_details': post.get('Training_or_Interest_Art_Details') or '',
                'inter_school_competitions': post.get('Inter_School_Competitions') or '',
                'inter_school_competitions_details': post.get('Inter_School_Competitions_Details') or '',
                'special_activity_interested': post.get('Special_Activity_Interested') or '',
                'adjusts_new_situations_with_ease': self.get_check_box_value(
                    post.get('Adjusts_New_Situations_with_Ease')) or '',
                'has_small_group_of_friends': self.get_check_box_value(
                    post.get('Has_Small_Group_of_Friends')) or '',
                'has_never_adjust_new_situation': self.get_check_box_value(
                    post.get('Has_Never_Adjust_New_Situation')) or '',
                'has_many_friends': self.get_check_box_value(
                    post.get('Has_Many_Friends')) or '',
                'likes_be_active_in_school': self.get_check_box_value(
                    post.get('Likes_be_Active_in_School')) or '',
                'expressions_describe_your_child': post.get('Expressions_Describe_your_Child') or '',
                'social_emotional_behavioural_difficulties': post.get('Social_Emotional_Behavioural_Difficulties') or '',
                'social_emotional_behavioural_difficulties_details': post.get(
                    'Social_Emotional_Behavioural_Difficulties_Details') or '',
                'useful_information_for_educating': post.get('Useful_Information_for_Educating') or '',
                'person_to_call' : post.get('Person_to_Call') or '',
                'emergency_relationship' : post.get('Emergency_Relationship') or '',
                'emergency_contact' : post.get('Emergency_Tel_No') or '',
                'has_use_bus_facility' : post.get('Has_Use_Bus_Facility') or '',
                'pick_up' : post.get('Pick_Up') or '',
            }
            student_rec.sudo().write(student_data)
	    reg_obj = env['registration']            
	    reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)            
	    reg_rec.sudo().write(student_data)
        e_page_code = base64.b64encode('5')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page5',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page5(self, **post):
        """
        this method store data from current(5) page,
        and redirect to page next page(6)
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            under_medi = False
            if post.get('Under_Medication') == True or post.get('Under_Medication') == 'True':
                under_medi = True
            student_data = {
                'normal_delivery' : post.get('Normal_Delivery') or '',
                'caesarean' : post.get('Caesarean') or '',
                'premature' : post.get('Premature') or '',
                # 'developmental_milestones' : post.get('Developmental_Milestones') or '',
                'age_your_child_talk' : post.get('Age_Your_Child_Talk') or '',
                'hand_preference' : post.get('Hand_Preference') or '',
                'can_button_his_shirt' : post.get('Can_Button_his_Shirt') or '',
                'can_zip_his_pant' : post.get('Can_Zip_his_Pant') or '',
                'can_child_indicate_his_toilet_needs' : post.get('Can_Child_Indicate_his_Toilet_Needs') or '',
                'child_indicate_his_toilet_needs_details' : post.get('Child_Indicate_his_Toilet_Needs_Details') or '',
                'child_know_his_phone_number' : post.get('Child_Know_his_Phone_Number') or '',
                'toys_likes_to_play_with' : post.get('Toys_Likes_to_Play_With') or '',
                'special_interest' : post.get('Special_Interest') or '',
                'child_like_to_play_with' : post.get('Child_Like_to_Play_With') or '',
                'child_like_to_look_at_picture' : post.get('Child_Like_to_Look_at_Picture') or '',
                'child_like_to_watch_tv_programmes' : post.get('Child_Like_to_Watch_TV_Programmes') or '',
                'channels_like_to_watch' : post.get('Channels_Like_to_Watch') or '',
                'child_have_any_health_problem' : post.get('Child_Have_Any_Health_Problem') or '',
                'health_problem_details' : post.get('Health_Problem_Details') or '',
                'under_medication' : under_medi or False,
                'w_medication_mention' : post.get('W_Medication_Mention') or '',
            }
            student_rec.sudo().write(student_data)
	    reg_obj = env['registration']            
	    reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)            
	    reg_rec.sudo().write(student_data)
        e_page_code = base64.b64encode('6')
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/pagecode?page_code=%s&student_id=%s" % (e_page_code,e_student_id))

    @http.route([
    '/otherinformation/page6',
    ], type='http', auth="public", website=True,csrf=False)
    def render_page6(self, **post):
        """
        this method store data from current(6) page,
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(post.get('student_id')))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            parents_data = {
                'name' : post.get('Father_Name') or '',
                'mother_name' : post.get('Mother_Name') or '',
                'parents_office_contact' : post.get('Parents_Office_Contact') or '',
                'parent_contact' : post.get('F_Mobile') or '',
                'mother_contact' : post.get('Mother_Contact') or '',
            }
            student_data = {
                'health_card_no' : post.get('Health_Card_No') or '',
                'street' : post.get('Residential_Address') or '',
                'mobile' : post.get('S_Mobile') or '',
                'prev_institute' : post.get('Previous_School_Name') or '',
                'prev_academic_country' : post.get('Prev_Academic_Country') or '',
                'diphtheria' : post.get('Diphtheria') or '',
                'accident' : post.get('Accident') or '',
                'dysentery' : post.get('Dysentery') or '',
                'allergies' : post.get('Allergies') or '',
                'infective_hepatitis' : post.get('Infective_Hepatitis') or '',
                'bronchial_asthma' : post.get('Bronchial_Asthma') or '',
                'measles' : post.get('Measles') or '',
                'congenital_heart_disease' : post.get('Congenital_Heart_Disease') or '',
                'mumps' : post.get('Mumps') or '',
                'diabetes_mellitus' : post.get('Diabetes_Mellitus') or '',
                'poliomyelitis' : post.get('Poliomyelitis') or '',
                'epilepsy' : post.get('Epilepsy') or '',
                'rubella' : post.get('Rubella') or '',
                'G6PD' : post.get('G6PD') or '',
                'scarlet_fever' : post.get('Scarlet_Fever') or '',
                'rheumatic_fever' : post.get('Rheumatic_Fever') or '',
                'tuberculosis' : post.get('Tuberculosis') or '',
                'surgical_operation' : post.get('Surgical_Operation') or '',
                'whooping_cough' : post.get('Whooping_Cough') or '',
                'thalassemia' : post.get('Thalassemia') or '',
                'chicken_pox' : post.get('Chicken_Pox') or '',
                'physically_challenged' : post.get('Physically_Challenged') or '',
                'infectious_disease_other' : post.get('Infectious_Disease_Other') or '',
                'hearing_speech_defect' : post.get('Hearing_Speech_Defect') or '',
                'vision_problems' : post.get('Vision_Problems') or '',
                'history_of_blood_transfusion' : post.get('History_Of_Blood_Transfusion') or '',
                'hospitalization' : post.get('Hospitalization') or '',
                'hospitalization_reason' : post.get('Hospitalization_Reason') or '',
                'diabetes' : post.get('Diabetes') or False,
                'HTN' : post.get('HTN') or False,
                'mental' : post.get('Mental') or False,
                # 'disorders' : post.get('Disorders') or False,
                'stroke' : post.get('Stroke') or False,
                'TB' : post.get('TB') or False,
                'HTN_other' : post.get('HTN_other') or '',
                'medicine_or_drugs' : post.get('Medicine_or_Drugs') or '',
                'medicine_or_drugs_details' : post.get('Medicine_or_Drugs_Details') or '',
                'w_medication_mention' : post.get('Medication_Mention') or '',
                'under_medication' : post.get('Under_Medication') or '',
                'give_consent_oral_analgesic' : post.get('Give_Consent_Oral_Analgesic') or '',
                'give_consent_hospital_treatment' : post.get('Give_Consent_Hospital_Treatment') or False,
                'give_consent_immunization' : post.get('Give_Consent_Immunization') or '',
                'add_form_filled' : True
            }
            student_rec.parents1_id.sudo().write(parents_data)
            student_rec.sudo().write(student_data)
            reg_obj = env['registration']
            reg_rec = reg_obj.sudo().search([('enquiry_no','=',student_rec.reg_no)],limit=1)
            reg_rec.add_form_filled = True
        e_student_id = base64.b64encode(str(post.get('student_id')))
        return request.redirect("/student/verification/success?student_id=%s" % (e_student_id))

    @http.route([
    '/student/verification/success',
    ], type='http', auth="public", website=True,csrf=False)
    def verification_success(self, **post):
        """
        ---------------------------------------------------
        :param post:
        :return:
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        e_student_id = self.decode_base64(str(post.get('student_id')))
        student_rec = student_obj.sudo().browse(int(e_student_id))
        if not student_rec.id:
            return request.redirect("/student/verification/expired")
        else:
            return request.render("edsys_paperless_registrations.paper_less_success_verification_templet",{
                'student_rec' : student_rec
            })

    @http.route([
    '/student/verification/expired',
    ], type='http', auth="public", website=True)
    def verification_expired(self, **post):
        """
        Link was expired, or student record not
        found in master then redirect to link expired page.
        ---------------------------------------------------
        :param post:
        :return:
        """

    @http.route([
    '/student/download'
    ], type='http', auth="public", website=True)
    def student_download_pdf(self, **post):
        """
        after form filup parent/student get
        PDF report containing all student releted
        information.
        -------------------------------------------
        :param post:
        :return:
        """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        student_id = post.get('student_id')
        if student_id:
            pdf = request.registry['report'].get_pdf(cr, uid, [int(student_id)],
                                                     'edsys_paperless_registrations.student_admission_report_templet',
                                                     data=None, context=context)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route([
    '/student/download/health'
    ], type='http', auth="public", website=True)
    def student_health_report_download_pdf(self, **post):
        """
        after form filup parent/student get
        PDF of Health report containing student health
        information.
        -------------------------------------------
        :param post:
        :return:
        """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        student_id = post.get('student_id')
        if student_id:
            pdf = request.registry['report'].get_pdf(cr, uid, [int(student_id)],
                                                     'edsys_paperless_registrations.student_health_report_templet',
                                                     data=None, context=context)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

    def get_page_wise_value(self, student_id, page_code):
        """
        this method is use to get student id and page code,
        based on that return page wise value in proper formate.
        -------------------------------------------------------
        :param student_id: student id
        :param page_code: page code
        :return: return list of tuple formate.
        """
        res = []
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        student_obj = env['res.partner']
        student_rec = student_obj.sudo().browse(int(student_id))
        if page_code == '0':
            res = [
                ('allergic',student_rec.child_allergic),
                ('under_medication',student_rec.under_medication),
                ('transport_type',student_rec.transport_type),
            ]
        if page_code == '3':
            res = [
                ('has_child_detained',student_rec.has_child_detained),
                ('child_received_academic_distinction',student_rec.child_received_academic_distinction),
                ('has_suspended_expelled_by_school',student_rec.has_suspended_expelled_by_school),
                ('child_associated_with_awareness',student_rec.child_associated_with_awareness),
                ('member_of_environment_protection',student_rec.member_of_environment_protection),
                ('leadership_positions_in_school',student_rec.leadership_positions_in_school),
                ('special_education_programme',student_rec.special_education_programme),
                ('special_learning_disability',student_rec.special_learning_disability),
                ('has_other_than_english_languages',student_rec.has_other_than_english_languages),
            ]
        if page_code == '4':
            res = [
                ('has_play_any_musical_instrument',student_rec.has_play_any_musical_instrument),
                ('has_formal_training_in_music',student_rec.has_formal_training_in_music),
                ('has_training_or_interest_art',student_rec.has_training_or_interest_art),
                ('inter_school_competitions',student_rec.inter_school_competitions),
                ('social_emotional_behavioural_difficulties',student_rec.social_emotional_behavioural_difficulties),
                ('has_use_bus_facility',student_rec.has_use_bus_facility),
            ]
        if page_code == '5':
            res = [
                ('can_child_indicate_his_toilet_needs',student_rec.can_child_indicate_his_toilet_needs),
                ('child_like_to_watch_tv_programmes',student_rec.child_like_to_watch_tv_programmes),
                ('child_have_any_health_problem',student_rec.child_have_any_health_problem),
                ('under_medication',student_rec.under_medication)
            ]

        return res

    @http.route([
    '/get_value_field',
    ], type='http', auth="public", website=True,csrf=False)
    def get_value_field(self, **post):
        """
        method call from javascript for get some fields value.
        ------------------------------------------------------
        :param post:
        :return: return json data
        """
        import json
        res = []
        student_id = int(post.get('student_id'))
        page_code = post.get('Page_Code')
        if not student_id and not page_code:
            return res
        get_fields_value = self.get_page_wise_value(student_id,page_code)
        print "=======", get_fields_value
        return json.dumps(get_fields_value)
