{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Manage books, members, borrowing and fines',
    'author': 'Aryan',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/book_view.xml',
        'views/member_view.xml',
        'views/borrow_view.xml',
        'views/fine_view.xml',
        'views/wizard_view.xml',
    ],
    'installable': True,
    'application': True,
}