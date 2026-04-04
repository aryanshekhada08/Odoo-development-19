from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IssueBookWizard(models.TransientModel):
    _name = 'library.issue.book.wizard'
    _description = 'Issue Book Wizard'

    # ─── Fields ────────────────────────────────────────

    member_id = fields.Many2one(
        'library.member',
        string="Member",
        required=True,
        domain="[('state', '=', 'active')]"
    )

    book_id = fields.Many2one(
        'library.book',
        string="Book",
        required=True,
        domain="[('available_copies', '>', 0)]"
    )

    borrow_date = fields.Date(
        "Borrow Date",
        default=fields.Date.today,
        required=True
    )

    due_date = fields.Date(
        "Due Date",
        compute="_compute_due_date",
        store=True,
        readonly=False
    )

    notes = fields.Text("Notes")

    # ─── Member Info (readonly display) ────────────────

    member_active_borrows = fields.Integer(
        "Active Borrows",
        related='member_id.active_borrows',
        readonly=True
    )

    member_state = fields.Selection(
        related='member_id.state',
        readonly=True
    )

    book_available_copies = fields.Integer(
        "Available Copies",
        related='book_id.available_copies',
        readonly=True
    )

    # ─── Compute ───────────────────────────────────────

    @api.depends('borrow_date')
    def _compute_due_date(self):
        from datetime import timedelta
        for record in self:
            if record.borrow_date:
                record.due_date = record.borrow_date + timedelta(days=14)
            else:
                record.due_date = False

    # ─── Onchange Warnings ─────────────────────────────

    @api.onchange('member_id')
    def _onchange_member_id(self):
        if self.member_id:
            if self.member_id.is_blocked:
                return {
                    'warning': {
                        'title': 'Blocked Member!',
                        'message': f'{self.member_id.name} is currently blocked. Please resolve unpaid fines first.',
                    }
                }
            if self.member_id.active_borrows >= 3:
                return {
                    'warning': {
                        'title': 'Borrow Limit!',
                        'message': f'{self.member_id.name} already has {self.member_id.active_borrows} active borrows. Maximum is 3.',
                    }
                }

    @api.onchange('book_id')
    def _onchange_book_id(self):
        if self.book_id:
            if self.book_id.available_copies <= 0:
                return {
                    'warning': {
                        'title': 'No Copies Available!',
                        'message': f'"{self.book_id.title}" has no available copies.',
                    }
                }
            if self.book_id.available_copies == 1:
                return {
                    'warning': {
                        'title': 'Last Copy!',
                        'message': f'This is the last available copy of "{self.book_id.title}".',
                    }
                }

    # ─── Validation ────────────────────────────────────

    @api.constrains('member_id', 'book_id')
    def _check_duplicate_borrow(self):
        for record in self:
            existing = self.env['library.borrow'].search_count([
                ('member_id', '=', record.member_id.id),
                ('book_id', '=', record.book_id.id),
                ('state', '=', 'borrowed'),
            ])
            if existing:
                raise ValidationError(
                    f'{record.member_id.name} has already borrowed "{record.book_id.title}" and not returned it yet!'
                )

    # ─── Action ────────────────────────────────────────

    def action_issue_book(self):
        self.ensure_one()

        # Final safety checks
        if self.member_id.is_blocked:
            raise ValidationError(
                f'Cannot issue book. Member {self.member_id.name} is blocked!'
            )

        if self.book_id.available_copies <= 0:
            raise ValidationError(
                f'Cannot issue book. No copies of "{self.book_id.title}" available!'
            )

        if self.member_id.active_borrows >= 3:
            raise ValidationError(
                f'Member {self.member_id.name} has reached the maximum borrow limit of 3 books!'
            )

        # Create the borrow record
        borrow = self.env['library.borrow'].create({
            'member_id': self.member_id.id,
            'book_id': self.book_id.id,
            'borrow_date': self.borrow_date,
            'notes': self.notes,
        })

        # Confirm borrow immediately
        borrow.action_borrow()

        # Return action to open the created borrow record
        return {
            'type': 'ir.actions.act_window',
            'name': 'Borrow Record',
            'res_model': 'library.borrow',
            'res_id': borrow.id,
            'view_mode': 'form',
            'target': 'current',
        }