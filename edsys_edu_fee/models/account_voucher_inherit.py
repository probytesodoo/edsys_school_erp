from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.report import render, report_sxw
from odoo.tools import float_compare


class account_voucher_inherit(models.Model):
    _inherit = "account.voucher"
    _track = {
        'state': {
            'account_voucher.mt_voucher_state_change': lambda self,  obj, ctx=None: True,
        },
    }

    account_id = fields.Many2one('account.account',string='Account')
    payment_ids = fields.Many2many('account.move.line', string='Payments',
        compute='_compute_payments')
    amount = fields.Float('Paid Amount')
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
    writeoff_amount = fields.Float(compute='_get_writeoff_amount', string='Difference Amount', help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines.")
    analytic_id = fields.Many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]})
    pay_now = fields.Selection([('pay_now','Pay Directly'),('pay_later','Pay Later or Group Funds')],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]})
   
    currency_id = fields.Many2one('res.currency', compute='_get_journal_currency',
        string='Currency', readonly=True, required=True, default=lambda self: self._get_currency())
    voucher_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('payment','Payment'),
        ('receipt','Receipt')
        ], string='Type', readonly=True, states={'draft': [('readonly', False)]}, oldname="type")
   
    def _compute_writeoff_amount(self,  line_dr_ids, line_cr_ids, amount, type):
        debit = credit = 0.0
        sign = type == 'payment' and -1 or 1
        for l in line_dr_ids:
            if isinstance(l, dict):
                debit += l['amount']
        for l in line_cr_ids:
            if isinstance(l, dict):
                credit += l['amount']
        return amount - sign * (credit - debit)

    def onchange_line_ids(self, line_dr_ids, line_cr_ids, amount, voucher_currency, type, context=None):
        context = context or {}
        if not line_dr_ids and not line_cr_ids:
            return {'value':{'writeoff_amount': 0.0}}
        # resolve lists of commands into lists of dicts
        line_dr_ids = self.resolve_2many_commands( 'line_dr_ids', line_dr_ids, ['amount'])
        line_cr_ids = self.resolve_2many_commands( 'line_cr_ids', line_cr_ids, ['amount'])
        #compute the field is_multi_currency that is used to hide/display options linked to secondary currency on the voucher
        is_multi_currency = False
        #loop on the voucher lines to see if one of these has a secondary currency. If yes, we need to see the options
        for voucher_line in line_dr_ids+line_cr_ids:
            line_id = voucher_line.get('id') and self.env['account.voucher.line'].browse( voucher_line['id']).move_line_id.id or voucher_line.get('move_line_id')
            if line_id and self.env['account.move.line'].browse( line_id ).currency_id:
                is_multi_currency = True
                break
        return {'value': {'writeoff_amount': self._compute_writeoff_amount( line_dr_ids, line_cr_ids, amount, type), 'is_multi_currency': is_multi_currency}}

    

    

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
        
        
    def onchange_partner_id_id(self, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        print amount,';;;;;;;;;;;;;;;;;;;;;;   amount   ;;;;;;;;;;;;;;;;;;;;;'
        print '=================oncahnge partner idid================'
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(partner_id, journal_id, amount, currency_id, ttype, date, context)
        vals2 = self.recompute_payment_rate(vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        return res
          
    def basic_onchange_partner(self, partner_id, journal_id, ttype, context=None):
        print '=======================basic onchange parttner==========='
        partner_pool = self.env['res.partner']
        journal_pool = self.env['account.journal']
        res = {'value': {'account_id': False}}
        if not partner_id or not journal_id:
           return res
  
        journal = journal_pool.browse(journal_id)
        partner = partner_pool.browse(partner_id)
        account_id = False
        if journal.type in ('sale','sale_refund'):
           account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
           account_id = partner.property_account_payable.id
        elif ttype in ('sale', 'receipt'):
           account_id = journal.default_debit_account_id.id
        elif ttype in ('purchase', 'payment'):
           account_id = journal.default_credit_account_id.id
        else:
           account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
  
        res['value']['account_id'] = account_id
        return res

    def recompute_voucher_lines(self, partner_id, journal_id, price, currency_id, ttype, date,
                                context=None):
        print price,'============================price****************************'
       

        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        print '======================recompute_voucher_lines================================'
        # def _remove_noise_in_o2m():
        #     """if the line is partially reconciled, then we must pay attention to display it only once and
        #         in the good o2m.
        #         This function returns True if the line is considered as noise and should not be displayed
        #     """
        #     if line.reconcile_partial_id:
        #         if currency_id == line.currency_id.id:
        #             if line.amount_residual_currency <= 0:
        #                 return True
        #         else:
        #             if line.amount_residual <= 0:
        #                 return True
        #     return False
        #
        # if context is None:
        #     context = {}
        # context_multi_currency = context.copy()

        currency_pool = self.env['res.currency']
        move_line_pool = self.env['account.move.line']
        partner_pool = self.env['res.partner']
        journal_pool = self.env['account.journal']
        line_pool = self.env['account.voucher.line']

        # set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        ids =self._ids
        line_ids = ids and line_pool.search([('voucher_id', '=', ids[0])])
        for each_line_id in line_ids:
            line = line_pool.search([('id' ,'=',each_line_id)])
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(self.env.context.get('journal_id', False))
        partner = partner_pool.browse(self.env.context.get('partner_id', False))
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.env['account.account'].browse(context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            print total_credit,'???????????????????????????????????????????total credit'
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):

            ids = move_line_pool.search([('account_id.internal_type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]).ids

        else:

            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []
        print ids,'====>'
        # order the lines by most old first
        ids.reverse()
        account_move_lines = self.env['account.move.line'].browse(ids)

        # compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            print line,'======================line'
            # if _remove_noise_in_o2m():
            #     continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    print line.invoice_id,'-------------------invoice id'
                    # if the invoice linked to the voucher line is equal to the invoice_id in context
                    # then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                # otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    # if the amount residual is equal the amount voucher, we assign it to that voucher
                    # line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                # otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit and line.amount_residual or 0.0
                total_debit += line.debit and line.amount_residual or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                line_residual = currency_pool.compute(company_currency, currency_id, abs(line.amount_residual),
                                                      )
                total_credit += line.credit and line_residual or 0.0
                total_debit += line.debit and line_residual or 0.0

        remaining_amount = price
        print remaining_amount,'=======================remaining amount'
        # voucher line creation
        for line in account_move_lines:

            # if _remove_noise_in_o2m():
            #     continue

            if line.currency_id and currency_id == line.currency_id.id:
                print line.currency_id,'=============currency_id'
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                # always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                currency_pool=self.env['res.currency'].search([('id','=',currency_id)])
                amount_original = currency_pool.compute(line.credit or line.debit or 0.0,company_currency)
                print amount_original,'---------------------amount_original--------------'

                amount_unreconciled = currency_pool.compute(abs(line.amount_residual),company_currency
                                                           )
                print amount_unreconciled,'------------------------amount_unreconciled'
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name': line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id': line.id,
                'account_id': line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original': line.date,
                'date_due': line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            print rs,"222222222222222222222222222222222222222222222222222           rs"
            remaining_amount -= rs['amount']
            print remaining_amount,'------------------------------remaining maount'
            # in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            # on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                        print'----------------------'
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount
                        print'============================='

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(
                                                                                default['value']['line_dr_ids'],
                                                                                default['value']['line_cr_ids'], price,
                                                                                ttype)
        return default

    

    def recompute_payment_rate(self, vals, currency_id, date, ttype, journal_id, amount, context=None):
        if context is None:
            context = {}
        # on change of the journal, we need to set also the default value for payment_rate and payment_rate_currency_id
        currency_obj = self.env['res.currency']
        journal = self.env['account.journal'].search([('id','=', journal_id)])
        company_id = journal.company_id.id
        payment_rate = 1.0
        currency_id = currency_id or journal.company_id.currency_id.id
        payment_rate_currency_id = currency_id
        ctx = context.copy()
        ctx.update({'date': date})
        o2m_to_loop = False
        if ttype == 'receipt':
            o2m_to_loop = 'line_cr_ids'
        elif ttype == 'payment':
            o2m_to_loop = 'line_dr_ids'
        if o2m_to_loop and 'value' in vals and o2m_to_loop in vals['value']:
            for voucher_line in vals['value'][o2m_to_loop]:
                if not isinstance(voucher_line, dict):
                    continue
                if voucher_line['currency_id'] != currency_id:
                    # we take as default value for the payment_rate_currency_id, the currency of the first invoice that
                    # is not in the voucher currency
                    payment_rate_currency_id = voucher_line['currency_id']
                    tmp = currency_obj.browse(payment_rate_currency_id).rate
                    payment_rate = tmp / currency_obj.browse(currency_id).rate
                    break
        vals['value'].update({
            'payment_rate': payment_rate,
            'currency_id': currency_id,
            'payment_rate_currency_id': payment_rate_currency_id
        })
        # read the voucher rate with the right date in the context
        # voucher_rate = self.env['res.currency'].read([currency_id], ['rate'])[0]['rate']
        voucher_rate = self.env['res.currency'].search([('id', '=', currency_id)]).rate
        ctx.update({
            'voucher_special_currency_rate': payment_rate * voucher_rate,
            'voucher_special_currency': payment_rate_currency_id})
        res = self.onchange_rate(payment_rate, amount, currency_id, payment_rate_currency_id, company_id,
                                 context=ctx)
        for key in res.keys():
            vals[key].update(res[key])
        return vals
    
    
    def onchange_rate(self, rate, amount, currency_id, payment_rate_currency_id, company_id,
                      context=None):
        res = {'value': {'paid_amount_in_company_currency': amount,
                         'currency_help_label': self._get_currency_help_label(currency_id, rate,
                                                                              payment_rate_currency_id)}}
        if rate and amount and currency_id:
            reso = self.env['res.currency'].search([('id','=',currency_id)])
            company_currency = self.env['res.company'].search([('id','=',company_id)]).currency_id
            # context should contain the date, the payment currency and the payment rate specified on the voucher
            #                                                                    company_currency.id, amount)
            amount_in_company_currency = reso.compute(amount, company_currency)


            res['value']['paid_amount_in_company_currency'] = amount_in_company_currency
        return res
    
    
    @api.multi
    def action_move_line_create(self):
        print '-----------------------------action move oline create injerit======='
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher
            move_line = self.env['account.move.line'].with_context(ctx).create(voucher.first_move_line_get(move.id, company_currency, current_currency))
            line_total = move_line.debit - move_line.credit
            if voucher.type == 'sale' or 'receipt' :
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.type == 'purchase' or 'payment':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, voucher.id,move.id, company_currency, current_currency)

            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search([('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                        'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

            # We post the voucher.
            voucher.write({
                'move_id': move.id,
                'state': 'posted',
                'number': move.name
            })
            move.post()
        return True

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        print '1111111111111111111 first move line get   1111111111'
        debit = credit = 0.0
        if self.type == ('purchase', 'payment'):
            credit = self._convert_amount(self.amount)
            print credit,'-----------credit'
        elif self.type == ('sale', 'receipt'):
            debit = self._convert_amount(self.amount)
            print debit,'----------debit'
        if debit < 0.0: debit = 0.0
        if credit < 0.0: credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': self.account_id.id,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due
            }
        print move_line,'9999999999999999 move line9999999999999'
        return move_line


    
#     def first_move_line_get(self, voucher_id, move_id, company_currency, current_currency):
#         '''
#         Return a dict to be use to create the first account move line of given voucher.
# 
#         :param voucher_id: Id of voucher what we are creating account_move.
#         :param move_id: Id of account move where this line will be added.
#         :param company_currency: id of currency of the company to which the voucher belong
#         :param current_currency: id of currency of the voucher
#         :return: mapping between fieldname and value of account move line to create
#         :rtype: dict
#         '''
#         voucher = self.env['account.voucher'].browse(voucher_id)
#         debit = credit = 0.0
#         # TODO: is there any other alternative then the voucher type ??
#         # ANSWER: We can have payment and receipt "In Advance".
#         # TODO: Make this logic available.
#         # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
#         if voucher.type in ('purchase', 'payment'):
#             credit = voucher.paid_amount_in_company_currency
#         elif voucher.type in ('sale', 'receipt'):
#             debit = voucher.paid_amount_in_company_currency
#         if debit < 0: credit = -debit; debit = 0.0
#         if credit < 0: debit = -credit; credit = 0.0
#         sign = debit - credit < 0 and -1 or 1
#         #set the first line of the voucher
#         move_line = {
#                 'name': voucher.name or '/',
#                 'debit': debit,
#                 'credit': credit,
#                 'account_id': voucher.account_id.id,
#                 'move_id': move_id,
#                 'journal_id': voucher.journal_id.id,
#                 'period_id': voucher.period_id.id,
#                 'partner_id': voucher.partner_id.id,
#                 'currency_id': company_currency <> current_currency and  current_currency or False,
#                 'amount_currency': (sign * abs(voucher.amount) # amount < 0 for refunds
#                     if company_currency != current_currency else 0.0),
#                 'date': voucher.date,
#                 'date_maturity': voucher.date_due
#             }
#         return move_line
    @api.multi
    def voucher_move_line_create(self, voucher_id, move_id, line_total,company_currency, current_currency, ):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).
 
        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
         
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
 
        tax_obj = self.env['account.tax']
        tot_line = line_total
        rec_lst_ids = []
         
        date = ''
        ctx = self._context.copy()
        ctx.update({'date': date})
        voucher = self.env['account.voucher'].browse( voucher_id)
        voucher_currency = voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.env['decimal.precision'].precision_get( 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount( line.untax_amount or line.amount)
         
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = line.type =='dr' and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'
 
            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount
 
#             if voucher.tax_id and voucher.type in ('sale', 'purchase'):
#                 move_line.update({
#                     'account_tax_id': voucher.tax_id.id,
#                 })
 
            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute( company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - abs(amount_currency)
 
            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.sudo().create( move_line)
            rec_ids = [voucher_line, line.move_line_id.id]
 
            if not currency_obj.is_zero( voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines( line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create( exch_lines[0],context)
                move_line_obj.create( exch_lines[1], context)
                rec_ids.append(new_id)
 
            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero( line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': (-1 if line.type == 'cr' else 1) * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create( move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)
     
    @api.multi
    def writeoff_move_line_get(self, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        print '========================eriteofffo ammline ge============='
        '''
        Set a dict to be use to create the writeoff move line.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param line_total: Amount remaining to be allocated on lines.
        :param move_id: Id of account move where this line will be added.
        :param name: Description of account move line.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        currency_obj = self.env['res.currency']
        move_line = {}

        voucher = self.env['account.voucher'].browse(voucher_id)
        current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id

        if not currency_obj.is_zero(current_currency_obj):
            diff = line_total
            account_id = False
            write_off_name = ''
            if voucher.payment_option == 'with_writeoff':
                account_id = voucher.writeoff_acc_id.id
                write_off_name = voucher.comment
            elif voucher.partner_id:
                if voucher.type in ('sale', 'receipt'):
                    account_id = voucher.partner_id.property_account_receivable_id
                else:
                    account_id = voucher.partner_id.property_account_payable_id
            else:
                # fallback on account of voucher
                account_id = voucher.account_id.id
            sign = voucher.type == 'payment' and -1 or 1
            move_line = {
                'name': write_off_name or name,
                'account_id': account_id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'date': voucher.date,
                'credit': diff > 0 and diff or 0.0,
                'debit': diff < 0 and -diff or 0.0,
                'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.writeoff_amount) or 0.0,
                'currency_id': company_currency <> current_currency and current_currency or False,
                'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
            }

        return move_line
    
    
    def _get_company_currency(self,  voucher_id):
        '''
        Get the currency of the actual company.

        :param voucher_id: Id of the voucher what i want to obtain company currency.
        :return: currency id of the company of the voucher
        :rtype: int
        '''
        return self.env['account.voucher'].browse(voucher_id).journal_id.company_id.currency_id.id
    
    def _get_current_currency(self, voucher_id):
        '''
        Get the currency of the voucher.

        :param voucher_id: Id of the voucher what i want to obtain current currency.
        :return: currency id of the voucher
        :rtype: int
        '''
        voucher = self.env['account.voucher'].browse(voucher_id)
        return voucher.currency_id.id or self._get_company_currency(voucher.id)

    def _sel_context(self, voucher_id ):
        """
        Select the context to use accordingly if it needs to be multicurrency or not.

        :param voucher_id: Id of the actual voucher
        :return: The returned context will be the same as given in parameter if the voucher currency is the same
                 than the company currency, otherwise it's a copy of the parameter with an extra key 'date' containing
                 the date of the voucher.
        :rtype: dict
        """
        company_currency = self._get_company_currency( voucher_id,)
        current_currency = self._get_current_currency( voucher_id)
        if current_currency <> company_currency:
            context_multi_currency = self._context.copy()
            voucher = self.env['account.voucher'].browse(voucher_id)
            context_multi_currency.update({'date': voucher.date})
            return context_multi_currency
        return self._context
   
    
#     def action_move_line_create(self):
#         print '=============action move line creat------------'
#         '''
#         Confirm the vouchers given in ids and create the journal entries for each of them
#         '''
# #         if context is None:
# #             context = {}
#         move_pool = self.env['account.move']
#         move_line_pool = self.env['account.move.line']
#         for voucher in self:
#             local_context = dict( force_company=voucher.journal_id.company_id.id)
#             if voucher.move_id:
#                 continue
#             company_currency = self._get_company_currency( voucher.id)
#             current_currency = self._get_current_currency( voucher.id,)
#             # we select the context to use accordingly if it's a multicurrency case or not
#             context = self._sel_context( voucher.id)
#             # But for the operations made by _convert_amount, we always need to give the date in the context
#             ctx = context.copy()
#             ctx.update({'date': voucher.date})
#             # Create the account move record.
#             move_id = move_pool.create(self.account_move_get() )
#             move = self.env['account.move'].create(voucher.account_move_get())
#             # Get the name of the account_move just created
#             name = move_pool.browse( move_id)
#             # Create the first line of the voucher
#             move_line = self.env['account.move.line'].with_context(ctx).create(voucher.first_move_line_get(move.id,voucher.id, company_currency, current_currency))
#             line_total = move_line.debit - move_line.credit
#             line_total = move_line_brw.debit - move_line_brw.credit
#             rec_list_ids = []
#             if voucher.type == 'sale':
#                 line_total = line_total - self._convert_amount( voucher.tax_amount, voucher.id, _context=ctx)
#             elif voucher.type == 'purchase':
#                 line_total = line_total + self._convert_amount( voucher.tax_amount, voucher.id, _context=ctx)
#             # Create one move line per voucher line where amount is not 0.0
#             line_total, rec_list_ids = self.voucher_move_line_create( voucher.id, line_total, move_id, company_currency, current_currency, context)
# 
#             # Create the writeoff line if needed
#             ml_writeoff = self.writeoff_move_line_get( voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
#             if ml_writeoff:
#                 move_line.create( ml_writeoff, local_context)
#             # We post the voucher.
#             self.write(cr, uid, [voucher.id], {
#                 'move_id': move_id,
#                 'state': 'posted',
#                 'number': name,
#             })
#             if voucher.journal_id.entry_posted:
#                 move_pool.post(cr, uid, [move_id], context={})
#             # We automatically reconcile the account move lines.
#             reconcile = False
#             for rec_ids in rec_list_ids:
#                 if len(rec_ids) >= 2:
#                     reconcile = move_line_pool.reconcile_partial(rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
#         return True

    
#     @api.multi
#     def action_move_line_create(self):
#         print '================action move line create==================='
#         '''
#         Confirm the vouchers given in ids and create the journal entries for each of them
#         '''
#         move_pool = self.env['account.move']
#         move_line_pool = self.env['account.move.line']
#         for voucher in self:
#             local_context = dict( force_company=voucher.journal_id.company_id.id)
#             if voucher.move_id:
#                 continue
#             company_currency = voucher.journal_id.company_id.currency_id.id
#             current_currency = voucher.currency_id.id or company_currency
#             # we select the context to use accordingly if it's a multicurrency case or not
#             # But for the operations made by _convert_amount, we always need to give the date in the context
#             ctx = local_context.copy()
#             ctx['date'] = voucher.account_date
#             ctx['check_move_validity'] = False
#              # Create the account move record.
#             move_id = move_pool.create(self.account_move_get())
#             # Get the name of the account_move just created
#             name = move_pool.browse( move_id)
#             # Create the account move record.
#               
#             move = self.env['account.move'].create(voucher.account_move_get())
#             # Get the name of the account_move just created
#             # Create the first line of the voucher
#             move_line = self.env['account.move.line'].with_context(ctx).create(voucher.first_move_line_get(move.id, company_currency, current_currency))
#             line_total = move_line.debit - move_line.credit
#             print line_total,'===========================line total'
#             rec_list_ids = []
#             if voucher.type == 'sale':
#                 line_total = line_total - voucher._convert_amount(voucher.tax_amount)
#                 print line_total,'--------------------line total sale==============='
#             elif voucher.type == 'purchase':
#                 line_total = line_total + voucher._convert_amount(voucher.tax_amount)
#             # Create one move line per voucher line where amount is not 0.0
#             line_total, rec_list_ids = self.voucher_move_line_create(voucher.id,  line_total, company_currency, current_currency)
#   
#              
#               
#              
#             # Add tax correction to move line if any tax correction specified
#             if voucher.tax_correction != 0.0:
#                 tax_move_line = self.env['account.move.line'].search([('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
#                 if len(tax_move_line):
#                     tax_move_line.write({'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
#                         'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})
#             # Create the writeoff line if needed
#             ml_writeoff = self.writeoff_move_line_get(voucher.id, line_total, move_id, name, company_currency, current_currency, )
#             if ml_writeoff:
#                 move_line_pool.create( ml_writeoff)
#             # We post the voucher.
#             self.write( [voucher.id], {
#                 'move_id': move_id,
#                 'state': 'posted',
#                 'number': name,
#             })
#             voucher.write({
#                 'move_id': move.id,
#                 'state': 'posted',
#                 'number': move.name
#             })
#              
#             reconcile = False
#             for rec_ids in rec_list_ids:
#                 if len(rec_ids) >= 2:
#                     reconcile = move_line_pool.reconcile_partial( rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
#             move.post()
#         return True

    

    # def onchange_amount(self,context):
    #     """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
    #     if not context:
    #         context = {}
    #     default = super(account_voucher, self).onchange_amount()
    #     if 'value' in default:
    #         amount = 'amount' in default['value'] and default['value']['amount'] or amount
    #         amount_in_word = self._amount_to_text(amount, currency_id, context=context)
    #         default['value'].update({'amount_in_word':amount_in_word})
    #         if journal_id:
    #             allow_check_writing = self.env['account.journal'].browse(journal_id).allow_check_writing
    #             default['value'].update({'allow_check':allow_check_writing})
    #     return default

    def proforma_voucher(self):
        self.action_move_line_create()
        return True

    def action_cancel_draft(self):
        self.create_workflow()
        self.write({'state':'draft'})
        return True


    def cancel_voucher(self,context=None):
        reconcile_pool = self.env['account.move.reconcile']
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for voucher in self:
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't unreconcile an already unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink( [line.reconcile_id.id])
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial( move_lines, 'auto',)
#             if voucher.move_id:
#                 move_pool.button_cancel( [voucher.move_id.id])
#                 move_pool.unlink( [voucher.move_id.id])
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write( res)
        return True
   
    @api.multi
    def _paid_amount_in_company_currency(self):
        if self._context is None:
            self._context = {}
        res = {}
        ctx = self._context.copy()
        for v in self:
            ctx.update({'date': v.date})
            #make a new call to browse in order to have the right date in the context, to get the right currency rate
            voucher = self.browse(v.id)
            ctx.update({
              'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,
              'voucher_special_currency_rate': voucher.currency_id.rate * voucher.payment_rate,})
            res[voucher.id] =  self.env['res.currency']
        return res

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(self._context.get('journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id
    
    @api.one
    @api.depends('journal_id', 'company_id')
    def _get_journal_currency(self):
        self.currency_id = self.journal_id.currency_id.id or self.company_id.currency_id.id


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


    def _compute_balance(self):
        currency_pool = self.env['res.currency']
        rs_data = {}
        for line in self.browse():
            ctx = self._context.copy()
            ctx.update({'date': line.voucher_id.date})
            voucher_rate = self.env['res.currency'].read(line.voucher_id.currency_id.id, ['rate'], context=ctx)['rate']
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
                res['amount_original'] = currency_pool.compute( company_currency, voucher_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute( company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)

            rs_data[line.id] = res
        return rs_data
    type = fields.Selection([('dr','Debit'),('cr','Credit')], 'Dr/Cr')
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'))
    move_line_id= fields.Many2one('account.move.line', 'Journal Item', copy=False)
    date_due = fields.Date(Related='move_line_id.date_maturity',relation='account.move.line', string='Due Date', readonly=1)
    date_original = fields.Date(Related='move_line_id.date',relation='account.move.line', string='Date', readonly=1)
    amount_original = fields.Float(compute='_compute_balance', multi='dc',string='Original Amount', store=True, digits_compute=dp.get_precision('Account'))
    amount_unreconciled = fields.Float(compute='_compute_balance', multi='dc',string='Open Balance', store=True, digits_compute=dp.get_precision('Account'))
    voucher_id =fields.Many2one('account.voucher', 'Voucher', required=1, ondelete='cascade')
    state = fields.Char(Related='voucher_id.state', string='State', readonly=True)
    reconcile = fields.Boolean('Full Reconcile')
    untax_amount = fields.Float('Untax Amount')

    @api.multi
    def onchange_reconcile(self):
        vals = {'amount': 0.0}
        if self.reconcile:
            vals = { 'amount': self.amount_unreconciled}
        return {'value': vals}

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
        move_line_id = self.move_line_id
        if move_line_id:
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

    ref = fields.Char(related='move_id.ref', string='Reference', store=True)
    move_id = fields.Many2one('account.move', 'Journal Entry', ondelete="cascade", help="The move of this entry line.", select=2, required=True, auto_join=True)
    debit = fields.Float('Debit', digits_compute=dp.get_precision('Account'))
    credit = fields.Float('Credit', digits_compute=dp.get_precision('Account'))
    # amount_currency = fields.Float('Amount Currency', help="The amount expressed in an optional other currency.")
    amount_currency = fields.Monetary('Amount Currency', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account'))
    date_maturity = fields.Date('Due date', select=True ,help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    reconcile_id = fields.Many2one('account.move.reconcile', 'Reconcile', readonly=True, ondelete='set null', select=2, copy=False)
    state = fields.Selection([('draft','Unbalanced'), ('valid','Balanced')], 'Status', readonly=True, copy=False)
    statement_id = fields.Many2one('account.bank.statement', 'Statement', help="The bank statement used for bank reconciliation", select=1, copy=False)

class account_invoice_inherit(models.Model):
    _inherit = "account.invoice"

    # payment_ids_ids = fields.Many2many('account.move.line', string='Payments',
    #     compute='_compute_payments')

    # credit = fields.Float('Credit', digits_compute=dp.get_precision('Account'))
    # debit = fields.Float('Debit', digits_compute=dp.get_precision('Account'))
    # date = fields.Date(string='Payment Date')
# 
#     # def _compute_payments(self):
#     #     partial_lines = lines = self.env['account.move.line']
#     #     for line in self.move_id.line_ids:
#     #         if line.account_id != self.account_id:
#     #             continue
#     #         if line.reconcile_id:
#     #             lines |= line.reconcile_id.line_ids
#     #         elif line.reconcile_partial_id:
#     #             lines |= line.reconcile_partial_id.line_partial_ids
#     #         partial_lines += line
#     #     self.payment_ids = (lines - partial_lines).sorted()


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