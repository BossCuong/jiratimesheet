from odoo import models, fields, api, _


class report_employee_project(models.AbstractModel):
    _name = "account.report.employee.project"
    _inherit = 'account.report'
    _description = 'Timesheet Report'

    filter_employees = True
    filter_projects = True
    filter_date = {'date_from' : '', 'date_to' : '', 'filter' : 'this_month'}

    def _get_report_name(self):
        return "Timesheet's Report All Employee"

    def _get_columns_name(self, options):
        columns = [{'name': 'Employee name'}, {'name': 'Work log'}]
        return columns

    @api.model
    def _get_lines(self, options, line_id = None):
        lines = []
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        context = self.env.context
        if context.get('print_mode') is None :

            if line_id == None :
                results = self.get_all_employee(date_from, date_to)
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
                    'columns' : [{'name' : round(total,3)}]
                })

            if line_id :

                results = self.get_all_employee(date_from, date_to, line_id[2:])

                total = 0
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

                results_task = self.get_all_project(date_from, date_to, line_id[2:])


                for line_task in results_task:
                    if line_task.get('total') < 0.00000001:
                        continue
                    lines.append({
                        'id': "2_" + str(line_task.get('id')),
                        'name': line_task.get('name'),
                        'parent_id': line_id,
                        'level': 3,
                        'unfoldable' : False,
                        'caret_options': 'employee.project',
                        'columns': [{'name': line_task.get('name'), 'name': self.convert_float2floatime(round(line_task.get('total'),3))}]
                })
            return lines


        else :

            results = self.get_all_employee(date_from, date_to)

            total = 0
            for line in results:
                total += line.get('total')
                lines.append({
                    'id':  str(line.get('id')),
                    'name': line.get('name'),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'columns': [{'name': line.get('name'), 'name': self.convert_float2floatime(round(line.get('total'), 3))}],
                })


            results_task = self.get_all_project(date_from, date_to)

            for line_task in results_task:
                if line_task.get('total') < 0.00000001:
                    continue
                lines.append({
                    'id':  str(line_task.get('id')),
                    'name': line_task.get('name'),
                    'parent_id': line_task.get('employee_id'),
                    'level': 3,
                    'unfoldable': False,
                    'columns': [{'name': line_task.get('name'), 'name': self.convert_float2floatime(round(line_task.get('total'), 3))}]
                })
            lines.append({
                'id': 'total',
                'name': _('Total'),
                'level': 0,
                'class': 'total',
                'columns': [{'name': self.convert_float2floatime(round(total, 3))}]
            })

            return lines

    def convert_float2floatime(self, time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(float(time) * 60, 60))

    def get_all_project(self, date_from, date_to, line_id = None):
        if line_id == None :
            query_task = """
                SELECT
                       "project_project".name, "project_project".id, "account_analytic_line".employee_id,sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN project_project
                ON "account_analytic_line".project_id = "project_project".id 
                WHERE "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".date <= '""" + date_to + """'
                GROUP BY "project_project".id, "account_analytic_line".employee_id
            """

            self.env.cr.execute(query_task)
            results_task = self.env.cr.dictfetchall()

            return results_task
        else :
            query_task = """
                SELECT
                       "project_project".name, "project_project".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN project_project
                ON "account_analytic_line".project_id = "project_project".id 

                WHERE "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".date <= '""" + date_to + """'
                AND "account_analytic_line".employee_id = """ + line_id + """
                GROUP BY "project_project".id
            """
            self.env.cr.execute(query_task)
            results = self.env.cr.dictfetchall()
            return results

    def get_all_employee(self,date_from, date_to, line_id = None):
        if line_id == None:

            sql_query = """
                SELECT
                       "hr_employee".name, "hr_employee".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN hr_employee
                ON  "account_analytic_line".employee_id = "hr_employee".id
                WHERE "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".date <= '""" + date_to + """'
                GROUP BY "hr_employee".id
            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
            return results
        else :
            sql_query = """
                SELECT
                       "hr_employee".name, "hr_employee".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN hr_employee
                ON  "account_analytic_line".employee_id = "hr_employee".id
                WHERE "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".employee_id = """ + line_id + """ 
                AND "account_analytic_line".date <= '""" + date_to + """'
                GROUP BY "hr_employee".id
            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()
            return results

    def _get_templates(self):
        templates = super(report_employee_project, self)._get_templates()
        templates['main_template'] = 'jiratimesheet.report_summary'
        templates['search_template'] = 'jiratimesheet.reports_employee_project_filter'
        templates['line_template'] = 'jiratimesheet.project_caret_option_line_template'

        return templates

    def _build_options(self, previous_options=None):

        options = super(report_employee_project, self)._build_options(previous_options=previous_options)
        if not previous_options or not previous_options.get("employees"):
            options["employees"] = self._get_employees()
        else:
            options["employees"] = previous_options["employees"]

        if not previous_options or not previous_options.get("projects"):
            options["projects"] = self._get_projects()
        else:
            options["projects"] = previous_options["projects"]
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

    def open_project_detail(self, options, params):
        if not params:
            params = {}

        ctx = self.env.context.copy()
        ctx.pop('id', '')

        # Redirect
        view_id = self.env['ir.model.data'].sudo().get_object_reference('project', 'edit_project')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'project.project',
            'view_id': view_id,
            'res_id': int(params['id'][2:]),
            'context': ctx,
        }