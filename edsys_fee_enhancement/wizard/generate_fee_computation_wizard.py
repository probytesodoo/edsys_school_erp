from odoo import models, fields, api, _
# from odoo.osv import osv

class generate_fee_computation_wizard(models.Model):
    _name = 'generate.fee.computation.wizard'

    @api.multi
    def generate_fee_computation_button(self):
        context = self._context
        active_ids = context['active_ids']
        
        for student_active_id in active_ids :
            partner_obj = self.env['res.partner']
            partner_rec = partner_obj.browse(student_active_id)
            if not partner_rec.fee_computation_ids :
                partner_rec.update_fee_structure()
        return True
            
