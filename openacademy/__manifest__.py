# -*- coding: utf-8 -*-
{
    'name':        "Citadel",

    'summary':
                   """
                   Manage classes
                   """,

    'description': """
        Module for managing trainings in a citadel:
            - classes, 
            - teachers, 
            - students, 
            - sessions,
            - and more...
    """,

    'author':      "The citadel of the seven kingdoms",
    'website':     "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':    'OpenAcademy',
    'version':     '0.9',

    # any module necessary for this one to work correctly
    # check, maybe mail is included in website 
    # 'depends':     ['base', 'mail', 'account', 'product', 'board', 'website', 'website_sale'],
    'depends': ['base', 'board', 'website', 'website_sale'],
    # always loaded
    'data':        [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/course_view.xml",
        "views/partner_view.xml",
        "views/session_view.xml",
        "views/menu_view.xml",
        "report/report.xml",
        "templates/templates.xml",
    ],
    # only loaded in demonstration mode
    'demo':        [
        # "demo/demo.xml",
    ],
}
