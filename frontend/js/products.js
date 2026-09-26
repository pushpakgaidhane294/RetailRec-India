/**
 * Product Explorer Controller for RetailRec India.
 * Fetches and renders catalog items with real transaction metrics.
 */
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("productSearchInput");
  const catSelect = document.getElementById("productCategorySelect");
  const sortSelect = document.getElementById("productSortSelect");

  searchInput.addEventListener("input", debounce(loadProducts, 250));
  catSelect.addEventListener("change", loadProducts);
  sortSelect.addEventListener("change", loadProducts);

  loadProducts();
});

async function loadProducts() {
  const query = document.getElementById("productSearchInput").value.trim();
  const category = document.getElementById("productCategorySelect").value;
  const sortBy = document.getElementById("productSortSelect").value;
  const grid = document.getElementById("productsGrid");

  try {
    let products;
    if (query) {
      products = await API.searchProducts(query, category);
    } else {
      products = await API.getProducts(category, sortBy, false);
    }

    if (!products || products.length === 0) {
      grid.innerHTML = `
        <div class="state-box" style="grid-column: 1 / -1;">
          <h4 class="state-title">No Products Found</h4>
          <p class="state-desc">Try clearing your search keyword or switching categories.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = products.map((item, index) => `
      <div class="rec-card">
        <div class="rec-card-top">
          <div class="rec-rank-badge" style="background: linear-gradient(135deg, #0b132b, #3a86ff);">
            ${index + 1}
          </div>
          <span class="rec-status-badge ai" style="background: rgba(58, 134, 255, 0.15); color: #2563eb; border-color: rgba(58, 134, 255, 0.3);">
            ${item.category}
          </span>
        </div>

        <div>
          <h4 class="rec-item-title">${item.sub_category}</h4>
          <span style="font-size: 0.8rem; color: var(--text-muted);">
            Item ID: <strong>${item.item_id}</strong>
          </span>
        </div>

        <div style="margin: 1rem 0; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.825rem;">
          <div style="background: #f8fafc; padding: 0.45rem 0.65rem; border-radius: 6px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.7rem; color: #64748b;">TOTAL SALES</div>
            <div style="font-weight: 700; color: #0f172a;">${UIUtils.formatINR(item.total_sales)}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.45rem 0.65rem; border-radius: 6px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.7rem; color: #64748b;">UNITS SOLD</div>
            <div style="font-weight: 700; color: #0f172a;">${UIUtils.formatNumber(item.total_quantity_sold)}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.45rem 0.65rem; border-radius: 6px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.7rem; color: #64748b;">CUSTOMERS</div>
            <div style="font-weight: 700; color: #0f172a;">${item.customer_count}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.45rem 0.65rem; border-radius: 6px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.7rem; color: #64748b;">ORDERS</div>
            <div style="font-weight: 700; color: #0f172a;">${item.order_count}</div>
          </div>
        </div>

        <div class="rec-details-row">
          <div>
            <div style="font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Avg Unit Price</div>
            <div class="rec-price" style="font-size: 1.1rem;">${UIUtils.formatINR(item.avg_price)}</div>
          </div>
          <div>
            <a href="/recommendations" class="btn btn-outline btn-sm">
              Find Customers →
            </a>
          </div>
        </div>
      </div>
    `).join("");
  } catch (err) {
    grid.innerHTML = `
      <div class="state-box" style="grid-column: 1 / -1;">
        <h4 class="state-title">Error Loading Products</h4>
        <p class="state-desc">${err.message}</p>
      </div>
    `;
  }
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
