/**
 * Dashboard Controller for RetailRec India.
 * Fetches genuine KPIs and renders Chart.js visualizations.
 */
document.addEventListener("DOMContentLoaded", async () => {
  // Check Health
  try {
    const health = await API.getHealth();
    const navText = document.getElementById("navStatusText");
    if (navText && health.model_loaded) {
      navText.textContent = "NCF Model Online";
    }
  } catch (e) {
    console.warn("Health check error:", e);
  }

  // Load KPI Stats
  try {
    const stats = await API.getStats();
    if (stats) {
      document.getElementById("kpiCustomers").textContent = UIUtils.formatNumber(stats.total_customers);
      document.getElementById("kpiOrders").textContent = UIUtils.formatNumber(stats.total_orders);
      document.getElementById("kpiSales").textContent = UIUtils.formatINR(stats.total_sales);
      document.getElementById("kpiQuantity").textContent = UIUtils.formatNumber(stats.total_quantity);
      document.getElementById("kpiProfit").textContent = UIUtils.formatINR(stats.total_profit);
      document.getElementById("kpiAOV").textContent = UIUtils.formatINR(stats.average_order_value);
    }
  } catch (err) {
    console.error("Failed to load dashboard stats:", err);
  }

  // Load Analytics Charts
  try {
    const analytics = await API.getAnalytics();
    if (analytics) {
      renderMonthlyChart(analytics.monthly_trends);
      renderCategoryChart(analytics.category_distribution);
      renderStateChart(analytics.state_distribution);
      renderPaymentChart(analytics.payment_distribution);
    }
  } catch (err) {
    console.error("Failed to load analytics charts:", err);
  }
});

function renderMonthlyChart(data) {
  const ctx = document.getElementById("monthlyChart");
  if (!ctx || !data) return;

  const labels = data.map(d => d.month_name || d.month_year || ('Month ' + d.month));
  const sales = data.map(d => d.sales);
  const profit = data.map(d => d.profit);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Sales (₹)",
          data: sales,
          backgroundColor: "rgba(79, 70, 229, 0.85)",
          borderRadius: 6,
          order: 2,
        },
        {
          label: "Profit (₹)",
          data: profit,
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.18)",
          type: "line",
          tension: 0.3,
          fill: true,
          order: 1,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top", labels: { boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${UIUtils.formatINR(ctx.raw)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: (v) => "₹" + (v >= 1000 ? (v / 1000) + "k" : v)
          },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderCategoryChart(data) {
  const ctx = document.getElementById("categoryChart");
  if (!ctx) return;

  const labels = data.map(d => d.category);
  const sales = data.map(d => d.sales);

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: sales,
        backgroundColor: [
          "#4f46e5",
          "#f97316",
          "#10b981"
        ],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { boxWidth: 14 } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${UIUtils.formatINR(ctx.raw)}`
          }
        }
      },
      cutout: "68%"
    }
  });
}

function renderStateChart(data) {
  const ctx = document.getElementById("stateChart");
  if (!ctx) return;

  const topStates = data.slice(0, 7);
  const labels = topStates.map(d => d.state);
  const sales = topStates.map(d => d.sales);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Sales (₹)",
        data: sales,
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
          ticks: {
            callback: (v) => "₹" + (v >= 1000 ? (v / 1000) + "k" : v)
          },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        y: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderPaymentChart(data) {
  const ctx = document.getElementById("paymentChart");
  if (!ctx || !data) return;

  const labels = data.map(d => d.payment_mode);
  const counts = data.map(d => d.count);

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: [
          "#f97316",
          "#4f46e5",
          "#10b981",
          "#06b6d4",
          "#f59e0b"
        ],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: {
            boxWidth: 12,
            padding: 10,
            font: { size: 11 }
          }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const item = data[ctx.dataIndex];
              return ` ${ctx.label}: ${ctx.raw} orders (${item.percentage}% • ${UIUtils.formatINR(item.total_amount)})`;
            }
          }
        }
      },
      cutout: "64%"
    }
  });
}
