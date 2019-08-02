from odoo import http
from odoo.http import request
from .api import Jira
from .utils import to_UTCtime,to_localTime
import datetime as dt
import pytz
class DataHandler():

    user_dict = {}
    employee_dict = {}
    project_dict = {}
    task_dict = {}
    worklog_dict = {}

    def __init__(self, login):
        userDB = request.env['res.users'].sudo().with_context(active_test=False)

        currentUser = userDB.search([('login', '=', login)])

        self.user = currentUser

        self.JiraAPI = Jira(currentUser.get_authorization())

        self.timesheetDB = request.env['account.analytic.line'].sudo()

        self.taskDB = request.env['project.task'].sudo()

        self.projectDB = request.env['project.project'].sudo()

        self.userDB = request.env['res.users'].sudo().with_context(active_test=False)

    def __create_project(self,data):
        project = self.projectDB.search([('jiraKey', '=', data["id"])])

        if not project:
            project = self.projectDB.create({
                        'name': data["name"],
                        'jiraKey': data["id"],
                        'user_id': self.user_dict.get(data["lead"]["key"]),
                        'user_ids': [(4, self.user.id, 0)]
                    })
        return project

    def __create_all_project(self):
        jira_projects = self.JiraAPI.get_all_project()

        for jira_project in jira_projects:
            if not self.project_dict.get(jira_project["id"]):
                db_project = self.__create_project(jira_project)
                self.project_dict[jira_project["id"]] = db_project.id

    def __create_user(self, name, login):
        user = self.userDB.search([('login', '=', login)])

        if not user:
            user = {
                'name': name,
                'login': login,
                'active': True,
                'employee': True,
                'email': login,
                'employee_ids': [(0, 0, {'name': name,'work_email': login})],
            }
            user = request.env.ref('base.default_user').sudo().copy(user)

        return user

    def __create_all_user_and_employee(self):
        jira_users = self.JiraAPI.get_all_user()

        for jira_user in jira_users:
            if not self.user_dict.get(jira_user["key"]):
                db_user = self.__create_user(jira_user["displayName"], jira_user["key"])
                self.user_dict[jira_user["key"]] = db_user.id
                self.employee_dict[jira_user["key"]] = db_user.employee_ids[0].id

    def __create_task(self, project_id, data, check_first_create=False):
        first_create = False
        task = self.taskDB.search([('jiraKey', '=', data["id"])])

        if not task:
            first_create = True
            res = data["fields"]["assignee"]

            assignee_id = self.user_dict.get(res["key"]) if res else None

            task = self.taskDB.create({
                'name': data["key"],
                'jiraKey': data["id"],
                'last_modified': to_UTCtime(data["fields"]["updated"]),
                'project_id': project_id,
                'summary': data["fields"]["summary"],
                'status': data["fields"]["status"]["name"],
                'user_id': assignee_id
            })

        if check_first_create:
            return task, first_create

        return task

    def __create_worklog(self, project_id, task_id, worklog_info):
        time = to_UTCtime(worklog_info["started"])

        time_limit = '2019-07-01 00:00:00'
        time_limit = dt.datetime.strptime(time_limit, '%Y-%m-%d %H:%M:%S')

        if time < time_limit:
            return

        time = to_localTime(time, request.env.user["tz"])

        author_id = self.employee_dict.get(worklog_info["author"]["key"])

        worklog = self.timesheetDB.create({
                                'task_id': task_id,
                                'project_id': project_id,
                                'employee_id': author_id,
                                'unit_amount': worklog_info["timeSpentSeconds"] / (60 * 60),
                                'name': worklog_info["comment"],
                                'date': time,
                                'last_modified': to_UTCtime(worklog_info["updated"]),
                                'jiraKey': worklog_info["id"]
                            })
        return worklog

    def __create_all_worklog_by_issue(self, project_id, task_id, data):
        worklogs = self.JiraAPI.getAllWorklogByIssue(data["id"])

        # Creat default worklog if issue has no worklog to show on view
        if not worklogs:
            self.timesheetDB.create({
                'task_id': task_id,
                'project_id': project_id,
            })
        else:
            for worklog in worklogs:
                self.__create_worklog(project_id, task_id, worklog)

    def __sync_all_worklog_by_issue(self, project_id, task_id, data):
        #Update worklog
        workLogs = self.JiraAPI.getAllWorklogByIssue(data["id"])

        #Set up worklog id list to consider delete on db
        worklog_id_dic = {}

        for workLog in workLogs:
            worklog_id_dic[workLog["id"]] = True

            res = self.timesheetDB.search([('jiraKey', '=', workLog["id"])])

            if not res:
                self.__create_worklog(project_id, task_id, workLog)
            else:
                isLogModified = (res.last_modified != to_UTCtime(workLog["updated"]))

                if isLogModified:
                    res.with_context(_is_not_sync_on_jira=True).write({
                        'name' : workLog["comment"], #fix this
                        'unit_amount': workLog["timeSpentSeconds"] / (60 * 60),
                        'last_modified' : to_UTCtime(workLog["updated"])
                    })

        # Delete worklog on odoo db
        for workLog in self.timesheetDB.search([('task_id','=',task_id)]):
            #Skip aug data
            if not workLog['jiraKey']:
                continue

            workLog_key = workLog['jiraKey']

            if not worklog_id_dic.get(workLog_key):
                workLog.with_context(_is_not_sync_on_jira=True).unlink()

    def __find_task(self,data):
        return self.taskDB.search([('jiraKey', '=', data["id"])])

    def __find_project(self,data):
        project_key = data["fields"]["project"]["id"]
        return self.projectDB.search([('jiraKey', '=', project_key)])

    def sync_data_from_jira(self):
        self.__create_all_user_and_employee()
        self.__create_all_project()

        issues = self.JiraAPI.getAllIssues()

        num_issues = len(issues)

        if num_issues > 200:
            num_folds = num_issues // 200
            for fold in range(num_folds + 1):
                start_idx = fold*200
                end_idx = (fold+1)*200

                if fold == num_folds:
                    end_idx = num_issues % 200
                request.env['account.analytic.line'].sudo().with_delay().update_issue(self.user.login, issues[start_idx:end_idx])
        else:
            request.env['account.analytic.line'].sudo().with_delay().update_issue(self.user.login, issues)


    def update_issues(self, issues):
        cnt = 0
        for issue in issues:
            print(cnt)
            cnt += 1
            project_id = self.project_dict.get(issue["fields"]["project"]["id"])
            project = self.projectDB.browse(project_id)
            project.sudo().write({'user_ids': [(4, self.user.id, 0)]})

            task_id = self.task_dict.get(issue["id"])
            if not task_id:
                task, is_task_first_create = self.__create_task(project_id, issue, check_first_create=True)
                self.task_dict[issue["id"]] = task.id

                if is_task_first_create:
                    self.__create_all_worklog_by_issue(project.id, task.id, issue)
                    continue
            else:
                task = self.taskDB.browse(task_id)


            ##Update task
            last_modified = to_UTCtime(issue["fields"]["updated"])

            # Is task modified ?
            if task.last_modified != last_modified:
                assignee = issue["fields"]["assignee"]
                assignee_id = self.user_dict.get(assignee["key"]) if assignee else None
                task.write({
                    'last_modified': last_modified,
                    'user_id': assignee_id
                })
                self.__sync_all_worklog_by_issue(project.id, task.id, issue)
        #   request.env.cr.commit()




