from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import base64

class visa_details(models.Model):
    
    _name = "visa.details"
    
    
    @api.multi
    def calculate_remaining_date(self):
        remaining_days = 0
        for visa_details in self:
            if visa_details.visa_expiry_date :
                current_date = datetime.datetime.now().date()
                current_date_new = datetime.datetime.strptime(str(current_date), DATE_FORMAT)
                visa_expiry_date = datetime.datetime.strptime(str(visa_details.visa_expiry_date), DATE_FORMAT)
                remaining_days = (visa_expiry_date - current_date_new).days
                visa_details.remaining_days = remaining_days

    @api.multi
    def compute_color(self):
        remaining_days = 0
        for record in self:
            remaining_days_new = record.remaining_days
            if remaining_days_new <= 10:
                record.visa_state = 'danger'
            if remaining_days_new > 10 and remaining_days_new <= 75:
                record.visa_state = 'yellow'
                
    visa_type = fields.Many2one('visa.type', string='Visa Type',domain=[('visible_to_pro','=',True)])
    #visa_type = fields.Selection([('tourist_visa','Tourist Visa' ),('resident_visa','Resident visa' ),('employer','Existing employment visa')],'Visa Type' )
    #visa_type = fields.Selection([('resident_visa','Residence visa' ),('employer','Employer' )],'Visa Type')
    visa_number = fields.Char('Visa Number' )
    visa_issue_date = fields.Date('Date Of Issue  ' ,  )
    visa_expiry_date = fields.Date('Date Of Expiry  ',  ) 
    
    relation_with_emp = fields.Char('Relation with employee')
    sponsor_name = fields.Char('Sponser Name' )
    sponsor_address = fields.Char('Sponser Address' )
    sponsor_visa_number = fields.Char('Sponsor Visa Number')
    sponsor_visa_start_date = fields.Date('Sponsor Visa start Date')
    sponsor_visa_expiry_date = fields.Date('Sponsor Visa Expiry Date')
    visa_uid = fields.Char('Visa UID' )
    
    employee_id = fields.Many2one('hr.employee','Employee' )        
    remaining_days = fields.Integer('Remaining Days',compute='calculate_remaining_date')
    confirm = fields.Boolean('confirm',default=False)
    employee_code = fields.Char(related='employee_id.employee_code')
    #employee_name = fields.Char(related='employee_id.employee_name')
    visa_state = fields.Selection([('danger','danger'),('normal','normal'),('yellow','Yellow')],'Status',compute='compute_color')
    renew_done = fields.Boolean('Renew Done',default=False)
    visa_remark = fields.Char('Remark')
    visa_details_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Visa Details Status' )
    visa_attachment =fields.Binary(string='Visa Copy' )
    visa_flag = fields.Boolean('Visa attached',default=False,readonly=True)
    visa_file_name =fields.Char('Visa Attachment Name')
    flag_cancelled = fields.Boolean('Flag',default=False)
    
    @api.model
    def create(self, vals):
        visa_expiry_date = False
        visa_issue_date = False
        if 'visa_issue_date' in vals and vals['visa_issue_date']:
            visa_issue_date = vals['visa_issue_date']
        if 'visa_expiry_date' in vals and vals['visa_expiry_date']:
            visa_expiry_date = vals['visa_expiry_date']
        if visa_issue_date != False:
            if visa_expiry_date != False:
                if  visa_expiry_date < visa_issue_date:
                    raise except_orm(_('Warning!'),_("Please select expiry date after issue date (%s)") % (visa_issue_date,))
        res = super(visa_details, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        ir_attachment = self.env['ir.attachment']
        if 'employee_id' in vals and vals['employee_id']:
            employee_id = vals['employee_id']
        else:
            employee_id = self.employee_id.id
        
        if 'visa_issue_date' in vals and vals['visa_issue_date']:
            visa_issue_date = vals['visa_issue_date']
        else:
            visa_issue_date = self.visa_issue_date
        if 'visa_expiry_date' in vals and vals['visa_expiry_date']:
            visa_expiry_date = vals['visa_expiry_date']
        else:
            visa_expiry_date = self.visa_expiry_date
        if visa_expiry_date != False:   
            if  visa_expiry_date < visa_issue_date:
                raise except_orm(_('Warning!'),_("Please select expiry date after issue date (%s)") % (visa_issue_date,))
        
            
        if 'visa_file_name' in vals and vals['visa_file_name']:
            if not 'visa_attachment' in vals :
                raise except_orm(_('Warning!'),_("Please attach visa copy"))
            elif 'visa_attachment' in vals:
                visa_attachment = vals['visa_attachment']
                if visa_attachment :
                    ir_attachment.sudo().create({  'name': vals['visa_file_name'],
                                                   'res_model':  'hr.employee',
                                                   'res_id': employee_id,
                                                   'datas': visa_attachment,
                                                   'type': 'binary',
                                                    'datas_fname': vals['visa_file_name'],
                                               })
                    ir_attachment.sudo().create({  'name': vals['visa_file_name'],
                                                   'datas_fname': vals['visa_file_name'],
                                                   'res_model':  'visa.details',
                                                   'res_id': self.id,
                                                   'datas': visa_attachment,
                                                   'type': 'binary'
                                               })
                    vals['visa_attachment'] = None
                    vals['visa_flag'] = True
            
        return super(visa_details, self).write(vals)
    
    @api.multi
    def confirm_visa_details(self):
        self.confirm = True
        if self.visa_details_status == 'completed' :
            if self.visa_type.name == 'None' :
                raise except_orm(_('Warning!'),_("Select Proper visa type"))
            if not self.visa_file_name :
                 raise except_orm(_('Warning!'),_("Please attach Visa Copy"))
        hr_vals = {
                    'pro_visa_type' : self.visa_type.id,
                    'pro_visa_number' : self.visa_number,
                    'pro_visa_issue_date' : self.visa_issue_date,
                    'pro_visa_expiry_date' : self.visa_expiry_date,
                    'pro_sponsor_name' : self.sponsor_name,
                    'pro_relation_with_emp' : self.relation_with_emp,
                    'pro_sponsor_visa_number' : self.sponsor_visa_number,
                    'pro_sponsor_visa_expiry_date' : self.sponsor_visa_expiry_date,
                    'pro_visa_details_status' : self.visa_details_status,
                    'pro_visa_file_name' : self.visa_file_name,
                    'pro_visa_attachment' : self.visa_attachment,
                    'pro_visa_remark':self.visa_remark,
                   }
        
        self.employee_id.write(hr_vals)
        self.flag_cancelled = True
        email_to = self.employee_id.hr_person.email_id
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_visa_cancellation')[1]
        template_rec = self.env['email.template'].browse(template_id)
        temp = template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        
        
    @api.multi
    def renew_visa(self):
        obj_model = self.env['ir.model.data']
        new_vals = {
                        'visa_type' : self.visa_type.id,
                        'confirm' : False,
                        'employee_code' : self.employee_code,
                        'employee_id' : self.employee_id.id,
                        'remaining_days' : False,
                        'sponsor_address' : self.sponsor_address,
                        'sponsor_name' : self.sponsor_name,
                        'visa_expiry_date' : False,
                        'visa_issue_date' : False,
                        'visa_number' : False,
                        'visa_state' : self.visa_number,
                        'visa_type' : self.visa_type.id,
                        'renew_done' : False,
                        'relation_with_emp' : False,
                        'visa_details_status' : False,
                        'visa_file_name' : False,
                        'visa_attachment' : False,
                        
                        }
        res_id = self.create(new_vals)
        self.write({'renew_done' : True})
        view_id = obj_model.get_object_reference('edsys_hrm', 'view_renewal_view_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'visa.details',
            'res_id' : res_id.id,
        }
        
class emirates_id_details(models.Model):
    
    _name = "emirates.id.details"
    
    @api.multi
    def calculate_remaining_date(self):
        remaining_days = 0
        for emirates_id in self:
            if emirates_id.emirates_expiry_date :
                current_date = datetime.datetime.now().date()
                current_date_new = datetime.datetime.strptime(str(current_date), DATE_FORMAT)
                emirates_expiry_date = datetime.datetime.strptime(emirates_id.emirates_expiry_date, DATE_FORMAT)
                remaining_days = (emirates_expiry_date - current_date_new).days
                emirates_id.remaining_days = remaining_days
            
    @api.multi
    def emirates_color(self):
        remaining_days = 0
        for record in self:
            remaining_days_new = record.remaining_days
            if remaining_days_new <= 10:
                record.emirates_state = 'danger'
            if remaining_days_new > 10 and remaining_days_new <= 75:
                record.emirates_state = 'yellow'
    
    emirates_card_no = fields.Char('Emirates Card No.' )
    emirates_start_date = fields.Date('Issue Date Of Emirates ID Card',   )   
    emirates_expiry_date = fields.Date('Expiry Date Of Emirates ID Card',   )   
    employee_id = fields.Many2one('hr.employee','HR Employee' )     
    remaining_days = fields.Integer('Remaining Days',compute='calculate_remaining_date')
    confirm = fields.Boolean('confirm',default=False)
    employee_code = fields.Char(related='employee_id.employee_code')
    renew_done = fields.Boolean('Renew Done',default=False)
    emirates_remark = fields.Char('Remark')
    emirates_state = fields.Selection([('danger','danger'),('normal','normal'),('yellow','Yellow')],'Status',compute='emirates_color')
    emirates_id_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Emirates Id Status' )
    emirates_id_attachment =fields.Binary(string='Emirates Copy' )
    emirates_flag = fields.Boolean('Emirates attached',default=False,readonly=True)
    emirates_card_file_name =fields.Char('Emirates Card Attachment Name' )
    flag_cancelled = fields.Boolean('Flag',default=False)
    
    @api.model
    def create(self, vals):
        emirates_expiry_date = False
        emirates_start_date = False
        if 'emirates_start_date' in vals and vals['emirates_start_date']:
            emirates_start_date = vals['emirates_start_date']
        if 'emirates_expiry_date' in vals and vals['emirates_expiry_date']:
            emirates_expiry_date = vals['emirates_expiry_date']
        if emirates_start_date != False:
            if emirates_expiry_date != False:
                if  emirates_expiry_date < emirates_start_date:
                    raise except_orm(_('Warning!'),_("Please select expiry date after issue date (%s)") % (emirates_start_date))
        return super(emirates_id_details, self).create(vals)
    
    
    @api.multi
    def write(self, vals):
        ir_attachment = self.env['ir.attachment']
        if 'emirates_expiry_date' in vals and vals['emirates_expiry_date']:
            emirates_expiry_date = vals['emirates_expiry_date']
        else :
            emirates_expiry_date = self.emirates_expiry_date
            
        if 'emirates_start_date' in vals and vals['emirates_start_date']:
            emirates_start_date = vals['emirates_start_date']
        else :
            emirates_start_date = self.emirates_start_date
            
        if 'employee_id' in vals and vals['employee_id']:
            employee_id = vals['employee_id']
        else :
            employee_id = self.employee_id.id
            
        if 'emirates_card_file_name' in vals and vals['emirates_card_file_name']:
            if not 'emirates_card_file_name' in vals :
                raise except_orm(_('Warning!'),_("Please attach Emirates ID copy"))
            elif 'emirates_id_attachment' in vals:
                emirates_id_attachment = vals['emirates_id_attachment']
                if emirates_id_attachment :
                    ir_attachment.sudo().create({  'name': vals['emirates_card_file_name'],
                                                   'res_model':  'hr.employee',
                                                   'res_id': employee_id,
                                                   'datas': emirates_id_attachment,
                                                   'type': 'binary',
                                                   'datas_fname': vals['emirates_card_file_name'],
                                               })
                    ir_attachment.sudo().create({  'name': vals['emirates_card_file_name'],
                                                   'datas_fname': vals['emirates_card_file_name'],
                                                   'res_model':  'emirates.id.details',
                                                   'res_id': self.id,
                                                   'datas': emirates_id_attachment,
                                                   'type': 'binary'
                                               })
                    vals['emirates_id_attachment'] = None
                    vals['labour_flag'] = True
        return super(emirates_id_details, self).write(vals)
    
    @api.multi
    def confirm_emirates_id_details(self):
        self.confirm = True
        if self.emirates_id_status == 'completed' and not self.emirates_card_file_name :
            raise except_orm(_('Warning!'),_("Please attach Emirates ID document"))
        hr_vals = {
                    'pro_emirates_id_status' : self.emirates_id_status,
                    'pro_emirates_card_no' : self.emirates_card_no,
                    'pro_emirates_start_date' : self.emirates_start_date ,
                    'pro_emirates_expiry_date' : self.emirates_expiry_date ,
                    'pro_emirates_card_file_name' : self.emirates_card_file_name,
                    'pro_emirates_card_attachment' : self.emirates_id_attachment,
                    'pro_emirates_remark' : self.emirates_remark,
                   }
        self.employee_id.write(hr_vals)
        self.flag_cancelled = True
        email_to = self.employee_id.hr_person.email_id
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_emirates_cancellation')[1]
        template_rec = self.env['email.template'].browse(template_id)
        temp = template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        
    @api.multi
    def renew_emirates(self):
        obj_model = self.env['ir.model.data']
        new_vals = {
                        'confirm' : False,
                        'emirates_card_no' : self.emirates_card_no,
                        'emirates_expiry_date' : False,
                        'emirates_start_date' : False,
                        'emirates_state' : self.emirates_state,
                        'employee_code' : self.employee_code,
                        'employee_id' : self.employee_id.id,
                        'remaining_days' : False,
                        'renew_done' : False,
                        'emirates_id_status' : False,
                        }
        res_id = self.create(new_vals)
        self.write({'renew_done' : True})
        view_id = obj_model.get_object_reference('edsys_hrm', 'view_emirates_id_renewal_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'emirates.id.details',
            'res_id' : res_id.id,
        }
    
class labour_card_details(models.Model):
    
    _name = "labour.card.details"
    
    @api.multi
    def calculate_remaining_date(self):
        remaining_days = 0
        for labour_card in self:
            if labour_card.permit_expiry_date :
                current_date = datetime.datetime.now().date()
                current_date_new = datetime.datetime.strptime(str(current_date), DATE_FORMAT)
                permit_expiry_date = datetime.datetime.strptime(labour_card.permit_expiry_date, DATE_FORMAT)
                remaining_days = (permit_expiry_date - current_date_new).days
                labour_card.remaining_days = remaining_days
            
    @api.multi
    def labour_color(self):
        remaining_days = 0
        for record in self:
            remaining_days_new = record.remaining_days
            if remaining_days_new <= 10:
                record.labour_state = 'danger'
            if remaining_days_new > 10 and remaining_days_new <= 75:
                record.labour_state = 'yellow'

    permit_card_no = fields.Char('Labour Card / Permit Card No.' )
    permit_expiry_date = fields.Date('Expiry Date Of Labour Card  ',   )
    permit_issue_date = fields.Date('Issue Date Of Labour Card  ',   )
    employee_id = fields.Many2one('hr.employee','HR Employee ' )       
    remaining_days = fields.Integer('Remaining Days',compute='calculate_remaining_date') 
    confirm = fields.Boolean('confirm',default=False)
    employee_code = fields.Char(related='employee_id.employee_code')
    renew_done = fields.Boolean('Renew Done',default=False)
    labour_remark = fields.Char('Remark')
    #employee_name = fields.Char(related='employee_id.employee_name')
    labour_state = fields.Selection([('danger','danger'),('normal','normal'),('yellow','Yellow')],'Status',compute='labour_color')
    labour_card_status = fields.Selection([('cancelled','Cancelled' ),('initiated','Initiated' ),('in_progress','In progress' ),('completed','Completed' ),('not_required','Not required' )],'Labour Card Status' )
    labour_card_attachment =fields.Binary(string='Labour Card Copy' )
    labour_flag = fields.Boolean('Labour card attached',default=False,readonly=True)
    labour_card_file_name =fields.Char('Labour Card Attachment Name')
    flag_cancelled = fields.Boolean('Flag',default=False)
    
    @api.model
    def create(self, vals):
        permit_expiry_date = False
        permit_issue_date = False
        if 'permit_issue_date' in vals and vals['permit_issue_date']:
            permit_issue_date = vals['permit_issue_date']
        if 'permit_expiry_date' in vals and vals['permit_expiry_date']:
            permit_expiry_date = vals['permit_expiry_date']
        if permit_issue_date != False:
            if permit_expiry_date != False:
                if  permit_expiry_date < permit_issue_date:
                    raise except_orm(_('Warning!'),_("Please select expiry date after issue date (%s)") % (permit_issue_date))
        res = super(labour_card_details, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        ir_attachment = self.env['ir.attachment']
        if 'permit_expiry_date' in vals and vals['permit_expiry_date']:
            visa_expiry_date = vals['permit_expiry_date']
        else :
            permit_expiry_date = self.permit_expiry_date
            
        if 'permit_issue_date' in vals and vals['permit_issue_date']:
            permit_issue_date = vals['permit_issue_date']
        else :
            permit_issue_date = self.permit_issue_date
            
        if 'employee_id' in vals and vals['employee_id']:
            employee_id = vals['employee_id']
        else :
            employee_id = self.employee_id.id
            
        if 'labour_card_file_name' in vals and vals['labour_card_file_name']:
            if not 'labour_card_attachment' in vals :
                raise except_orm(_('Warning!'),_("Please attach Labour Card copy"))
            elif 'labour_card_attachment' in vals:
                labour_card_attachment = vals['labour_card_attachment']
                if labour_card_attachment :
                    ir_attachment.sudo().create({  'name': vals['labour_card_file_name'],
                                                   'res_model':  'hr.employee',
                                                   'res_id': employee_id,
                                                   'datas': labour_card_attachment,
                                                   'type': 'binary',
                                                   'datas_fname': vals['labour_card_file_name'],
                                               })
                    ir_attachment.sudo().create({  'name': vals['labour_card_file_name'],
                                                   'datas_fname': vals['labour_card_file_name'],
                                                   'res_model':  'labour.card.details',
                                                   'res_id': self.id,
                                                   'datas': labour_card_attachment,
                                                   'type': 'binary'
                                               })
                    vals['labour_card_attachment'] = None
                    vals['labour_flag'] = True
        return super(labour_card_details, self).write(vals)
    
    @api.multi
    def confirm_labour_card_details(self):
        self.confirm = True
        if self.labour_card_status == 'completed' and not self.labour_card_file_name :
            raise except_orm(_('Warning!'),_("Please attach labour card document"))
        hr_vals = {
                    'pro_labour_card_status' : self.labour_card_status ,
                    'pro_labour_card_no' : self.permit_card_no ,
                    'pro_labour_card_start_date' : self.permit_issue_date,
                    'pro_permit_expiry_date' : self.permit_expiry_date,
                    'pro_labour_card_file_name' : self.labour_card_file_name,
                    'pro_labour_card_attachment' : self.labour_card_attachment,
                    'pro_labour_card_remark':self.labour_remark,
                   }
        self.employee_id.write(hr_vals)
        self.flag_cancelled = True
        email_to = self.employee_id.hr_person.email_id
        email_server=self.env['ir.mail_server']
        email_sender=email_server.search([])[0]
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_labour_cancellation')[1]
        template_rec = self.env['email.template'].browse(template_id)
        temp = template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
        template_rec.send_mail(self.id, force_send=True)
        
        
    @api.multi
    def renew_labour(self):
        obj_model = self.env['ir.model.data']
        new_vals = {
                        'confirm' : False,    
                        'permit_card_no' : False,
                        'permit_expiry_date' : False,
                        'permit_issue_date' : False,
                        'employee_id' : self.employee_id.id,
                        'remaining_days' : False,
                        'employee_code' : self.employee_code,
                        'labour_state' : False,
                        'labour_card_status' : False,
                        'renew_done' : False,
                        'labour_card_attachment' : False,
                        'labour_card_file_name' : False,
                    }
        res_id = self.create(new_vals)
        self.write({'renew_done' : True})
        view_id = obj_model.get_object_reference('edsys_hrm', 'view_labour_card_renewal_form')[1]
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'labour.card.details',
                'res_id' : res_id.id,
                }
