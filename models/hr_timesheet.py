from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ## Remove unnecessary attributes
    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")

    last_modified = fields.Datetime()

    def get_next_thursday(self, currentDate):
        date0 = currentDate
        next_thursday = date0 - datetime.timedelta(7)
        return next_thursday

    def auto_gen_new_line(self):

        taskDB      = self.env['project.task'].sudo()

        task_records = taskDB.search([])

        timesheetDB = self.env['account.analytic.line'].sudo()

        username = self.env.user['login']
        employee_DB = self.env['hr.employee'].sudo()
        employee = employee_DB.search([('name','=',username)])


        for record in task_records :
            timesheetDB.create({
                'task_id': record.id,
                'project_id': record.project_id.id,
                'employee_id': employee.id,
                'unit_amount': 0.0,
                'name': "",
                'date': self.get_next_thursday(datetime.datetime.now()),
                'description' : ""
            })
