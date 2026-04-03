from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'name'

    partner_id = fields.Many2one(
        'res.partner',
        string="Related Partner",
        required=True,
        ondelete='restrict'
    )

    membership_number = fields.Char("Membership Number", readonly=True)
    membership_date = fields.Date("Member Since", default=fields.Date.today)
    expiry_date = fields.Date("Expiry Date")

    total_borrowed = fields.Integer("Total Books Borrowed", default=0)
    active_borrows = fields.Integer("Currently Borrowed", compute="_compute_active_borrows")

    is_blocked = fields.Boolean("Blocked", default=False)
    block_reason = fields.Char("Block Reason")

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('blocked', 'Blocked'),
    ], default='active', string="Status")

    def _compute_active_borrows(self):
        for record in self:
            record.active_borrows = self.env['library.borrow'].search_count([
                ('member_id', '=', record.id),
                ('state', '=', 'borrowed'),
            ])

    @api.constrains('expiry_date', 'membership_date')
    def _check_dates(self):
        for record in self:
            if record.expiry_date and record.membership_date:
                if record.expiry_date < record.membership_date:
                    raise ValidationError("Expiry date cannot be before membership date!")

    def action_block(self):
        for record in self:
            record.is_blocked = True
            record.state = 'blocked'

    def action_unblock(self):
        for record in self:
            record.is_blocked = False
            record.state = 'active'

    @api.model
    def create(self, vals):
        vals['membership_number'] = self.env['ir.sequence'].next_by_code('library.member') or 'New'
        return super().create(vals)