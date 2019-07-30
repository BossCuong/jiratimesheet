from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = "project.project"

    jiraKey  = fields.Char()

    user_ids = fields.Many2many('res.users', string = "user ids ")


class Task(models.Model):
    _inherit = "project.task"

    last_modified = fields.Datetime()

    status  = fields.Char()

    jiraKey = fields.Char()

    summary = fields.Char()

    @api.multi
    def name_get(self):
        result = []
        for task in self:
            result.append((task.id, "%s %s" % (task.name, task.summary or '')))
        return result
