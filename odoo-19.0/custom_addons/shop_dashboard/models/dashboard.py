from odoo import models, fields, api
import json
from collections import defaultdict

class ShopDashboard(models.Model):
    _name = 'shop.dashboard'
    _description = 'Shop Dashboard'

    total_sales = fields.Integer("Total Orders", compute="_compute_data")
    total_revenue = fields.Float("Total Revenue", compute="_compute_data")
    total_customers = fields.Integer("Total Customers", compute="_compute_data")
    chart_data = fields.Text(compute="_compute_chart_data")
    top_products_data = fields.Text(compute="_compute_top_products")

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


    def _compute_chart_data(self):
            for record in self:

                sales = self.env['shop.sale'].search([])

                monthly_data = defaultdict(float)

                for sale in sales:
                    if sale.create_date:
                        month = sale.create_date.strftime("%b %Y")
                        monthly_data[month] += sale.total

                labels = list(monthly_data.keys())
                values = list(monthly_data.values())

                record.chart_data = json.dumps({
                    'labels': labels,
                    'values': values
                })
    def _compute_top_products(self):
            for record in self:

                product_data = defaultdict(float)

                sales = self.env['shop.sale'].search([])

                for sale in sales:
                    for line in sale.order_line:
                        product_data[line.product_id.name] += line.subtotal

                labels = list(product_data.keys())
                values = list(product_data.values())

                record.top_products_data = json.dumps({
                    'labels': labels,
                    'values': values
                })