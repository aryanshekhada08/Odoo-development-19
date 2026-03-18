{
    'name': 'Shop Product',
    'version': '1.0',
    'depends': ['base', 'shop_base', 'shop_customer'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
}