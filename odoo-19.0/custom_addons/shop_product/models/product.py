from odoo import models, fields

class Product(models.Model):
    _name = 'shop.product'
    _description = 'Shop Product'

    name = fields.Char("Product Name", required=True)
    price = fields.Float("Price")
    quantity = fields.Integer("Stock Quantity", default=0)
    category = fields.Selection([
        ('food', 'Food'),
        ('electronics', 'Electronics'),
        ('clothes', 'Clothes'),
    ], string="Category")

    is_out_of_stock = fields.Boolean(compute="_compute_stock_status")

    def _compute_stock_status(self):
      for record in self:
         record.is_out_of_stock = record.quantity <= 0