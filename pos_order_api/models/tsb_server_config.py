from odoo import models, fields, api, _
from openerp.addons.payment.models.payment_acquirer import ValidationError

class TSB_ServerConfig(models.Model):

    _name = 'tsb.server.config'

    name = fields.Char(string='URL')
    port = fields.Char(string ='Port')
    app_key= fields.Char(string ='App Key')
    customer_id  = fields.Char(string ='Customer Id')
    operator_id  = fields.Char(string ='Operator Id')
    active_tsb  = fields.Boolean(string ='Active')

    @api.constrains('name','active_tsb')
    def check_active_record(self):
        for s in self:
            tsb_id = self.search([('active_tsb','=',True)])
            # print"tttttttttttttttssssssssssssssssssbbbbbbbb",tsb_id
            if len(tsb_id.ids)>1:
                raise ValidationError(_('Only 1 Record should be active'))