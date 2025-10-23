{
    'name': 'JobCard',
    'version': '1.0.0',
    'category': 'Job',
    'summary': 'JobCard',
    'description': """Job Card """,
    'depends': ['base', 'aretx_vehicle', 'contacts', 'sale', 'stock', 'mail', 'base_setup', 'uom', 'account', 'product'],
    'author': 'areterix',
    'sequence': -100,
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_view.xml',
        # 'wizard/account_invoice_send_views.xml',
        'views/job_card_view.xml',
        'views/sale_order_views.xml',
        'reports/qr_view.xml',
        'wizard/advance_payment_wizard_view.xml',
        'wizard/refund_payment_wizard_view.xml',
        # 'reports/report.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,  # app after right module name then  show application name
    'auto_install': False,
    # 'post_init_hook': '_create_seq',
    # 'uninstall_hook': '_uninstall_hook',
    'assets': {},

    'license': 'LGPL-3',

}
# -*- coding: utf-8 -*-
