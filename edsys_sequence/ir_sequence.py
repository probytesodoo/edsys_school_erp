from odoo import models, fields, api, _

class ir_sequence(models.Model):

    _inherit = 'ir.sequence'

    model_id = fields.Many2one("ir.model", 'Model')
    #field_id = fields.Many2one('ir.model.fields', 'Field', domain="[('model_id', '=', model_id), ('ttype', '=', 'integer')]")
    field_id = fields.Many2one('ir.model.fields', 'Field', domain="[('model_id', '=', model_id)]")
    
    @api.multi    
    def generate_sequence_button(self):
        if self.model_id.model == 'registration' :
            reg_ids = self.env['registration'].search([('state','!=', 'done')])
            for reg_id in reg_ids :
                number_seq = {self.field_id.name : self._next()}
                reg_id.write(number_seq)
                
        if self.model_id.model == 'account.voucher' :
            vocuher_ids = self.env['account.voucher'].search([('state','=', 'draft')])
            for vocuher_id in vocuher_ids :
                number_seq = {self.field_id.name : self._next()}
                vocuher_id.write(number_seq)
        
        if self.model_id.model == 'account.invoice' :
            invoice_ids = self.env['account.invoice'].search([('state','not in', ('paid', 'cancel'))])
            for invoice_id in invoice_ids :
                number_seq = {self.field_id.name : self._next()}
                invoice_id.write(number_seq)
                
        if self.model_id.model == 're.reg.waiting.responce.parents' :
            re_reg_ids = self.env['re.reg.waiting.responce.parents'].search([('state','not in', ('re_registration_confirmed', 'tc_expected'))])
            for re_reg_id in re_reg_ids :
                number_seq = {self.field_id.name : self._next()}
                re_reg_id.write(number_seq)
                
        if self.model_id.model == 'trensfer.certificate' :
            tc_ids = self.env['trensfer.certificate'].search([('state','not in', ('tc_complete', 'tc_cancel'))])
            for tc_id in tc_ids :
                number_seq = {self.field_id.name : self._next()}
                tc_id.write(number_seq)
                
        if self.model_id.model == 'hr.employee' :
            emp_ids = self.env['hr.employee'].search([('employee_state','in', ('probation', 'employee'))])
            for emp_id in emp_ids :
                #if emp_id.employee_code :
                #    emp_id.biometric_id = emp_id.employee_code
                #number_seq = {self.field_id.name : self._next()}
                #emp_id.write(number_seq)
		if not emp_id.employee_code :
                    number_seq = {self.field_id.name : self._next()}
                    emp_id.write(number_seq)
