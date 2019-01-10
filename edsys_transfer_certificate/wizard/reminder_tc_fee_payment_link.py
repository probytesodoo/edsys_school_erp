from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import except_orm
import base64

class SendReminderTCFeePaymentLink(models.TransientModel):

    _name = 'send.reminder.tc.fee.payment.wiz'

    @api.multi
    def resend_tc_fee_payment_link(self):
        """
        this method is use to resend TC Fee Payment link.
        ---------------------------------------------------
        :return:
        """
        active_ids = self._context['active_ids']
        tc_obj = self.env['trensfer.certificate']
        for tc_student_rec in tc_obj.browse(active_ids):
            if tc_student_rec.state != 'final_fee_awaited':
                raise except_orm(_('Warning!'),
                    _("Fee Payment Link Reminder send only in Final Fee Awaited State !"))

            if tc_student_rec.credit == 0.00 and tc_student_rec.parent_credit == 0.00:
                raise except_orm(_('Warning!'),
                    _("You can not send Fee Payment Link with 0.00 amount !"))
            else:
                tc_student_rec.send_mail_payfort_payment_link()