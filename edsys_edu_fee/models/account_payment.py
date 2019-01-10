from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class account_payment(models.Model):
  
    _inherit = 'account.payment'
    
    
    is_parent = fields.Boolean('Is Parent')
    partner_id = fields.Many2one('res.partner', string='Customer' , required=True)
    
    parent_email = fields.Char(string='Parent Email')
    parent_mobile = fields.Char(string='Mobile')
    student_class = fields.Many2one('course',string="Class")
    student_section = fields.Many2one('section', 'Section')

    bank_name = fields.Char('Bank Name')
    jounral_id_store = fields.Boolean(string='Jounral Store')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    cheque = fields.Boolean(string='Cheque')
    payfort_type = fields.Boolean('For Online Payment')
    payfort_link_order_id = fields.Char('Online Payment Order Id')
    
    
    
#     @api.multi
#     # @api.depends('journal_id')
#     def _onchange_journal(self, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id):
#         res = super(AccountVoucher, self)._onchange_journal(
#             journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id)
#         type_rec = self.env['account.journal'].browse(journal_id)
#         if res:
#             res['value'].update({
#                 'jounral_id_store': type_rec.is_cheque
#             })
#         return res
    
    
    @api.onchange('cheque_start_date','cheque_expiry_date')
    def cheque_start(self):
        if self.cheque_start_date and self.cheque_expiry_date:
            if self.cheque_start_date > self.cheque_expiry_date:
                raise except_orm(_('Warning!'),
                    _("Start Date must be lower than to Expiry date!"))
                
                
#     @api.multi
#     def action_invoice_paid(self):
#         print '--------------action invoice paid-------------------'
#         reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
#         if reg_rec.id:
#             reg_rec.fee_status = 'academy_fee_pay'
#             reg_rec.acd_trx_date = date.today()
#         return super(StudentFeeInvoice, self).action_invoice_paid()
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
#         to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
#         if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
#             raise UserError(_('Invoice must be validated in order to set it to register payemnt.'))
#         if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
#             raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
#          
#         reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
#         if reg_rec.id:
#             reg_rec.fee_status = 'academy_fee_pay'
#             reg_rec.acd_trx_date = date.today()
#          
#         return to_pay_invoices.write({'state': 'paid'})
         
   
    


#     @api.multi
#     def invoice_validate(self):
#         print'-------------invoice-validate----------------'
#         """
#         invoice line remaining amount update base on discount.
#         ------------------------------------------------------
#         :return:
#         """
#         for invoice_line_rec1 in self.invoice_line_ids:
#             for invoice_line_rec2 in self.invoice_line_ids:
#                 if invoice_line_rec1.product_id.fees_discount.id == invoice_line_rec2.product_id.id:
#                     if invoice_line_rec1.rem_amount > 0.00 and invoice_line_rec1.rem_amount >= abs(
#                             invoice_line_rec2.rem_amount):
#                         invoice_line_rec1.rem_amount -= abs(invoice_line_rec2.rem_amount)
#                         invoice_line_rec2.rem_amount = 0.00
#         res = super(StudentFeeInvoice, self).invoice_validate()
#         if self.type == "out_invoice" :
#             self.bulk_reconciliation()
#         return res
# 
#     def proforma_voucher(self):
#         self.action_move_line_create()
#         return True
#     
#     
#     @api.multi
#     def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
#         print '=================oncahnge_partner id==============='
#         student_obj = self.env['res.partner']
#         stud_rec = student_obj.browse(partner_id)
#   
#         if stud_rec.id and stud_rec.is_parent == True and stud_rec.is_student == False:
#             # payment from parent then check parent and it's all child id
#             child_lst = []
#             child_lst.append(partner_id)
#             for student_rec in student_obj.search([('is_parent','=',False),
#                                                    ('parents1_id','=',partner_id)]):
#                 child_lst.append(student_rec.id)
#             partner_id = child_lst
#             res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
#             if res:
#                 res['value']['parent_email'] = stud_rec.parents_email
#                 res['value']['parent_mobile'] = stud_rec.parent_contact
#         elif stud_rec.is_parent == False and stud_rec.is_student == True:
#             # payment from child then child id and it's parent id
#             child_parent_lst = []
#             child_parent_lst.append(partner_id)
#               
#             if stud_rec.parents1_id.id:
#                 child_parent_lst.append(stud_rec.parents1_id.id)
#             partner_id = child_parent_lst
#             print partner_id,'==========================partner id'
#             res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
#             print amount,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa mont  -----------aaaaaaaaaaa'
#             print res,'=============================res'
#             if res:
#                 res['value']['student_class'] = stud_rec.class_id.id
#                 res['value']['student_section'] = stud_rec.student_section_id.id
#         else:
#             res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
#             
#         total_pay_amount = 0.0
#           
#         if 'value' in res:
#             print'================value============='
#             if 'line_cr_ids' in res['value'] and res['value']['line_cr_ids']:
#                 for each in res['value']['line_cr_ids']:
#                     if isinstance(each,dict):
#                         total_pay_amount += each['amount_unreconciled']
#                         print total_pay_amount,'------crrrr------------total pay amount'
#             if 'line_dr_ids' in res['value'] and res['value']['line_dr_ids']:
#                 for each in res['value']['line_dr_ids']:
#                     if isinstance(each,dict):
#                         total_pay_amount -= each['amount_unreconciled']
#                         print total_pay_amount,'------------drrr-------total pay amount'
#             res['value']['total_payble_amount'] = total_pay_amount
#         return res
#   