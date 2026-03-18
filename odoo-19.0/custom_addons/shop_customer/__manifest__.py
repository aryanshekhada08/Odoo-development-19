{
    'name': 'Shop Customer',
    'version': '1.0',
    'depends': ['base', 'shop_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_view.xml',
    ],
    'installable': True,
    'application': True,
}