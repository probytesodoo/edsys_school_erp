from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning


class MinistryApprovalConfirm(models.TransientModel):
    _name = 'ministry.approval.confirm'

    @api.multi
    def ministry_confirm(self):
        active_ids = self._context['active_ids']
        trans_obj = self.env['trensfer.certificate']
        for trans_rec in trans_obj.browse(active_ids):
            trans_rec.ministry_approval_confirm()
