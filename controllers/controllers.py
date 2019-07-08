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
                userDB = request.env['res.users'].sudo().with_context(active_test=False)

                currentUser = userDB.search([('login', '=', request.params['login'])])

                #If user not exist,creat one
                if not currentUser:
                    user = {
                        'name' : request.params['login'],
                        'login' : request.params['login'],
                        'active': True,
                        'authorization' : JiraAPI.encodeAuthorization(credentials),
                        'employee' : True,
                        'employee_ids': [(0, 0, {'name': request.params['login']})]
                    }

                    currentUser = request.env.ref('base.default_user').sudo().copy(user)

                issues = JiraAPI.getAllIssues()

                ## Setup all database
                timesheetDB = request.env['account.analytic.line'].sudo()

                taskDB = request.env['project.task'].sudo()

                projectDB = request.env['project.project'].sudo()

                employeeDB = request.env['hr.employee'].sudo()


                employee = currentUser.employee_ids[0]

                for issue in issues:
                    task = taskDB.search([('jiraKey', '=', issue["id"])])
                    project = projectDB.search([('jiraKey', '=', issue["fields"]["project"]["id"])])

                    if task:
                        last_modified_OnJira = to_UTCtime(issue["fields"]["updated"])


                        isTaskModified = (task.last_modified != last_modified_OnJira)

                        if isTaskModified:
                            task.write({
                                'last_modified' : last_modified_OnJira
                            })

                            # Update worklog
                            workLogs = issue["fields"]["worklog"]["worklogs"]

                            for workLog in workLogs:
                                res = timesheetDB.search([('jiraKey', '=', workLog["id"])])

                                if not res:
                                    res = timesheetDB.search([('task_id', '=', task.id)])
                                    time = workLog["created"]
                                    timesheetDB.create({
                                        'task_id': task.id,
                                        'project_id': project.id,
                                        'employee_id': employee.id,
                                        'unit_amount': workLog["timeSpentSeconds"] / (60 * 60),
                                        'name': workLog["comment"],
                                        'date': to_UTCtime(time),
                                        'last_modified': to_UTCtime(workLog["updated"]),
                                        'jiraKey': workLog["id"]
                                    })
                                else:
                                    isLogModified = (res.last_modified != to_UTCtime(workLog["updated"]))

                                    if isLogModified:
                                        res.write({
                                            'name' : workLog["comment"],
                                            'last_modified' : to_UTCtime(workLog["updated"])
                                        })

                        continue



                    if not project:
                        project = projectDB.create({
                            'name': issue["fields"]["project"]["name"],
                            'jiraKey': issue["fields"]["project"]["id"],
                        })

                    task = taskDB.create({
                        'name': issue["key"],
                        'jiraKey': issue["id"],
                        'last_modified': to_UTCtime(issue["fields"]["updated"]),
                        'project_id': project.id

                    })

                    workLogs = issue["fields"]["worklog"]["worklogs"]
                    if not workLogs:
                        timesheetDB.create({
                            'task_id': task.id,
                            'project_id': project.id,
                            'employee_id': employee.id
                        })
                    for workLog in workLogs:
                        time = workLog["created"]
                        timesheetDB.create({
                            'task_id': task.id,
                            'project_id': project.id,
                            'employee_id': employee.id,
                            'unit_amount': workLog["timeSpentSeconds"] / (60 * 60),
                            'name': workLog["comment"],
                            'date': to_UTCtime(time),
                            'last_modified': to_UTCtime(workLog["updated"]),
                            'jiraKey': workLog["id"]
                        })

                #Always update jira password each login time
                currentUser.sudo().write({'password' : request.params['password']})

                request.env.cr.commit()


        response = super().web_login(redirect, **kw)

        return response

