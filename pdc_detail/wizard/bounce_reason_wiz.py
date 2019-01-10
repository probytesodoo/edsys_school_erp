from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class bounce_reason_wiz(models.TransientModel):

    _name='bounce.reason.wiz'
    
    reason = fields.Char(string="Please mention reason for bounce cheque",size=126)
    
    @api.multi
    def bounce_cheque(self):
        pdc=self.env['pdc.detail']
        active_ids=self._context['active_ids']
        for active_id in active_ids:
            pdc_obj=pdc.browse(active_id)
            if pdc_obj.state =='draft':
                raise except_orm(_('Warning!'),
                    _("You can not bounce Draft cheque"))
            
            pdc_obj.reason=self.reason
            if pdc_obj.chk_fee_type=='reg':
                pdc_obj.state='bounced'
                pdc_obj.journal_entry_id.button_cancel()
            elif pdc_obj.chk_fee_type=='academic':
                if pdc_obj.voucher_id:
                    pdc_obj.voucher_id.cancel_voucher()
                    pdc_obj.state='bounced'
            else:
                pdc_obj.state='bounced'
                pdc_obj.journal_entry_id.button_cancel()
                if pdc_obj.journal_entry_id.pdc_id:
                    pdc_obj.journal_entry_id.pdc_id=False
            if pdc_obj.cleared_entry_id:
                pdc_obj.cleared_entry_id.button_cancel()
                pdc_obj.cleared_entry_id.unlink()
                
        return True