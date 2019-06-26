# -*- coding: utf-8 -*-
from odoo import http
from . import  API
from odoo.http import request
from odoo.addons.web.controllers.main import Home
class HomeExtend(Home):
    api_url = 'https://jira.novobi.com'

    @http.route('/web/login',type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':

            JiraAPI = API(self.api_url)

            credentials = {
                'username' : request.params['login'],
                'password' : request.params['password']
            }

            httpResponse = JiraAPI.authentication(credentials)

            if httpResponse.status_code == 200:
                UserDB = request.env['res.users'].sudo().with_context(active_test=False)

                currentUser = UserDB.search([('login', '=', request.params['login'])])

                token = JiraAPI.getToken()

                #If user not exist,creat one
                if not currentUser:
                    user = {
                        'name' : request.params['login'],
                        'login' : request.params['login'],
                        'authorization' : token,
                        'active': True
                    }
                    currentUser = request.env.ref('base.default_user').sudo().copy(user)

                #Always update jira password each login time
                currentUser.sudo().write({'authorization' : token})

                request.env.cr.commit()

                httpResponse = JiraAPI.getIssues

                httpResponse = callAPI.get(
                    url = self.api_url + "/rest/api/2/search",
                    headers = {
                        'Content-Type'  : 'application/json',
                        'Authorization' : 'Basic' + ' ' + str(token.decode("utf-8"))
                    },
                    data = {
                        "jql": "assignee = %s" % (request.params['login'].replace("@","\\u0040")),
                        "startAt": 0,
                        "maxResults": 50,
                        "fields": [
                            "project",
                            "status"
                        ]
                    }
                )

                issues = httpResponse.json()["issues"]

                timesheetDB = request.env['account.analytic.line'].sudo()

                taskDB = request.env['project.task'].sudo()

                projectDB = request.env['project.project'].sudo()

                employeeDB = request.env['hr.employee'].sudo()

                employee = employeeDB.create(
                    {
                        'name': request.params['login']
                    }
                )

                for issue in issues:
                    task = taskDB.create({
                        'name': issue["key"]
                    })

                    project = projectDB.create({
                        'name' : issue["fields"]["project"]["key"]
                    })


                    timesheetDB.create({
                        'task_id' : task.id,
                        'project_id' : project.id,
                        'employee_id' : employee.id
                    })

        response = super().web_login(redirect, **kw)

        return response

