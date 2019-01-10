from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning

class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        self.action_move_line_create()
        pdc_obj = self.env['pdc.detail']
        for voucher in self:
            if voucher.journal_id.is_cheque:
                vals={
                    'name':voucher.chk_num,
                    'amount':voucher.amount,
                    'journal_id':voucher.journal_id and voucher.journal_id.id or False,
                    'cheque_start_date':voucher.cheque_start_date,
                    'cheque_expiry_date':voucher.cheque_expiry_date,
                    'bank_name':voucher.bank_name,
                    'party_name':voucher.party_name,
                    'period_id':voucher.period_id and voucher.period_id.id or False ,
                    'state':'draft',
                    'chk_fee_type':'academic',
                    'voucher_id':voucher.id,
                    'partner_id':voucher.partner_id.id
                        }
                pdc=pdc_obj.create(vals)
        return True

    @api.multi
    def cancel_voucher(self):
        """
        When we unreconcile voucher, and if payment
        from pdc then delete pdc record.
        :return:
        """
        for voucher_rec in self:
            if voucher_rec.journal_id.is_cheque:
                pdc_obj = self.env['pdc.detail']
                pdc_records = pdc_obj.search([('voucher_id', '=', voucher_rec.id)])
                for pdc_rec in pdc_records:
                    if pdc_rec.id:
                        if pdc_rec.state in ['draft', 'posted']:
                            pdc_rec.state = 'cancel'
                        elif pdc_rec.state in ['cleared']:
                            if pdc_rec.cleared_entry_id.state == 'draft':
                                pdc_rec.cleared_entry_id.unlink()
                                pdc_rec.state = 'cancel'
                            elif pdc_rec.cleared_entry_id.state == 'posted':
                                raise except_orm(_('Warning!'),
                                                 _("This Cheque %s Has been Already Cleared. Please Cancle Journal Entry for Unreconcile.") % (
                                                 pdc_rec.name))
        res = super(AccountVoucher, self).cancel_voucher()
        return res