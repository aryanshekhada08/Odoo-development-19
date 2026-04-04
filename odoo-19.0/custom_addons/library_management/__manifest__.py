{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Manage books, members, borrowing and fines',
    'author': 'Aryan',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/book_view.xml',     # ← actions defined first
        'views/member_view.xml',
        'views/borrow_view.xml',
        'views/fine_view.xml',
        'views/wizard_view.xml',
        'views/menu.xml',          
    ],
    'installable': True,
    'application': True,
}