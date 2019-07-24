# -*- coding: utf-8 -*-
{
    'name': "jiratimesheet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_timesheet', 'project','hr'],

    # always loaded
    'data': [

        # 'security/ir.model.access.csv',
        'views/assets.xml',

        'views/timesheet_view.xml',

        'views/timesheet_menu.xml',

        'views/project_view_rule.xml',

        'views/task_view_rule.xml',

        'wizard/customize_view.xml',

        'views/search_template_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}