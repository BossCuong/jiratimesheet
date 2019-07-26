from odoo import models, fields, api, _


class report_project_employee(models.AbstractModel):
    _name = "account.report.project.employee"
    _inherit = 'account.report'
    _description = 'Timesheet Report'
    filter_date = {'date_from' : '', 'date_to' : '', 'filter' : 'this_month'}
    filter_employees = True

    def _get_report_name(self):
        return "Timesheet's Report Employee"

    def _get_columns_name(self, options):
        columns = [{'name': 'Project name'}, {'name': 'Work log'}]
        return columns

    @api.model
    def _get_lines(self, options, line_id = None):
        lines = []
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        lines = []
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
                    'columns' : [{'name' : self.convert_float2floatime(round(total,3))}]
                })

            if line_id :

                results = self._get_all_project(date_from, date_to, line_id[2:])

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

                results_task = self._get_all_employee(date_from, date_to, line_id[2:])

                for line_task in results_task:
                    if line_task.get('total') < 0.00000001:
                        continue
                    line_task_check = '2_' + str(line_task.get('id'))
                    lines.append({
                        'id': "2_" + str(line.get('id')),
                        'name': line_task.get('name'),
                        'parent_id': line_id,
                        'level': 3,
                        'caret_options': 'project.employee',
                        'unfoldable' : False,
                        'columns': [{'name': line_task.get('name'), 'name': self.convert_float2floatime(round(line_task.get('total'),3))}]
                })
            return lines

    def convert_float2floatime(self, time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(float(time) * 60, 60))


    def _get_templates(self):
        templates = super(report_project_employee, self)._get_templates()
        templates['main_template'] = 'jiratimesheet.report_summary'
        templates['search_template'] = 'jiratimesheet.reports_project_employee_filter'
        templates['line_template'] = 'jiratimesheet.employee_caret_option_line_template'
        return templates

    def _build_options(self, previous_options=None):
        options = super(report_project_employee, self)._build_options(previous_options=previous_options)
        if not previous_options or not previous_options.get("projects"):
            options["projects"] = self._get_projects()
        else:
            options["projects"] = previous_options["projects"]

        if not previous_options or not previous_options.get("employees"):
            options["employees"] = self._get_employees()
        else:
            options["employees"] = previous_options["employees"]
        return options

    def _get_employees(self):
        employees = []
        employees_read = self.env["hr.employee"].search([])
        for e in employees_read:
            employees.append({
                'id': e.id,
                'name': e.name,
                'code': e.name,
                'type': e.name,
                'selected': False
            })
        return employees


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

    def open_employee_detail(self, options, params = None):
        if not params:
            params = {}

        ctx = self.env.context.copy()
        ctx.pop('id', '')

        # Redirect
        view_id = self.env['ir.model.data'].sudo().get_object_reference('hr', 'view_employee_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'hr.employee',
            'view_id': view_id,
            'res_id': int(params['id'][2:]),
            'context': ctx,
        }


    def _get_all_project(self,date_from, date_to, line_id):
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
                WHERE "account_analytic_line".project_id = """ + line_id + """
                AND "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".date <= '""" + date_to + """'
                GROUP BY "project_project".id
            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
            return results

    def _get_all_employee(self,date_from, date_to, line_id):
        query_task = """
            SELECT
                   "hr_employee".name, "hr_employee".id, sum("account_analytic_line".unit_amount) as total
            FROM account_analytic_line LEFT JOIN hr_employee
            ON "account_analytic_line".employee_id = "hr_employee".id 
            AND "account_analytic_line".project_id = """ + line_id + """
            WHERE "account_analytic_line".date >= '""" + date_from + """'
            AND "account_analytic_line".date <= '""" + date_to + """'
            GROUP BY "hr_employee".id
        """

        self.env.cr.execute(query_task)
        results_employee = self.env.cr.dictfetchall()
        return results_employee