from odoo import http
from odoo.http import request
from .api import Jira
from .utils import to_UTCtime


class DataHandler():
    def __init__(self, login):
        userDB = request.env['res.users'].sudo().with_context(active_test=False)

        currentUser = userDB.search([('login', '=', login)])

        self.user = currentUser

        self.JiraAPI = Jira(currentUser.authorization)

        self.timesheetDB = request.env['account.analytic.line'].sudo()

        self.taskDB = request.env['project.task'].sudo()

        self.projectDB = request.env['project.project'].sudo()

        self.userDB = request.env['res.users'].sudo().with_context(active_test=False)

    def __create_project(self,data):
        project_info = data["fields"]["project"]

        project_detail = self.JiraAPI.get_project(project_info["key"])

        project_lead = self.__add_user(project_detail["lead"]["name"])

        project = self.projectDB.create({
                    'name': project_info["name"],
                    'jiraKey': project_info["id"],
                    'user_id' : project_lead.id,
                    'user_ids': [(4, self.user.id, 0)]
                })
        return project

    def __create_task(self,project_id,data):
        task = self.taskDB.create({
            'name': data["key"],
            'jiraKey': data["id"],
            'last_modified': to_UTCtime(data["fields"]["updated"]),
            'project_id': project_id
        })
        return task

    def __add_user(self,userName):
        currentUser = self.userDB.search([('login', '=', userName)])

        if not currentUser:
            user = {
                'name': userName,
                'login': userName,
                'active': True,
                'employee': True,
                'employee_ids': [(0, 0, {'name': userName})],
            }
            currentUser = request.env.ref('base.default_user').sudo().copy(user)

        return currentUser

    def __create_worklog(self,project_id,task_id,worklog_info):
        worklog = self.timesheetDB.create({
                                'task_id': task_id,
                                'project_id': project_id,
                                'employee_id': self.user.employee_ids[0].id,
                                'unit_amount': worklog_info["timeSpentSeconds"] / (60 * 60),
                                'name': worklog_info["comment"],
                                'date': to_UTCtime(worklog_info["started"]),
                                'last_modified': to_UTCtime(worklog_info["updated"]),
                                'jiraKey': worklog_info["id"]
                            })
        return worklog

    def __create_all_worklog_by_issue(self,project_id,task_id,data):
        workLogs = self.JiraAPI.getAllWorklogByIssue(data["id"])

        # Creat default worklog if issue has no worklog to show on view
        if not workLogs:
            self.timesheetDB.create({
                'task_id': task_id,
                'project_id': project_id,
                'employee_id': self.user.employee_ids[0].id,
            })
        else:
            for workLog in workLogs:
                self.__create_worklog(project_id,task_id,workLog)

    def __sync_all_worklog_by_issue(self,project_id,task_id,data):
        #Update worklog
        workLogs = self.JiraAPI.getAllWorklogByIssue(data["id"])

        for workLog in workLogs:
            res = self.timesheetDB.search([('jiraKey', '=', workLog["id"])])
            if not res:
                self.__create_worklog(project_id,task_id,workLog)
            else:
                isLogModified = (res.last_modified != to_UTCtime(workLog["updated"]))

                if isLogModified:
                    res.write({
                        'name' : workLog["comment"],
                        'unit_amount': workLog["timeSpentSeconds"] / (60 * 60),
                        'last_modified' : to_UTCtime(workLog["updated"])
                    })


    def __find_task(self,data):
        return self.taskDB.search([('jiraKey', '=', data["id"])])

    def __find_project(self,data):
        project_key = data["fields"]["project"]["id"]
        return self.projectDB.search([('jiraKey', '=', project_key)])

    def sync_data_from_jira(self):
        issues = self.JiraAPI.getAllIssues()

        for issue in issues:
            task = self.__find_task(issue)
            project = self.__find_project(issue)

            if project:
                project.sudo().write({'user_ids': [(4, self.user.id, 0)]})

            if task:
                last_modified = to_UTCtime(issue["fields"]["updated"])

                # Is task modified ?
                if task.last_modified != last_modified:
                    task.write({
                        'last_modified' : last_modified
                    })
                    self.__sync_all_worklog_by_issue(project.id,task.id,issue)

                continue

            if not project:
                project = self.__create_project(issue)

            task = self.__create_task(project.id,issue)

            self.__create_all_worklog_by_issue(project.id,task.id,issue)

        request.env.cr.commit()



