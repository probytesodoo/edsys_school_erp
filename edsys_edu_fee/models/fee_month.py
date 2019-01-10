# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _

class fee_month(models.Model):

    _name = 'fee.month'

    _rec_name = 'name'

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

    code= fields.Char(string='Code')
    name= fields.Selection(List_Of_Month,string='Month')
    year = fields.Char(string="Year")
    batch_id = fields.Many2one('batch',string='Batch')
    alt_month = fields.Boolean('Alternate Month')
    quater_month = fields.Boolean('Quater Month')
    # generate_month = fields.Boolean('Month Calculated')
    qtr_month = fields.Boolean('Quater Month')
    leave_month = fields.Boolean('Leave Month')

    @api.multi
    def name_get(self):
        res = []
        def _month(month):
            val = {
                1:'January',
                2:'February',
                3:'March',
                4:'April',
                5:'May',
                6:'June',
                7:'July',
                8:'August',
                9:'September',
                10:'October',
                11:'November',
                12:'December',
            }
            for i in val:
                if val.get(month):
                    return val[month]

        for record in self:
            name = _month(record.name)
            res.append((record.id, name))
        return res

    @api.model
    def allocation_alt_qtr_half_month_false(self, batch_id):
        for month_id in self.batch_id.month_ids.search([('batch_id','=',batch_id)]):
            month_id.write({'alt_month': False,
                            'quater_month': False,
                            'qtr_month': False})

    @api.model
    def allocation_alt_qtr_half_month(self, batch_id):
        code = 0
        total_month = self.batch_id.month_ids.search_count([('batch_id','=',batch_id),('leave_month','=',False)])
        if total_month % 2 == 0:
            half_month = total_month / 2
        else:
            total_month += 1
            half_month = total_month / 2
        for month_id in self.batch_id.month_ids.search([('batch_id','=',batch_id)]):
            if month_id.leave_month == False:
                code += 1
                # half year
                if code in [1,half_month+1]:
                    month_id.quater_month = True
                else:
                    month_id.quater_month = False
                # Quater month
                if code % 3 == 1:
                    month_id.qtr_month = True
                else:
                    month_id.qtr_month = False
                # Alter month
                if code % 2 == 0:
                    month_id.alt_month = False
                else:
                    month_id.alt_month = True

    @api.multi
    def make_it_leave_month(self):
        self.leave_month = True
        batch_id = self.batch_id.id
        self.allocation_alt_qtr_half_month_false(batch_id)
        self.allocation_alt_qtr_half_month(batch_id)

    @api.multi
    def make_it_unleave_month(self):
        self.leave_month = False
        batch_id = self.batch_id.id
        self.allocation_alt_qtr_half_month_false(batch_id)
        self.allocation_alt_qtr_half_month(batch_id)
