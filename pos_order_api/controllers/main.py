from odoo import models, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request
import json
from odoo.tools import config
import functools
import requests
import jwt
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


db_name = str(config.get('dbfilter'))
# print(db_name)
secret_token_key = str(config.get('secret_token_key') or "abc123!@#")


def validate_token(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get('access_token')
        if not access_token:
            return {'message': 'access_token_not_found, missing access token in request header'}#invalid_response('access_token_not_found', 'missing access token in request header', 401)
        access_token_data = request.env['api.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return {'message': 'token seems to have expired or invalid'}#invalid_response('access_token', 'token seems to have expired or invalid', 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class POSDataSet(http.Controller):

    # @validate_token
    # @http.route('/api/user/get_access_token', type='http', auth="none", methods=['GET'], csrf=False)
    # def get(self, barcode=None):
    #     user = request.env['res.users'].search(
    #         [("barcode", "=", barcode)])
    #     access_token = request.env['api.access_token'].search(
    #         [("user_id", "=", user.id)])
    #     data = {"access_token": access_token.token}
    #     return HttpSuccessResponse(data)

    @http.route('/api/user/get_encrypted_token', type='json', auth="none", csrf=False, methods=['POST'])
    def get_access_token(self, barcode):

        jwt_payload = {"barcode": barcode,
                       "app_key": secret_token_key,
                       "password": "",
                       "db": db_name,
                       }
        jwt_token = jwt.encode(jwt_payload, secret_token_key)
        key = AESCipher(secret_token_key)
        encrypted_token = key.encrypt(jwt_token)

        return {"jwt_token": encrypted_token}


    # @validate_token
    # @http.route('/api/user/get_access_token', type='http', auth="none", csrf=False, methods=['GET'])
    # def get_access_token(self):
    #     user = request.env['res.users'].search(
    #         [("barcode", "=", barcode)])
    #     access_token = request.env['api.access_token'].search(
    #         [("user_id", "=", user.id)])
    #     return {"access_token": access_token.token}

    @validate_token
    @http.route('/api/session/get_session_info', type='http', auth="none", csrf=False)
    def get_session_info(self):
        request.session.check_security()
        request.uid = request.session.uid
        request.disable_db = False
        return request.env['ir.http'].session_info()

    @http.route('/api/session/authenticate', type='json', auth="none")
    def authenticate(self, login, password, jwt_token=None, base_location=None):
        if not password:
            try:
                key = AESCipher(secret_token_key)
                decrypted_token = key.decrypt(jwt_token)
                jwt_payload_back = jwt.decode(str(decrypted_token), secret_token_key)

                if jwt_payload_back:
                    if jwt_payload_back['barcode'] == login and jwt_payload_back['app_key'] == secret_token_key and \
                            jwt_payload_back['db'] == db_name and jwt_payload_back['password'] == '':
                        request.session.authenticate(db_name, login, password)
                        return request.env['ir.http'].session_info()
                    else:
                        raise UserError(_("RFID not found"))
                else:
                    raise UserError(_("RFID not found"))
            except:
                raise UserError(_("RFID or Token not found"))
        else:
            request.session.authenticate(db_name, login, password)
            return request.env['ir.http'].session_info()

    # @http.route('/api/session/authenticate', type='json', auth="none")
    # def authenticate(self, login, password, base_location=None):
    #     request.session.authenticate(db_name, login, password)
    #     return request.env['ir.http'].session_info()

    @http.route('/api/session/logout', type='json', auth="none")
    def logout(self):
        request.session.logout(keep_db=True)
        return {"message": "logout"}


    @http.route('/api/dataset/search_read', type='json', auth="user")
    def search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None, type=None):
        return self.do_search_read(model, fields, offset, limit, domain, sort, type)

    def do_search_read(self, model, fields=False, offset=0, limit=False, domain=None
                       , sort=None, type=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        Model = request.env[model]

        records = Model.search_read(domain, fields,
                                    offset=offset or 0, limit=limit or False, order=sort or False)

        if type:
            updated_records = []
            for rec in records:
                if Model.get_product_type(rec['product_tmpl_id'], type):
                    updated_records.append(rec)
        else:
            updated_records = records

        if not updated_records:
            return {
                'length': 0,
                'records': []
            }
        if limit and len(updated_records) == limit:
            length = Model.search_count(domain)
        else:
            length = len(updated_records) + (offset or 0)
        return {
            'length': length,
            'records': updated_records
        }


    @http.route('/api/dataset/search_or_read_category_wise', type='json', auth="user")
    def search_read_category_wise(self, model, fields=False, offset=0, limit=False, domain=None, sort=None,
                                  category_id=None):
        return self.do_search_read_category_wise(model, fields, offset, limit, domain, sort, category_id)

    def do_search_read_category_wise(self, model, fields=False, offset=0, limit=False, domain=None
                                     , sort=None, category_id=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        Model = request.env[model]

        # records = Model.search_read(domain, fields,
        #                             offset=offset or 0, limit=limit or False, order=sort or False)
        #
        # records = Model.search_read(domain, fields,
        #                             offset=offset or 0, limit=limit or False, order=sort or False)
        if category_id:
            domain = [('pos_categ_id', '=', category_id)]

        records = Model.search_read(domain, ['id', 'name', 'pos_categ_id'])

        if not records:
            return {
                'length': 0,
                'records': []
            }
        if limit and len(records) == limit:
            length = Model.search_count(domain)
        else:
            length = len(records) + (offset or 0)
        return {
            'length': length,
            'records': records
        }

    @http.route('/api/dataset/create_or_get_pos_session', type='json', auth="user")
    def create_or_get_pos_session(self, values):
        user_id = values.get('uid')
        config_id = values.get('config_id')

        pos_session = request.env['pos.session'].search(
            [('user_id', '=', user_id), ('config_id', '=', config_id), ('state', '=', 'opened')])

        pos_config = request.env['pos.config'].search(
            [('id', '=', config_id)])

        if not pos_session:
            pos_session = request.env['pos.session'].create({'user_id': user_id, 'config_id': config_id})
        return {'pos_session_id': pos_session.name, 'session_id':pos_session.id, 'pos_session_state': pos_session.state, 'journal_id':pos_config.journal_ids.id, 'account_id':pos_config.journal_ids.default_credit_account_id.id}

    @http.route('/api/dataset/create_or_get_pos_order', type='json', auth="user")
    def create_or_get_pos_order(self, values):
        tsb_order = values

        tsb_ids = request.env['tsb.server.config'].search(
            [('active_tsb', '=', True)])

        if values.get('pos_session_id'):
            # set name based on the sequence specified on the config
            session = request.env['pos.session'].browse(values['pos_session_id'])
            if not session.state == 'opened':
                raise UserError(_("Session for session id %s already closed.") % (values['pos_session_id'],))

            values['name'] = session.config_id.sequence_id._next()
            values.setdefault('pricelist_id', session.config_id.pricelist_id.id)
        else:
            # fallback on any pos.order sequence
            values['name'] = request.env['ir.sequence'].next_by_code('pos.order')

        pos_statement_id = request.env['account.bank.statement'].search([("pos_session_id", "=", session.id), ("user_id", "=", values['user_id'])])

        if 'partner_id' in values and values['partner_id']:
            customer = request.env['res.partner'].search(
                [("id", "=", values['partner_id'])])

        if 'barcode' in values and values["barcode"]:
            customer = request.env['res.partner'].search(
                [("barcode", "=", values['barcode'])])
            values['partner_id'] = customer.id

        amount_paid = values['amount_paid']

        # if not tsb_ids and customer.credit_limit < values['amount_paid']:
        #     raise UserError(_("Your card credit limit is insufficient, Please Recharge your card."))

        if not pos_statement_id:
            pos_statement_id = request.env['account.bank.statement'].create(
                {'journal_id': values['statement_ids'][0][2]['journal_id'], 'user_id': values['user_id'], 'pos_session_id': values['pos_session_id']})
        statement_id = request.env['account.bank.statement.line'].create(
            {'journal_id': values['statement_ids'][0][2]['journal_id'], 'amount': values['statement_ids'][0][2]['amount'], 'account_id': values['statement_ids'][0][2]['account_id'], 'partner_id': values['partner_id'], 'statement_id': pos_statement_id.id,
             "name": values['statement_ids'][0][2]['name'], "ref":session.name})


        values['statement_ids'][0][2]['statement_id'] = statement_id.statement_id.id

        values = {
            'data': values,#dict(values.items() + raw_dict.items()),
            'to_invoice': values['to_invoice']
        }

        order_list = []
        order_list.append(values)
        # order = request.env['pos.order'].create(values)
        order = request.env['pos.order'].create_from_ui(order_list)
        # order.action_pos_order_paid()
        # print(order[0])
        if not tsb_ids:
            customer.credit_limit = customer.credit_limit - amount_paid

        if tsb_ids:
            resp = self.post_order_to_tsb(request.env['pos.order'].search([('id','=',order[0])]), tsb_ids )
        return {'order_details': order}

    @http.route('/api/dataset/load_student', type='json', auth="user")
    def load(self, model, barcode, fields):
        value = {}
        resp = None
        r = request.env[model].search([("barcode","=",barcode)]).read()

        tsb_ids = request.env['tsb.server.config'].search(
            [('active_tsb', '=', True)])

        if tsb_ids:

            resp = self.get_studen_balance_from_TSB(tsb_ids, barcode)
            if resp and resp != False:
                data = eval(resp.content.replace("true","True").replace("false","False"))

                if not data['result']:
                    raise UserError(_("Student with RFID %s does not exist in TSB.") % (barcode,))

        if r:
            value = r[0]

            raw_dict = {
                'id': value['id'],
                'name': value['name'],
                'credit_limit': data['data']['balance_amount'] if resp and resp != False else value['credit_limit']
            }
        else:
            raise UserError(_("Student with RFID %s not found.") % (barcode,))

        return {'value': raw_dict}

    @http.route('/api/dataset/validate_and_close_pos_session', type='json', auth="user")
    def validate_and_close_pos_session(self, values):
        session_id = values.get('session_id')

        pos_session = request.env['pos.session'].search(
            [('id', '=', session_id), ('state', '=', 'opened')])
        if pos_session:
            try:
                pos_session.action_pos_session_closing_control()
                request.session.logout(keep_db=True)
            except :
                pass
        else:
            raise {'error': 'Session not found'}

        return {'msg': 'Session closed.'}

    @http.route('/api/dataset/get_or_update_student_balance', type='json', auth="user")
    def get_or_update_student_balance(self, values):
        student_id = values.get('student_id')
        rfid = values.get('rfid')
        balance_amount = values.get('recharge_amount')

        if balance_amount and balance_amount < 0:
            raise UserError(_("Recharge amount must be greater than 0"))

        pos_customer = request.env['res.partner'].search(
            [('id', '=', student_id), ('barcode', '=', rfid), ('active', '=', 'True'), ('is_student', '=', 'True'), ('customer', '=', 'True')])
        if pos_customer:
            raw_dict = {}
            raw_dict['student_id'] = student_id
            if balance_amount:
                total_amount = float(pos_customer.credit_limit) + float(balance_amount)
                pos_customer.credit_limit = total_amount
                raw_dict['balance_amount'] =  pos_customer.credit_limit
            else:
                raw_dict['balance_amount'] =  pos_customer.credit_limit

        else:
            raise UserError(_("Student with student id %s and RFID %s not found.") % (student_id,rfid))


        return {'result': raw_dict}

    @http.route('/api/dataset/get_student_orders_details', type='json', auth="user")
    def get_student_orders_details(self, values):
        student_id = values.get('student_id')

        pos_customer_order = request.env['report.pos.order'].search(
            [('partner_id', '=', student_id)])
        if pos_customer_order:
            return {'order_details':[order.to_dict() for order in pos_customer_order]}
        else:
            raise UserError(_("Student with student id %s not found.") % (student_id,))


    def post_order_to_tsb(self, order, tsb_ids):

        items_lines = []
        order_description = ''
        count = 0
        for rec in order['lines']:
            raw_items_dict = {
                    "category_id": rec['product_id']['categ_id']['id'],
                    "category_name": rec['product_id']['categ_id']['name'],
                    "item_id": rec['product_id']['id'],
                    "item_name": rec['display_name'],
                    "price": rec['price_unit'],
                    "qty": rec['qty'],
                    "total": rec['price_subtotal']
                }
            if count <= 3:
                order_description += str(rec['display_name'])
                if count < len(order['lines']) - 1:
                    order_description += ','
                    count = count + 1
            items_lines.append(raw_items_dict)

        post_data = {
            "customer_id":tsb_ids.customer_id,#order['partner_id']['old_id'],
            "api_key": tsb_ids.app_key,#"b17012c17367b5bab452c78ab7fe11ed",
            "mifare_card_id": order['partner_id']['barcode'],
            "amount": order['amount_paid'],
            "imei": "351884062415726",
            "operator_id": tsb_ids.operator_id,#order['user_id']['id'],
            "reference_no": order['id'],
            "description": order_description if order_description else order['name'],
            "items": items_lines
        }

        try:
            resp = requests.post(
                tsb_ids.name+':'+tsb_ids.port+'/api/wallet/transaction',
                data=json.dumps(post_data))
            if resp.status_code == 200:
                return True
        except Exception as e:
            return False


    def get_studen_balance_from_TSB(self, tsb_ids, student_rfid):
        post_data = {
            "customer_id":tsb_ids.customer_id,
            "api_key":tsb_ids.app_key,
            "mifare_card_id":student_rfid
        }

        try:
            resp = requests.post(
                tsb_ids.name+':'+tsb_ids.port+'/api/wallet/balance',
                data=json.dumps(post_data))
            if resp.status_code == 200:
                return resp
        except Exception as e:
            return False


class report_pos_order(models.Model):
    _inherit = 'report.pos.order'

    def to_dict(self):
        resp = {
            'id':self.id,
            'date':self.date,
            'product_qty':self.product_qty,
            'price_sub_total':self.price_sub_total,
            'average_price':self.average_price,
            'total_discount':self.total_discount,
            'order_id':self.order_id.id,
            'partner_id':self.partner_id.id,
            'user_id':self.user_id.id,
            'company_id':self.company_id.id,
            'product_id':self.product_id.id,
            'pos_categ_id':self.pos_categ_id.id,
            'session_id':self.session_id.id

        }
        return resp

class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_type(self, product_tmpl_id, type):
        return request.env['product.template'].search(
            [('id', '=', product_tmpl_id[0]), ('available_in_pos', '=', True), ('type', '=', type)])