{
    'name': 'Shop Dashboard',
    'version': '1.0',
    'depends': ['web', 'shop_sales'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_graph.xml',
        'views/sale_pivot.xml',
        'views/dashboard_view.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'shop_dashboard/static/src/css/dashboard.css',
        ],
    },
}
