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
    'version':     '0.1',

    # any module necessary for this one to work correctly
    'depends':     ['base'],

    # always loaded
    'data':        [
        
        "data/openacademy_data.xml",
        "views/templates.xml",
        "security/ir.model.access.csv",
    ],
    # only loaded in demonstration mode
    'demo':        [
        "demo/demo.xml",
    ],
}
