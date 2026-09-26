# RetailRec India 🇮🇳

## Deep Learning-Based Personalized Product Recommendation System Using Neural Collaborative Filtering (NCF)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow 2.x](https://img.shields.io/badge/TensorFlow-2.x-FF6F00.svg?style=flat&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Render Deployable](https://img.shields.io/badge/Render-Deployable-46E3B7.svg?style=flat&logo=render&logoColor=white)](https://render.com/)

> **Core System Summary:**  
> **RetailRec India** is an end-to-end, production-ready recommendation system designed for Indian e-commerce. Powered by a custom **Neural Collaborative Filtering (NCF)** deep learning architecture trained on authentic transactional data (Madhav E-Commerce dataset across 19 Indian states), it learns 32-dimensional dense latent representations for customers and product sub-categories to output real-time, personalized Top-K recommendations. Built with **FastAPI** on the backend and a high-performance, responsive **Vanilla HTML5/CSS3/JavaScript** frontend with zero client-side framework overhead.

---

## 🌟 Key System Features

- 🧠 **Neural Collaborative Filtering (NCF)**: Replaces linear matrix factorization with non-linear neural network embeddings (17,569 parameters) with dropout regularization.
- ⚡ **Real-Time Inference Engine**: Sub-10ms model inference with preloaded singleton model weights in memory.
- 🎨 **Tri-Color E-Commerce Theme**: Clean, accessible palette inspired by leading Indian retail platforms — Deep Indigo (`#4f46e5`), Vivid Action Orange (`#f97316`), and Emerald Margin Green (`#10b981`) with soft gradient backdrops.
- 🔍 **Live Autocomplete Customer Search**: Instant search across 336 authentic consumers by Customer ID, Name, City, or State.
- 📜 **Complete Transaction History**: Full audit trail of past orders with product categories, quantities, amounts, payment methods, and net margins.
- 📊 **Executive Dashboard & Deep-Dive Analytics**: High-level KPI cockpit plus granular merchandising tables (Category revenue share, Top-10 sub-category rankings).
- 🛡️ **Cold-Start Fallback**: Gracefully detects unseen/new customer inputs and safely falls back to genuine popularity-based recommendations.
- 🚀 **1-Click Cloud Deployment**: Ready for zero-configuration deployment on Render via Blueprint (`render.yaml`) and Docker/Procfile.

---

## 📐 System Architecture

```
Authentic Indian E-Commerce Transactions (Orders.csv + Details.csv)
   │
   ▼
Data Cleaning & Feature Normalization (500 Orders, 1,500 Line Items)
   │
   ▼
Customer-Item Interaction Matrix (336 Consumers × 17 Sub-Categories, 20.24% Density)
   │
   ▼
Chronological Train / Validation / Test Holdout Split (Strict Temporal Order)
   │
   ▼
Leakage-Free Negative Sampling (2:1 Ratio, Reproducible Seed 42)
   │
   ▼
Neural Collaborative Filtering (Customer Embedding 32d + Item Embedding 32d + MLP 64-32-1)
   │
   ▼
FastAPI High-Performance REST Service (Singleton In-Memory Model Cache)
   │
   ▼
Vanilla HTML5 / CSS3 / ES6 Frontend (Responsive, Zero External UI Frameworks)
   │
   ▼
Production Cloud Deployment on Render (Oregon / Free Tier Optimized)
```

---

## 🔬 Dataset & Ground-Truth Statistics

All statistics and recommendations are derived strictly from the authentic **Madhav E-Commerce Sales Dataset**:

| Metric | Ground-Truth Value | Description |
| :--- | :--- | :--- |
| **Total Orders** | `500` | Distinct completed sales transactions |
| **Total Line Items** | `1,500` | Individual item purchase rows |
| **Unique Customers** | `336` | Authentically identified consumers |
| **Product Sub-Categories** | `17` | Real catalog units across Clothing, Electronics, Furniture |
| **Gross Revenue** | `₹4,37,771.00` | Cumulative transactional order revenue |
| **Total Units Sold** | `5,615` | Total physical units purchased |
| **Net Profit** | `₹36,963.00` | Total realized order margin |
| **Average Order Value (AOV)** | `₹875.54` | Per-order average basket value |
| **Geographic Span** | `19 States, 25 Cities` | Extensive Indian retail market representation |
| **Interaction Matrix Density** | `20.24%` | High collaborative filtering convergence density |

---

## 🧠 Neural Collaborative Filtering (NCF) Model

```
Customer ID (Scalar)            Product Sub-Category (Scalar)
       │                                     │
       ▼                                     ▼
Customer Embedding (336, 32)         Product Embedding (17, 32)
       │                                     │
       ▼                                     ▼
32-dim Latent Vector                 32-dim Latent Vector
       │                                     │
       └──────────────────┬──────────────────┘
                          ▼
               Concatenate Vector (64)
                          │
                          ▼
                Dense(64, ReLU) Layer
                          │
                          ▼
                    Dropout(0.20)
                          │
                          ▼
                Dense(32, ReLU) Layer
                          │
                          ▼
                    Dropout(0.20)
                          │
                          ▼
                Dense(1, Sigmoid) Layer
                          │
                          ▼
               Affinity Score in [0, 1]
```

### Hyperparameters & Training Specs:
- **Embedding Dimension:** `32`
- **MLP Layers:** `64 -> 32 -> 1`
- **Activation Functions:** `ReLU` for hidden layers, `Sigmoid` for output
- **Optimizer:** Adam (`learning_rate = 0.001`)
- **Loss Function:** Binary Crossentropy
- **Regularization:** Dropout (0.20) + EarlyStopping (patience = 8)
- **Trainable Parameters:** `17,569` (~68.6 KB storage footprint)

### Verified Model Performance Metrics:
All metrics are evaluated on held-out chronological test purchases:

| Metric | Value | Meaning |
| :--- | :--- | :--- |
| **Test Binary Accuracy** | `71.83%` | Classification accuracy on positive vs negative interaction pairs |
| **Test Loss (BCE)** | `0.7094` | Crossentropy loss on test holdout set |
| **Hit Rate @ 5** | `46.90%` | Probability that held-out test item appears in Top-5 predictions |
| **Recall @ 5** | `46.90%` | Fraction of held-out test items retrieved in Top-5 |
| **Hit Rate @ 10** | `65.04%` | Probability that held-out test item appears in Top-10 predictions |
| **Recall @ 10** | `65.04%` | Fraction of held-out test items retrieved in Top-10 |

---

## 🗂️ Project File Structure

```
Retail_Rec-India/
├── app/
│   ├── main.py                     # FastAPI application & static asset routes
│   ├── api/
│   │   ├── routes_customers.py     # Customer listing, profile, and history APIs
│   │   ├── routes_recommendations.py # Top-K personalized recommendation API
│   │   ├── routes_products.py      # Catalog & product explorer APIs
│   │   ├── routes_analytics.py     # High-level KPIs & chart data APIs
│   │   └── routes_model.py         # NCF architecture specs & evaluation metrics APIs
│   ├── core/
│   │   └── config.py               # Application settings, ports, and relative paths
│   ├── models/
│   │   └── schemas.py              # Pydantic v2 validation models
│   └── services/
│       ├── customer_service.py     # Customer lookup, overview, and history service
│       ├── recommendation_service.py # Recommendation workflow orchestrator
│       ├── product_service.py      # Catalog queries and category aggregation
│       └── analytics_service.py    # Revenue, profit, and geographic metrics service
├── ml/
│   ├── preprocessing.py            # Dataset cleaning, joining, and validation
│   ├── interaction_builder.py      # Interaction matrix and chronological train/val/test split
│   ├── negative_sampling.py        # Leak-free reproducible negative sampler
│   ├── model.py                    # NCF model architecture definition
│   ├── train.py                    # Training orchestrator with checkpoints
│   ├── evaluate.py                 # Hit Rate@K, Recall@K, Precision@K calculator
│   └── predict.py                  # Singleton inference engine & cold-start handler
├── frontend/
│   ├── index.html                  # Executive Dashboard & Quick AI Sandbox
│   ├── recommendations.html        # Interactive AI Recommendation Studio
│   ├── history.html                # Customer Purchase History & Transaction Ledger
│   ├── products.html               # 17 Product Sub-Categories Explorer
│   ├── analytics.html              # Merchandising BI & Tabular Reports
│   ├── model.html                  # Model Performance & Loss Curves
│   ├── about.html                  # Architecture Pipeline & Business Problem/Solution
│   ├── css/
│   │   └── style.css               # Tri-color Indian retail theme & responsive layout
│   └── js/
│       ├── api.js                  # Centralized async API client & UIUtils
│       ├── app.js                  # Dashboard controller & Chart.js charts
│       ├── recommendations.js      # Recommendation studio controller
│       ├── history.js              # History controller with filters
│       ├── products.js             # Catalog explorer controller
│       ├── analytics.js            # BI charts & data tables controller
│       └── model.js                # Training loss/accuracy curves controller
├── artifacts/
│   ├── model/
│   │   ├── retailrec_model.keras   # Trained NCF neural network weights
│   │   ├── model_metadata.json     # Architecture specs & parameters
│   │   ├── evaluation_metrics.json # Genuine evaluation scores
│   │   └── training_history.json   # Epoch-by-epoch loss and accuracy
│   └── encoders/
│       ├── customer_encoder.json   # 336 Customer ID <-> Index mapping
│       └── item_encoder.json       # 17 Sub-Category <-> Index mapping
├── data/
│   ├── raw/                        # Orders.csv and Details.csv
│   └── processed/                  # Cleaned CSVs & preprocessing report
├── scripts/
│   ├── download_dataset.py         # Autonomous download from verified mirrors
│   ├── prepare_data.py             # Data preparation pipeline runner
│   ├── train_model.py              # Model training runner
│   └── evaluate_model.py           # Model evaluation runner
├── tests/
│   ├── test_api.py                 # FastAPI integration tests
│   ├── test_model.py               # Model loading & shape verification tests
│   ├── test_preprocessing.py       # Data integrity & cleansing tests
│   ├── test_recommendations.py     # Recommendation & fallback tests
│   └── verify_live.py              # Live health & endpoint probe
├── run.py                          # Local startup entry point for VS Code
├── runtime.txt                     # Python 3.11.8 specification for Render
├── render.yaml                     # Automated Render Blueprint configuration
├── requirements.txt                # Production dependencies
├── .gitignore                      # Clean Git exclusion rules
├── LICENSE                         # MIT License
└── README.md                       # Comprehensive documentation
```

---

## 💻 Local Setup & Execution Guide

### Prerequisites
- Python 3.11 (or 3.10)
- Git
- VS Code (recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/Retail_Rec-India.git
cd Retail_Rec-India
```

### Step 2: Create Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Automated Tests
```bash
pytest -v tests/
```
*(All 16 unit and API integration tests will run and pass).*

### Step 5: Start Local Web Server
You can start the server using either method:

**Option A — Using `run.py` (Easiest in VS Code):**
```bash
python run.py
```

**Option B — Using Uvicorn CLI:**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
- 🌐 **Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 🎯 **AI Recommendations:** [http://127.0.0.1:8000/recommendations](http://127.0.0.1:8000/recommendations)
- 📜 **Customer History:** [http://127.0.0.1:8000/history](http://127.0.0.1:8000/history)
- 📚 **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🩺 **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📤 Upload to GitHub from VS Code

Follow these commands in your VS Code terminal to push your project to a new GitHub repository:

```powershell
# 1. Check git status (working tree is clean on branch main)
git status

# 2. Add your GitHub remote repository
# (Create an empty repo on https://github.com/new first)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/Retail_Rec-India.git

# 3. Push to GitHub
git push -u origin main
```

---

## 🚀 Cloud Deployment on Render

The repository is configured for automated deployment on [Render](https://render.com/).

### Method 1: Using the Render Blueprint (Recommended)
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ select **Blueprint**.
3. Connect your GitHub account and choose your `Retail_Rec-India` repository.
4. Render automatically reads `render.yaml` and configures:
   - **Environment:** Python 3.11.8
   - **Build Command:** `pip install -r requirements.txt && python scripts/prepare_data.py`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
5. Click **Apply**. Your service will be live in 2–3 minutes at `https://retailrec-india.onrender.com`.

### Method 2: Manual Web Service Setup
1. On Render, click **New +** $\rightarrow$ **Web Service**.
2. Select your repository.
3. Configure settings:
   - **Name:** `retailrec-india`
   - **Runtime:** `Python 3`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt && python scripts/prepare_data.py`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Under **Advanced Settings**:
   - **Health Check Path:** `/health`
   - **Environment Variable:** `PYTHON_VERSION` = `3.11.8`
5. Click **Deploy Web Service**.

---

## 🌐 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status, model load state, data check |
| `GET` | `/api/stats` | Top-level KPI counts (customers, orders, revenue, profit) |
| `GET` | `/api/customers` | Searchable list of all 336 customers with spending metrics |
| `GET` | `/api/customers/{id}` | Detailed customer profile summary and spending aggregates |
| `GET` | `/api/customers/{id}/history` | Chronological purchase ledger with category and search filters |
| `GET` | `/api/customers/{id}/recommendations` | Top-K AI recommendations scored by NCF neural network |
| `GET` | `/api/products` | All 17 sub-categories with total sales and unit prices |
| `GET` | `/api/products/categories` | High-level category summary (Clothing, Electronics, Furniture) |
| `GET` | `/api/analytics` | Aggregated monthly sales, state distribution, payment modes |
| `GET` | `/api/model/info` | NCF architecture specs, embedding dimensions, parameter count |
| `GET` | `/api/model/metrics` | Evaluated test metrics (Hit Rate@K, Recall@K, Precision@K) |
| `GET` | `/api/model/history` | Epoch-by-epoch training and validation loss/accuracy curves |

---

## 💡 Frequently Asked Questions

### 1. What is the difference between Dashboard (`/`) and Analytics (`/analytics`)?
- **Dashboard (`/`)** is the **Executive Cockpit & Launchpad**. It displays glanceable KPI metric cards, high-level macro charts, and the **1-Click AI Recommendation Sandbox** to immediately test predictions for sample customers.
- **Analytics (`/analytics`)** is the **Commercial Merchandising Suite**. In addition to macro charts, it provides **granular tabular reports**:
  1. *Category Performance Table*: Exact revenue, profit, quantity, and market share across Clothing, Electronics, and Furniture.
  2. *Top 10 Sub-Categories Table*: Ranked merchandise analysis with unit prices, units sold, and unique customer reach.

### 2. Why are "Total Spend" and "Average Order Value (AOV)" sometimes the same?
$$\text{Average Order Value} = \frac{\text{Total Spending}}{\text{Total Orders}}$$
In the authentic dataset, **68% of customers placed exactly 1 order** (which often contains multiple items in that single order). For customers with 1 order (e.g. `CUST-001` or `CUST-103`), $\text{Total Spend} / 1 = \text{Total Spend}$, so the numbers are mathematically identical. For repeat customers (e.g. `CUST-002`, `CUST-008`), the AOV correctly divides total spend by their order count.

### 3. Why is the Customer Profile shown on both Customer History and AI Recommendations?
- **Customer History (`/history`)** is **Backward-looking (Audit)**: It displays recorded historical purchases (what the customer has *already* bought).
- **AI Recommendations (`/recommendations`)** is **Forward-looking (Predictive)**: It uses the NCF model to predict what they *will buy next* (filtering out already-purchased items). Showing the profile above the recommendations provides immediate merchandiser context (e.g., whether a recommended item matches the customer's typical spending level).

---

## 📜 Academic & Presentation Defense (15-Mark Script)

> *"We engineered an end-to-end personalized product recommendation system for Indian e-commerce transactions using Neural Collaborative Filtering (NCF).*
> 
> *Using the authentic Madhav E-Commerce sales dataset covering 336 customers and 17 product sub-categories across 19 Indian states, we built a non-linear deep learning model. We projected customers and products into continuous 32-dimensional embedding spaces, combined them through a multi-layer neural network with dropout regularization, and trained on temporal holdout splits with zero-leakage negative sampling.*
> 
> *The model achieves 71.83% binary test accuracy and a Hit Rate@10 of 65.04%. The system is deployed using FastAPI for sub-10ms inference and served via a lightweight, responsive vanilla frontend with a tri-color retail design system ready for cloud production on Render."*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
