# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import datetime as d
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

class BatchInherit(models.Model):
    _inherit = 'batch'
    
    re_reg_start_date = fields.Date(string='Start Date')
    re_reg_end_date = fields.Date(string='End Date')
    promotion_start_date = fields.Date(string='Start Date')
    promotion_end_date = fields.Date(string='End Date')
    tc_start_date = fields.Date(string='Start Date')
    tc_end_date = fields.Date(string='End Date')