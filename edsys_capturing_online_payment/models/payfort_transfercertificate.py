# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TransferCertificateInheritPayfort(models.Model):

    _inherit = 'trensfer.certificate'

    @api.model
    def _get_payfort_payment_link(self,amount,order_id):
        """
        Genarate link for online payfort payment.
        ----------------------------------------
        :return:
        """
        link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(amount,order_id)
        return link