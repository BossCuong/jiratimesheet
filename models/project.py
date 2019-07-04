from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = "project.project"

    jiraKey = fields.Char()

class Project(models.Model):
    _inherit = "project.task"

    last_modified = fields.Datetime()

    jiraKey = fields.Char()