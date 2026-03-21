from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Sale(models.Model):
    _name = 'shop.sale'
    _description = 'Shop Sale'

    name = fields.Char("Order Reference", default="New")

    customer_id = fields.Many2one('shop.customer', string="Customer")

    order_line = fields.One2many('shop.sale.line', 'sale_id', string="Order Lines")

    total = fields.Float("Total", compute="_compute_total")
    invoice_count = fields.Integer("Invoice Count", compute="_compute_invoice_count")
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
    
    def action_create_invoice(self):
        for record in self:
            invoice = self.env['shop.invoice'].create({
                'sale_id': record.id,
            })

    def _compute_invoice_count(self):
        for record in self:
            count = self.env['shop.invoice'].search_count([
                ('sale_id', '=', record.id)
            ])
            record.invoice_count = count

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'shop.invoice',
            'view_mode': 'list,form',
            'domain': [('sale_id', '=', self.id)],
        }
    def action_done(self):
        for record in self:

            if record.state == 'done':
                continue

            for line in record.order_line:

                if line.product_id.quantity < line.quantity:
                    raise ValidationError(f"Not enough stock for {line.product_id.name}")

                # Reduce stock
                line.product_id.quantity -= line.quantity

                # 🔥 CREATE HISTORY
                self.env['shop.stock.history'].create({
                    'product_id': line.product_id.id,
                    'change_qty': -line.quantity,
                    'note': f"Sold in Order {record.name}"
                })

            record.state = 'done'
    def action_cancel(self):
        for record in self:

            if record.state == 'done':
                for line in record.order_line:

                    # Restore stock
                    line.product_id.quantity += line.quantity

                    # 🔥 CREATE HISTORY
                    self.env['shop.stock.history'].create({
                        'product_id': line.product_id.id,
                        'change_qty': line.quantity,
                        'note': f"Restored from Cancel {record.name}"
                    })

            record.state = 'cancel'