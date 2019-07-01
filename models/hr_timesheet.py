from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")
    