from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class post_cheque_wiz(models.TransientModel):

    _name='post.cheque.wiz'
    
    label = fields.Char()
    
    @api.multi
    def post_cheque(self):
        pdc=self.env['pdc.detail']
        active_ids=self._context['active_ids']
        for active_id in active_ids:
            chk=pdc.browse(active_id)
            if chk.state !='draft':
                raise except_orm(_('Warning!'),
                    _("You can post only draft cheque"))
            if chk.chk_fee_type=='reg':
                if chk.journal_entry_id and chk.journal_entry_id.id:
                    chk.journal_entry_id.button_validate()
                    chk.state='posted'
            elif chk.chk_fee_type=='academic':
                if not chk.voucher_id:
                    raise except_orm(_('Warning!'),
                        _("No payment linked with this Check"))
                chk.voucher_id.move_id.button_validate()
                chk.state='posted'
            else:
                if chk.journal_entry_id and chk.journal_entry_id.id:
                    chk.journal_entry_id.button_validate()
                    chk.state='posted'
        return True