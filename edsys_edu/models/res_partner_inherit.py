from odoo import models, fields, api
from odoo.exceptions import UserError
class res_partner_has_image(models.Model):
	_inherit = "res.partner"

	@api.multi
	def _has_image(self):
		return dict((p.id, bool(p.image)) for p in self)


	has_image = fields.Boolean(compute='_has_image',string="Image Res")
	property_account_customer_advance = fields.Many2one('account.account',
            string="Account Customer Advance",
            help="This account will be used for advance payment of custom")

	@api.multi
	def _get_re_reg_advance_account(self):
		re_reg_account_rec = self.env['account.account'].search([('code', '=', '210602')])
		for rec in self:
			if rec.is_student or rec.is_parent:
				if re_reg_account_rec.id:
					rec.re_reg_advance_account = re_reg_account_rec.id
				else:
					rec.re_reg_advance_account = False

	# @api.depends('advance_total_recivable')
	# def get_advance_total_recivable(self):
	# 	"""
     #    -----------------------------------------------------
     #    :return:
     #    """
    #
	# 	account_move_line_obj = self.env['account.move.line']
	# 	query = account_move_line_obj._query_get_get()
	# 	for record in self:
	# 		if record.property_account_customer_advance.id:
	# 			amount_difference = 0.00
	# 			# for account_move_line_rec in account_move_line_obj.search([('partner_id','=',record.id)]):
	# 			#     if account_move_line_rec.account_id.id == record.property_account_customer_advance.id:
	# 			#         amount_difference += account_move_line_rec.credit
	# 			#         amount_difference -= account_move_line_rec.debit
	# 			# record.re_reg_total_recivable = amount_difference
	# 			ctx = self._context.copy()
	# 			ctx['all_fiscalyear'] = True
	# 			query = self.env['account.move.line']._query_get_get()
	# 			self._cr.execute("""SELECT l.partner_id, SUM(l.debit),SUM(l.credit), SUM(l.debit-l.credit)
	#                              FROM account_move_line l
	#                              WHERE l.partner_id IN %s
	#                              AND l.account_id IN %s
	#                              AND l.reconcile_id IS NULL
	#                              AND """ + query + """
	#                              GROUP BY l.partner_id
	#                              """, (tuple(record.ids), tuple(record.property_account_customer_advance.ids),))
	# 			fetch = self._cr.fetchall()
	# 			for pid, total_debit, total_credit, val in fetch:
	# 				amount_difference += total_credit
	# 				amount_difference -= total_debit
	# 				self.advance_total_recivable = amount_difference

	@api.depends('re_reg_total_recivable')
	def get_re_registration_total_recivable(self):
		"""
        -----------------------------------------------------
        :return:
        """
		account_move_line_obj = self.env['account.move.line']
		query = account_move_line_obj._query_get()
		for record in self:
			if record.re_reg_advance_account.id:
				amount_difference = 0.00
				# for account_move_line_rec in account_move_line_obj.search([('partner_id','=',record.id)]):
				#     if account_move_line_rec.account_id.id == record.property_account_customer_advance.id:
				#         amount_difference += account_move_line_rec.credit
				#         amount_difference -= account_move_line_rec.debit
				# record.re_reg_total_recivable = amount_difference
				ctx = self._context.copy()
				ctx['all_fiscalyear'] = True
				query = self.env['account.move.line']._query_get()
				self._cr.execute("""SELECT l.partner_id, SUM(l.debit),SUM(l.credit), SUM(l.debit-l.credit)
	                             FROM account_move_line l
	                             WHERE l.partner_id IN %s
	                             AND l.account_id IN %s
	                             AND l.reconcile_id IS NULL
	                             AND """ + query + """
	                             GROUP BY l.partner_id
	                             """, (tuple(record.ids), tuple(record.re_reg_advance_account.ids),))
				fetch = self._cr.fetchall()
				for pid, total_debit, total_credit, val in fetch:
					amount_difference += total_credit
					amount_difference -= total_debit
					self.re_reg_total_recivable = amount_difference

	@api.one
	@api.depends('tc_initiated')
	def _get_tc_initiad(self):
		obj_transfer_certificate = self.env['trensfer.certificate']
		for rec in self:
			if rec.is_student == True:
				if rec.id:
					tc_rec = obj_transfer_certificate.search([('name', '=', rec.id)], limit=1)
					if tc_rec.id:
						if tc_rec.state in ('tc_requested', 'fee_balance_review', 'final_fee_awaited'):
							rec.tc_initiated = 'yes'
						if tc_rec.state in ('tc_complete', 'tc_cancel'):
							rec.tc_initiated = 'no'
					else:
						rec.tc_initiated = 'no'

	student_state = fields.Selection(
		[('academic_fee_paid', 'Academic fee paid'), ('academic_fee_unpaid', 'Academic fee unpaid'),
		 ('academic_fee_partially_paid', 'Academic fee partially paid'),
		 ('tc_initiated', 'TC initiated'),
		 ('confirmed_student', 'Confirmed Student'), ('ministry_approved_old', 'Ministry Approved')],
		string='Status')

	tc_initiated = fields.Selection(
		[('yes', 'Yes'), ('no', 'No')],
		string='TC Initiated', compute='_get_tc_initiad')

	re_reg_next_academic_year = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Re-registered for next Academic year',
												 default='no')
	re_reg_advance_account = fields.Many2one('account.account',
											 string="Account Re-Registration Advance",
											 help="This account will be used for Re-Registration fee advance payment of Student/Parent",
											 compute=_get_re_reg_advance_account)
	re_reg_total_recivable = fields.Float(compute='get_re_registration_total_recivable',
										  string='Re-Reg Advance Total Recivable')
	advance_total_recivable = fields.Float(compute='get_advance_total_recivable', string='Advance Total Recivable')



class account_move_reconcile(models.Model):
    _name = "account.move.reconcile"

class account_move_line_inherit(models.Model):
	_inherit = "account.move.line"


	reconcile_id = fields.Many2one('account.move.reconcile', string='Reconcile', readonly=True, ondelete='set null', select=2, copy=False)




	def _query_get_get(self, obj='l'):

	    fiscalyear_obj = self.env['account.fiscalyear']
	    fiscalperiod_obj = self.env['account.period']
	    account_obj = self.env['account.account']
	    fiscalyear_ids = []
	    context = dict(self._context or {})
	    initial_bal = context.get('initial_bal', False)
	    company_clause = " "
	    query = ''
	    query_params = {}
	    if context.get('company_id'):
	        company_clause = " AND " +obj+".company_id = %(company_id)s"
	        query_params['company_id'] = context['company_id']
	    if not context.get('fiscalyear'):
	        if context.get('all_fiscalyear'):
	            #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
	            fiscalyear_ids = fiscalyear_obj.search([])
	        else:
	            fiscalyear_ids = self.env['account.fiscalyear'].search([('state', '=', 'draft')]).ids
	    else:
	        #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
	        fiscalyear_ids = context['fiscalyear']
	        if isinstance(context['fiscalyear'], (int, long)):
	            fiscalyear_ids = [fiscalyear_ids]

	    query_params['fiscalyear_ids'] = tuple(fiscalyear_ids) or (0,)
	    state = context.get('state', False)
	    where_move_state = ''
	    where_move_lines_by_date = ''

	    if context.get('date_from') and context.get('date_to'):
	        query_params['date_from'] = context['date_from']
	        query_params['date_to'] = context['date_to']
	        if initial_bal:
	            where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < %(date_from)s)"
	        else:
	            where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= %(date_from)s AND date <= %(date_to)s)"

	    if state:
	        if state.lower() not in ['all']:
	            query_params['state'] = state
	            where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = %(state)s)"
	    if context.get('period_from') and context.get('period_to') and not context.get('periods'):
	        if initial_bal:
	            period_company_id = fiscalperiod_obj.browse(context['period_from'], context=context).company_id.id
	            first_period = fiscalperiod_obj.search([('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
	            context['periods'] = fiscalperiod_obj.build_ctx_periods(first_period, context['period_from'])
	        else:
	            context['periods'] = fiscalperiod_obj.build_ctx_periods(context['period_from'], context['period_to'])
	    if 'periods_special' in context:
	        periods_special = ' AND special = %s ' % bool(context.get('periods_special'))
	    else:
	        periods_special = ''
	    if context.get('periods'):
	        query_params['period_ids'] = tuple(context['periods'])
	        if initial_bal:
	            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
	            period_ids = fiscalperiod_obj.search([('id', 'in', context['periods'])], order='date_start', limit=1)
	            if period_ids and period_ids[0]:
	                first_period = fiscalperiod_obj.browse(period_ids[0], context=context)
	                query_params['date_start'] = first_period.date_start
	                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND date_start <= %(date_start)s AND id NOT IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
	        else:
	            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s AND id IN %(period_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date
	    else:
	        query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN %(fiscalyear_ids)s" + periods_special + ")" + where_move_state + where_move_lines_by_date

	    if initial_bal and not context.get('periods') and not where_move_lines_by_date:
	        #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
	        #so we have to invalidate this query
	        raise UserError(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))

	    if context.get('journal_ids'):
	        query_params['journal_ids'] = tuple(context['journal_ids'])
	        query += ' AND '+obj+'.journal_id IN %(journal_ids)s'

	    if context.get('chart_account_id'):
	        child_ids = account_obj._get_children_and_consol([context['chart_account_id']], context=context)
	        query_params['child_ids'] = tuple(child_ids)
	        query += ' AND '+obj+'.account_id IN %(child_ids)s'

	    query += company_clause
	    cursor = self.env.cr
	    return cursor.mogrify(query,query_params)

