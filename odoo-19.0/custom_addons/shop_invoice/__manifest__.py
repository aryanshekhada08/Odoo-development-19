{
    'name': 'Shop Invoice',
    'version': '1.0',
    'depends': ['base', 'shop_sales'],
    'data': [ 
        'data/sequence.xml',
        'views/invoice_view.xml',
        'security/ir.model.access.csv',
       
    ],
    'installable': True,
    'application': True,
}