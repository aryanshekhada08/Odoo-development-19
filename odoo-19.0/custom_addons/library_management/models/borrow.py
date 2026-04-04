from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class LibraryBorrow(models.Model):
    _name = 'library.borrow'
    _description = 'Library Borrow'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'

    reference = fields.Char("Reference", readonly=True, default="New")

    book_id = fields.Many2one('library.book', string="Book", required=True)
    member_id = fields.Many2one('library.member', string="Member", required=True)

    borrow_date = fields.Date("Borrow Date", default=fields.Date.today)
    due_date = fields.Date("Due Date", compute="_compute_due_date", store=True)
    return_date = fields.Date("Return Date")

    days_overdue = fields.Integer("Days Overdue", compute="_compute_days_overdue")
    fine_amount = fields.Float("Fine Amount", compute="_compute_fine_amount", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], default='draft', string="Status", tracking=True)

    notes = fields.Text("Notes")

    # ─── Compute Methods ───────────────────────────────

    @api.depends('borrow_date')
    def _compute_due_date(self):
        for record in self:
            if record.borrow_date:
                record.due_date = record.borrow_date + timedelta(days=14)
            else:
                record.due_date = False

    @api.depends('due_date', 'return_date', 'state')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.state in ('borrowed', 'overdue') and record.due_date:
                if today > record.due_date:
                    record.days_overdue = (today - record.due_date).days
                else:
                    record.days_overdue = 0
            else:
                record.days_overdue = 0

    @api.depends('days_overdue')
    def _compute_fine_amount(self):
        for record in self:
            record.fine_amount = record.days_overdue * 5.0

    # ─── Business Logic ────────────────────────────────

    @api.constrains('member_id')
    def _check_member_blocked(self):
        for record in self:
            if record.member_id.is_blocked:
                raise ValidationError(
                    f"Member {record.member_id.name} is blocked and cannot borrow books!"
                )

    def action_borrow(self):
        for record in self:
            if record.book_id.available_copies <= 0:
                raise ValidationError(
                    f"No copies of '{record.book_id.title}' are available!"
                )

            # reduce available copies
            record.book_id.available_copies -= 1
            record.book_id.borrow_count += 1

            # update member stats
            record.member_id.total_borrowed += 1

            record.state = 'borrowed'
            record.message_post(
                body=f"Book '{record.book_id.title}' borrowed by {record.member_id.name}. Due: {record.due_date}"
            )

    def action_return(self):
        for record in self:
            record.return_date = fields.Date.today()

            # restore available copies
            record.book_id.available_copies += 1

            if record.days_overdue > 0:
                # create fine automatically
                self.env['library.fine'].create({
                    'borrow_id': record.id,
                    'member_id': record.member_id.id,
                    'amount': record.fine_amount,
                })
                record.state = 'overdue'
                record.message_post(
                    body=f"Book returned {record.days_overdue} day(s) late. Fine of {record.fine_amount} created automatically."
                )
            else:
                record.state = 'returned'
                record.message_post(
                    body=f"Book '{record.book_id.title}' returned on time by {record.member_id.name}."
                )

    def action_cancel(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("Only draft borrows can be cancelled.")
            record.unlink()
        return True

    def action_mark_overdue(self):
        overdue_borrows = self.search([
            ('state', '=', 'borrowed'),
            ('due_date', '<', fields.Date.today()),
        ])
        for record in overdue_borrows:
            record.state = 'overdue'
            record.message_post(
                body=f"Automatically marked overdue. {record.days_overdue} day(s) past due date."
            )

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('library.borrow') or 'New'
        return super().create(vals)
