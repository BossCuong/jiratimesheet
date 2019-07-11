from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = "project.project"

    manager_id = fields.Many2one('hr.employee', "Employee")

    jiraKey = fields.Char()
    user_ids = fields.Many2many('res.users', string = "user ids ")


class Task(models.Model):
    _inherit = "project.task"

    last_modified = fields.Datetime()

    status = fields.Char()

    jiraKey = fields.Char()
