{
    'name': 'Shop Sales',
    'version': '1.0',
    'depends': ['base', 'shop_base', 'shop_customer', 'shop_product'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
    ],
    'installable': True,
    'application': True,
}