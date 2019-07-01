# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class transientTest(models.TransientModel):
    _name = 'customize.transient'

    Date = fields.Date()
    Employee = fields.Char()
    Description = fields.Char()
    Project = fields.Char()
    Task = fields.Char()
    duration = fields.Float('Duration in hours ')

    def add_record(self):
        print("222")

        return {'type': 'ir.actions.act_window_close'}

