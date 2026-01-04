from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CollegeStudent(models.Model):
    _name = 'college.student'
    _description = 'College Student'
    _rec_name = 'name'

    name = fields.Char(string="Student Name", required=True)
    enrollment_number = fields.Char(string="Enrollment No", required=True)
    admission_date = fields.Date(
        string="Admission Date", default=fields.Date.today
    )
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(
        string="Age", compute="_compute_age", store=True
    )

    course_id = fields.Many2one(
        'college.course', string="Course", ondelete='restrict', required=True
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        string="Status"
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'unique_enrollment_number',
            'unique(enrollment_number)',
            'Enrollment number must be unique!'
        )
    ]

    # -------------------------
    # COMPUTE METHODS
    # -------------------------
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = fields.Date.today()
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0

    # -------------------------
    # VALIDATIONS
    # -------------------------
    @api.constrains('date_of_birth')
    def _check_dob(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(
                    "Date of Birth cannot be in the future."
                )

    # -------------------------
    # BUTTON ACTIONS
    # -------------------------
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
