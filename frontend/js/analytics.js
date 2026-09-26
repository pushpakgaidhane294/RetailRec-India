/**
 * Analytics Page Controller for RetailRec India.
 * Renders in-depth sales charts and categorized data tables.
 */
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const data = await API.getAnalytics();
    if (!data) return;

    // Update KPI numbers
    if (data.kpi_summary) {
      document.getElementById("analyticsSales").textContent = UIUtils.formatINR(data.kpi_summary.total_sales);
      document.getElementById("analyticsProfit").textContent = UIUtils.formatINR(data.kpi_summary.total_profit);
      document.getElementById("analyticsOrders").textContent = UIUtils.formatNumber(data.kpi_summary.total_orders);
      document.getElementById("analyticsAov").textContent = UIUtils.formatINR(data.kpi_summary.average_order_value);
    }

    // Render Charts
    renderMonthlyAnalyticsChart(data.monthly_trends);
    renderCategoryAnalyticsChart(data.category_distribution);
    renderStateAnalyticsChart(data.state_distribution);
    renderPaymentAnalyticsChart(data.payment_distribution);

    // Render Tables
    renderCategoryTable(data.category_distribution);
    renderTopSubcatTable(data.top_subcategories);
  } catch (err) {
    console.error("Failed to load analytics:", err);
  }
});

function renderMonthlyAnalyticsChart(data) {
  const ctx = document.getElementById("analyticsMonthlyChart");
  if (!ctx || !data) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map(d => d.month_name || d.month_year || ('M' + d.month)),
      datasets: [
        {
          label: "Gross Sales (₹)",
          data: data.map(d => d.sales),
          backgroundColor: "rgba(79, 70, 229, 0.85)",
          borderRadius: 6,
          order: 2,
        },
        {
          label: "Net Profit (₹)",
          data: data.map(d => d.profit),
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.18)",
          type: "line",
          tension: 0.35,
          fill: true,
          order: 1,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${UIUtils.formatINR(ctx.raw)}`
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: (v) => "₹" + (v >= 1000 ? (v / 1000) + "k" : v)
          },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderCategoryAnalyticsChart(data) {
  const ctx = document.getElementById("analyticsCategoryChart");
  if (!ctx || !data) return;

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: data.map(d => d.category),
      datasets: [{
        data: data.map(d => d.sales),
        backgroundColor: ["#4f46e5", "#f97316", "#10b981"],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${UIUtils.formatINR(ctx.raw)} (${data[ctx.dataIndex].percentage}%)`
          }
        }
      }
    }
  });
}

function renderStateAnalyticsChart(data) {
  const ctx = document.getElementById("analyticsStateChart");
  if (!ctx || !data) return;

  const topStates = data.slice(0, 8);
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: topStates.map(d => d.state),
      datasets: [{
        label: "Sales (₹)",
        data: topStates.map(d => d.sales),
        backgroundColor: "rgba(79, 70, 229, 0.85)",
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Sales: ${UIUtils.formatINR(ctx.raw)}`
          }
        }
      },
      scales: {
        x: {
          ticks: { callback: (v) => "₹" + (v >= 1000 ? (v / 1000) + "k" : v) },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        y: { grid: { display: false } }
      }
    }
  });
}

function renderPaymentAnalyticsChart(data) {
  const ctx = document.getElementById("analyticsPaymentChart");
  if (!ctx || !data) return;

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.map(d => d.payment_mode),
      datasets: [{
        data: data.map(d => d.total_amount),
        backgroundColor: [
          "#f97316",
          "#4f46e5",
          "#10b981",
          "#06b6d4",
          "#f59e0b"
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${UIUtils.formatINR(ctx.raw)} (${data[ctx.dataIndex].percentage}%)`
          }
        }
      },
      cutout: "60%"
    }
  });
}

function renderCategoryTable(data) {
  const tbody = document.getElementById("categoryTableBody");
  if (!tbody || !data) return;

  tbody.innerHTML = data.map(c => `
    <tr>
      <td><strong>${c.category}</strong></td>
      <td>${UIUtils.formatINR(c.sales)}</td>
      <td style="color: ${c.profit >= 0 ? '#16a34a' : '#dc2626'}; font-weight: 600;">
        ${UIUtils.formatINR(c.profit)}
      </td>
      <td>${UIUtils.formatNumber(c.quantity)} units</td>
      <td>
        <span class="preset-pill" style="cursor: default; background: #e0f2fe; color: #0369a1; border-color: #bae6fd;">
          ${c.percentage}%
        </span>
      </td>
    </tr>
  `).join("");
}

function renderTopSubcatTable(data) {
  const tbody = document.getElementById("topSubcatTableBody");
  if (!tbody || !data) return;

  tbody.innerHTML = data.map((item, idx) => `
    <tr>
      <td><strong>#${idx + 1}</strong></td>
      <td><strong>${item.sub_category}</strong></td>
      <td><span class="preset-pill" style="cursor: default;">${item.category}</span></td>
      <td><strong>${UIUtils.formatINR(item.total_sales)}</strong></td>
      <td>${UIUtils.formatNumber(item.total_quantity_sold)}</td>
      <td>${UIUtils.formatINR(item.avg_price)}</td>
      <td>${item.customer_count}</td>
    </tr>
  `).join("");
}
