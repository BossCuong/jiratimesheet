from odoo import models, fields, api, _


class report_project_task(models.AbstractModel):
    _name = "account.report.project.task"
    _inherit = 'account.report'
    _description = 'Timesheet Report'

    filter_date     = {'date_from' : '', 'date_to' : '', 'filter' : 'this_month'}
    filter_projects = True
    filter_tasks    = True
    def _get_report_name(self):
        return "Timesheet's Report Project"


    def _get_columns_name(self, options):
        columns = [{'name': 'Project name'}, {'name': 'Work log'}]
        return columns

    @api.model
    def _get_lines(self, options, line_id = None):
        lines = []
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        print(type(date_from),date_to)
        context = self.env.context
        if context.get('print_mode') is None :
            if line_id == None :

                results = self._get_all_project(date_from, date_to, line_id)

                total = 0
                for line in results:
                    total += line.get('total')
                    lines.append({
                        'id' : "1_" + str(line.get('id')),
                        'name' : line.get('name'),
                        'level' : 2,
                        'unfoldable' : True,
                        'unfolded' : str(line_id) == '1_'+str(line.get('id')) and True or False,
                        'columns' : [{'name' : line.get('name'), 'name' : self.convert_float2floatime(round(line.get('total'),3))}],
                    })
                lines.append({
                    'id' : 'total',
                    'name' : _('Total'),
                    'level' : 0,
                    'class' : 'total',
                    'columns' : [{'name' : self.convert_float2floatime(round(round(total,3)))}]
                })

            if line_id :

                results = self._get_all_project(date_from, date_to)

                total = 0
                for line in results:
                    for line in results:
                        total += line.get('total')
                        lines.append({
                            'id': "1_" + str(line.get('id')) ,
                            'name': line.get('name'),
                            'level': 2,
                            'unfoldable': True,
                            'unfolded': str(line_id) == '1_' + str(line.get('id')) and True or False,
                            'columns': [{'name': line.get('name'), 'name': self.convert_float2floatime(round(line.get('total'),3))}],
                        })

                results_task = self._get_all_task(date_from, date_to, line_id[2:])

                for line_task in results_task:
                    if line_task.get('total') < 0.00000001:
                        continue
                    lines.append({
                        'id': "2_" + str(line.get('id')),
                        'name': line_task.get('name'),
                        'parent_id': line_id,
                        'level': 3,
                        'unfoldable' : False,
                        'caret_options': 'project.task',

                        'columns': [{'name': line_task.get('name'), 'name': self.convert_float2floatime(round(line_task.get('total'),3))}]
                })

            return lines

        else :

            results = self._get_all_project(date_from, date_to)

            total = 0
            for line in results:
                total += line.get('total')
                lines.append({
                    'id': str(line.get('id')),
                    'name': line.get('name'),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded':  True,
                    'columns': [{'name': line.get('name'), 'name': self.convert_float2floatime(round(line.get('total'), 3))}],
                })

                results_task = self._get_all_task(date_from, date_to, str(line.get('id')))

                for line_task in results_task:
                    if line_task.get('total') < 0.00000001:
                        continue
                    lines.append({
                        'id': str(line_task.get('id')),
                        'name': line_task.get('name'),
                        'parent_id': line_task.get('project_id'),
                        'level': 3,
                        'unfoldable': False,
                        'columns': [{'name': line_task.get('name'), 'name': self.convert_float2floatime(round(line_task.get('total'), 3))}]
                    })
            lines.append({
                'id' : 'total',
                'name' : _('Total'),
                'level' : 0,
                'class' : 'total',
                'columns' : [{'name' : self.convert_float2floatime(round(total,3))}]
            })
            return lines


    def convert_float2floatime(self, time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(float(time) * 60, 60))


    def _get_templates(self):
        templates = super(report_project_task, self)._get_templates()
        templates['main_template'] = 'jiratimesheet.report_summary'
        templates['search_template'] = 'jiratimesheet.reports_project_task_filter'

        return templates

    def _build_options(self, previous_options=None):
        options = super(report_project_task, self)._build_options(previous_options=previous_options)

        if not previous_options or not previous_options.get("projects"):
            options["projects"] = self._get_projects()
        else:
            options["projects"] = previous_options["projects"]

        if not previous_options or not previous_options.get("tasks"):
            options["tasks"] = self._get_tasks()
        else:
            options["tasks"] = previous_options["tasks"]

        return options


    def _get_projects(self):
        projects = []
        projects_read = self.env["project.project"].search([])
        for e in projects_read:
            projects.append({
                'id': e.id,
                'name': e.name,
                'code': e.name,
                'type': e.name,
                'selected': False
            })
        return projects

    def _get_tasks(self):
        tasks = []
        tasks_read = self.env["project.task"].search([])
        for e in tasks_read:
            tasks.append({
                'id': e.id,
                'name': e.name,
                'code': e.name,
                'type': e.name,
                'selected': False
            })
        return tasks

    def _get_all_project(self, date_from, date_to, line_id = None):
        if line_id == None :
            sql_query = """
                                SELECT
                                       "project_project".name, "project_project".id, sum("account_analytic_line".unit_amount) as total
                                FROM account_analytic_line, project_project
                                WHERE  "account_analytic_line".project_id = "project_project".id
                                AND "account_analytic_line".date >= '""" + date_from + """'
                                AND "account_analytic_line".date <= '""" + date_to + """'
                                GROUP BY "project_project".id
                            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
            return results
        else :
            sql_query = """
                                SELECT
                                       "project_project".name, "project_project".id, sum("account_analytic_line".unit_amount) as total
                                FROM account_analytic_line LEFT JOIN project_project
                                ON "account_analytic_line".project_id = "project_project".id
                                WHERE "account_analytic_line".project_id = """+ line_id +"""
                                AND "account_analytic_line".date >= '""" + date_from + """'
                                AND "account_analytic_line".date <= '""" + date_to + """'
                                GROUP BY "project_project".id
                            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
            return results

    def _get_all_task(self, date_from, date_to, line_id):
        query_task = """
              SELECT
                     "project_task".name, "project_task".id,sum("account_analytic_line".unit_amount) as total
              FROM account_analytic_line LEFT JOIN project_task
              ON "account_analytic_line".task_id = "project_task".id 
              AND "account_analytic_line".project_id = """ + line_id + """
              WHERE "account_analytic_line".date >= '""" + date_from + """'
              AND "account_analytic_line".date <= '""" + date_to + """'
              GROUP BY "project_task".id
          """

        self.env.cr.execute(query_task)
        results_task = self.env.cr.dictfetchall()
        return results_task

    def _get_templates(self):
        templates = super(report_project_task, self)._get_templates()
        templates['main_template'] = 'jiratimesheet.report_summary'
        templates['search_template'] = 'jiratimesheet.reports_project_task_filter'
        templates['line_template'] = 'jiratimesheet.task_caret_option_line_template'
        return templates

    def open_task_detail(self, options, params):
        if not params:
            params = {}

        ctx = self.env.context.copy()
        ctx.pop('id', '')
        print(ctx)
        # Redirect
        view_id = self.env['ir.model.data'].get_object_reference('project', 'view_task_form2')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'project.task',
            'res_id': int(params['id'][2:]),
            'context': ctx,
        }

