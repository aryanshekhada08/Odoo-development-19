{
    'name': 'Shop Dashboard',
    'version': '1.0',
    'depends': ['base', 'shop_base'],   # IMPORTANT CHANGE
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',
    ],
    'installable': True,
    'application': True,
}