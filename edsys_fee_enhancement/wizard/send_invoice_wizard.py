from odoo import models, fields, api 
# from openerp.exceptions import except_orm

# from datetime import date

class send_invoice_wizard(models.Model):
   
    _name = 'send.invoice.wizard'
     
    class_id = fields.Many2one('course','Class')
    student_section_id = fields.Many2one('section', 'Section')
    batch_id = fields.Many2one('batch', 'Academic Year')
    month = fields.Many2one('fee.month', string='Month')
    parent_ids = fields.Many2many('res.partner','send_invoice_parent_id','parent_id','invoice_id', 'Parent')
    
    
    @api.onchange('batch_id')
    def onchange_batch_id(self):
        res = {}
        if self.batch_id :
            res['domain'] = {'month': [('batch_id','=',self.batch_id.id) ]}
        return res
    
    
    @api.onchange('class_id', 'student_section_id', 'batch_id')
    def onchange_class_ids(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.class_id or self.student_section_id or self.batch_id: 
            if self.class_id :
                for class_id in self.class_id :
                    class_id_list.append(class_id.id)
            if self.student_section_id :
                for section_id in self.student_section_id :
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
    def send_invoice_button(self):
        context = self._context
        parent_id_list = []
        for parent_id in self.parent_ids:
            parent_id_list.append(parent_id.id)
        
        partner_obj = self.env['res.partner']
        student_rec = partner_obj.search([('parents1_id','in',parent_id_list), ('year_id','=',self.batch_id.id), ('class_id','=',self.class_id.id)])
        
        
        student_id_list = []
        for student in student_rec:
            student_id_list.append(student.id)
             
        fee_payment_obj = self.env['fee.payment']
        fee_payment_rec = fee_payment_obj.search([('course_id','=',self.class_id.id), ('academic_year_id','=',self.batch_id.id), ('month','=',self.month.id)])
        selected_students_payment_rec = fee_payment_rec.fee_payment_line_ids.search([('fee_payment_id','=',fee_payment_rec.id),('student_id','in',student_id_list)])

        for student_pay in selected_students_payment_rec:
            student_rec = student_pay.student_id
            parent_rec = student_pay.student_id.parents1_id
            invoice_obj = self.env['account.invoice']
            invoice_rec = invoice_obj.search([('partner_id','=',student_rec.id),('batch_id','=',self.batch_id.id), ('month_id','=',self.month.id)])
            if invoice_rec:
                payfort_amount = invoice_rec.residual
                if payfort_amount > 0.00:
                    payable_amount = payfort_amount
                    link = '/redirect/payfort?AMOUNT=%s&ORDERID=%s'%(payfort_amount,invoice_rec.number)
                    month_value = str(dict(invoice_obj.fields_get(allfields=['month'])['month']['selection'])[invoice_rec.month])
                    email_server = self.env['ir.mail_server']
                    email_sender = email_server.search([], limit=1)
                    ir_model_data = self.env['ir.model.data']
                    template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_monthly_fee_calculation')[1]
                    template_rec = self.env['email.template'].browse(template_id)
                    body_html = template_rec.body_html
                    body_dynamic_html = template_rec.body_html + '<p>The total fee amount for the month of %s is AED %s.'%(month_value,invoice_rec.amount_total)
                    body_dynamic_html += 'After adjusting your advances, the amount you have to pay is AED %s.'%(payable_amount)
                    body_dynamic_html += ' The fee details are listed in the invoice attached </p>'
                    body_dynamic_html += '<a href=%s><button>Click Here</button>For Online Payment</a></div>'%(link)
                    template_rec.write({'email_to': parent_rec.parents_email,
                                                    'email_from': email_sender.smtp_user,
                                                    'email_cc': '',
                                                    'body_html': body_dynamic_html})
                    template_rec.send_mail(invoice_rec.id, force_send=False)
                    template_rec.body_html = body_html
                    invoice_rec.fee_calculation_mail_sent = True
        return True
        
