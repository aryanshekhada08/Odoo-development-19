from odoo import models, fields, api

class Sale(models.Model):
    _name = 'shop.sale'
    _description = 'Shop Sale'

    customer_id = fields.Many2one('shop.customer', string="Customer")
    product_id = fields.Many2one('shop.product', string="Product")
    quantity = fields.Integer("Quantity", default=1)
    price = fields.Float("Price", related='product_id.price')
    total = fields.Float("Total", compute="_compute_total")

    @api.depends('quantity', 'price')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity * record.price