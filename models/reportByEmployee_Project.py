from odoo import models, fields, api, _


class reportByEmployee_Project(models.AbstractModel):
    _name = "account.report.byemployee.project"
    _inherit = 'account.report'
    _description = 'Timesheet Report'
    filter_date = {'date_from' : '', 'date_to' : '', 'filter' : 'this_month'}

    def _get_report_name(self):
        return "Timesheet's Report"

    def _get_columns_name(self, options):
        columns = [{'name': 'Employee name'}, {'name': 'Work log'}]
        return columns

    @api.model
    def _get_lines(self, options, line_id = None):
        lines = []
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        if line_id == None :
            sql_query = """
                SELECT
                       "hr_employee".name, "hr_employee".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN hr_employee
                ON  "account_analytic_line".employee_id = "hr_employee".id

                GROUP BY "hr_employee".id
            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()

            total = 0
            for line in results:
                total += line.get('total')
                lines.append({
                    'id' : "1_" + str(line.get('id')),
                    'name' : line.get('name'),
                    'level' : 2,
                    'unfoldable' : True,
                    'unfolded' : str(line_id) == '1_'+str(line.get('id')) and True or False,
                    'columns' : [{'name' : line.get('name'), 'name' : round(line.get('total'),3)}],
                })
            lines.append({
                'id' : 'total',
                'name' : _('Total'),
                'level' : 0,
                'class' : 'total',
                'columns' : [{'name' : round(total,3)}]
            })

        if line_id :
            sql_query = """
                SELECT
                       "hr_employee".name, "hr_employee".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN hr_employee
                ON  "account_analytic_line".employee_id = "hr_employee".id
                GROUP BY "hr_employee".id
            """

            self.env.cr.execute(sql_query)
            results = self.env.cr.dictfetchall()

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
                        'columns': [{'name': line.get('name'), 'name': round(line.get('total'),3)}],
                    })
            query_task = """
                SELECT
                       "project_project".name, "project_project".id, sum("account_analytic_line".unit_amount) as total
                FROM account_analytic_line LEFT JOIN project_project
                ON "account_analytic_line".project_id = "project_project".id 
                AND "account_analytic_line".employee_id = """ + line_id[2:] + """
                WHERE "account_analytic_line".date >= '""" + date_from + """'
                AND "account_analytic_line".date <= '""" + date_to + """'
                GROUP BY "project_project".id
            """

            self.env.cr.execute(query_task)
            results_task = self.env.cr.dictfetchall()

            for line_task in results_task:
                if line_task.get('total') < 0.00000001:
                    continue
                line_task_check = '2_' + str(line_task.get('id'))
                lines.append({
                    'id': "2_" + str(line.get('id')),
                    'name': line_task.get('name'),
                    'parent_id': line_id,
                    'level': 3,
                    'unfoldable' : False,
                    'columns': [{'name': line_task.get('name'), 'name': round(line_task.get('total'),3)}]
            })




        return lines