from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class MoveTcToAwaitingFee(models.Model):
    _name = 'move.tc.to.awaiting.fee'
    
    @api.multi
    def move_to_awaiting_fee(self):
        active_ids=self._context['active_ids']
        student_rereg_obj = self.env['re.reg.waiting.responce.student']
        for re_reg_rec in student_rereg_obj.browse(active_ids):
            if re_reg_rec.state != 'tc_expected':
                raise except_orm(_('Warning!'),
                    _(" Student  '%s' is not in 'TC Expected' state so you can not move him to Awaiting Re-registration Fee state!")%
                            re_reg_rec.name.name)
            re_reg_rec.come_tc_expected_to_waiting_fee()