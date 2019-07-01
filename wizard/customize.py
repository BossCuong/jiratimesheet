# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class transientTest(models.TransientModel):
    _name = 'customize.transient'

    Date = fields.Date()
    Description = fields.Char()
    Project = fields.Char()
    Task = fields.Char()
    duration = fields.Float('Duration in hours ')
    project_ID = fields.Char()
    task_ID = fields.Char()


    @api.multi
    def add_record(self):
        self.ensure_one()

        timesheetDB = self.env['account.analytic.line'].sudo()

        timesheetDB.create({
            'task_id': self.task_ID,
            'project_id': self.project_ID,
            'employee_id': employee.id,
            'unit_amount': self.duration,
            'name': self.Description,
            'description' : self.Description,
            'date': self.Date
        })

        return {'type': 'ir.actions.act_window_close'}

