/**
 * Centralized API client for RetailRec India.
 * Automatically resolves relative API endpoints so it works identically
 * on local development (localhost) and production deployment (Render).
 */
const API = {
  // Use relative root so requests match the serving host and port
  baseUrl: "",

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const response = await fetch(url, {
        headers: {
          "Accept": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errorDetail = errData.detail;
          }
        } catch (_) {}
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on ${url}:`, err);
      throw err;
    }
  },

  // Health
  async getHealth() {
    return this.request("/health");
  },

  // Top-level KPI stats
  async getStats() {
    return this.request("/api/stats");
  },

  // Customers
  async getCustomers(query = "", limit = 100) {
    const params = new URLSearchParams();
    if (query) params.append("query", query);
    if (limit) params.append("limit", limit.toString());
    return this.request(`/api/customers?${params.toString()}`);
  },

  async getCustomer(customerId) {
    return this.request(`/api/customers/${encodeURIComponent(customerId)}`);
  },

  async getCustomerHistory(customerId, page = 1, pageSize = 10, category = "", search = "") {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (category && category !== "all") params.append("category", category);
    if (search) params.append("search", search);
    return this.request(`/api/customers/${encodeURIComponent(customerId)}/history?${params.toString()}`);
  },

  // Recommendations
  async getRecommendations(customerId, topK = 5, category = "", excludePurchased = true) {
    const params = new URLSearchParams({
      top_k: topK.toString(),
      exclude_purchased: excludePurchased.toString(),
    });
    if (category && category !== "all") params.append("category", category);
    return this.request(`/api/customers/${encodeURIComponent(customerId)}/recommendations?${params.toString()}`);
  },

  // Products / Catalog
  async getProducts(category = "", sortBy = "total_sales", ascending = false) {
    const params = new URLSearchParams({
      sort_by: sortBy,
      ascending: ascending.toString(),
    });
    if (category && category !== "all") params.append("category", category);
    return this.request(`/api/products?${params.toString()}`);
  },

  async searchProducts(query = "", category = "") {
    const params = new URLSearchParams();
    if (query) params.append("q", query);
    if (category && category !== "all") params.append("category", category);
    return this.request(`/api/products/search?${params.toString()}`);
  },

  async getCategories() {
    return this.request("/api/products/categories");
  },

  // Analytics
  async getAnalytics() {
    return this.request("/api/analytics");
  },

  // Model Metadata & Metrics
  async getModelInfo() {
    return this.request("/api/model/info");
  },

  async getModelMetrics() {
    return this.request("/api/model/metrics");
  },

  async getModelHistory() {
    return this.request("/api/model/history");
  },
};

// Global formatters
const UIUtils = {
  formatINR(val) {
    if (val === undefined || val === null || isNaN(val)) return "₹0.00";
    return "₹" + Number(val).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  },

  formatNumber(val) {
    if (val === undefined || val === null || isNaN(val)) return "0";
    return Number(val).toLocaleString("en-IN");
  },

  formatPercent(val) {
    if (val === undefined || val === null || isNaN(val)) return "0.0%";
    return Number(val).toFixed(2) + "%";
  },

  formatScore(val) {
    if (val === undefined || val === null || isNaN(val)) return "0.0000";
    return Number(val).toFixed(4);
  },
};
