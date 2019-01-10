# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class PayfortPaymentCapture(models.Model):

    _name = 'payfort.payment.capture'

    date = fields.Date('Date')
    partner = fields.Many2one('res.partner', string="Partner")
    pay_id = fields.Char('Payment ID')
    reference_number = fields.Char('Reference Number')
    paid_amount = fields.Float('Paid Amount')
    bank_charges = fields.Float('Bank charges from students')
    gross_transaction_value = fields.Float('Gross Transaction Value')
    transaction_charges = fields.Float('PayFort charges from students')
    net_amount = fields.Float('Net amount credited in the bank')
    transaction_charges_deducted_by_bank = fields.Float('Transaction charges deducted by bank')