/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class DashboardChart extends Component {
    mounted() {
        const data = JSON.parse(this.props.data || "{}");

        const ctx = this.el.querySelector("#myChart");

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Monthly Sales',
                    data: data.values || [],
                    borderWidth: 1
                }]
            },
        });
    }
}

DashboardChart.template = "shop_dashboard.ChartTemplate";

registry.category("actions").add("dashboard_chart", DashboardChart);