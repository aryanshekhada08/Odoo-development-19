from odoo import models, fields, api


class SaleLine(models.Model):
    _name = 'shop.sale.line'
    _description = 'Shop Sale Line'

    sale_id = fields.Many2one('shop.sale', string="Sale Order", ondelete="cascade")
    product_id = fields.Many2one('shop.product', string="Product")
    quantity = fields.Integer("Quantity", default=1)
    price = fields.Float("Price", related='product_id.price')
    subtotal = fields.Float("Subtotal", compute="_compute_subtotal")

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price