from collections import defaultdict
import json

from odoo import api, fields, models


class ShopDashboard(models.Model):
    _name = "shop.dashboard"
    _description = "Shop Dashboard"

    total_sales = fields.Integer("Total Orders", compute="_compute_data")
    total_revenue = fields.Float("Total Revenue", compute="_compute_data")
    total_customers = fields.Integer("Total Customers", compute="_compute_data")
    chart_data = fields.Text(compute="_compute_chart_data")
    top_products_data = fields.Text(compute="_compute_top_products")

    def _compute_data(self):
        for record in self:
            sales = self.env["shop.sale"].search([])
            customers = self.env["shop.customer"].search([])

            record.total_sales = len(sales)
            record.total_customers = len(customers)
            record.total_revenue = sum(sale.total for sale in sales)

    @api.model
    def _get_or_create_dashboard(self):
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({})
        return dashboard

    @api.model
    def action_open_dashboard(self):
        dashboard = self._get_or_create_dashboard()
        return {
            "type": "ir.actions.act_window",
            "name": "Dashboard",
            "res_model": "shop.dashboard",
            "view_mode": "form",
            "res_id": dashboard.id,
            "target": "current",
        }

    def _compute_chart_data(self):
        for record in self:
            sales = self.env["shop.sale"].search([], order="create_date asc")
            monthly_data = defaultdict(float)

            for sale in sales:
                if sale.create_date:
                    month = sale.create_date.strftime("%b %Y")
                    monthly_data[month] += sale.total

            record.chart_data = json.dumps(
                [
                    {
                        "key": "Monthly Sales",
                        "values": [
                            {"label": month, "value": amount, "type": "past"}
                            for month, amount in monthly_data.items()
                        ],
                        "is_sample_data": False,
                    }
                ]
            )

    def _compute_top_products(self):
        for record in self:
            product_data = defaultdict(float)
            sales = self.env["shop.sale"].search([])

            for sale in sales:
                for line in sale.order_line:
                    product_data[line.product_id.name] += line.subtotal

            top_products = sorted(
                product_data.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:5]

            record.top_products_data = json.dumps(
                [
                    {
                        "key": "Top Products",
                        "values": [
                            {"label": product, "value": amount, "type": "past"}
                            for product, amount in top_products
                        ],
                        "is_sample_data": False,
                    }
                ]
            )
