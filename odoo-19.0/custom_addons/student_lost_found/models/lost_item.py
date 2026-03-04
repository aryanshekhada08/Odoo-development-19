from odoo import models, fields, api

class LostItem(models.Model):
    _name = 'student.lost.item'
    _description = 'Lost & Found Item'
    _order = 'create_date desc'

    name = fields.Char(string="Item Name", required=True)
    description = fields.Text(string="Description")
    lost_date = fields.Date(default=fields.Date.today)
    location = fields.Char(string="Lost Location")

    student_id = fields.Many2one(
        'res.partner',
        string="Reported By",
        required=True
    )

    found_by = fields.Char(string="Found By")

    state = fields.Selection([
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('verified', 'Verified'),
        ('returned', 'Returned'),
    ], default='lost')

    is_active = fields.Boolean(default=True)

    # ✅ METHODS MUST BE INSIDE CLASS
    def action_mark_found(self):
        self.state = 'found'

    def action_verify(self):
        self.state = 'verified'

    def action_return(self):
        self.state = 'returned'
