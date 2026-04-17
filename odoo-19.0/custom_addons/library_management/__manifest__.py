{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Manage books, members, borrowing and fines',
    'author': 'Aryan',
    'depends': ['base', 'mail'],
    'data': [
        'security/library_security.xml',
        'security/library_rules.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_templates.xml',
        'data/cron.xml',
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
