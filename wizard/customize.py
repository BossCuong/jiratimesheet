# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions, _


class transientTest(models.TransientModel):
    _name = 'customize.transient'

    Date = fields.Datetime()
    Description = fields.Char()
    Project = fields.Char()
    Task = fields.Char()
    duration = fields.Float('Duration in hours ')
    project_ID = fields.Integer()
    task_ID = fields.Integer()

    @api.multi
    def add_record(self):
        self.ensure_one()

        # validate input data
        if self.duration <= 0:
            raise exceptions.UserError(_("Duration is invalied, please input again !"))
        if self.Description == "":
            raise exceptions.UserError(_("Oohh, you forget filling Description field "))


        timesheetDB = self.env['account.analytic.line'].sudo()

        username = self.env.user['login']
        employee_DB = self.env['hr.employee'].sudo()
        employee = employee_DB.search([('name','=',username)])

        timesheetDB.create({
            'task_id': self.task_ID,
            'project_id': self.project_ID,
            'employee_id': employee.id,
            'unit_amount': self.duration ,
            'description' : self.Description,
            'name' : self.Description,
            'date': self.Date
        })

        action = self.env.ref('jiratimesheet.action_timesheet_views').read()[0]
        action['target'] = 'main'
        action['context'] = {'grid_anchor' : fields.Date.to_string(self.Date)}
        return action

