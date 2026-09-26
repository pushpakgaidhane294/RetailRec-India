/**
 * Model Performance Controller for RetailRec India.
 * Fetches verified NCF evaluation metrics and plots training loss/accuracy curves.
 */
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const [info, metrics, history] = await Promise.all([
      API.getModelInfo(),
      API.getModelMetrics(),
      API.getModelHistory()
    ]);

    // Update Top KPIs
    if (metrics) {
      document.getElementById("metricTestAcc").textContent = UIUtils.formatPercent(metrics.test_binary_accuracy * 100);
      document.getElementById("metricTestLoss").textContent = UIUtils.formatScore(metrics.test_loss);
      document.getElementById("metricHit5").textContent = UIUtils.formatPercent((metrics.hit_rate_at_5 || 0) * 100);
      document.getElementById("metricHit10").textContent = UIUtils.formatPercent((metrics.hit_rate_at_10 || 0) * 100);
      document.getElementById("metricRecall10").textContent = UIUtils.formatPercent((metrics.recall_at_10 || 0) * 100);
      document.getElementById("metricPrec5").textContent = UIUtils.formatPercent((metrics.precision_at_5 || 0) * 100);
    }

    // Update Split Distribution numbers
    if (info) {
      document.getElementById("splitTrainSamples").textContent = `${UIUtils.formatNumber(info.n_training_samples)} pairs`;
      document.getElementById("splitValSamples").textContent = `${UIUtils.formatNumber(info.n_validation_samples)} pairs`;
      document.getElementById("splitTestSamples").textContent = `${UIUtils.formatNumber(info.n_test_samples)} pairs`;
    }

    // Render Training Curves
    if (history) {
      renderLossChart(history);
      renderAccuracyChart(history);
    }
  } catch (err) {
    console.error("Failed to load model metrics:", err);
  }
});

function renderLossChart(history) {
  const ctx = document.getElementById("lossChart");
  if (!ctx || !history.loss) return;

  const epochs = history.loss.map((_, i) => `Epoch ${i + 1}`);

  new Chart(ctx, {
    type: "line",
    data: {
      labels: epochs,
      datasets: [
        {
          label: "Training Loss",
          data: history.loss,
          borderColor: "#4f46e5",
          backgroundColor: "rgba(79, 70, 229, 0.15)",
          tension: 0.3,
          fill: true,
        },
        {
          label: "Validation Loss",
          data: history.val_loss,
          borderColor: "#ef4444",
          backgroundColor: "transparent",
          borderDash: [5, 5],
          tension: 0.3,
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
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw.toFixed(4)}`
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: "Binary Crossentropy" },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderAccuracyChart(history) {
  const ctx = document.getElementById("accChart");
  if (!ctx || !history.binary_accuracy) return;

  const epochs = history.binary_accuracy.map((_, i) => `Epoch ${i + 1}`);

  new Chart(ctx, {
    type: "line",
    data: {
      labels: epochs,
      datasets: [
        {
          label: "Training Accuracy",
          data: history.binary_accuracy.map(v => v * 100),
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.15)",
          tension: 0.3,
          fill: true,
        },
        {
          label: "Validation Accuracy",
          data: history.val_binary_accuracy.map(v => v * 100),
          borderColor: "#f97316",
          backgroundColor: "transparent",
          borderDash: [5, 5],
          tension: 0.3,
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
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw.toFixed(2)}%`
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: "Accuracy (%)" },
          ticks: { callback: v => v + "%" },
          grid: { color: "rgba(221, 214, 254, 0.5)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}
