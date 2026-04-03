from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _rec_name = 'title'

    title = fields.Char("Title", required=True)
    author = fields.Char("Author", required=True)
    isbn = fields.Char("ISBN")
    category = fields.Selection([
        ('fiction', 'Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('technology', 'Technology'),
        ('education', 'Education'),
    ], string="Category", required=True)

    total_copies = fields.Integer("Total Copies", default=1)
    available_copies = fields.Integer("Available Copies", default=1)

    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('unavailable', 'Unavailable'),
    ], default='available', string="Status")

    borrow_count = fields.Integer("Times Borrowed", default=0)

    @api.constrains('total_copies', 'available_copies')
    def _check_copies(self):
        for record in self:
            if record.available_copies < 0:
                raise ValidationError("Available copies cannot be negative!")
            if record.available_copies > record.total_copies:
                raise ValidationError("Available copies cannot exceed total copies!")

    @api.onchange('available_copies')
    def _onchange_available_copies(self):
        if self.available_copies <= 0:
            self.state = 'borrowed'
        else:
            self.state = 'available'