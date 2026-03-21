from odoo import models, fields, api


class Invoice(models.Model):
    _name = 'shop.invoice'
    _description = 'Shop Invoice'

    name = fields.Char("Invoice Number", default="New")

    sale_id = fields.Many2one('shop.sale', string="Sale Order")

    amount = fields.Float("Total Amount", related='sale_id.total')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
    ], default='draft')

    def action_paid(self):
        for record in self:
            record.state = 'paid'

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('shop.invoice') or 'New'
        return super().create(vals_list)