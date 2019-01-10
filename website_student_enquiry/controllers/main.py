from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import date,datetime,timedelta
import base64
import json

class WebsiteStudentEnquiry(http.Controller):
    @http.route([
        '/enquiry',
    ], type='http', auth="public", website=True)
    def render_enquiry(self, **kwargs):
        """
        this method is used to call webpage,
        also we pass the data we required in web form.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                required data
        """
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        country_obj = env['res.country']
        state_obj = env['res.country.state']
        academic_Year_obj = env['batch']
        course_obj = env['course']
        language_obj = env['res.lang']
        religion_obj = env['religion']
        # nationality_obj = env['nationality']
        religion = []
        course = []
        batch = []
        country = []
        state = []
        language = []
        nationality=[]
        eff_date = ''
        min_max = ''
        for country_rec in country_obj.sudo().search([]):
            country.append(country_rec)
        for state_rec in state_obj.sudo().search([]):
            state.append(state_rec)
        for each in country_obj.sudo().search([]):
            nationality.append(each)   
        for batch_rec in academic_Year_obj.sudo().search([]):
            eff_date += str(batch_rec.id) + ',' + str(batch_rec.effective_date) + ','
            current_year = int(date.today().year)
            if int(str(batch_rec.start_date).split("-")[0]) >= current_year or int(str(batch_rec.end_date).split("-")[0]) == current_year:
                batch.append(batch_rec)

        for course_rec in course_obj.sudo().search([]):
            min_max += str(course_rec.id) + ',' + str(course_rec.min_age) + '|' + str(course_rec.max_age) + ','
            course.append(course_rec)
        for lang in language_obj.sudo().search([]):
            language.append(lang)
        for reg in religion_obj.sudo().search([]):
            religion.append(reg)
        return http.request.render("website_student_enquiry.index", {
            'country_id' : country,
            'state_rec' : state,
            'batch_rec' : batch,
            'course_rec' : course,
            'language_rec' : language,
            'regligion_rec' : religion,
            'nationality_id':nationality,
            'eff_date': eff_date,
            'min_max_age' : min_max,
            })

    @http.route([
        '/enquiry/thankyou'
    ], methods=['POST'], type='http', auth="public", website=True,csrf=False)
    def render_thankyou(self, **post):
        """
        this method is used to call webpage,
        also we pass the data we required in web form.
        hear we create new enquiry for student,
        also send mail to new created student with
        enquiry number.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        env = request.env(user=SUPERUSER_ID)

        date_birth = post.get('Date_of_Birth') or ""
        date_of_birth = ""
        if date_birth:
            date_of_birth = date_birth.split("-")[2] + "-" + date_birth.split("-")[1] + "-" + date_birth.split("-")[0]
        date_pass = post.get('Pass_Date_of_issue') or ""
        date_of_pass = ""
        if date_pass:
            date_of_pass = date_pass.split("-")[2] + "-" + date_pass.split("-")[1] + "-" + date_pass.split("-")[0]
        date_pass_ex = post.get('Pass_Date_of_Expiry') or ""
        date_of_pass_ex = ""
        if date_pass_ex:
            date_of_pass_ex = date_pass_ex.split("-")[2] + "-" + date_pass_ex.split("-")[1] + "-" + date_pass_ex.split("-")[0]
        date_visa = post.get('visa_date_of_issue') or ""
        date_of_visa = ""
        if date_visa:
            date_of_visa = date_visa.split("-")[2] + "-" + date_visa.split("-")[1] + "-" + date_visa.split("-")[0]
        date_visa_ex = post.get('visa_date_of_exp') or ""
        date_of_visa_ex = ""
        if date_visa_ex:
            date_of_visa_ex = date_visa_ex.split("-")[2] + "-" + date_visa_ex.split("-")[1] + "-" + date_visa_ex.split("-")[0]
        last_date_att = post.get('last_date_attend') or ""
        lase_date_of_att = ""
        if last_date_att:
            lase_date_of_att = last_date_att.split("-")[2] + "-" + last_date_att.split("-")[1] + "-" + last_date_att.split("-")[0]

        student_dict = {}
        student_enq_obj = env['registration']
        student_dict.update({
	    'first_acd_year_of_child' : int(post.get('Academic_Year')) or "",
            'batch_id' : int(post.get('Academic_Year')) or "",
            'course_id' : int(post.get('Course')) or "",
            'name' : post.get('Name_of_Student1') or "",
            'middle_name' : post.get('Name_of_Student2') or "",
            'last_name' : post.get('Name_of_Student3') or "",
            'birth_date' : date_of_birth or False,
            'birth_place' : post.get('Place_of_Birth') or "",
            'birth_country' : int(post.get('Country')) or "",
            'gender' : post.get('Gender') or "",
            'nationality_id' : int(post.get('Nationality')) or "",
            'religion_id' : int(post.get('Religion')) or "",
            'lang_id' : int(post.get('Mother_Tongue')) or "",
            'passport_no' : post.get('Passport_No') or "",
            'place_of_issue' :int(post.get('Pass_Place_of_issue')) or "",
            'passport_issue_date' : date_of_pass or False,
            'passport_expiry_date' : date_of_pass_ex or False,
            'visa_no' : post.get('Visa_Number') or "",
            'visa_issue_date' : date_of_visa or False,
            'visa_expiry_date' : date_of_visa_ex or False,
            'other_lang_id' : int(post.get('oplanguage')) or "",
            'parent_name' : post.get('father_name') or "",
            'parent_profession' : post.get('father_profession') or "",
            'parent_email' : post.get('email') or "",
            'email' : post.get('email') or "",
            'parent_contact' : post.get('mother_contact') or "",
            'mobile' : post.get('mother_contact') or "",
            'street' : post.get('local_address') or "",
            'prev_institute' : post.get('last_attend') or "",
            'last_attendance' : lase_date_of_att or False,
            'curriculum' : post.get('curriculum') or "",
            'prev_grade' : post.get('grade_last_attend') or "",
            'prev_academic_year' : int(post.get('sepradio')) or "",
            'city' : post.get('city') or "",
            'prev_academic_city' : post.get('city') or "",
            'tranfer_reason' : post.get('reason_transfer') or "",
            'sibling_info' : post.get('sibling_info') or "",
           # 'sibling_ids' : [(0,0,{'sibling_name' : post.get('sibling_name')})] or "",
            'remarks' : post.get('remarks') or "",
            'about_us' : post.get('optionsRadios') or "",
            'state' : 'enquiry',
            'isd_code' : post.get('mother_contact_code') or "",
            'about_us_other' : post.get('otherradiotextbox') or "",
            'transport_type' : post.get('transport_type') or "",
            'pick_up' : post.get('pick_up') or "",
            'droup_off_pick' : post.get('droup_off') or "",
        })
        if student_dict:
            new_student_enq = student_enq_obj.sudo().create(student_dict)

        if new_student_enq and new_student_enq.id:
            return request.render("website_student_enquiry.thankyou", {
                'enquiry_no' : new_student_enq.enquiry_no,
                })
    def decode_base64(self,data):
        """
        Decode base64, padding being optional.
        ------------------------------------------------
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
        """
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += b'='* missing_padding
        try:
            res = base64.decodestring(data)
            if res:
                return res
        except:
            return ''


    @http.route([
        '/student/verification',
    ], type='http', auth="public", website=True)
    def render_student_verification(self, **post):
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
                                    student_rec = student_obj.sudo().search([('is_parent','=',False),
                                                                             ('reg_no','=',eq_no)],limit=1)
                                    if student_rec.id:
                                        return request.render("website_student_enquiry.student_other_information",{
                                            'student_rec' : student_rec,
                                            'parent_email': student_rec.parents1_id.parents_email,
                                            'reg_rec':reg_rec,
                                        })
                                    else:
                                        strick_off_student = student_obj.sudo().search([('is_parent','=',False),
                                                                                        ('reg_no','=',eq_no),
                                                                                        ('active','=',False),
                                                                                        ('strike_off','=',True)],limit=1)
                                        if strick_off_student.id:
                                            return request.render("website_student_enquiry.student_other_information",{
                                                'student_rec' : strick_off_student,
                                                'parent_email': strick_off_student.parents1_id.parents_email,
                                                'reg_rec':reg_rec,
                                                })
                            else:
                                return request.render("website_student_enquiry.student_link_expired_templet",{})
                        else:
                            if 'ENQUIRY' in post and post['ENQUIRY']:
                                eq_no = str(post['ENQUIRY'])
                                env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
                                student_obj = env['res.partner']
                                student_rec = student_obj.sudo().search([('is_parent','=',False),('reg_no','=',eq_no)],limit=1)
                                # cr = request.cr
                                # cr.execute("SELECT id FROM res_partner WHERE reg_no = %s", (eq_no,))
                                # rows = cr.fetchall()
                                if student_rec.id:
                                    return request.render("website_student_enquiry.student_other_information",{
                                        'student_rec' : student_rec,
                                        'parent_email': student_rec.parents1_id.parents_email,
                                        'reg_rec':reg_rec,
                                    })
                                else:
                                    strick_off_student = student_obj.sudo().search([('is_parent','=',False),
                                                                                    ('reg_no','=',eq_no),
                                                                                    ('active','=',False),
                                                                                    ('strike_off','=',True)],limit=1)
                                    if strick_off_student.id:
                                        return request.render("website_student_enquiry.student_other_information",{
                                            'student_rec' : strick_off_student,
                                            'parent_email': strick_off_student.parents1_id.parents_email,
                                            'reg_rec':reg_rec,
                                            })
                    else:
                        return request.render("website_student_enquiry.student_link_expired_templet",{})

    # @http.route([
    #     '/student/information',
    # ], type='http', auth="public", website=True)
    # def render_student_info(self, **post):
    #     """
    #     this method is used to call webpage,
    #     In this method we are checked student exiest with parents email address.
    #     if student is exiest then move to other page and fill remaining details.
    #     ------------------------------------------
    #     @param self : object pointer
    #     @param type : http
    #     @param auth : public
    #     @param website : True
    #     @return : call templet also pass dictonary for
    #               required data
    #     """
    #     s_email = post.get('email')
    #     env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
    #     student_obj = env['res.partner']
    #     student_rec = student_obj.sudo().search([('is_parent','=',False),('email','=',s_email)],limit=1)
    #     if student_rec.id:
    #         return request.render("website_student_enquiry.student_other_information",{
    #             'student_rec' : student_rec,
    #             'parent_email': student_rec.parents1_id.parents_email,
    #                 })
    #     else:
    #         return request.render("website_student_enquiry.student_verification_templet",{
    #             'msg_again' : 'this email address does not exist.'
    #         })



    @http.route([
    '/otherinformation/thankyou',
    ], type='http', auth="public", website=True)
    def render_student_other_info(self, **post):
        """
        this method is used to call webpage,
        also we pass the data we required in web form.
        ------------------------------------------
        @param self : object pointer
        @param type : http
        @param auth : public
        @param website : True
        @return : call templet also pass dictonary for
                  required data
        """
        
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        user_obj = env['res.partner']
        reg_obj = env['registration']
        attach_obj = env['ir.attachment']
        enquery_no = post.get('senquiry')
        #OLD LOGIC
        #stud_rec = user_obj.sudo().search([('is_parent','=',False),('reg_no','=',enquery_no)],limit=1)
        # UPDATED LOGIC 21JUNE 2016 IF STUDENT IS IN STRIKE OFF MODE ALLOW FOR REGITERATION
        
         
        stud_rec = user_obj.sudo().search(['|',('active','=',True),\
                   ('strike_off','=',True),('is_student','=',True),('reg_no','=',enquery_no)],limit=1)
        
        reg_id_obj=reg_obj.sudo().search([('student_id','=',stud_rec.id)],limit=1)
        student_data = {}
        parents_data = {}

        if stud_rec:
            parents_data.update({
                'parent_email': post.get('semail') or "",
                'mother_name' : post.get('mother_name'),
                'mother_profession' : post.get('mother_profession') or "",
                'mother_contact' : post.get('mother_mobile_no') or "",
                'mother_email' : post.get('mother_email') or "",
                'parents_office_contact' : post.get('office_no') or "",
                'mother_office_contact' : post.get('mother_tel_no') or "",
                'parent_address' : post.get('parents_address') or "",
                'mother_address' : post.get('mother_address') or "",
            })

            for document,values in {'f_visa_copy1':'parent_visa_copy','f_emirates_copy1':'f_emirates_copy1',
                                    'f_emirates_copy2':'f_emirates_copy2','m_visa_copy1':'mother_visa_copy',
                                    'm_emirates_copy1':'m_emirates_copy1','m_emirates_copy2':'m_emirates_copy2'}.items():
                if post.get(document):
                    parents_data.update({values:base64.encodestring(post[document].read())})

            student_data.update({
                #'image' : post.get('student_pic') or "",
                'emirati' : post.get('emirati') or "",
                'arab' : post.get('Arab_v') or "",
                'email' : post.get('semail') or "",
                'emirates_id' : post.get('emirates_id') or "",
                'blood_group' : post.get('blood_group') or "",
                's_height' : post.get('hight') or "",
                's_width' : post.get('weight') or "",
                'child_allergic' : post.get('allergic') or "",
                'w_allergic' : post.get('yes_allergic') or "",
                'w_reaction' : post.get('reaction') or "",
                'w_treatment' : post.get('treatment') or "",
                'under_medication' : post.get('under_medication') or "",
                'w_medication_mention' : post.get('mention') or "",
                'w_treatment_mention' : post.get('w_treatment') or "",
                'emergency_contact' : post.get('emergency_mobile_no') or "",
                'transport_type' : post.get('transport_type') or "",
                'pick_up' : post.get('pick_up') or "",
                'droup_off_pick' : post.get('droup_off') or "",
                'street' : str(post.get('parents_address')) or "",
            })

            for sdocument,svalues in {'transfer_certi':'transfer_certificate','s_emirates_copy1':'s_emirates_copy1',
                                      's_emirates_copy2':'s_emirates_copy2','s_pass_copy1':'passport_copy1',
                                      's_pass_copy2':'passport_copy2','s_visa':'medical_documents_file'}.items():
                if post.get(sdocument):
                    student_data.update({svalues:base64.encodestring(post[sdocument].read())})

            # update student record
            stud_rec.sudo().write(student_data)
            stud_rec.parents1_id.sudo().write(parents_data)
            if reg_id_obj.id:
                reg_id_obj.add_form_filled=True
                reg_id_obj.sudo().write(student_data)
                reg_id_obj.sudo().write(parents_data)
                reg_id_obj.parent_office_contact = post.get('office_no') or ""
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
                        res_name = stud_rec.parents1_id.name
                    else:
                        res_name = stud_rec.parents1_id.mother_name

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
        return request.render("website_student_enquiry.student_verification_templet",{})



    @http.route([
    '/get_status_',
    ], type='http', auth="public", website=True)
    def render_state_info(self, **post):
        country_id = post.get('country_id')
        env = request.env(context=dict(request.env.context, show_address=True,no_tag_br=True))
        state_obj = env['res.country.state']
        state_str = ''
        res = []
        for state_rec in state_obj.sudo().search([('country_id','=',int(country_id))]):
            res.append((state_rec.id,state_rec.name))
        return json.dumps(res)

    @http.route([
    '/get_class_',
    ], type='http', auth="public", website=True)
    def render_class_info(self, **post):
        """
        this method is use for filter class based on selected academic year,
        also check registration fee structure is define or not.
        --------------------------------------------------------------------
        :param post:
        :return: json
        """
        batch_id = post.get('batch_rec')
        env = request.env(context=dict(request.env.context, show_address=True,no_tag_br=True))
        batch_obj = env['batch']
        fee_str_obj = env['fees.structure']
        res = []
        for batch_rec in batch_obj.sudo().search([('id','=',int(batch_id))]):
            for class_rec in batch_rec.course_ids:
                fee_str_rec = fee_str_obj.sudo().search([('type','=','reg'),('course_id','=',class_rec.id),('academic_year_id','=',batch_rec.id)])
                if fee_str_rec.id:
                    res.append((class_rec.id,class_rec.name))
        return json.dumps(res)
