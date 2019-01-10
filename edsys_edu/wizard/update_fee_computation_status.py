from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time
from odoo.exceptions import except_orm, Warning, RedirectWarning

class update_fee_computation_status(models.TransientModel):
    _name='update.fee.computation.status'
    

    @api.multi
    def update_fee_computation_status_button(self):
        """
        this method is used to manualy subbimit fee.
        -------------------------------------------------
        :return:
        """
        payment_status_month_ids = []
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        res_partners = self.env[active_model].browse(active_ids)
        for res_partner in res_partners :
            if res_partner.is_student and res_partner.active :
                if len(res_partner.payment_status) > 0:
                    for payment_status in res_partner.payment_status:
                        if payment_status.month_id:
                            payment_status_month_ids.append(payment_status.month_id)
                            
                if len(res_partner.fee_computation_ids) > 0:
                    for fee_computation_id in res_partner.fee_computation_ids:
                        if len(payment_status_month_ids) > 0:
                            for payment_status_month_id in payment_status_month_ids:
                                if fee_computation_id.month_id == payment_status_month_id:
                                    fee_computation_id.status = 'invoice_raised'
                                    break
                                    

