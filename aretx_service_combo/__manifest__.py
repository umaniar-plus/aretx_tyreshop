# -*- coding: utf-8 -*-
{
    'name': "service_combo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','aretx_job_card','sale', 'account'],
    'sequence': -100,

    # always loaded
    'data': [
        'security/aretx_service_combo_security.xml',
        'demo/demo.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/inherit_view_job_card.xml',
        'views/inherit_view_sale_order.xml',
        'views/inherit_view_product.xml',
        'views/service_combo_tracker_view.xml',
        'views/service_combo_master_view.xml',
        'views/service_combo_tracker_form_view.xml',
        'views/service_status_master_view.xml',
        # 'views/service_combo_tracker_vehicle_view.xml',

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'auto_install': False,
    'assets': {
            'web.assets_backend': [
                'aretx_service_combo/static/src/css/service_combo.css',
            ],
    },
    'application': True,
    'license': 'LGPL-3'
}
