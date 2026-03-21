from odoo import models, fields, api

class ShopDashboard(models.Model):   # changed from TransientModel
    _name = 'shop.dashboard'
    _description = 'Shop Dashboard'

    total_sales = fields.Integer("Total Orders")
    total_revenue = fields.Float("Total Revenue")
    total_customers = fields.Integer("Total Customers")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        sales = self.env['shop.sale'].search([]) if 'shop.sale' in self.env else []
        customers = self.env['shop.customer'].search([]) if 'shop.customer' in self.env else []

        res.update({
            'total_sales': len(sales),
            'total_customers': len(customers),
            'total_revenue': sum(s.total for s in sales) if sales else 0,
        })

        return res
    

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        try:
            sales = self.env['shop.sale'].search([])
            total_sales = len(sales)
            total_revenue = sum(s.total for s in sales)
        except:
            total_sales = 0
            total_revenue = 0

        try:
            customers = self.env['shop.customer'].search([])
            total_customers = len(customers)
        except:
            total_customers = 0

        res.update({
            'total_sales': total_sales,
            'total_customers': total_customers,
            'total_revenue': total_revenue,
        })

        return res