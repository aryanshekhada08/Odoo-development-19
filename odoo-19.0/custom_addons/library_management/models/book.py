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
    ], compute="_compute_state", store=True, string="Status")

    is_out_of_stock = fields.Boolean(
        "Out of Stock",
        compute="_compute_is_out_of_stock",
        store=True,
    )

    borrow_count = fields.Integer("Times Borrowed", default=0)

    @api.depends('total_copies', 'available_copies')
    def _compute_state(self):
        for record in self:
            if record.available_copies <= 0:
                record.state = 'unavailable'
            elif record.available_copies < record.total_copies:
                record.state = 'borrowed'
            else:
                record.state = 'available'

    @api.depends('available_copies')
    def _compute_is_out_of_stock(self):
        for record in self:
            record.is_out_of_stock = record.available_copies <= 0

    @api.constrains('total_copies', 'available_copies')
    def _check_copies(self):
        for record in self:
            if record.available_copies < 0:
                raise ValidationError("Available copies cannot be negative!")
            if record.available_copies > record.total_copies:
                raise ValidationError("Available copies cannot exceed total copies!")
            
    def action_view_borrows(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Borrows',
            'res_model': 'library.borrow',
            'view_mode': 'list,form',
            'domain': [('book_id', '=', self.id)],
        }