from odoo import models, fields, api, _
from odoo.exceptions import except_orm

class TCFeeStructure(models.Model):

    _name = 'tc.fees.structure'

    name = fields.Char('Name')
    code = fields.Char('Code')
    tc_fees_line_ids = fields.One2many('tc.fees.line','tc_fees_structure_id')

    @api.model
    def create(self, vals):
        """
        apply validation : only one record for TC fee structure.
        ---------------------------------------------------------
        :param vals: data dictonary
        :return:
        """
        res = super(TCFeeStructure,self).create(vals)
        exist_record = self.search([])
        if len(exist_record) > 1:
            raise except_orm(_('Warning!'),
                    _("You Can not Create More than One Record !"))
        return res

class TCFeeLine(models.Model):

    _name = 'tc.fees.line'

    name = fields.Many2one('product.product','Name',required=True)
    sequence = fields.Integer('Priority')
    amount = fields.Float('Amount',required=True)
    type = fields.Selection([('required','Required'),('optional','optional')])
    tc_fees_structure_id = fields.Many2one('tc.fees.structure','Fees')
    tc_type = fields.Selection([('within_uae', 'Different Emirate'),
                                ('outside_uae', 'Outside UAE'),
                                ('within_dubai', 'Within Same Emirate')])
