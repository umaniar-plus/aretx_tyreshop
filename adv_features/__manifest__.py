{
    'name': 'Sale Order Technician',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Add Technician field in Sale Order',
    'description': 'Adds a Technician field to the Sale Order form view.',
    'depends': ['sale'],
    'data': [
        # 'reports/sale_order_jobcard_report.xml',
        'views/sale_order_view.xml',
        'data/custom_sale_report_action.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
