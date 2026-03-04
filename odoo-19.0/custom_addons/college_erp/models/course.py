from odoo import models, fields


class CollegeCourse(models.Model):
    _name = 'college.course'
    _description = 'College Course'
    _rec_name = 'name'

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code", required=True)
    duration = fields.Integer(string="Duration (Years)", required=True)
    student_ids = fields.One2many(
        'college.student', 'course_id', string="Students"
    )

    _sql_constraints = [
        ('unique_course_code', 'unique(code)', 'Course code must be unique!')
    ]
