from odoo import models, fields, api


class ShopDashboard(models.Model):
    _name = 'shop.dashboard'
    _description = 'Shop Dashboard'

    total_sales = fields.Integer("Total Orders", compute="_compute_data")
    total_revenue = fields.Float("Total Revenue", compute="_compute_data")
    total_customers = fields.Integer("Total Customers", compute="_compute_data")

    def _compute_data(self):
        for record in self:
            sales = self.env['shop.sale'].search([])
            customers = self.env['shop.customer'].search([])

            record.total_sales = len(sales)
            record.total_customers = len(customers)
            record.total_revenue = sum(s.total for s in sales)

    @api.model
    def create_dashboard(self):
        if not self.search([]):
            self.create({})