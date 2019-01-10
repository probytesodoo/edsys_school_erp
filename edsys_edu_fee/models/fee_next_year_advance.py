from odoo import models, fields, api, _

class NextYearAdvanceFee(models.Model):

    _name = 'next.year.advance.fee'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Advance Fee"

    @api.depends('next_year_advance_fee_line_ids')
    def _get_total_amount(self):
        for rec in self:
            t_amount = 0.00
            for fee_line_id in rec.next_year_advance_fee_line_ids:
                t_amount += round(fee_line_id.amount,2)
            rec.total_amount = t_amount

    @api.one
    @api.depends('total_amount','total_paid_amount')
    def _get_residual_amount(self):
        for rec in self:
            rec.residual = rec.total_amount - self.total_paid_amount

    partner_id = fields.Many2one('res.partner',string='Student')
    reg_id = fields.Many2one('registration',string ='Registration ID')
    enq_date = fields.Date('Enquiry Date')
    order_id = fields.Char(string='Order Id')
    batch_id = fields.Many2one('batch', 'Academic Year',required=True)
    state = fields.Selection([('fee_unpaid', 'Un paid'), ('fee_partial_paid', 'Partial Paid'),
                              ('fee_paid', 'Fee Paid'),('invoice_reconcile','Invoiced & Reconcile')],
                             select=True, string='Stage',default='fee_unpaid', track_visibility='onchange')
    next_year_advance_fee_line_ids = fields.One2many('next.year.advance.fee.line','next_year_advance_fee_id',
                                                     string='Fee Line')
    total_amount = fields.Float('Total Amount', compute='_get_total_amount')
    residual = fields.Float('residual', compute='_get_residual_amount', readonly='1')
    total_paid_amount = fields.Float('Total Paid Amount')
    payment_ids = fields.Many2many('account.payment','next_year_advance_payment','next_year_adv_fee','voucher_ids')
    journal_id = fields.Many2one('account.journal')
    journal_ids = fields.Many2many('account.journal','next_year_journal','next_year_id','journal_id')

    @api.multi
    def create(self,vals):
        order_id = self.env['ir.sequence'].get('next.year.adv.fee') or '/'
        vals['order_id'] = order_id
        return super(NextYearAdvanceFee, self).create(vals)

class NextYearAdvanceFeeLine(models.Model):

    _name = 'next.year.advance.fee.line'

    name = fields.Many2one('product.product',string='Name')
    description  = fields.Char('Description ')
    account_id = fields.Many2one('account.account',string='Account')
    next_year_advance_fee_id = fields.Many2one('next.year.advance.fee',string='Next Year Advance Fee')
    priority = fields.Integer('Priority')
    amount = fields.Float('Amount')
    rem_amount = fields.Float('Remaining Amount')

class AccounntVoucherInheritAdvance(models.Model):

    _inherit = 'account.voucher'

    # @api.multi
    # def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     res = super(AccounntVoucherInheritAdvance, self).onchange_partner_id(partner_id, journal_id, amount, currency_id, ttype, date)
    #     partner_rec = self.env['res.partner'].browse(partner_id)
    #     account_move_line_obj = self.env['account.move.line']
    #     next_year_advance_obj = self.env['next.year.advance.fee']
    #     if 'value' in res:
    #         if 'line_dr_ids' in res['value']:
    #             line_dr_ids_list = []
    #             orignal_line_dr_ids_list = res['value']['line_dr_ids']
    #             for line_dr_ids_dict in res['value']['line_dr_ids']:
    #                 if isinstance(line_dr_ids_dict,dict):
    #                     if line_dr_ids_dict['move_line_id']:
    #                         account_move_line_rec = account_move_line_obj.browse(line_dr_ids_dict['move_line_id'])
    #                         if account_move_line_rec.id:
    #                             if partner_rec.id:
    #                                 next_year_advance_rec = next_year_advance_obj.search([('order_id','=',account_move_line_rec.ref)],limit=1)
    #                                 if next_year_advance_rec.id:
    #                                     line_dr_ids_list.append(line_dr_ids_dict)
    #             for dr_dict in line_dr_ids_list:
    #                 if dr_dict in orignal_line_dr_ids_list:
    #                     orignal_line_dr_ids_list.pop(orignal_line_dr_ids_list.index(dr_dict))
    #             res['value']['line_dr_ids'] = orignal_line_dr_ids_list
    #     return res

    @api.multi
    def send_receipt(self):
        """
        send payment receipt to parents
        -----------------------
        :return:
        """
        email_server = self.env['ir.mail_server']
        email_sender = email_server.sudo().search([])
        ir_model_data = self.env['ir.model.data']

        if self.partner_id.is_student == True:
            template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_send_receipt')[1]
            template_rec = self.env['mail.template'].sudo().browse(template_id)
            email = self.partner_id.parents1_id.parents_email
        elif self.partner_id.is_parent == True:
            template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_send_receipt_parent')[1]
            template_rec = self.env['mail.template'].sudo().browse(template_id)
            email = self.partner_id.parents_email

        else:
            template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_send_receipt_parent')[1]
            template_rec = self.env['mail.template'].sudo().browse(template_id)
            email = self.partner_id.email


        template_rec.write({'email_to': email , 'email_from': email_sender.smtp_user, 'email_cc': ''})
        template_rec.send_mail(self.id, force_send=False)