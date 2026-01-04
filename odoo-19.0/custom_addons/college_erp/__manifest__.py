{
    'name': 'College ERP',
    'version': '1.0',
    'summary': 'College Management System',
    'description': 'Manage students and courses in a college',
    'author': 'Aryan',
    'category': 'Education',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/course_views.xml',
        'views/menu.xml',
    ],
    'application': True,
    'installable': True,
}
