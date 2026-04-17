from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

class LibraryFine(models.Model):
    _name = 'library.fine'
    _description = 'Library Fine'
    _inherit = ['mail.thread']
    _rec_name = 'reference'

    reference = fields.Char("Reference", readonly=True, default="New")

    borrow_id = fields.Many2one(
        'library.borrow',
        string="Borrow Reference",
        required=True,
        ondelete='cascade'
    )

    member_id = fields.Many2one(
        'library.member',
        string="Member",
        required=True
    )

    amount = fields.Float("Fine Amount", required=True)

    paid_amount = fields.Float("Paid Amount", default=0.0)

    remaining_amount = fields.Float(
        "Remaining Amount",
        compute="_compute_remaining",
        store=True
    )

    state = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], default='unpaid', string="Status", tracking=True)

    payment_date = fields.Date("Payment Date")
    notes = fields.Text("Notes")

    def _check_manager_access(self):
        if not self.env.user.has_group('library_management.group_library_manager'):
            raise AccessError("Only library managers can perform this action.")

    # ─── Compute ───────────────────────────────────────

    @api.depends('amount', 'paid_amount')
    def _compute_remaining(self):
        for record in self:
            record.remaining_amount = record.amount - record.paid_amount

    # ─── Constraints ───────────────────────────────────

    @api.constrains('paid_amount')
    def _check_paid_amount(self):
        for record in self:
            if record.paid_amount < 0:
                raise ValidationError("Paid amount cannot be negative!")
            if record.paid_amount > record.amount:
                raise ValidationError("Paid amount cannot exceed fine amount!")

    # ─── Business Logic ────────────────────────────────

    def action_pay_full(self):
        self._check_manager_access()
        for record in self:
            record.paid_amount = record.amount
            record.state = 'paid'
            record.payment_date = fields.Date.today()
            record.message_post(
                body=f"Fine of {record.amount} fully paid on {record.payment_date}."
            )

            # unblock member if they were blocked due to fines
            unpaid_fines = self.search_count([
                ('member_id', '=', record.member_id.id),
                ('state', '!=', 'paid'),
            ])
            if unpaid_fines == 0:
                record.member_id.action_unblock()

    def action_pay_partial(self, amount):
        self._check_manager_access()
        for record in self:
            record.paid_amount += amount
            if record.remaining_amount <= 0:
                record.state = 'paid'
                record.payment_date = fields.Date.today()
            else:
                record.state = 'partial'
            record.message_post(
                body=f"Partial payment of {amount} received. Remaining: {record.remaining_amount}"
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('library.fine') or 'New'
            member = self.env['library.member'].browse(vals.get('member_id'))
            if member:
                member.action_block()
                member.block_reason = "Unpaid fine"
        return super().create(vals_list)
