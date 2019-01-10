from openerp import models, fields, api, _
from datetime import date, datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
import base64

class SendRequestReRegistration(models.TransientModel):
    _name = 're.registration.parent.wiz'

    batch_id = fields.Many2one('batch', "Academic Year")
    class_ids = fields.Many2many('course', 'rereg_class', 'reg_id', 'course_id', "Class")
    student_section_ids = fields.Many2many('section', 'rereg_section', 'reg_id', 'section_id', "Section")
    parent_ids = fields.Many2many('res.partner', 'rereg_partner', 'reg_id', 'partner_id', 'Parents')
    exclude_strike_off_student = fields.Boolean('Exclude striked off students',default=False)
    
    @api.onchange('exclude_strike_off_student')
    def onchange_exclude_strike_off_student(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.exclude_strike_off_student:
            if self.class_ids or self.student_section_ids or self.batch_id: 
                if self.class_ids :
                    for class_id in self.class_ids :
                        class_id_list.append(class_id.id)
                if self.student_section_ids :
                    for section_id in self.student_section_ids :
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
            if self.class_ids or self.student_section_ids or self.batch_id: 
                if self.class_ids :
                    for class_id in self.class_ids :
                        class_id_list.append(class_id.id)
                if self.student_section_ids :
                    for section_id in self.student_section_ids :
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

    
    @api.onchange('class_ids', 'student_section_ids', 'batch_id')
    def onchange_class_ids(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.class_ids or self.student_section_ids or self.batch_id: 
            if self.class_ids :
                for class_id in self.class_ids :
                    class_id_list.append(class_id.id)
            if self.student_section_ids :
                for section_id in self.student_section_ids :
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

    @api.multi
    def filter_student(self,chlidren_list,class_id,section):
        remaining_children_list = []
        for child in chlidren_list:
            if class_id and section:
                if child.class_id.id in class_id.ids and child.student_section_id.id in section.ids:
                    remaining_children_list.append(child)
            elif class_id and not section:
                if child.class_id.id in class_id.ids:
                    remaining_children_list.append(child)
            elif not class_id and section:
                if child.student_section_id.id in section.ids:
                    remaining_children_list.append(child)
            else:
                remaining_children_list.append(child)
        return remaining_children_list

    @api.multi
    def send_re_registration_link(self):
        re_reg_parent_obj = self.env['re.reg.waiting.responce.parents']
        re_reg_student_obj = self.env['re.reg.waiting.responce.student']
        batch_obj = self.env['batch']
        course_obj = self.env['course']
        stud_parent_obj = self.env['res.partner']
        # find next year batch
        if not self.batch_id.next_batch.id:
            raise except_orm(_('Warning!'), _("Next batch is not defined for %s !")%(self.batch_id.name))
        req_batch_rec = self.batch_id.next_batch
        # check for period(time duration)
        if not self.batch_id.re_reg_start_date or not self.batch_id.re_reg_end_date:
            raise except_orm(_('Warning!'), _("Re-registration process period is not defined!"))
        start_date = datetime.strptime(self.batch_id.re_reg_start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self.batch_id.re_reg_end_date, "%Y-%m-%d").date()
        current_date = datetime.today().date()
        if ((current_date<start_date) or (current_date>end_date)):
            raise except_orm(_('Warning!'),
            _("Re-registration process might not be started or already ended!"))

        regular_student_rec = stud_parent_obj.search([('batch_id','=',self.batch_id.id),
                                                      ('parents1_id','in',self.parent_ids.ids),
                                                      ('re_reg_next_academic_year','=','no')])
        student_list = []
        c_date = datetime.strptime(str(date.today()), "%Y-%m-%d")
        if regular_student_rec:
            for student_rec in regular_student_rec:
                if student_rec.admission_date:
                    joining_date = datetime.strptime(str(student_rec.admission_date), "%Y-%m-%d")
                    if not joining_date:
                        raise except_orm(_('Warning!'),
                                 _("Please mention joining date for student %s!") %student_rec)
                    if joining_date <= c_date:
                        student_list.append(student_rec)

            re_reg_children_list = self.filter_student(student_list,self.class_ids,self.student_section_ids)
            if len(re_reg_children_list) > 0:
                parents_list = []
                for child in re_reg_children_list:
                    re_reg_advance_account = child.re_reg_advance_account
                    if not re_reg_advance_account.id:
                        raise except_orm(_('Warning!'),
                            _("Please define re-registration advance account for student %s!")%(child.name))
                    # find next course
                    if not child.course_id.next_course.id:
                        raise except_orm(_('Warning!'), _("Next Class is not defined for %s !")%(child.course_id.name))
                    req_course_rec = child.course_id.next_course
                    # check fee structure define for next year or not
                    fee_structure_rec = self.env['fees.structure'].search([('type','=','re_reg'),
                                                                           ('course_id','=',req_course_rec.id),
                                                                           ('academic_year_id','=',req_batch_rec.id)],
                                                                          limit=1)
                    if not fee_structure_rec.id:
                        raise except_orm(_('Warning!'),
                                         _("Re-Registration fees structure not defined for class %s and year %s!")%
                                         (req_course_rec.name,req_batch_rec.name))

                    re_reg_parent_rec = re_reg_parent_obj.search([('name', '=', child.parents1_id.id),
                                                                  ('state','not in',["re_registration_confirmed"]),
                                                                  ('request_batch_id', '=', req_batch_rec.id)])
                    if not re_reg_parent_rec:
                        re_reg_parent_rec_val = {
                                'name': child.parents1_id.id,
                                'state': 'awaiting_response',
                                'request_batch_id' : req_batch_rec.id,
                                }

                    re_reg_child_rec = re_reg_student_obj.search([('name', '=', child.id),
                                                                ('batch_id', '=', self.batch_id.id)])
                    if not re_reg_child_rec:
                        if not re_reg_parent_rec:
                            re_reg_parent_rec = re_reg_parent_obj.create(re_reg_parent_rec_val)

                        re_reg_child_rec = re_reg_student_obj.create({
                                            'name': child.id,
                                            'reg_no': child.reg_no,
                                            'batch_id': child.batch_id.id,
                                            'course_id': child.course_id.id,
                                            'next_year_batch_id': req_batch_rec.id,
                                            'next_year_course_id': req_course_rec.id,
                                            're_reg_parents': re_reg_parent_rec.id,
                                            'state': 'awaiting_response',
                                        })

                        if re_reg_child_rec.re_reg_parents not in parents_list:
                            parents_list.append(re_reg_child_rec.re_reg_parents)

                end_date = datetime.strptime(str(self.batch_id.re_reg_end_date), "%Y-%m-%d").date().strftime("%d-%m-%Y")         
                for parent_rec in parents_list:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    encoded_data = base64.b64encode(parent_rec.code)
                    c_link = base_url + '/student/re_registration/request?REREG=%s'%(encoded_data)

                    email_server = self.env['ir.mail_server']
                    email_sender = email_server.search([], limit=1)
                    ir_model_data = self.env['ir.model.data']
                    template_id = ir_model_data.get_object_reference('edsys_edu_re_registration', 'email_template_re_registration_request')[1]
                    template_rec = self.env['mail.template'].browse(template_id)
                    body_html = template_rec.body_html
                    body_dynamic_html = template_rec.body_html
                    body_dynamic_html += '<p>Re-registration form to be submitted before: %s</p>'%(end_date)
                    body_dynamic_html += '<p><a href=%s><button>Click here</button>to complete the Re-registration form</a></p></div>'%(c_link)
                    template_rec.write({'email_to': parent_rec.name.parents_email,
                                        'email_from': email_sender.smtp_user,
                                        'email_cc': '',
                                        'body_html': body_dynamic_html})
                    template_rec.send_mail(parent_rec.id)
                    template_rec.body_html = body_html

