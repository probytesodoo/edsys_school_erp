from odoo import models, fields, api, _

class TCCancleReasonWiz(models.Model):

    _name='tc.cancle.reason.wiz'
    
    reason = fields.Char(string="Please mention reason to cancel this TC application", size=126)

    @api.multi
    def come_to_cancle_state(self):
        """
        ---------------------------
        :return:
        """
        active_ids = self._context['active_ids']
        tc_object = self.env['trensfer.certificate']
        for tc_record in tc_object.browse(active_ids):
            tc_record.reason = self.reason
            tc_record.come_to_cancle()

