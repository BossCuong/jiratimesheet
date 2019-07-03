# -*- coding: utf-8 -*-
from odoo import http
from ..services.api import Jira
from odoo.http import request
from odoo import fields
from ..services.utils import to_UTCtime
import datetime
import pytz

from odoo.addons.web.controllers.main import Home
class HomeExtend(Home):
    api_url = 'https://jira.novobi.com'

    @http.route('/web/login',type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':

            JiraAPI = Jira(self.api_url)

            credentials = {
                'username' : request.params['login'],
                'password' : request.params['password']
            }

            httpResponse = JiraAPI.authentication(credentials)

            if httpResponse.status_code == 200:
                UserDB = request.env['res.users'].sudo().with_context(active_test=False)

                currentUser = UserDB.search([('login', '=', request.params['login'])])

                #If user not exist,creat one
                if not currentUser:
                    user = {
                        'name' : request.params['login'],
                        'login' : request.params['login'],
                        'active': True
                    }
                    currentUser = request.env.ref('base.default_user').sudo().copy(user)

                #Always update jira password each login time
                currentUser.sudo().write({'password' : request.params['password']})

                request.env.cr.commit()

                issues = JiraAPI.getAllIssues()

                timesheetDB = request.env['account.analytic.line'].sudo()

                taskDB = request.env['project.task'].sudo()

                projectDB = request.env['project.project'].sudo()

                employeeDB = request.env['hr.employee'].sudo()

                employee = employeeDB.create({
                        'name': request.params['login']

                    }
                )

                for issue in issues:
                    pass
                    project = projectDB.create({
                        'name': issue["fields"]["project"]["key"],

                    })

                    task = taskDB.create({
                        'name': issue["key"]
                    })


                    workLogs = issue["fields"]["worklog"]["worklogs"]
                    for workLog in workLogs:
                        time = workLog["created"]
                        timesheetDB.create({
                            'task_id': task.id,
                            'project_id': project.id,
                            'employee_id': employee.id,
                            'unit_amount': workLog["timeSpentSeconds"] / (60 * 60),
                            'name': workLog["comment"],
                            'date': to_UTCtime(time)
                        })
                        print(time)
                        print(to_UTCtime(time))

        response = super().web_login(redirect, **kw)

        return response

