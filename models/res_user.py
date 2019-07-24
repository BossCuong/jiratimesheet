# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..services import crypto

class Users(models.Model):
    _inherit = "res.users"

    authorization = fields.Char()

    @api.model
    def get_authorization(self):
        crypto_service = crypto.AESCipher()

        return crypto_service.decrypt(self.authorization)
