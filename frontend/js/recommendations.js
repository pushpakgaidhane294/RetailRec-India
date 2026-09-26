/**
 * Interactive Recommendation Controller for RetailRec India.
 * Handles customer autocomplete, customer profile retrieval,
 * and NCF inference rendering.
 */
let allCustomersCache = [];

document.addEventListener("DOMContentLoaded", async () => {
  const customerInput = document.getElementById("customerInput");
  const dropdown = document.getElementById("autocompleteDropdown");
  const generateBtn = document.getElementById("generateBtn");

  // Pre-fetch initial customer list for fast autocomplete
  try {
    allCustomersCache = await API.getCustomers("", 336);
  } catch (err) {
    console.warn("Could not pre-fetch customer list:", err);
  }

  // Autocomplete Input Handler
  customerInput.addEventListener("input", (e) => {
    const val = e.target.value.trim().toLowerCase();
    if (!val) {
      dropdown.style.display = "none";
      return;
    }

    const matches = allCustomersCache.filter(c =>
      c.customer_name.toLowerCase().includes(val) ||
      c.customer_id.toLowerCase().includes(val) ||
      c.city.toLowerCase().includes(val) ||
      c.state.toLowerCase().includes(val)
    ).slice(0, 8);

    if (matches.length === 0) {
      dropdown.innerHTML = `<div class="autocomplete-item" style="color: var(--text-muted);">No matching customer found</div>`;
      dropdown.style.display = "block";
      return;
    }

    dropdown.innerHTML = matches.map(c => `
      <div class="autocomplete-item" onclick="selectCustomer('${c.customer_id}', '${c.customer_name.replace(/'/g, "\\'")}')">
        <div>
          <span class="cust-id">${c.customer_id}</span> &bull; <strong>${c.customer_name}</strong>
        </div>
        <span class="cust-loc">${c.city}, ${c.state}</span>
      </div>
    `).join("");

    dropdown.style.display = "block";
  });

  // Close dropdown on click outside
  document.addEventListener("click", (e) => {
    if (!customerInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });

  // Enter key generates recommendations
  customerInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      dropdown.style.display = "none";
      generateRecommendations();
    }
  });

  generateBtn.addEventListener("click", () => {
    dropdown.style.display = "none";
    generateRecommendations();
  });

  // Handle URL query param: ?id=CUST-001
  const urlParams = new URLSearchParams(window.location.search);
  const paramId = urlParams.get("id");
  if (paramId) {
    customerInput.value = paramId;
    generateRecommendations();
  }
});

function selectCustomer(id, name) {
  const input = document.getElementById("customerInput");
  const dropdown = document.getElementById("autocompleteDropdown");
  input.value = `${name} (${id})`;
  dropdown.style.display = "none";
  generateRecommendations();
}

function selectPreset(id) {
  const input = document.getElementById("customerInput");
  input.value = id;
  generateRecommendations();
}

async function generateRecommendations() {
  const inputVal = document.getElementById("customerInput").value.trim();
  const topK = parseInt(document.getElementById("topKSelect").value) || 5;
  const category = document.getElementById("categorySelect").value;
  const excludePurchased = document.getElementById("excludePurchased").checked;

  const alertContainer = document.getElementById("alertContainer");
  const customerCard = document.getElementById("customerSummaryCard");
  const loadingState = document.getElementById("loadingState");
  const recsSection = document.getElementById("recommendationsSection");
  const initialState = document.getElementById("initialState");
  const recsGrid = document.getElementById("recommendationsGrid");

  alertContainer.innerHTML = "";

  if (!inputVal) {
    showAlert("Please enter or select a Customer ID or name to generate recommendations.", "warning");
    return;
  }

  // UI state: loading
  initialState.style.display = "none";
  recsSection.style.display = "none";
  loadingState.style.display = "block";

  try {
    // 1. Fetch recommendations from NCF backend
    const res = await API.getRecommendations(inputVal, topK, category, excludePurchased);

    loadingState.style.display = "none";

    // 2. Render Customer Profile Card
    if (res.customer_summary) {
      renderCustomerSummary(res.customer_summary);
      customerCard.style.display = "block";
    } else {
      customerCard.style.display = "none";
    }

    // 3. Handle Warnings & Cold Start
    if (res.fallback_used) {
      showAlert(
        `<strong>Cold Start Fallback:</strong> Customer "${inputVal}" was not found in the historical training set. Displaying popular products as an explicitly labelled fallback.`,
        "warning"
      );
    } else if (res.warning) {
      showAlert(`<strong>Advisory:</strong> ${res.warning}`, "warning");
    }

    // 4. Update Header & Meta
    const titleEl = document.getElementById("recsTitle");
    const metaEl = document.getElementById("recommendationMeta");

    titleEl.textContent = res.fallback_used
      ? `📦 Popular Items Fallback for "${res.customer_name}"`
      : `🎯 Personalized Recommendations for ${res.customer_name} (${res.customer_id})`;

    metaEl.innerHTML = `Model: <strong>${res.model_type}</strong> &bull; Evaluated: <strong>${res.total_candidates_evaluated} candidates</strong> (Excluded ${res.excluded_purchased_count} previously purchased)`;

    // 5. Render Recommendation Cards
    if (!res.recommendations || res.recommendations.length === 0) {
      recsGrid.innerHTML = `
        <div class="state-box" style="grid-column: 1 / -1;">
          <h4>No Candidate Items Match the Filters</h4>
          <p class="state-desc">Try choosing "All Categories" or unchecking "Exclude previously purchased items".</p>
        </div>
      `;
    } else {
      recsGrid.innerHTML = res.recommendations.map(item => `
        <div class="rec-card">
          <div class="rec-card-top">
            <div class="rec-rank-badge">#${item.rank}</div>
            <span class="rec-status-badge ${item.is_fallback ? 'fallback' : 'ai'}">
              ${item.badge}
            </span>
          </div>

          <div>
            <h4 class="rec-item-title">${item.sub_category}</h4>
            <span class="rec-item-category">Category: ${item.category}</span>
          </div>

          <div class="rec-details-row">
            <div>
              <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Avg Line Price</div>
              <div class="rec-price">${UIUtils.formatINR(item.avg_price)}</div>
            </div>

            <div class="rec-score-box">
              <div class="rec-score-label">${item.score_label}</div>
              <div class="rec-score-val">${UIUtils.formatScore(item.model_score)}</div>
            </div>
          </div>
        </div>
      `).join("");
    }

    recsSection.style.display = "block";
  } catch (err) {
    loadingState.style.display = "none";
    showAlert(`Error generating recommendations: ${err.message}`, "warning");
    console.error("Recommendation failure:", err);
  }
}

function renderCustomerSummary(cust) {
  const card = document.getElementById("customerSummaryCard");
  card.innerHTML = `
    <div class="cust-summary-header">
      <div>
        <div class="cust-summary-name">${cust.customer_name} <span style="font-size: 0.95rem; font-weight: 600; color: #0284c7;">(${cust.customer_id})</span></div>
        <div style="font-size: 0.85rem; color: #475569;">📍 ${cust.city}, ${cust.state}</div>
      </div>
      <div>
        <a href="/history?id=${cust.customer_id}" class="btn btn-outline btn-sm" style="background: #ffffff;">
          View Full History (${cust.total_orders} Orders) →
        </a>
      </div>
    </div>

    <div class="cust-metrics-grid">
      <div class="cust-metric-item">
        <div class="cust-metric-label">Total Orders</div>
        <div class="cust-metric-val">${cust.total_orders}</div>
      </div>
      <div class="cust-metric-item">
        <div class="cust-metric-label">Total Spending</div>
        <div class="cust-metric-val">${UIUtils.formatINR(cust.total_spending)}</div>
      </div>
      <div class="cust-metric-item">
        <div class="cust-metric-label">Units Bought</div>
        <div class="cust-metric-val">${cust.total_quantity}</div>
      </div>
      <div class="cust-metric-item">
        <div class="cust-metric-label">Unique Items</div>
        <div class="cust-metric-val">${cust.unique_items} / 17</div>
      </div>
      <div class="cust-metric-item">
        <div class="cust-metric-label">Avg Order Value</div>
        <div class="cust-metric-val">${UIUtils.formatINR(cust.average_order_value)}</div>
      </div>
      <div class="cust-metric-item">
        <div class="cust-metric-label">Last Purchase</div>
        <div class="cust-metric-val" style="font-size: 0.95rem;">${cust.last_purchase_date}</div>
      </div>
    </div>
  `;
}

function showAlert(message, type = "info") {
  const container = document.getElementById("alertContainer");
  const icon = type === "warning" ? "⚠️" : "ℹ️";
  container.innerHTML = `
    <div class="alert alert-${type}">
      <span class="alert-icon">${icon}</span>
      <div>${message}</div>
    </div>
  `;
}
