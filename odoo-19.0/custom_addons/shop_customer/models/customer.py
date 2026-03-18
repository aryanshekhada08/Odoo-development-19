from odoo import models, fields

class Customer(models.Model):
    _name = 'shop.customer'
    _description = 'Shop Customer'

    name = fields.Char("Customer Name", required=True)
    phone = fields.Char("Phone")
    email = fields.Char("Email")
    address = fields.Text("Address")