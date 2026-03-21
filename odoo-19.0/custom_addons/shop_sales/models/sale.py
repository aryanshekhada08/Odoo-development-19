from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Sale(models.Model):
    _name = 'shop.sale'
    _description = 'Shop Sale'

    name = fields.Char("Order Reference", default="New")

    customer_id = fields.Many2one('shop.customer', string="Customer")

    order_line = fields.One2many('shop.sale.line', 'sale_id', string="Order Lines")

    total = fields.Float("Total", compute="_compute_total")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status")

    @api.depends('order_line.subtotal')
    def _compute_total(self):
        for record in self:
            record.total = sum(line.subtotal for line in record.order_line)

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('shop.sale') or 'New'
        return super().create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'


    def action_done(self):
        for record in self:
            record.state = 'done'


    def action_cancel(self):
        for record in self:
            record.state = 'cancel'


    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("You can only delete Draft orders!")
        return super().unlink()