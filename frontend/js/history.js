/**
 * Customer History Controller for RetailRec India.
 * Loads and displays authentic purchase transaction records
 * with complete 336 customer catalog browsing and real-time filtering.
 */
let currentPage = 1;
let currentCustomerId = "CUST-001";
const pageSize = 100;
let allCustomersList = [];

function resolveCustIdFromInput(val) {
  if (!val) return "";
  const match = val.match(/\b(CUST-\d{3,4})\b/i);
  if (match) return match[1].toUpperCase();
  return val.trim();
}

document.addEventListener("DOMContentLoaded", async () => {
  const inputEl = document.getElementById("historyCustInput");
  const dropdownEl = document.getElementById("historyAutocompleteDropdown");
  const selectPickerEl = document.getElementById("historyCustomerSelect");
  const viewBtn = document.getElementById("viewHistoryBtn");
  const catSelect = document.getElementById("historyCategorySelect");
  const searchInput = document.getElementById("historySearchInput");
  const recBtn = document.getElementById("recommendForThisCustBtn");

  // 1. Fetch all 336 customers to populate dropdown & enable autocomplete
  try {
    allCustomersList = await API.getCustomers("", 350);
    if (selectPickerEl && allCustomersList.length > 0) {
      allCustomersList.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.customer_id;
        opt.textContent = `${c.customer_id}: ${c.customer_name} (${c.city}, ${c.state}) - ₹${c.total_spending}`;
        selectPickerEl.appendChild(opt);
      });
    }
  } catch (err) {
    console.warn("Could not load full customer list for dropdown:", err);
  }

  // 2. Check URL query param: ?id=CUST-001 or ?id=Harivansh
  const urlParams = new URLSearchParams(window.location.search);
  const paramId = urlParams.get("id");
  if (paramId) {
    const resolved = resolveCustIdFromInput(paramId);
    if (inputEl) inputEl.value = paramId;
    currentCustomerId = resolved || paramId;
    if (selectPickerEl) selectPickerEl.value = resolved || paramId;
  }

  // 3. Dropdown select change handler
  if (selectPickerEl) {
    selectPickerEl.addEventListener("change", (e) => {
      if (e.target.value) {
        if (inputEl) inputEl.value = e.target.value;
        currentCustomerId = e.target.value;
        currentPage = 1;
        loadHistory();
      }
    });
  }

  // 4. Autocomplete input handler
  if (inputEl && dropdownEl) {
    inputEl.addEventListener("input", (e) => {
      const val = e.target.value.trim().toLowerCase();
      if (!val) {
        dropdownEl.style.display = "none";
        return;
      }

      const matches = allCustomersList.filter(c =>
        c.customer_name.toLowerCase().includes(val) ||
        c.customer_id.toLowerCase().includes(val) ||
        c.city.toLowerCase().includes(val) ||
        c.state.toLowerCase().includes(val)
      ).slice(0, 8);

      if (matches.length === 0) {
        dropdownEl.innerHTML = `<div class="autocomplete-item" style="color: var(--text-muted);">No matching customer found</div>`;
        dropdownEl.style.display = "block";
        return;
      }

      dropdownEl.innerHTML = matches.map(c => `
        <div class="autocomplete-item" onclick="selectHistoryCustomer('${c.customer_id}', '${c.customer_name.replace(/'/g, "\\'")}')">
          <div>
            <span class="cust-id">${c.customer_id}</span> &bull; <strong>${c.customer_name}</strong>
          </div>
          <span class="cust-loc">${c.city}, ${c.state} (₹${c.total_spending})</span>
        </div>
      `).join("");

      dropdownEl.style.display = "block";
    });

    // Close dropdown on click outside
    document.addEventListener("click", (e) => {
      if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
        dropdownEl.style.display = "none";
      }
    });

    // Enter key handler on search & input
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        dropdownEl.style.display = "none";
        currentPage = 1;
        currentCustomerId = resolveCustIdFromInput(inputEl.value);
        loadHistory();
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        currentPage = 1;
        loadHistory();
      }
    });

    searchInput.addEventListener("input", debounce(() => {
      currentPage = 1;
      loadHistory();
    }, 250));
  }

  // 5. View button click
  if (viewBtn) {
    viewBtn.addEventListener("click", () => {
      if (dropdownEl) dropdownEl.style.display = "none";
      currentPage = 1;
      const rawVal = inputEl ? inputEl.value : "";
      currentCustomerId = resolveCustIdFromInput(rawVal);
      loadHistory();
    });
  }

  // 6. Filter change handlers
  if (catSelect) {
    catSelect.addEventListener("change", () => {
      currentPage = 1;
      loadHistory();
    });
  }

  // 7. Recommend button
  if (recBtn) {
    recBtn.addEventListener("click", () => {
      window.location.href = `/recommendations?id=${encodeURIComponent(currentCustomerId)}`;
    });
  }

  // Initial load
  loadHistory();
});

function selectHistoryCustomer(id, name) {
  const inputEl = document.getElementById("historyCustInput");
  const dropdownEl = document.getElementById("historyAutocompleteDropdown");
  const selectPickerEl = document.getElementById("historyCustomerSelect");

  if (inputEl) inputEl.value = `${name} (${id})`;
  currentCustomerId = id;
  if (selectPickerEl) selectPickerEl.value = id;
  if (dropdownEl) dropdownEl.style.display = "none";
  currentPage = 1;
  loadHistory();
}

function loadCustomerHistoryPreset(id) {
  const inputEl = document.getElementById("historyCustInput");
  const selectPickerEl = document.getElementById("historyCustomerSelect");

  if (inputEl) inputEl.value = id;
  currentCustomerId = id;
  if (selectPickerEl) selectPickerEl.value = id;
  currentPage = 1;
  loadHistory();
}

async function loadHistory() {
  const alertEl = document.getElementById("historyAlert");
  const cardEl = document.getElementById("historyCard");
  const loadingEl = document.getElementById("historyLoadingState");
  const tbodyEl = document.getElementById("historyTableBody");
  const custOverview = document.getElementById("historyCustomerOverview");
  const subtitleEl = document.getElementById("historyTableSubtitle");

  if (alertEl) alertEl.innerHTML = "";

  if (!currentCustomerId) {
    showAlert("Please enter or select a valid Customer ID or Name.", "warning");
    return;
  }

  const catEl = document.getElementById("historyCategorySelect");
  const searchEl = document.getElementById("historySearchInput");
  const category = catEl ? catEl.value : "all";
  const search = searchEl ? searchEl.value.trim() : "";

  // Show loading
  if (loadingEl) loadingEl.style.display = "block";
  if (cardEl) cardEl.style.display = "none";

  try {
    // 1. Fetch customer summary profile
    try {
      const cust = await API.getCustomer(currentCustomerId);
      if (cust && custOverview) {
        custOverview.style.display = "block";
        custOverview.innerHTML = `
          <div class="cust-summary-header">
            <div>
              <div class="cust-summary-name">${cust.customer_name} <span style="font-size: 0.95rem; font-weight: 600; color: #4f46e5;">(${cust.customer_id})</span></div>
              <div style="font-size: 0.85rem; color: #6b7280;">📍 ${cust.city}, ${cust.state}</div>
            </div>
            <div>
              <a href="/recommendations?id=${cust.customer_id}" class="btn btn-primary btn-sm">
                ⚡ Generate AI Recommendations for ${cust.customer_name} →
              </a>
            </div>
          </div>
          <div class="cust-metrics-grid">
            <div class="cust-metric-item">
              <div class="cust-metric-label">Total Orders</div>
              <div class="cust-metric-val">${cust.total_orders}</div>
            </div>
            <div class="cust-metric-item">
              <div class="cust-metric-label">Total Spend</div>
              <div class="cust-metric-val">${UIUtils.formatINR(cust.total_spending)}</div>
            </div>
            <div class="cust-metric-item">
              <div class="cust-metric-label">Units Bought</div>
              <div class="cust-metric-val">${cust.total_quantity}</div>
            </div>
            <div class="cust-metric-item">
              <div class="cust-metric-label">Unique Products</div>
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
      } else if (custOverview) {
        custOverview.style.display = "none";
      }
    } catch (_) {
      if (custOverview) custOverview.style.display = "none";
    }

    // 2. Fetch history records from API
    const data = await API.getCustomerHistory(currentCustomerId, currentPage, pageSize, category, search);
    if (loadingEl) loadingEl.style.display = "none";

    if (!data || !data.records || data.records.length === 0) {
      if (cardEl) cardEl.style.display = "block";
      if (subtitleEl) subtitleEl.textContent = "0 transactions found matching your criteria.";
      if (tbodyEl) {
        const filterNote = (category && category !== "all") || search
          ? ` matching filter (Category: "${category}", Search: "${search}")`
          : "";
        tbodyEl.innerHTML = `
          <tr>
            <td colspan="9" style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
              <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
              <strong>No transaction records found${filterNote}.</strong><br>
              <span style="font-size: 0.8rem;">Try choosing "All Categories" or clearing the keyword filter.</span>
            </td>
          </tr>
        `;
      }
      return;
    }

    // Update table subtitle with total records loaded
    if (subtitleEl) {
      subtitleEl.textContent = `Showing all ${data.total_records} purchase record${data.total_records === 1 ? '' : 's'} sorted chronologically.`;
    }

    // Render table rows
    if (tbodyEl) {
      tbodyEl.innerHTML = data.records.map(row => {
        const profitColor = row.profit >= 0 ? "#10b981" : "#ef4444";
        const profitSign = row.profit > 0 ? "+" : "";
        return `
          <tr>
            <td><strong>${row.order_id}</strong></td>
            <td>${row.order_date}</td>
            <td><span class="preset-pill" style="cursor: default;">${row.category}</span></td>
            <td><strong>${row.sub_category}</strong></td>
            <td>${row.quantity}</td>
            <td>${UIUtils.formatINR(row.amount)}</td>
            <td style="color: ${profitColor}; font-weight: 600;">${profitSign}${UIUtils.formatINR(row.profit)}</td>
            <td>${row.payment_mode}</td>
            <td style="font-size: 0.8rem; color: var(--text-muted);">${row.city}, ${row.state}</td>
          </tr>
        `;
      }).join("");
    }

    if (cardEl) cardEl.style.display = "block";
  } catch (err) {
    if (loadingEl) loadingEl.style.display = "none";
    if (cardEl) cardEl.style.display = "none";
    if (custOverview) custOverview.style.display = "none";
    showAlert(`Error loading purchase history: ${err.message}`, "warning");
  }
}

function showAlert(message, type = "info") {
  const container = document.getElementById("historyAlert");
  if (!container) return;
  const icon = type === "warning" ? "⚠️" : "ℹ️";
  container.innerHTML = `
    <div class="alert alert-${type}">
      <span class="alert-icon">${icon}</span>
      <div>${message}</div>
    </div>
  `;
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
