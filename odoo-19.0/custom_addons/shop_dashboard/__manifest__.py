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
     'assets': {
        'web.assets_backend': [
            
              'shop_dashboard/static/src/css/dashboard.css',
              'shop_dashboard/static/src/xml/dashboard_chart.xml',
              'https://cdn.jsdelivr.net/npm/chart.js',
          
       ],
     },
}