from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Timesheet(models.Model):
    _inherit = 'account.analytic.line'
