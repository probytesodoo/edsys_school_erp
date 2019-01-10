# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from lxml import etree

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    @api.multi
    def reconcile(self,  type='auto', writeoff_acc_id=False, writeoff_period_id=False,
                  writeoff_journal_id=False):
        print self,'=======================contest'
        print '========================reconcile======================='
        cheque = False
        re_reg_std_obj = ''
        pdc = ''
        if 're_reg_student_rec' in self:
            re_reg_obj = self.env['re.reg.waiting.responce.student'].browse( _context)
            re_reg_std_obj = re_reg_obj.search([('code', '=', str(context['re_reg_student_rec']))])

        if 'pdc_id' in self:
            print context,'=================context'
            pdc_rec_obj = self.env['pdc.detail'].browse( _context)
            pdc = pdc_rec_obj.search([('id', '=', str(_context['pdc_id']))])

        account_obj = self.env['account.account']
        move_obj = self.env['account.move']
        move_rec_obj = self.env['account.move.reconcile']
        partner_obj = self.env['res.partner']
        currency_obj = self.env['res.currency']
        lines = self.browse( self._context)
        unrec_lines = filter(lambda x: not x['reconcile_id'], lines)
        credit = debit = 0.0
        currency = 0.0
        account_id = False
        partner_id = False
        if _context is None:
            _context = {}
        company_list = []
        for line in lines:
            if company_list and not line.company_id.id in company_list:
                raise UserError(_('To reconcile the entries company should be the same for all entries.'))
            company_list.append(line.company_id.id)
        for line in unrec_lines:
            if line.state <> 'valid':
                raise UserError(_('Entry "%s" is not valid !') % line.name)
            credit += line['credit']
            debit += line['debit']
            currency += line['amount_currency'] or 0.0
            account_id = line['account_id']['id']
            partner_id = (line['partner_id'] and line['partner_id']['id']) or False
        writeoff = debit - credit

        if context.has_key('cheque') and context['cheque']:
            cheque = context['cheque']

        # Ifdate_p in context => take this date
        if context.has_key('date_p') and context['date_p']:
            date = context['date_p']
        else:
            date = time.strftime('%Y-%m-%d')
        cr.execute('SELECT account_id, reconcile_id ' \
                   'FROM account_move_line ' \
                   'WHERE id IN %s ' \
                   'GROUP BY account_id,reconcile_id',
                   (tuple(ids),))
        r = cr.fetchall()
        # TODO: move this check to a constraint in the account_move_reconcile object
        if cheque:
            pass
        else:
            if len(r) != 1:
                raise UserError(_('Entries are not of the same account or already reconciled ! '))
        if not unrec_lines:
            raise UserError(_('Entry is already reconciled.'))
        account = account_obj.browse(account_id,  self._context)
        if not account.reconcile:
            raise UserError(_('The account is not defined to be reconciled !'))
        if r[0][1] != None:
            raise UserError(_('Some entries are already reconciled.'))

        if (not currency_obj.is_zero( account.company_id.currency_id, writeoff)) or \
                (account.currency_id and (not currency_obj.is_zero( account.currency_id, currency))):
            if not writeoff_acc_id:
                raise UserError(_('You have to provide an account for the write off/exchange difference entry.'))
            if writeoff > 0:
                debit = writeoff
                credit = 0.0
                self_credit = writeoff
                self_debit = 0.0
            else:
                debit = 0.0
                credit = -writeoff
                self_credit = 0.0
                self_debit = -writeoff
            # If comment exist in context, take it
            if 'comment' in  self._context and  self._context['comment']:
                libelle =  self._context['comment']
            else:
                libelle = _('Write-Off')

            cur_obj = self.env['res.currency']
            cur_id = False
            amount_currency_writeoff = 0.0
            if  self._context.get('company_currency_id', False) !=  self._context.get('currency_id', False):
                cur_id =  self._context.get('currency_id', False)
                for line in unrec_lines:
                    if line.currency_id and line.currency_id.id ==  self._context.get('currency_id', False):
                        amount_currency_writeoff += line.amount_currency
                    else:
                        tmp_amount = cur_obj.compute( line.account_id.company_id.currency_id.id,
                                                      self._context.get('currency_id', False), abs(line.debit - line.credit),
                                                     _context={'date': line.date})
                        amount_currency_writeoff += (line.debit > 0) and tmp_amount or -tmp_amount

            writeoff_lines = [
                (0, 0, {
                    'name': libelle,
                    'debit': self_debit,
                    'credit': self_credit,
                    'account_id': account_id,
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': amount_currency_writeoff and -1 * amount_currency_writeoff or (
                    account.currency_id.id and -1 * currency or 0.0)
                }),
                (0, 0, {
                    'name': libelle,
                    'debit': debit,
                    'credit': credit,
                    'account_id': writeoff_acc_id,
                    'analytic_account_id':  self._context.get('analytic_id', False),
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': amount_currency_writeoff and amount_currency_writeoff or (
                    account.currency_id.id and currency or 0.0)
                })
            ]

            writeoff_move_id = move_obj.create({
                'period_id': writeoff_period_id,
                'journal_id': writeoff_journal_id,
                'date': date,
                'state': 'draft',
                'line_id': writeoff_lines
            })

            writeoff_line_ids = self.search(
                                            [('move_id', '=', writeoff_move_id), ('account_id', '=', account_id)])
            if account_id == writeoff_acc_id:
                writeoff_line_ids = [writeoff_line_ids[1]]
            ids += writeoff_line_ids

        # marking the lines as reconciled does not change their validity, so there is no need
        # to revalidate their moves completely.
        reconcile_context = dict( self._context, novalidate=True)
        r_id = move_rec_obj.create( {'type': type}, _context=reconcile_context)
        self.write({'reconcile_id': r_id, 'reconcile_partial_id': False}, _context=reconcile_context)

        # the id of the move.reconcile is written in the move.line (self) by the create method above
        # because of the way the line_id are defined: (4, x, False)
        for id in ids:
            workflow.trg_trigger( 'account.move.line')

        if lines and lines[0]:
            partner_id = lines[0].partner_id and lines[0].partner_id.id or False
            if partner_id and not partner_obj.has_something_to_reconcile( partner_id,  self._context):
                partner_obj.mark_as_reconciled( [partner_id],  self._context)
                
        if re_reg_std_obj:
            re_reg_std_obj.state = 'awaiting_re_registration_fee'
            re_reg_std_obj.fee_status = 're_unpaid'
            re_reg_std_obj.total_paid_amount = 0.00
            re_reg_parent = re_reg_std_obj.re_reg_parents
            if re_reg_parent:
                re_reg_parent.state = 'awaiting_re_registration_fee'
        if pdc:
            pdc.state = 'bounced'

	if 'invoice_ids' in  self._context and  self._context['invoice_ids']:

            invoice_rec_obj = self.env['account.invoice'].browse(  self._context)
            for invoice_id in json.loads(context['invoice_ids']):

                invoice_rec = invoice_rec_obj.search([('id', '=', str(invoice_id))])
                total_amount = 0.0
                sortBy = "priority desc"
                current_date = time.strftime('%Y-%m-%d')

                account_invoice_line = self.env['account.invoice.line'].browse(  self._context)

                for record in invoice_rec:
                    if record.state == 'open':
                        if record.payment_move_line_ids:
                            for payment_id in record.payment_move_line_ids:
                                total_amount = total_amount + payment_id.credit

                            account_invoice_line_ids = account_invoice_line.search([('invoice_id', '=', record.id)],
                                                                                   order=sortBy)
                            for account_invoice_line_id in account_invoice_line_ids:
                                if total_amount > 0:
                                    if account_invoice_line_id.price_subtotal < 0:
                                        total_amount += abs(account_invoice_line_id.price_subtotal)
                                    if total_amount > account_invoice_line_id.price_subtotal:
                                        print total_amount - account_invoice_line_id.price_subtotal, '=====line_amount - account_invoice_line_id.allocation'
                                        account_invoice_line_id.rem_amount = 0.0
                                        total_amount -= account_invoice_line_id.price_subtotal
                                    else:
                                        account_invoice_line_id.rem_amount = account_invoice_line_id.price_subtotal - total_amount
                                        total_amount = 0
                                else:
                                    account_invoice_line_id.rem_amount = account_invoice_line_id.price_subtotal - total_amount
                        else:
                            account_invoice_line_ids = account_invoice_line.search([('invoice_id', '=', record.id)],
                                                                                   order=sortBy)
                            for account_invoice_line_id in account_invoice_line_ids:
                                account_invoice_line_id.rem_amount = account_invoice_line_id.price_subtotal - total_amount
                                account_invoice_line_id.amount_balance = 0

        return r_id
    
        
