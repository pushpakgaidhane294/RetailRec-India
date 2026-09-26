"""
Live HTTP Verification Script for RetailRec India.
Tests all endpoints against the running server.
"""
import urllib.request
import json

base = "http://127.0.0.1:8000"


def check_url(url, is_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        code = resp.status
        content = resp.read()
        if is_json:
            return code, json.loads(content.decode("utf-8"))
        return code, len(content)


def main():
    print("=== 1. CHECKING HEALTH ===")
    code, data = check_url(f"{base}/health")
    print(f"Health: {code} -> {data}")

    print("\n=== 2. CHECKING STATS ===")
    code, data = check_url(f"{base}/api/stats")
    print(f"Stats: {code} -> {data}")

    print("\n=== 3. CHECKING CUSTOMERS (LIMIT 3) ===")
    code, data = check_url(f"{base}/api/customers?limit=3")
    print(f"Customers sample: {code} -> returned {len(data)} items")
    for c in data:
        print(f"   {c['customer_id']}: {c['customer_name']} ({c['city']}, {c['state']}) - Spend: Rs.{c['total_spending']}")

    print("\n=== 4. CHECKING REAL CUSTOMER RECOMMENDATIONS ===")
    test_customers = ["CUST-001", "CUST-100", "CUST-165", "Harivansh", "Madhav"]
    for cid in test_customers:
        code, data = check_url(f"{base}/api/customers/{cid}/recommendations?top_k=3")
        print(f"Customer {cid} ({data['customer_name']}) -> Model: {data['model_type']}, Recs: {len(data['recommendations'])}")
        for r in data["recommendations"]:
            print(f"   #{r['rank']} {r['sub_category']} ({r['category']}) - Price: Rs.{r['avg_price']} - Model Score: {r['model_score']} - Badge: {r['badge']}")

    print("\n=== 5. CHECKING COLD START FALLBACK ===")
    code, data = check_url(f"{base}/api/customers/NON_EXISTENT_CUSTOMER/recommendations?top_k=3")
    print(f"Cold start response: {data['model_type']} | Fallback used: {data['fallback_used']}")
    for r in data["recommendations"]:
        print(f"   #{r['rank']} {r['sub_category']} - Score: {r['model_score']} - Badge: {r['badge']}")

    print("\n=== 6. CHECKING CUSTOMER HISTORY ===")
    code, data = check_url(f"{base}/api/customers/CUST-001/history?page=1&page_size=3")
    print(f"History for CUST-001: {code} -> {data['total_records']} total records")
    for item in data["records"]:
        print(f"   Order: {item['order_id']} ({item['order_date']}) - {item['sub_category']} - Rs.{item['amount']}")

    print("\n=== 7. CHECKING PRODUCTS CATALOG ===")
    code, data = check_url(f"{base}/api/products")
    print(f"Catalog sub-categories count: {len(data)}")

    print("\n=== 8. CHECKING MODEL METRICS ===")
    code, data = check_url(f"{base}/api/model/metrics")
    print(f"Metrics: loss={data['test_loss']}, acc={data['test_binary_accuracy']}, hit@5={data['hit_rate_at_5']}, hit@10={data['hit_rate_at_10']}")

    print("\n=== 9. CHECKING ALL FRONTEND HTML PAGES ===")
    pages = [
        "/",
        "/recommendations",
        "/history",
        "/products",
        "/analytics",
        "/model",
        "/about",
        "/css/style.css",
        "/js/api.js",
        "/js/app.js",
        "/js/recommendations.js",
        "/js/history.js",
        "/js/products.js",
        "/js/analytics.js",
        "/js/model.js",
    ]
    for p in pages:
        code, length = check_url(f"{base}{p}", is_json=False)
        print(f"   Page {p:24} -> HTTP {code}, Length: {length} bytes")

    print("\n>>> ALL VERIFICATIONS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    main()
