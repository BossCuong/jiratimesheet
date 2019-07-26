from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ..services.datahandler import DataHandler
from ..services.api import Jira
from ..services.utils import to_UTCtime
import datetime
from odoo.addons.queue_job.job import job
class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ## Remove unnecessary attributes

    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")

    last_modified = fields.Datetime()

    assignee_id = fields.Many2one('hr.employee', "Employee")

    jiraKey = fields.Char()

    @api.model
    def auto_gen_new_line(self):
        taskDB = self.env['project.task'].sudo()
        task_records = taskDB.search([])

        username = self.env.user['login']
        employee_DB = self.env['hr.employee'].sudo()
        employee = employee_DB.search([('name','=',username)])

        for record in task_records :
            print("hello : ",record.project_id.id)
            self.env['account.analytic.line'].create({
                'task_id': record.id,
                'project_id': record.project_id.id,
                'employee_id': employee.id,
                'unit_amount': 0,
                'name': "test",
                'date': datetime.datetime.now() + datetime.timedelta(7),
            })

    @api.model
    def auto_sync_data(self):
        if not self.env.user["authorization"]:
            return
        self.sync_data(self.env.user["login"])

    @api.multi
    @job
    def sync_data(self,login):
        dataHandler = DataHandler(login)

        dataHandler.sync_data_from_jira()


    @api.multi
    def button_sync(self):
        if not self.env.user["authorization"]:
            raise UserError(_("Please authenticated"))

        self.sync_data(self.env.user["login"])

    @api.model
    def create(self, vals):
        # put code sync to Jira here
        # if fail return pop
        if self.env.context.get("_is_sync_on_jira"):
            if not self.env.user["authorization"]:
                raise UserError(_("Please authenticated"))

            JiraAPI = Jira(self.env.user.get_authorization())
            task = self.env['project.task'].sudo().search([('id', '=', vals["task_id"])])

            time = vals["date"].strftime("%Y-%m-%dT%H:%M:%S.000%z")

            arg = {
                'task_id': task.name,
                'description': vals["name"],
                'date': time,
                'unit_amount': vals["unit_amount"]
            }

            httpResponse = JiraAPI.add_worklog(arg)

            if httpResponse:
                vals['last_modified'] = to_UTCtime(httpResponse["updated"])
            else:
                raise UserError(_("Falled to update"))

        return super(Timesheet, self).create(vals)

    @api.multi
    def write(self, vals):
        if not self.env.context.get("_is_not_sync_on_jira") and vals.get("amount") is None:
            if not self.env.user["authorization"]:
                raise UserError(_("Please authenticated"))

            JiraAPI = Jira(self.env.user.get_authorization())

            time = vals["date"].strftime("%Y-%m-%dT%H:%M:%S.000%z") if vals.get("date") else None

            arg = {
                'task_id': self.task_id["jiraKey"],
                'worklog_id' : self.jiraKey,
                'description': vals.get("name"),
                'date': time,
                'unit_amount': vals.get("unit_amount")
            }

            httpResponse = JiraAPI.update_worklog(arg)

            if httpResponse:
                vals['last_modified'] = to_UTCtime(httpResponse["updated"])
            else:
                raise UserError(_("Falled to update"))

        return super(Timesheet, self).write(vals)