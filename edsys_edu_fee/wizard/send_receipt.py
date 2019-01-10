from odoo import models, fields, api, _


class SendReceipt(models.TransientModel):
    _name = 'send.receipt.student'

    @api.multi
    def send_payment_receipt(self):
        active_ids = self._context['active_ids']
        voucher_obj = self.env['account.voucher']
        for voucher in voucher_obj.browse(active_ids):
            if voucher.state == 'posted':
                voucher.send_receipt()