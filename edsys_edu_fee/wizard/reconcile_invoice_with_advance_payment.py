from odoo import models, fields, api, _
import datetime as d
from datetime import datetime
from odoo.exceptions import except_orm
import time

class ReconcileInvoice(models.Model):

    _name = 'reconcile.invoice'

    @api.model
    def _get_period(self):
        """
        this method use for get account period.
        ---------------------------------------
        :return: record set of period
        """
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].search([])
        return periods and periods[0] or False

    @api.multi
    def reconcile_invoice_with_advance_payment(self):
        """
        first month invoice reconcile with advance payment,
        :return:
        """
        account_invoice = self.env['account.invoice']
        account_invoice_line = self.env['account.invoice.line']
        for record in account_invoice.browse(self._context['active_ids']):
            if record.state == 'open':
                account_invoice_line_ids = account_invoice_line.search([('invoice_id','=',record.id)])
                for account_invoice_line_id in account_invoice_line_ids:
                    if account_invoice_line_id.rem_amount == 0:
                        account_invoice_line_id.print_line = True
                    if account_invoice_line_id.rem_amount < account_invoice_line_id.price_unit:
                        account_invoice_line_id.amount_balance = account_invoice_line_id.price_unit - account_invoice_line_id.rem_amount
                        