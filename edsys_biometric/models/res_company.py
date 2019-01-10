# import openerp
from odoo import models, fields, api, _
# from openerp.osv import osv
# import os
# from datetime import datetime

class res_company(models.Model):
    
    _inherit = "res.company"
    
    bio_cmp_id = fields.Char('Company Code',required=True)