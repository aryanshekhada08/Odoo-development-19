from odoo import models, fields

class Product(models.Model):
    _name = 'shop.product'
    _description = 'Shop Product'

    name = fields.Char("Product Name", required=True)
    price = fields.Float("Price")
    quantity = fields.Integer("Stock Quantity")
    category = fields.Selection([
        ('food', 'Food'),
        ('electronics', 'Electronics'),
        ('clothes', 'Clothes'),
    ], string="Category")