from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import logging
import odoo
_logger = logging.getLogger(__name__)

class Users(models.Model):
    _name = "res.users"
    _inherit="res.users"

    pos_config = fields.Many2one('pos.config', 'Default Point of Sale')

    @api.model
    def new_check_credentials(self, password):
        """ Override this method to plug additional authentication methods"""
        if not password:
            user = self.sudo().search([('id', '=', self._uid)])
        user = self.sudo().search([('id', '=', self._uid), ('password', '=', password)])
        if not user:
            # super(Users, self).check_credentials(password)
            raise AccessDenied()

    @api.model
    def check_credentials(self, password):
        # convert to base_crypt if needed
        self.env.cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND active', (self.env.uid,))
        encrypted = None
        user = self.env.user
        if self.env.cr.rowcount:
            stored, encrypted = self.env.cr.fetchone()
            if stored and not encrypted:
                user._set_password(stored)
                self.invalidate_cache()
        try:
            if not password:
                return self.new_check_credentials(password)
            return super(Users, self).check_credentials(password)
        except odoo.exceptions.AccessDenied:
            if encrypted:
                valid_pass, replacement = user._crypt_context() \
                    .verify_and_update(password, encrypted)
                if replacement is not None:
                    user._set_encrypted_password(replacement)
                if valid_pass:
                    return
            raise

    @classmethod
    def _login(cls, db, login, password):
        if not password and str(request.params.get('redirect')) != 'http://localhost:8069/web?':
            pass
        if not password and str(request.params.get('redirect')) == '':
            return False
        # if not password:
        #     return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]

                user = self.search([('login', '=', login)])
                if not password:
                    user = self.search([('barcode', '=', login)])

                if user:
                    user_id = user.id
                    user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()

        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        return user_id


    def check_withou_password(self, db, uid, passwd=None):
        """Verifies that the given (uid, password) is authorized for the database ``db`` and
           raise an exception if it is not."""
        # if not passwd:
        #     # empty passwords disallowed for obvious security reasons
        #     raise openerp.exceptions.AccessDenied()
        db = self.pool.db_name
        if self.__uid_cache.setdefault(db, {}).get(uid) == passwd:
            return
        cr = self.pool.cursor()
        try:
            self.check_credentials(cr, uid, passwd)
            self.__uid_cache[db][uid] = passwd
        finally:
            cr.close()


