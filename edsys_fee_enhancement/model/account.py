from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import except_orm

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    fee_calculation_mail_sent =fields.Boolean('Fee Calculation Mail Sent')
    
class AccountVoucher(models.Model):
    _inherit = "account.voucher"


# 
#     def button_proforma_voucher(self):
#         self.signal_workflow('proforma_voucher')
#         return {'type': 'ir.actions.act_window_close'}

    def proforma_voucher(self):
        print '============proforma voucher========='
        self.action_move_line_create()
        return True
     
    @api.model
    def create(self, vals):
        context = self.env.context
        if 'search_default_state' not in context :
            is_warning = False
            if 'invoice_type' in context :
                if context['invoice_type'] == 'out_refund' :
                    is_warning = False
                else :
                    is_warning = True
            if is_warning :
                registration_obj = self.env['registration']
                account_invoice_obj = self.env['account.invoice']
                student_id = vals['partner_id']
                account_invoice_rec =  False
                month = False 
                if student_id :
                    registration_rec = registration_obj.search([('student_id','=', student_id)])
                    if registration_rec.student_id.fee_computation_ids :
                        #if registration_rec.fee_status == 'academy_fee_unpaid' or registration_rec.fee_status == 'academy_fee_partial_pay' :
                        if registration_rec.student_id.fee_computation_ids[0].status == 'invoice_raised' and registration_rec.fee_status == 'academy_fee_partial_pay' :
                                raise except_orm(_("Warning!"), _('Selected student have some partial paid entries in awaiting fee tab'))
        #raise except_orm(_("Warning!"), _('stop'))
        return super(AccountVoucher, self).create(vals)







