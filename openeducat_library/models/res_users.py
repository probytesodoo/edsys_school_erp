from openerp import models, fields
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class res_users(models.Model):
    _inherit = 'res.users'

    library_id = fields.Many2one(
        'library.location', 'Library', copy = False
        )

#     @api.model
#     def create(self,vals):
#         """
#         write user id in library.
#         ---------------------------------------
# 
#         """
#         library_location_obj = self.env["library.location"]
#         if vals.get("library_id") :
#             import ipdb;ipdb.set_trace()
#             library = library_location_obj.sudo().browse(vals.get("library_id"))
#             library.user_ids = [self.id]
#         return super(res_users,self).create(vals)
# 
#     @api.multi
#     def write(self,vals):
#         """
#         write user id in library.: dictonary
#         
#         """
#         import ipdb;ipdb.set_trace()
#         library_location_obj = self.env["library.location"]
#         if vals.get("library_id") :
#             library = library_location_obj.sudo().browse(vals.get("library_id"))
#             library.user_ids = [self.id]
#         return super(res_users,self).write(vals)
#     