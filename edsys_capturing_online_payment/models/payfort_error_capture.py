# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PayfortErrorCapture(models.Model):

    _name = 'payfort.error.capture'

    date = fields.Date('Date')
    # partner = fields.Many2one('res.partner', string="Partner")
    pay_id = fields.Char('Payment ID')
    reference_number = fields.Char('Reference Number')
    amount = fields.Float('Paid Amount')
    error_message = fields.Text('Error Message')
    payment_status = fields.Char('Status')