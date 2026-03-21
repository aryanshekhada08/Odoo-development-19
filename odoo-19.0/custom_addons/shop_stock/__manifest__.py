{
    'name': 'Shop Stock',
    'version': '1.0',
    'depends': ['base', 'shop_product', 'shop_sales'],
    'data': [
            'security/ir.model.access.csv',
            'views/product_view.xml',
            'views/stock_history_view.xml',
    ],
    'installable': True,
}