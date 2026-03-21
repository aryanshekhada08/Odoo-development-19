from odoo import models, fields

class StockHistory(models.Model):
        _name = 'shop.stock.history'
        _description = 'Stock History'

        product_id = fields.Many2one('shop.product', string="Product")
        change_qty = fields.Integer("Quantity Change")
        note = fields.Char("Description")
        date = fields.Datetime("Date", default=fields.Datetime.now)