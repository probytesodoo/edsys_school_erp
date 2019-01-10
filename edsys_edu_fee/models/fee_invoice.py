from odoo import models, fields, api, _
from num2words import num2words
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
# from odoo.osv import osv
from odoo.tools import float_compare
import json
from odoo.tools import float_is_zero, float_compare

class AccountMoveReconcile(models.Model):
    _name = "account.move.reconcile"

    def _check_same_partner(self, cr, uid, ids, context=None):
        for reconcile in self.browse(cr, uid, ids, context=context):
            move_lines = []
            if not reconcile.opening_reconciliation:
                if reconcile.line_id:
                    first_partner = reconcile.line_id[0].partner_id.id
                    move_lines = reconcile.line_id

                elif reconcile.line_partial_ids:
                    first_partner = reconcile.line_partial_ids[0].partner_id.id
                    move_lines = reconcile.line_partial_ids

                if any([(line.account_id.type in ('receivable', 'payable') and line.partner_id.id != first_partner) for line in move_lines]):
                    return False
        return True

    # _constraints = [
    #     (_check_same_partner, 'You can only reconcile journal items with the same partner.', ['line_id', 'line_partial_ids']),
    # ]

class StudentFeeInvoice(models.Model):

    _inherit = 'account.invoice'
    
    @api.multi
    def amount_to_text(self, amount):
        amount_in_text= num2words(amount)
        amount_upper=amount_in_text.upper()
        return amount_upper

    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]

    batch_id = fields.Many2one('batch',string='Acadamic Year')
    term_id = fields.Many2one('acd.term',string='Term')
    month_id = fields.Many2one('fee.month',string='Month Ref')
    month = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    year = fields.Char(string="Year", related="month_id.year")
    payfort_payment_id = fields.Char(string='PAY ID')
    payfort_pay_date = fields.Date("Payment Date")
    invoice_number = fields.Char('Invoice Number',readolny=True)
    pos_invoice = fields.Boolean('Pos Invoice',default=False)

    @api.multi
    def confirm_paid(self):
        print'=============confirm paid===================='
        reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
        if reg_rec.id:
            reg_rec.fee_status = 'academy_fee_pay'
            reg_rec.acd_trx_date = date.today()
        return super(StudentFeeInvoice, self).confirm_paid()
    
    
   
    
                
    
    @api.multi
    def action_invoice_paid(self):
        print '--------------action invoice paid-------------------'
#         reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
#         if reg_rec.id:
#             reg_rec.fee_status = 'academy_fee_pay'
#             reg_rec.acd_trx_date = date.today()
#         return super(StudentFeeInvoice, self).action_invoice_paid()
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        print to_pay_invoices,'============================to pay invoices=-=='
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            print'99999999999999999999999999999999'
            raise UserError(_('Invoice must be validated in order to set it to register payemnt.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            print '000000000000000000000000000'
            raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
           
        reg_rec = self.env['registration'].search([('student_id','=',self.partner_id.id)],limit=1)
        if reg_rec.id:
            print reg_rec.id,'==========================reg_rec.id'
            reg_rec.fee_status = 'academy_fee_pay'
            reg_rec.acd_trx_date = date.today()
        print to_pay_invoices.write,'===========================to_pay_invoices.write'  
        return to_pay_invoices.write({'state': 'paid'})
#        
    # @api.multi
    # def invoice_validate(self):
    #     print'-------------invoice-validate----------------'
    #     """
    #     invoice line remaining amount update base on discount.
    #     ------------------------------------------------------
    #     :return:
    #     """
    #     for invoice_line_rec1 in self.invoice_line_ids:
    #         for invoice_line_rec2 in self.invoice_line_ids:
    #             if invoice_line_rec1.product_id.fees_discount.id == invoice_line_rec2.product_id.id:
    #                 if invoice_line_rec1.rem_amount > 0.00 and invoice_line_rec1.rem_amount >= abs(
    #                         invoice_line_rec2.rem_amount):
    #                     invoice_line_rec1.rem_amount -= abs(invoice_line_rec2.rem_amount)
    #                     invoice_line_rec2.rem_amount = 0.00
    #     res = super(StudentFeeInvoice, self).invoice_validate()
    #     if self.type == "out_invoice" :
    #         self.bulk_reconciliation()
    #     return res


   
    
    
    @api.model
    def create(self, vals):
        """
        update remaining amount on create invoice line.
        -----------------------------------------------
        :param vals: dictonary
        :return:
        """
        invoice_number = ''
        obj_ir_sequence = self.env['ir.sequence']
        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Invoice Number Sequence')])
        if ir_sequence_ids:
            invoice_number = obj_ir_sequence.next_by_code('account.invoice')
            print invoice_number,'////////////// invoice number seq'
        else:
            sequence_vals = {
                                'name' : 'Invoice Number Sequence',
                                'prefix' : 24,
                                'padding' : 7,
                                'number_next_actual' : 1,
                                'number_increment' : 1,
                                'implementation_standard' : 'standard',
                             }
            ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
            invoice_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
            print invoice_number,'==============invoice number sequence vals'
#         dyanamic_registration_number = random.randrange(1000, 1000000, 1)
#         dyanamic_order_number = random.randrange(1000, 1000000, 1)
        vals['invoice_number'] = invoice_number
        print("vaaaaaaaaaaaaaalllllllllllllsssss",vals)
        res = super(StudentFeeInvoice, self).create(vals)
        return res

class StudentFeeInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    parent_id = fields.Many2one('res.partner', string='parent', readonly=True)
    priority = fields.Integer('Priority')
    full_paid = fields.Boolean('Full Paid')
    rem_amount = fields.Float('Remaining Amount')
    print_line = fields.Boolean('Print',default=False)
    amount_balance = fields.Float('Amount Balance')
    reconcile_receipt_date = fields.Date('Reconcile Receipt Date')
    reconcile_receipt_flag = fields.Boolean('Reconcile Receipt Flag',default=False)
    voucher_id = fields.Many2one('account.voucher', string='Voucher ID')
    allocation = fields.Float('Allocation')

    @api.model
    def create(self, vals):
        """
        update remaining amount on create invoice line.
        -----------------------------------------------
        :param vals: dictonary
        :return:
        """
        if vals:
            vals['rem_amount'] = vals['price_unit']
        res = super(StudentFeeInvoiceLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """
        update remaining amount on write invoice line unite price.
        ----------------------------------------------------------
        :param vals:dictonary
        :return:
        """
        if 'price_unit' in vals:
            vals['rem_amount'] = vals['price_unit']
        res = super(StudentFeeInvoiceLine, self).write(vals)
        return res

class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    is_parent = fields.Boolean('Is Parent')
    jounral_id_store = fields.Boolean(string='Jounral Store')
    cheque_start_date = fields.Date('Cheque Start Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    bank_name = fields.Char('Bank Name')
    cheque = fields.Boolean(string='Cheque')
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')
    invoice_id=fields.Many2one('account.invoice','Invoice')
    parent_email = fields.Char(string='Parent Email')
    parent_mobile = fields.Char(string='Mobile')
    student_class = fields.Many2one('course',string="Class")
    student_section = fields.Many2one('section', 'Section')
    payfort_payment_id = fields.Char(string='PAY ID')
    payfort_pay_date = fields.Date("Payment Date")
    payfort_link_order_id = fields.Char('Payfort Order Id')
    payfort_type = fields.Boolean('For Payfort Payment')
    total_payble_amount = fields.Float()
    voucher_number = fields.Char('order ID',readolny=True)
    voucher_amount = fields.Float('Voucher Amount')
    
    
    #new filed are added for receipt print 
    line_cr_ids = fields.One2many('account.voucher.line','voucher_id','Credits',
            domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)]})
    
    state = fields.Selection([
            ('draft','Draft'),
            ('review','Review'),
            ('cancel','Cancelled'),
            ('proforma','Pro-forma'),
            ('posted','Posted')
            ], 'Status', readonly=True, track_visibility='onchange', copy=False,)
    
    invoice_line_ids = fields.One2many('account.invoice.line','voucher_id','Invoice Lines')
    total_reconciled_amount = fields.Float('Total Reconciled Amount')
    invoice_ids = fields.Char('Invoice Id', readonly=True)   
    
    @api.model
    def create(self, vals):
        partner_id = ''
        invoice_line_ids = []
        voucher_number = ''
        obj_ir_sequence = self.env['ir.sequence']
        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Voucher Number Sequence')])
        if ir_sequence_ids:
            voucher_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
        else:
            sequence_vals = {
                                'name' : 'Voucher Number Sequence',
                                'prefix' : 22,
                                'padding' : 7,
                                'number_next_actual' : 1,
                                'number_increment' : 1,
                                'implementation_standard' : 'standard',
                             }
            ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
#             print obj_ir_sequence.next_by_id(ir_sequence_ids),'----obj_ir_sequence.next_by_id(ir_sequence_ids)'
            voucher_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
#         dyanamic_registration_number = random.randrange(1000, 1000000, 1)
#         dyanamic_order_number = random.randrange(1000, 1000000, 1)
#         vals['invoice_number'] = invoice_number
        
#         dyanamic_order_number = random.randrange(1000, 1000000, 1)
        vals['voucher_number'] = voucher_number
        res = super(AccountVoucher, self).create(vals)
#         return res

        if vals['partner_id']:
            partner_id = vals['partner_id']
        line_amount = 0
        if partner_id:
            for line in res.line_cr_ids:
                if line.amount > 0:
                    line_amount = line.amount
                    if line.move_line_id:
                            account_move_line_ids = line.move_line_id
                            if account_move_line_ids:
                                account_move_line_id = account_move_line_ids.id
                                obj_account_move_ids = obj_account_move_line.search([('id','=',account_move_line_id)])
                                if obj_account_move_ids:
                                    invoice_number = obj_account_move_ids.ref
                                    if invoice_number:
                                        account_invoice_ids = obj_account_invoice.search(['|',('number','=',invoice_number),('name','=',invoice_number)])
                                        for account_invoice_id in account_invoice_ids:
                                            account_invoice_id.allocation = 0
                                            sortBy = "priority desc"
                                            account_invoice_line_ids = obj_account_invoice_line.search([('invoice_id','=',account_invoice_id.id),('rem_amount','!=',0)],order=sortBy)
                                            if account_invoice_line_ids:
                                                for account_invoice_line_id in account_invoice_line_ids:
                                                    if account_invoice_line_id.price_subtotal > 0:
                                                        account_invoice_line_id.voucher_id = res.id
                                                        if line_amount > 0:
                                                            if account_invoice_line_id.price_subtotal == account_invoice_line_id.rem_amount:
                                                                if line_amount > account_invoice_line_id.price_subtotal:
                                                                    account_invoice_line_id.allocation = account_invoice_line_id.price_subtotal
                                                                    line_amount -= account_invoice_line_id.price_subtotal
                                                                    
                                                                else:
                                                                    account_invoice_line_id.allocation = line_amount
                                                                    line_amount = 0
                                                            else:
                                                                if line_amount > account_invoice_line_id.rem_amount:
                                                                    account_invoice_line_id.allocation = account_invoice_line_id.rem_amount
                                                                    line_amount -= account_invoice_line_id.rem_amount
                                                                   
                                                                else:
                                                                    account_invoice_line_id.allocation = line_amount
                                                                    line_amount = 0
        return res



    @api.multi
    def review_voucher(self):
        self.state='review'



    @api.multi
    def get_invoice_line(self, voucher):
        print'====================get invoice line=========='
        invoice_lines =[]
        paid_invoice_lines = []
        if voucher:

            self.total_amount = self.amount
            
            for invoice_line in voucher.invoice_line_ids:
                if invoice_line.allocation > 0:
                    invoice_line_list = []
                    invoice_line_list.append(invoice_line.invoice_id.number)
                    invoice_line_list.append(invoice_line.name)
                    invoice_line_list.append(invoice_line.invoice_line_tax_id.amount)
                    invoice_line_list.append(invoice_line.tax_amount)
                    invoice_line_list.append(invoice_line.allocation)
                    invoice_line_list.append(invoice_line.allocation)
                    if bool(invoice_line_list):
                        paid_invoice_lines.append(invoice_line_list)
        if len(paid_invoice_lines) > 0:
            for paid_invoice_line in paid_invoice_lines:
                invoice_lines.append(paid_invoice_line)
        return invoice_lines 
    
    
    @api.multi
    def write(self, vals):

        total_reconciled_amount = 0.0
        obj_account_invoice = self.env['account.invoice']
        obj_account_invoice_line = self.env['account.invoice.line']
        obj_account_move_line = self.env['account.move.line']
        if 'line_dr_ids' in vals and vals['line_dr_ids']:
            line_dr_ids = vals['line_dr_ids']
            for line in line_dr_ids:
                if line[2] is 'dict':
                    if line[2]['amount_original'] > 0:
                        total_reconciled_amount += line[2]['amount']
        else:
            line_dr_ids = self.line_dr_ids
            for line in line_dr_ids:
                if line.amount_original > 0:
                    total_reconciled_amount += line.amount
        
        vals['total_reconciled_amount'] = total_reconciled_amount
        
        
        line_amount = 0
        if 'line_cr_ids' in vals and vals['line_cr_ids']:
            line_cr_ids = vals['line_cr_ids']
            for line in line_cr_ids:
                if isinstance(line[2],dict):
                    if line[2]['amount'] > 0:
                        line_amount = line[2]['amount']
                        if 'move_line_id' in line[2]:
                            if line[2]['move_line_id']:
                                    account_move_line_ids = line[2]['move_line_id']
                                    if account_move_line_ids:
                                        account_move_line_id = account_move_line_ids
                                        obj_account_move_ids = obj_account_move_line.search([('id','=',account_move_line_id)])
                                        if obj_account_move_ids:
                                            invoice_number = obj_account_move_ids.ref
                                            if invoice_number:
                                                account_invoice_ids = obj_account_invoice.search(['|',('number','=',invoice_number),('name','=',invoice_number)])
                                                for account_invoice_id in account_invoice_ids:
                                                    sortBy = "priority desc"
                                                    account_invoice_line_ids = obj_account_invoice_line.search([('invoice_id','=',account_invoice_id.id),('rem_amount','!=',0)],order=sortBy)
                                                    if account_invoice_line_ids:
                                                        for account_invoice_line_id in account_invoice_line_ids:
                                                            if account_invoice_line_id.price_subtotal > 0:
                                                                account_invoice_line_id.allocation = 0
                                                                account_invoice_line_id.voucher_id = self.id
                                                                if line_amount > 0:
                                                                    if account_invoice_line_id.price_subtotal == account_invoice_line_id.rem_amount:
                                                                        if line_amount > account_invoice_line_id.price_subtotal:
                                                                            account_invoice_line_id.allocation = account_invoice_line_id.price_subtotal
                                                                            line_amount -= account_invoice_line_id.price_subtotal
                                                                            
                                                                        else:
                                                                            account_invoice_line_id.allocation = line_amount
                                                                            line_amount = 0
                                                                    else:
                                                                        if line_amount > account_invoice_line_id.rem_amount:
                                                                            account_invoice_line_id.allocation = account_invoice_line_id.rem_amount
                                                                            line_amount -= account_invoice_line_id.rem_amount
                                                                            
                                                                        else:
                                                                            account_invoice_line_id.allocation = line_amount
                                                                            line_amount = 0
                
                        
            
                    
        else:
            line_cr_ids = self.line_cr_ids
            for line in line_cr_ids:
                if line.amount > 0:
                        line_amount = line.amount
                        if line.move_line_id:
                                account_move_line_ids = line.move_line_id
                                if account_move_line_ids:
                                    account_move_line_id = account_move_line_ids.id
                                    obj_account_move_ids = obj_account_move_line.search([('id','=',account_move_line_id)])
                                    if obj_account_move_ids:
                                        invoice_number = obj_account_move_ids.ref
                                        if invoice_number:
                                            account_invoice_ids = obj_account_invoice.search(['|',('number','=',invoice_number),('name','=',invoice_number)])
                                            for account_invoice_id in account_invoice_ids:
                                                sortBy = "priority desc"
                                                account_invoice_line_ids = obj_account_invoice_line.search([('invoice_id','=',account_invoice_id.id),('rem_amount','!=',0)],order=sortBy)
                                                if account_invoice_line_ids:
                                                    for account_invoice_line_id in account_invoice_line_ids:
                                                        if account_invoice_line_id.price_subtotal > 0:
                                                            account_invoice_line_id.allocation = 0
                                                            account_invoice_line_id.voucher_id = self.id
                                                            if line_amount > 0:
                                                                if account_invoice_line_id.price_subtotal == account_invoice_line_id.rem_amount:
                                                                    if line_amount > account_invoice_line_id.price_subtotal:
                                                                        account_invoice_line_id.allocation = account_invoice_line_id.price_subtotal
                                                                        line_amount -= account_invoice_line_id.price_subtotal
                                                                    else:
                                                                        account_invoice_line_id.allocation = line_amount
                                                                        line_amount = 0
                                                                else:
                                                                    if line_amount > account_invoice_line_id.rem_amount:
                                                                        account_invoice_line_id.allocation = account_invoice_line_id.rem_amount
                                                                        line_amount -= account_invoice_line_id.rem_amount
                                                                    else:
                                                                        account_invoice_line_id.allocation = line_amount
                                                                        line_amount = 0



        account_journal = self.env['account.journal']
        journal_type = ''
        journal_id = ''
        if 'type' in vals:
            journal_type = vals['type']
        else:
            journal_type = self.type
        if 'journal_id' in vals:
            journal_id = vals['journal_id']
        else:
            journal_id = self.journal_id.id
        if journal_id:
                if journal_type in ('sale', 'receipt'):
                    account_journal_ids = account_journal.search([('id','=',journal_id)])
                    if account_journal_ids:
                        account_id = account_journal_ids[0].default_debit_account_id.id
                        vals['account_id'] = account_id
                if journal_type in ('purchase', 'payment'):
                 
                    account_journal_ids = account_journal.search([('id','=',journal_id)])
                    if account_journal_ids:
                        account_id = account_journal_ids[0].default_credit_account_id.id
                        vals['account_id'] = account_id
    
            
        return super(AccountVoucher, self).write(vals)

                                
                                                        

    @api.multi
    def students_class(self, voucher):
        st_class=''
        if voucher:
            for line in voucher.line_cr_ids:
                if line.move_line_id and line.move_line_id.partner_id:
                   st_class=st_class + (line.move_line_id.partner_id.class_id and line.move_line_id.partner_id.class_id.name or '')+','
        return st_class

    @api.multi
    def childs_name(self, voucher):
        names=''
        if voucher:
            for line in voucher.line_cr_ids:
                if line.move_line_id and line.move_line_id.partner_id:
                   names=names + (line.move_line_id.partner_id.name or '')+','
        return names

    def academic_years(self,parent):
        year=[]
        if parent:
            for child in parent.chield1_ids:
                year.append(child.year_id and child.year_id.name or '')
            year=list(set(year))
            if len (year)>0:
                return year[0]
        return ''       

    @api.model
    def account_move_get_get(self, voucher_id):


        print "account_move_get_get instead of account_move_get in account.voucher module"
        ''' i change the funtion name because got error account_move_get takes exactly 2 arument 1given
        so,change the funtion name''' 

        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.env['ir.sequence']
        voucher = self.env['account.voucher'].browse()
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise except_orm(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict()
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_code(voucher.journal_id.sequence_id.id, context=c)
        else:
            raise except_orm(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
            'cheque_date':voucher.cheque_start_date,
            'cheque_expiry_date':voucher.cheque_expiry_date,
            'bank_name':voucher.bank_name,
            'cheque':voucher.cheque
        }
        return move

    @api.onchange('journal_id')
    def _onchange_journal(self):
        # res = super(AccountVoucher, self)._onchange_journal()
        type_rec = self.journal_id
        if type_rec:
                self.jounral_id_store= type_rec.is_cheque

    @api.onchange('cheque_start_date','cheque_expiry_date')
    def cheque_start(self):
        if self.cheque_start_date and self.cheque_expiry_date:
            if self.cheque_start_date > self.cheque_expiry_date:
                raise except_orm(_('Warning!'),
                    _("Start Date must be lower than to Expiry date!"))
                
                

#     @api.multi
#     @api.onchange('partner_id')
#     def onchange_partner_id(self):
#         print'======onchange partner id=============='
# #         student_obj = self.env['res.partner']
# #         print student_obj,'=================student obj'
# #         stud_rec = student_obj.browse(partner_id)
#         stud_rec = self.env['res.partner'].browse(self.partner_id.id)
#         print stud_rec,'======================stud_rec'
#         if stud_rec.id and stud_rec.is_parent == True and stud_rec.is_student == False:
#             print stud_rec.id,'======================stud_rec.id'
#             # payment from parent then check parent and it's all child id
#             child_lst = []
#             student_obj = self.env['res.partner']
#             child_lst.append(self.partner_id.id)
#             for student_rec in student_obj.search([('is_parent', '=', False),
#                                                    ('parents1_id', '=', partner_id)]):
#                 child_lst.append(student_rec.id)
#             partner_id = child_lst
#             res = super(AccountVoucher, self).onchange_partner_id()
#             if res:
#                 res['value']['parent_email'] = stud_rec.parents_email
#                 res['value']['parent_mobile'] = stud_rec.parent_contact
#         elif stud_rec.is_parent == False and stud_rec.is_student == True:
#             print stud_rec.is_parent,'================stud_rec.is_parent'
#             # payment from child then child id and it's parent id
#             child_parent_lst = []
#              
#             print self.partner_id.id,'===================partner_id.id'
#             child_parent_lst.append(self.partner_id.id)
#             print child_parent_lst,'===================child_parent_lst'
#             if stud_rec.parents1_id.id:
#                 child_parent_lst.append((stud_rec.parents1_id.id))
#             partner_id = child_parent_lst
#             print partner_id,'==================partner id============'
#             res = super(AccountVoucher, self).onchange_partner_id()
#             print res,'---------------res-------------'
#             if res:
#                 res['value']['student_class'] = stud_rec.class_id.id
#                 res['value']['student_section'] = stud_rec.student_section_id.id
#         else:
#             res = super(AccountVoucher, self).onchange_partner_id()
#         print res,'=====================res'
#         total_pay_amount = 0.0
#         if 'value' in res:
#             print '===============value============='
#             if 'line_cr_ids' in res['value'] and res['value']['line_cr_ids']:
#                 for each in res['value']['line_cr_ids']:
#                     if isinstance(each, dict):
#                         total_pay_amount += each['amount_unreconciled']
#             if 'line_dr_ids' in res['value'] and res['value']['line_dr_ids']:
#                 for each in res['value']['line_dr_ids']:
#                     if isinstance(each, dict):
#                         total_pay_amount -= each['amount_unreconciled']
#             res['value']['total_payble_amount'] = total_pay_amount
#         return res


#         for each in self.line_cr_ids:
#             if isinstance(each, dict):
#                 total_pay_amount += each.amount_unreconciled
# 
#         for each in self.line_dr_ids:
#             if isinstance(each, dict):
#                 total_pay_amount -= each.amount_unreconciled
#         res['value']['total_payble_amount'] = total_pay_amount
#         return res

    @api.multi
    def onchange_partner_id(self, partner_id, journal_id, amount, currency_id, ttype, date):
        print '=================oncahnge_partner id==============='
        student_obj = self.env['res.partner']
        stud_rec = student_obj.browse(partner_id)
  
        if stud_rec.id and stud_rec.is_parent == True and stud_rec.is_student == False:
            # payment from parent then check parent and it's all child id
            child_lst = []
            child_lst.append(partner_id)
            for student_rec in student_obj.search([('is_parent','=',False),
                                                   ('parents1_id','=',partner_id)]):
                child_lst.append(student_rec.id)
            partner_id = child_lst
            res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
            if res:
                res['value']['parent_email'] = stud_rec.parents_email
                res['value']['parent_mobile'] = stud_rec.parent_contact
        elif stud_rec.is_parent == False and stud_rec.is_student == True:
            # payment from child then child id and it's parent id
            child_parent_lst = []
            child_parent_lst.append(partner_id)
              
            if stud_rec.parents1_id.id:
                child_parent_lst.append(stud_rec.parents1_id.id)
            partner_id = child_parent_lst
            print partner_id,'==========================partner id'
            res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
            print amount,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa mont  -----------aaaaaaaaaaa'
            print res,'=============================res'
            if res:
                res['value']['student_class'] = stud_rec.class_id.id
                res['value']['student_section'] = stud_rec.student_section_id.id
        else:
            res = self.onchange_partner_id_id(partner_id, journal_id, amount, currency_id, ttype, date)
        total_pay_amount = 0.0
          
        if 'value' in res:
            print'================value============='
            if 'line_cr_ids' in res['value'] and res['value']['line_cr_ids']:
                for each in res['value']['line_cr_ids']:
                    if isinstance(each,dict):
                        total_pay_amount += each['amount_unreconciled']
                        print total_pay_amount,'------crrrr------------total pay amount'
            if 'line_dr_ids' in res['value'] and res['value']['line_dr_ids']:
                for each in res['value']['line_dr_ids']:
                    if isinstance(each,dict):
                        total_pay_amount -= each['amount_unreconciled']
                        print total_pay_amount,'------------drrr-------total pay amount'
            res['value']['total_payble_amount'] = total_pay_amount
        return res
  
#     def onchange_partner_id_id(self, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
#         print '=================oncahnge partner idid================'
#         if not journal_id:
#             return {}
#         if context is None:
#             context = {}
#         #TODO: comment me and use me directly in the sales/purchases views
#         res = self.basic_onchange_partner(partner_id, journal_id, ttype, context=context)
#         if ttype in ['sale', 'purchase']:
#             return res
#         ctx = context.copy()
#         # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
#         ctx.update({'date': date})
#         vals = self.recompute_voucher_lines(partner_id, journal_id, amount, currency_id, ttype, date, context)
#         vals2 = self.recompute_payment_rate(vals, currency_id, date, ttype, journal_id, amount, context=context)
#         for key in vals.keys():
#             res[key].update(vals[key])
#         for key in vals2.keys():
#             res[key].update(vals2[key])
#         #TODO: can probably be removed now
#         #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
#         # [pre_line, line_cr_ids, payment_rate...] for type purchase.
#         # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
#         # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
#         # onchange returns a value for them
#         if ttype == 'sale':
#             del(res['value']['line_dr_ids'])
#             del(res['value']['pre_line'])
#             del(res['value']['payment_rate'])
#         elif ttype == 'purchase':
#             del(res['value']['line_cr_ids'])
#             del(res['value']['pre_line'])
#             del(res['value']['payment_rate'])
#         return res
#          
#     def basic_onchange_partner(self, partner_id, journal_id, ttype, context=None):
#         print '=======================basic onchange parttner==========='
#         partner_pool = self.env['res.partner']
#         journal_pool = self.env['account.journal']
#         res = {'value': {'account_id': False}}
#         if not partner_id or not journal_id:
#            return res
#  
#         journal = journal_pool.browse(journal_id)
#         partner = partner_pool.browse(partner_id)
#         account_id = False
#         if journal.type in ('sale','sale_refund'):
#            account_id = partner.property_account_receivable.id
#         elif journal.type in ('purchase', 'purchase_refund','expense'):
#            account_id = partner.property_account_payable.id
#         elif ttype in ('sale', 'receipt'):
#            account_id = journal.default_debit_account_id.id
#         elif ttype in ('purchase', 'payment'):
#            account_id = journal.default_credit_account_id.id
#         else:
#            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
#  
#         res['value']['account_id'] = account_id
#         return res

    @api.multi
    def onchange_amount(self, amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id):
        partner_obj = self.env['res.partner']
        partner_rec = partner_obj.browse(partner_id)
        if partner_rec.is_parent == True and partner_rec.is_student == False:
            # partner payment then parent id and all child id
            child_lst = []
            child_lst.append(partner_id)
            for student_rec in partner_obj.search([('is_parent','=',False),
                                                   ('parents1_id','=',partner_id)]):
                child_lst.append(student_rec.id)
            partner_id = child_lst
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        elif partner_rec.is_parent == False and partner_rec.is_student == True:
            # child payment then child id and its parent id
            child_parent_lst = []
            child_parent_lst.append(partner_id)
            if partner_rec.parents1_id.id:
                child_parent_lst.append(partner_rec.parents1_id.id)
            partner_id = child_parent_lst
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        else:
            res = super(AccountVoucher, self).onchange_amount(amount, payment_rate, partner_id, journal_id, currency_id, type, date, payment_rate_currency_id, company_id)
        return res

   

    def _get_currency_help_label(self, cr, uid, currency_id, payment_rate, payment_rate_currency_id, context=None):
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
        rml_parser = report_sxw.rml_parse( 'currency_help_label', context=context)
        currency_pool = self.env['res.currency']
        currency_str = payment_rate_str = ''
        if currency_id:
            currency_str = rml_parser.formatLang(1, currency_obj=currency_pool.browse(cr, uid, currency_id,
                                                                                      context=context))
        if payment_rate_currency_id:
            payment_rate_str = rml_parser.formatLang(payment_rate, currency_obj=currency_pool.browse(cr, uid,
                                                                                                     payment_rate_currency_id,
                                                                                                     context=context))
        currency_help_label = _('At the operation date, the exchange rate was\n%s = %s') % (
        currency_str, payment_rate_str)
        return currency_help_label

    # @api.multi
    # def recompute_voucher_lines(self, partner_id, journal_id, amount, currency_id, ttype, date):
    #     res = super(AccountVoucher, self).recompute_voucher_lines(partner_id, journal_id, amount, currency_id, ttype, date)
    #     student_obj = self.env['res.partner']
    #     total_amount = amount
    #     # advance payment calculation
    #     advance_pay_amount = 0.0
    #     if isinstance(partner_id,list):
    #         for res_value in res:
    #             if res[res_value]['line_dr_ids']:
    #                 for element in res[res_value]['line_dr_ids']:
    #                     if isinstance(element,dict):
    #                         advance_pay_amount += element['amount_unreconciled']
    #
    #     total_amount += advance_pay_amount
    #     if isinstance(partner_id,list):
    #         for partner in partner_id:
    #             if student_obj.browse(partner).is_parent != True:
    #                 for res_value in res:
    #                     if res[res_value]['line_cr_ids']:
    #                         ele_tuple = []
    #                         ele_dict = []
    #                         for element in res[res_value]['line_cr_ids']:
    #                             if isinstance(element,dict):
    #                                 ele_dict.append(element)
    #                             else:
    #                                 ele_tuple.append(element)
    #                         if ele_dict:
    #                             for ele_line in sorted(ele_dict, key=lambda k: k['amount_unreconciled']):
    #                                 if total_amount == 0:
    #                                     ele_line['amount'] = 0
    #                                 else:
    #                                     if ele_line['amount_unreconciled'] > total_amount:
    #                                         ele_line['amount'] = total_amount
    #                                         total_amount = 0
    #                                     else:
    #                                         ele_line['amount'] = ele_line['amount_unreconciled']
    #                                         total_amount -= ele_line['amount_unreconciled']
    #                         line_cr = ele_tuple + ele_dict
    #                         res[res_value]['line_cr_ids'] = line_cr
    #                 return res
    #     return res

    @api.multi
    def action_move_line_create(self):
        print '------------------action move line create fee.invoice----------------'
        res = super(AccountVoucher, self).action_move_line_create()
        invoice_obj = self.env['account.invoice']
        reg_obj = self.env['registration']
        move_ids = []
        amount_alocation = {}
        for voucher_line in self.line_cr_ids:
            move_ids.append(voucher_line.move_line_id.move_id.id)
            amount_alocation.update({voucher_line.move_line_id.move_id.id:voucher_line.amount})

        for invoice_rec in invoice_obj.search([('move_id','in',move_ids)]):
            total_amount = amount_alocation[invoice_rec.move_id.id]
            reg_rec = reg_obj.search([('invoice_id','=',invoice_rec.id)])
            for invoice_line_ids in invoice_rec.invoice_line_ids.search([('invoice_id','=',invoice_rec.id),
                                                                 ('rem_amount','>',0.00)],order='priority desc'):

                if total_amount > 0.00:
                    if total_amount >= invoice_line_ids.rem_amount:
                        # Student fee line Update (full fee paid)
                        fee_line1 = invoice_rec.partner_id.payble_fee_ids.search(
                            [('name', '=', invoice_line_ids.product_id.id),
                             ('student_id', '=', invoice_rec.partner_id.id),
                             ('month_id.batch_id', '=', invoice_rec.batch_id.id)],
                            limit=1)
                        if fee_line1.id:
                            discount_amount = 0.00
                            for discount_fee in invoice_rec.invoice_line_ids.search([('invoice_id', '=', invoice_rec.id)]):
                                if invoice_line_ids.product_id.fees_discount.id == discount_fee.product_id.id:
                                    discount_amount = discount_fee.rem_amount
                                    total_amount -= discount_amount
                                    discount_fee.rem_amount = 0.00

                                fee_line1.cal_turm_amount = fee_line1.cal_turm_amount + invoice_line_ids.rem_amount + discount_amount
                                total_amount -= invoice_line_ids.rem_amount
                                invoice_line_ids.rem_amount = 0.00
                                # update fee status on registration obj
                                if reg_rec.id and reg_rec.fee_status != 'academy_fee_pay':
                                    reg_rec.fee_status = 'academy_fee_partial_pay'

                                # invoice_line.full_paid = True

                                #fee Status
                                fee_status = invoice_rec.partner_id.payment_status.search([('month_id','=',invoice_rec.month_id.id),
                                                                            ('student_id','=',invoice_rec.partner_id.id)],limit=1)
                                if not fee_status.id:
                                    status_val = {
                                        'month_id': invoice_rec.month_id,
                                        'paid': True,
                                    }
                                    invoice_rec.partner_id.payment_status = [(0,0,status_val)]
                                else:
                                    fee_status.paid = True
                            else:
                                total_amount -= invoice_line_ids.rem_amount
                                invoice_line_ids.rem_amount = 0.00
                        else:
                            fee_line2 =  invoice_rec.partner_id.payble_fee_ids.search([('name','=',invoice_line_ids.product_id.id),
                                                                      ('student_id','=',invoice_rec.partner_id.id)],limit=1)
                            if fee_line2.id:
                                fee_line2.cal_turm_amount = fee_line2.cal_turm_amount + total_amount
                                invoice_line_ids.rem_amount -= total_amount
                                total_amount = 0.00
                            else:
                                invoice_line_ids.rem_amount -= total_amount
                                total_amount = 0.00
        return res

    def voucher_move_line_create_old_10august2016(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):

        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, [voucher_id], ['date'], context=context)[0]['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')


        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = line.type =='dr' and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0

            move_rec = move_line_obj.search(cr, uid, [('id', '=', line.move_line_id.id)], context=context)
            move_brw = move_line_obj.browse(cr, uid, move_rec, context=context)

            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': move_brw.partner_id.id,
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

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

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
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = line.move_line_id.amount_residual_currency - abs(amount_currency)

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': move_brw.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)

        res = (tot_line, rec_lst_ids)
        return self.post_voucher_move_line(cr, uid, res, voucher_id, context)


    @api.model
    def voucher_move_line_create_get(self, voucher_id, line_total, move_id, company_currency, current_currency):
        voucher_rec = self.env['account.voucher'].browse(voucher_id)
        account_move_obj = self.env['account.move']
        if res and len(res) > 1 and res[1]:
            res_move_id = res[1]
            for each in range(0, len(res_move_id)):
                move_first1_id = account_move_obj.search([('line_id', '=', res_move_id[each][0])])
                if move_first1_id.id:
                    if voucher_rec.jounral_id_store == 'bank':
                        move_first1_id.write({'bank_name': voucher_rec.bank_name})
                    if voucher_rec.cheque == True:
                        move_first1_id.write({'cheque_pay': True,
                                              'cheque_date': voucher_rec.cheque_start_date,
                                              'cheque_expiry_date': voucher_rec.cheque_expiry_date, })
        if voucher_rec.partner_id.is_parent == True:
            account_move_obj = self.env['account.move']
            invoice_obj = self.env['account.invoice']
            account_move_line_obj = self.env['account.move.line']
            if res and len(res) > 1 and res[1]:
                res_move_id = res[1]
                for each in range(0, len(res_move_id)):
                    move_first_id = account_move_obj.search([('line_id', '=', res_move_id[each][1])])
                    if move_first_id.id:
                        account_move_line_rec = account_move_line_obj.browse(res_move_id[each][0])
                        parent_id = account_move_line_rec.partner_id.id
                        account_move_line_rec.write({'partner_id': move_first_id.partner_id.id})
        return res
    
    
    
#     @api.model
#     def voucher_move_line_create(self, voucher_id, line_total, company_currency, current_currency):
#         res = super(AccountVoucher, self).voucher_move_line_create(voucher_id, line_total, company_currency,
#                                                                    current_currency)
#         voucher_rec = self.env['account.voucher'].browse(voucher_id)
#         account_move_obj = self.env['account.move']
#         if res and len(res) > 1 and res[1]:
#             res_move_id = res[1]
#             for each in range(0, len(res_move_id)):
#                 move_first1_id = account_move_obj.search([('line_id', '=', res_move_id[each][0])])
#                 if move_first1_id.id:
#                     if voucher_rec.jounral_id_store == 'bank':
#                         move_first1_id.write({'bank_name': voucher_rec.bank_name})
#                     if voucher_rec.cheque == True:
#                         move_first1_id.write({'cheque_pay': True,
#                                               'cheque_date': voucher_rec.cheque_start_date,
#                                               'cheque_expiry_date': voucher_rec.cheque_expiry_date, })
#         if voucher_rec.partner_id.is_parent == True:
#             account_move_obj = self.env['account.move']
#             invoice_obj = self.env['account.invoice']
#             account_move_line_obj = self.env['account.move.line']
#             if res and len(res) > 1 and res[1]:
#                 res_move_id = res[1]
#                 for each in range(0, len(res_move_id)):
#                     move_first_id = account_move_obj.search([('line_id', '=', res_move_id[each][1])])
#                     if move_first_id.id:
#                         account_move_line_rec = account_move_line_obj.browse(res_move_id[each][0])
#                         parent_id = account_move_line_rec.partner_id.id
#                         account_move_line_rec.write({'partner_id': move_first_id.partner_id.id})
#         return res



    def post_voucher_move_line(self,  res, voucher_id, context=None):
        voucher_obj = self.env['account.voucher']
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']

        voucher_rec = voucher_obj.browse( voucher_id)

        if res and len(res) > 1 and res[1]:
            res_move_id = res[1]
            for each in range(0, len(res_move_id)):
                move_first1_id = account_move_obj.search([('line_id', '=', res_move_id[each][0])])
                move_first1_brw = account_move_obj.browse( move_first1_id )
                if move_first1_brw.id:
                    if voucher_rec.jounral_id_store == 'bank':
                        move_first1_brw.write({'bank_name': voucher_rec.bank_name})
                    if voucher_rec.cheque == True:
                        move_first1_brw.write({'cheque_pay': True,
                                              'cheque_date': voucher_rec.cheque_start_date,
                                              'cheque_expiry_date': voucher_rec.cheque_expiry_date, })
        if voucher_rec.partner_id.is_parent == True:
            if res and len(res) > 1 and res[1]:
                res_move_id = res[1]
                for each in range(0, len(res_move_id)):
                    move_first_id = account_move_obj.search([('line_id', '=', res_move_id[each][1])])
                    move_first_brw = account_move_obj.browse( move_first_id)
                    if move_first_brw.id:
                        account_move_line_rec = account_move_line_obj.browse( res_move_id[each][0])
                        parent_id = account_move_line_rec.partner_id.id
                        account_move_line_rec.write({'partner_id': move_first_brw.partner_id.id})
        return res


class Account_Invoice_Line(models.Model):

    _inherit = 'account.move.line'

    parents1_id = fields.Many2one('res.partner', 'Parent')