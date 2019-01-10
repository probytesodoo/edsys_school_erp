from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.report import render, report_sxw


class account_voucher_inherit(models.Model):
    _inherit = "account.voucher"
    _track = {
        'state': {
            'account_voucher.mt_voucher_state_change': lambda self, cr, uid, obj, ctx=None: True,
        },
    }

    
    payment_ids = fields.Many2many('account.move.line', string='Payments',
        compute='_compute_payments')
    # reconcile = fields.Boolean('Full Reconcile')
    comment = fields.Char('Counterpart Comment', required=False, readonly=True, states={'draft': [('readonly', False)]})
    is_multi_currency = fields.Boolean('Multi Currency Voucher', help='Fields with internal purpose only that depicts if the voucher is a multi currency one or not')
    line_dr_ids = fields.One2many('account.voucher.line','voucher_id','Debits',domain=[('type','=','dr')], context={'default_type':'dr'}, readonly=True, states={'draft':[('readonly',False)]})
    line_cr_ids = fields.One2many('account.voucher.line','voucher_id','Credits',domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)]})
    payment_rate_currency_id = fields.Many2one('res.currency', 'Payment Rate Currency', required=False, readonly=True, states={'draft':[('readonly',False)]})
    payment_rate = fields.Float('Exchange Rate', digits=(12,6), required=False, readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('account.period', 'Period', required=False, readonly=True, states={'draft':[('readonly',False)]})
    writeoff_acc_id = fields.Many2one('account.account', 'Counterpart Account', readonly=True, states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many('account.move.line','move_id',Related='move_id.line_ids', string='Journal Items', readonly=True)
    payment_option = fields.Selection([
                                           ('without_writeoff', 'Keep Open'),
                                           ('with_writeoff', 'Reconcile Payment Balance'),
                                           ], 'Payment Difference', required=False, readonly=True, states={'draft': [('readonly', False)]}, help="This field helps you to choose what you want to do with the eventual difference between the paid amount and the sum of allocated amounts. You can either choose to keep open this difference on the partner's account, or reconcile it with the payment(s)")
    paid_amount_in_company_currency = fields.Float(compute='_paid_amount_in_company_currency', string='Paid Amount in Company Currency',readonly=True)

    type = fields.Selection([('sale','Sale'),('purchase','Purchase'),('payment','Payment'),('receipt','Receipt')],'Default Type', readonly=True, states={'draft':[('readonly',False)]})
    currency_help_label = fields.Text(compute='_fnct_currency_help_label', string="Helping Sentence", help="This sentence helps you to know how to specify the payment rate by giving you the direct effect it has")
    pre_line = fields.Boolean('Previous Payments ?', required=False)
    audit = fields.Boolean(Related='move_id.to_check',help='Check this box if you are unsure of that journal entry and if you want to note it as \'to be reviewed\' by an accounting expert.', relation='account.move', string='To Review')
    writeoff_amount = fields.Float(compute='_get_writeoff_amount', string='Difference Amount', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines.")
    analytic_id = fields.Many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]})
    pay_now = fields.Selection([('pay_now','Pay Directly'),('pay_later','Pay Later or Group Funds')],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]})
    voucher_type = fields.Selection([('sale', 'Sale'),('purchase', 'Purchase')], string='Type', readonly=True, states={'draft': [('readonly', False)]}, oldname="type")
    


   

    def _compute_payments(self):
        partial_lines = lines = self.env['account.move.line']
        for line in self.move_id.line_ids:
            if line.account_id != self.account_id:
                continue
            if line.reconcile_id:
                lines |= line.reconcile_id.line_id
            elif line.reconcile_partial_id:
                lines |= line.reconcile_partial_id.line_partial_ids
            partial_lines += line
        self.payment_ids = (lines - partial_lines).sorted()





    # def onchange_amount(self):
    #     """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
    #     default = super(account_voucher_inherit, self).onchange_amount()
    #     if 'value' in default:
    #         amount = 'amount' in default['value'] and default['value']['amount'] or amount
    #         amount_in_word = self._amount_to_text(amount, currency_id, context=context)
    #         default['value'].update({'amount_in_word':amount_in_word})
    #         if journal_id:
    #             allow_check_writing = self.env['account.journal'].browse(journal_id).allow_check_writing
    #             default['value'].update({'allow_check':allow_check_writing})
    #     return default

    # def proforma_voucher(self):
    #     self.action_move_line_create()
    #     return True

    def action_cancel_draft(self):
        self.create_workflow()
        self.write({'state':'draft'})
        return True


    def cancel_voucher(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't unreconcile an already unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink(cr, uid, [line.reconcile_id.id], context=context)
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(cr, uid, move_lines, 'auto',context=context)
            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id], context=context)
                move_pool.unlink(cr, uid, [voucher.move_id.id], context=context)
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write(cr, uid, ids, res, context=context)
        return True

    def _paid_amount_in_company_currency(self, context=None):
        if context is None:
            context = {}
        res = {}
        ctx = context.copy()
        for v in self:
            ctx.update({'date': v.date})
            #make a new call to browse in order to have the right date in the context, to get the right currency rate
            voucher = self.browse(v.id)
            ctx.update({
              'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,
              'voucher_special_currency_rate': voucher.currency_id.rate * voucher.payment_rate,})
            res[voucher.id] =  self.env['res.currency'].compute(voucher.currency_id.id, voucher.company_id.currency_id.id, voucher.amount)
        return res




    def _get_writeoff_amount(self):
        if not id: return {}
        currency_obj = self.env['res.currency']
        res = {}
        for voucher in self:
            debit = credit = 0.0
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            currency = voucher.currency_id or voucher.company_id.currency_id
            res[voucher.id] =  currency_obj.round(voucher.amount - sign * (credit - debit))
        return res

    def _get_currency_help_label(self, currency_id, payment_rate, payment_rate_currency_id):
        """
        This function builds a string to help the users to understand the behavior of the payment rate fields they can specify on the voucher.
        This string is only used to improve the usability in the voucher form view and has no other effect.

        :param currency_id: the voucher currency
        :type currency_id: integer
        :param payment_rate: the value of the payment_rate field of the voucher
        :type payment_rate: float
        :param payment_rate_currency_id: the value of the payment_rate_currency_id field of the voucher
        :type payment_rate_currency_id: integer
        :return: translated string giving a tip on what's the effect of the current payment rate specified
        :rtype: str
        """
        rml_parser = report_sxw.rml_parse(self._cr, self._uid, 'currency_help_label', self._context)
        currency_pool = self.env['res.currency'].browse(currency_id)
        currency_str = payment_rate_str = ' '
        if currency_id:
            currency_str = rml_parser.formatLang(1, currency_pool)
        if payment_rate_currency_id:
            payment_rate_str = rml_parser.formatLang(payment_rate, currency_obj=currency_pool.browse())
        currency_help_label = ('At the operation date, the exchange rate was\n%s = %s') % (
        currency_str, payment_rate_str)
        return currency_help_label

    def _fnct_currency_help_label(self):
        res = {}
        for voucher in self:
            res[voucher.id] = self._get_currency_help_label(voucher.currency_id.id, voucher.payment_rate, voucher.payment_rate_currency_id.id)
        return res

            # self.currency_id = self.journal_id.currency_id.id or self.company_id.currency_id.id
            # res[voucher.id] = self._get_currency_help_label(self.currency_id, self.payment_rate, self.payment_rate_currency_id.id)


        


class account_voucher_line_inherit(models.Model):
    _inherit = "account.voucher.line"
    # _order = "move_line_id"



    type = fields.Selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr')
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'))
    move_line_id= fields.Many2one('account.move.line', 'Journal Item', copy=False)
    date_due = fields.Date(Related='move_line_id.date_maturity',relation='account.move.line', string='Due Date', readonly=1)
    date_original = fields.Date(Related='move_line_id.date',relation='account.move.line', string='Date', readonly=1)
    amount_original = fields.Float(compute='_compute_balance', multi='dc',string='Original Amount', store=True, digits_compute=dp.get_precision('Account'))
    amount_unreconciled = fields.Float(compute='_compute_balance', multi='dc',string='Open Balance', store=True, digits_compute=dp.get_precision('Account'))
    voucher_id =fields.Many2one('account.voucher', 'Voucher', required=1, ondelete='cascade')
    state = fields.Char(Related='voucher_id.state', string='State', readonly=True)



    def _compute_balance(self):
	    currency_pool = self.pool.get('res.currency')
	    rs_data = {}
	    for line in self.browse():
	        ctx = context.copy()
	        ctx.update({'date': line.voucher_id.date})
	        voucher_rate = self.pool.get('res.currency').read(line.voucher_id.currency_id.id, ['rate'], context=ctx)['rate']
	        ctx.update({
	            'voucher_special_currency': line.voucher_id.payment_rate_currency_id and line.voucher_id.payment_rate_currency_id.id or False,
	            'voucher_special_currency_rate': line.voucher_id.payment_rate * voucher_rate})
	        res = {}
	        company_currency = line.voucher_id.journal_id.company_id.currency_id.id
	        voucher_currency = line.voucher_id.currency_id and line.voucher_id.currency_id.id or company_currency
	        move_line = line.move_line_id or False

	        if not move_line:
	            res['amount_original'] = 0.0
	            res['amount_unreconciled'] = 0.0
	        elif move_line.currency_id and voucher_currency==move_line.currency_id.id:
	            res['amount_original'] = abs(move_line.amount_currency)
	            res['amount_unreconciled'] = abs(move_line.amount_residual_currency)
	        else:
	            #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
	            res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
	            res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)

	        rs_data[line.id] = res
	    return rs_data

    @api.onchange('move_line_id')
    def onchange_move_line_id(self):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        move_line_pool = self.env['account.move.line']
        if self.move_line_id:
            move_line = move_line_pool.browse()
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
            res.update({
                'account_id': move_line.account_id.id,
                'type': ttype,
                'currency_id': move_line.currency_id and move_line.currency_id.id or move_line.company_id.currency_id.id,
            })
        return {
            'value':res,
        }




class account_move_line_inherit(models.Model):
    _inherit = "account.move.line"

# ref = fields.Char('move_id', 'ref', string='Reference', store=True)
# move_id = fields.Many2one('account.move', 'Journal Entry', ondelete="cascade", help="The move of this entry line.", select=2, required=True, auto_join=True)
# debit = fields.Float('Debit', digits_compute=dp.get_precision('Account'))
# credit = fields.Float('Credit', digits_compute=dp.get_precision('Account'))
# amount_currency = fields.Float('Amount Currency', help="The amount expressed in an optional other currency.")
    date_maturity = fields.Date('Due date', select=True ,help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    reconcile_id = fields.Many2one('account.move.reconcile', 'Reconcile', readonly=True, ondelete='set null', select=2, copy=False)
    state = fields.Selection([('draft','Unbalanced'), ('valid','Balanced')], 'Status', readonly=True, copy=False)
    statement_id = fields.Many2one('account.bank.statement', 'Statement', help="The bank statement used for bank reconciliation", select=1, copy=False)



class res_currency(models.Model):
    _inherit = "res.currency"


#     def _query_get_get(self, obj='l'):

#         fiscalyear_obj = self.env['account.fiscalyear']
#         fiscalperiod_obj = self.env['account.period']
#         account_obj = self.env['account.account']
#         fiscalyear_ids = []
#         context = dict(self._context or {})
#         initial_bal = context.get('initial_bal', False)
#         company_clause = " "
#         query = ''
#         query_params = {}
#         if context.get('company_id'):
#             company_clause = " AND " +obj+".company_id = %(company_id)s"
#             query_params['company_id'] = context['company_id']
#         if not context.get('fiscalyear'):
#             if context.get('all_fiscalyear'):
#                 #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
#                 fiscalyear_ids = fiscalyear_obj.search([])
#             else:
#                 fiscalyear_ids = self.env['account.fiscalyear'].search([('state', '=', 'draft')]).ids
#         else:
#             #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
#             fiscalyear_ids = context['fiscalyear']
#             if isinstance(context['fiscalyear'], (int, long)):
#                 fiscalyear_ids = [fiscalyear_ids]

#         query_params['fiscalyear_ids'] = tuple(fiscalyear_ids) or (0,)
#         state = context.get('state', False)
#         where_move_state = ''
#         where_move_lines_by_date = ''

#         if context.get('date_from') and context.get('date_to'):
#             query_params['date_from'] = context['date_from']
#             query_params['date_to'] = context['date_to']
#             if initial_bal:
#                 where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < %(date_from)s)"
#             else:
#                 where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= %(date_from)s AND date <= %(date_to)s)"

#         if state:
#             if state.lower() not in ['all']:
#                 query_params['state'] = state
#                 where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = %(state)s)"
#         if context.get('period_from') and context.get('period_to') and not context.get('periods'):
#             if initial_bal:
#                 period_company_id = fiscalperiod_obj.browse(context['period_from'], context=context).company_id.id
#                 first_period = fiscalperiod_obj.search([('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
#                 context['periods'] = fiscalperiod_obj.build_ctx_periods(first_period, context['period_from'])
#             else:
#                 context['periods'] = fiscalperiod_obj.build_ctx_periods(context['period_from'], context['period_to'])
#         if 'periods_special' in context:
#             periods_special = ' AND special = %s ' % bool(context.get('periods_special'))
#         else:
#             periods_special = ''
#         if context.get('periods'):
#             query_params['period_ids'] = tuple(context['periods'])
#             if initial_bal:
#                 query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
#                 period_ids = fiscalperiod_obj.search([('id', 'in', context['periods'])], order='date_start', limit=1)
#                 if period_ids and period_ids[0]:
#                     first_period = fiscalperiod_obj.browse(period_ids[0], context=context)
#                     query_params['date_start'] = first_period.date_start
#                     query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND date_start <= %(date_start)s AND id NOT IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
#             else:
#                 query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND id IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
#         else:
#             query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date

#         if initial_bal and not context.get('periods') and not where_move_lines_by_date:
#             #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
#             #so we have to invalidate this query
#             raise UserError(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))

#         if context.get('journal_ids'):
#             query_params['journal_ids'] = tuple(context['journal_ids'])
#             query += ' AND '+obj+'.journal_id IN %(journal_ids)s'

#         if context.get('chart_account_id'):
#             child_ids = account_obj._get_children_and_consol([context['chart_account_id']], context=context)
#             query_params['child_ids'] = tuple(child_ids)
#             query += ' AND '+obj+'.account_id IN %(child_ids)s'

#         query += company_clause
#         cursor = self.env.cr
#         return cursor.mogrify(query,query_params)
