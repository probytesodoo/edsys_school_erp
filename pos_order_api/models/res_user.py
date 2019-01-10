from odoo import models, fields, api, _

class res_users(models.Model):

    _inherit = 'res.users'

    pos_config = fields.Many2one('pos.config', 'Default Point of Sale')
