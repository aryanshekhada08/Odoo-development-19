import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


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

    def _check_manager_access(self):
        if not self.env.user.has_group('library_management.group_library_manager'):
            raise AccessError("Only library managers can perform this action.")

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
                record.days_overdue = max((today - record.due_date).days, 0)
            else:
                record.days_overdue = 0

    @api.depends('days_overdue')
    def _compute_fine_amount(self):
        for record in self:
            record.fine_amount = record.days_overdue * 5.0

    @api.constrains('member_id')
    def _check_member_blocked(self):
        for record in self:
            if record.member_id.is_blocked:
                raise ValidationError(
                    f"Member {record.member_id.name} is blocked and cannot borrow books!"
                )

    def _apply_borrow_updates(self):
        for record in self:
            if record.book_id.available_copies <= 0:
                raise ValidationError(
                    f"No copies of '{record.book_id.title}' are available!"
                )
            record.book_id.available_copies -= 1
            record.book_id.borrow_count += 1
            record.member_id.total_borrowed += 1

    def _apply_return_updates(self):
        for record in self:
            if not record.return_date:
                record.return_date = fields.Date.today()
            record.book_id.available_copies += 1

    def _send_email_from_template(self, template_xmlid):
        for record in self:
            recipient_email = record.member_id.email or record.member_id.partner_id.email
            if not recipient_email:
                continue
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
            if not template:
                continue
            try:
                template.send_mail(
                    record.id,
                    force_send=True,
                    email_values={'email_to': recipient_email},
                )
            except Exception:
                _logger.exception(
                    "Failed to send template %s for borrow %s",
                    template_xmlid,
                    record.id,
                )

    def action_borrow(self):
        self._check_manager_access()
        for record in self:
            record._apply_borrow_updates()
            record.with_context(skip_state_transition_hooks=True).write({'state': 'borrowed'})
            record.message_post(
                body=f"Book '{record.book_id.title}' borrowed by {record.member_id.name}. Due: {record.due_date}"
            )
            record._send_email_from_template('library_management.email_template_borrow_confirm')

    def action_return(self):
        self._check_manager_access()
        for record in self:
            record._apply_return_updates()

            if record.days_overdue > 0:
                self.env['library.fine'].create({
                    'borrow_id': record.id,
                    'member_id': record.member_id.id,
                    'amount': record.fine_amount,
                })
                record.with_context(skip_state_transition_hooks=True).write({'state': 'overdue'})
                record.message_post(
                    body=f"Book returned {record.days_overdue} day(s) late. Fine of {record.fine_amount} created automatically."
                )
                record._send_email_from_template('library_management.email_template_fine_notify')
            else:
                record.with_context(skip_state_transition_hooks=True).write({'state': 'returned'})
                record.message_post(
                    body=f"Book '{record.book_id.title}' returned on time by {record.member_id.name}."
                )

    def action_cancel(self):
        self._check_manager_access()
        for record in self:
            if record.state != 'draft':
                raise ValidationError("Only draft borrows can be cancelled.")
            record.unlink()
        return True

    def action_mark_overdue(self):
        self._check_manager_access()
        overdue_borrows = self.search([
            ('state', '=', 'borrowed'),
            ('due_date', '<', fields.Date.today()),
        ])
        for record in overdue_borrows:
            record.write({'state': 'overdue'})
            record.message_post(
                body=f"Automatically marked overdue. {record.days_overdue} day(s) past due date."
            )
            record._send_email_from_template('library_management.email_template_overdue_notify')

    def write(self, vals):
        if 'state' in vals and not self.env.context.get('skip_state_transition_hooks'):
            new_state = vals['state']
            for record in self:
                old_state = record.state

                if old_state == 'draft' and new_state == 'borrowed':
                    record._apply_borrow_updates()
                    record.message_post(
                        body=f"Book '{record.book_id.title}' borrowed via kanban."
                    )
                    record._send_email_from_template('library_management.email_template_borrow_confirm')
                elif old_state in ('borrowed', 'overdue') and new_state == 'returned':
                    record._apply_return_updates()
                    record.message_post(
                        body=f"Book '{record.book_id.title}' returned via kanban."
                    )

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('library.borrow') or 'New'
        return super().create(vals_list)

    def action_view_fines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fines',
            'res_model': 'library.fine',
            'view_mode': 'list,form',
            'domain': [('borrow_id', '=', self.id)],
        }
