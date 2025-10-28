# 🏦 Project: Global Market Index Analytics

## 📘 Context
You are a **Data Engineer** at **GlobeQuant**, a financial analytics firm.  
The goal of this project is to build an **end-to-end data platform** that collects, transforms, analyzes, and forecasts **global stock index trends** to generate business intelligence and support investment decisions.

The system leverages the Kaggle dataset [Stock Exchange Data](https://www.kaggle.com/datasets/mattiuzc/stock-exchange-data), which includes global daily index data such as *open, high, low, close,* and *volume*.

---

## 📊 Objectives
- Ingest global index time series into a structured database.  
- Clean, normalize, and model index behavior across markets.  
- Provide analytics and dashboards to explore:
  - Cross-market trends  
  - Volatility and returns  
  - Forecasts and future insights  
- Enable filtering by region, index type, and time window.

---

## ⚙️ Technical Stack

| Layer | Tools / Frameworks | Description |
|-------|--------------------|--------------|
| **Data Ingestion** | Python (MySQL Connector) | Load raw CSV data into MySQL staging tables |
| **Data Warehouse / Analytics Store** | MySQL | Store transformed and analytical data |
| **Transformation & Modeling** | dbt (staging, intermediate, final models) | Data cleaning, metric computation, aggregation |
| **Forecasting** | Python (Prophet) | Predict index prices and volatility |
| **Orchestration** | Apache Airflow | Schedule and automate ingestion → transform → forecasting → dashboard |
| **Visualization** | Plotly Dash | Interactive dashboard for analysis |
| **Documentation** | Markdown / PDF | System design and pipeline explanation |

---

## 🧱 Project Structure

```
global-market-index-analytics/
│
├── sql/              
│   ├── create_tables.sql       → SQL script to create raw tables.
│   └── load_data.py            → Python ETL script to load CSV data into MySQL.
│
├── dbt/              
│   ├── models/ 
│   │   ├── staging/            → Clean and standardize raw index data (e.g. stg_global_index.sql)
│   │   ├── intermediate/       → Compute daily returns, log returns, rolling volatility (int_market_metrics.sql)
│   │   └── final/              → Aggregate metrics by market and time (fct_market_summary.sql)
│   ├── logs/                   → dbt run logs and manifest files
│   ├── dbt_packages/           → Dependencies for dbt models
│   └── dbt_project.yml         → dbt configuration file
│
├── forecasting/      
│   └── model_forecast.py      → ML forecasting model for future index prices.
│
├── airflow/          
│   └── global-market-dag.py   → Airflow DAG orchestrating ETL, dbt, and forecasting jobs.
│
├── dash/             
│   └── app.py                 → Plotly Dash web app visualizing analytics and forecasts.
│
├── docs/             
│   ├── architecture_diagram.png → Data architecture and pipeline flow.
│   └── Project_Documentation.md → Technical documentation.
│
└── README.md                  → Project overview and run instructions.
```

---

## 🧩 dbt Model Lineage

```
stg_global_index.sql
      ↓
int_market_metrics.sql
      ↓
fct_market_summary.sql
```

**Explanation:**
1. **Staging Layer (`stg_global_index.sql`)**  
   - Loads and cleans raw CSV data.  
   - Converts data types and removes nulls.

2. **Intermediate Layer (`int_market_metrics.sql`)**  
   - Calculates **daily returns**, **log returns**, and **rolling volatility**.  
   - Prepares data for analytical use.

3. **Final Layer (`fct_market_summary.sql`)**  
   - Aggregates metrics across indices and computes average volatility & return.  
   - Provides data for dashboards and forecasting.

---

## 📈 Data Flow Overview

```
Raw CSV Data (Kaggle)
        ↓
MySQL (Staging Tables)
        ↓
dbt Transformations (Staging → Intermediate → Final)
        ↓
Forecasting Engine (model_forecast.py)
        ↓
Dash Dashboard (app.py)
```

---

## 🕹️ Airflow Orchestration

**DAG:** `global-market-dag.py`  
**Tasks:**
1. `ingest_data` → Run `load_data.py`  
2. `run_dbt` → Execute dbt transformations  
3. `dbt_test` → Test dbt
4. `forecast_model` → Generate forecasts  
5. `update_dashboard` → Refresh Dash data layer

---

## 📉 Forecasting Logic
- The script `model_forecast.py` trains a time-series model on historical **close prices**.
- It outputs:
  - **Next 7-day price forecasts**
  - **Confidence intervals**
  - **Forecast accuracy metrics (MAE, RMSE)**

---

## 📊 Dashboard Features (dash/app.py)
- View **index time series** for global markets.  
- Compare **regions (US, EU, Asia)** by volatility and return.  
- Display **forecasted vs actual** trends.  
- Highlight **high-risk periods** using alerts and color-coded charts.

---

## 🧠 Architecture Diagram
*(Located in `docs/architecture_diagram.png`)*  

**Components:**
- **Source:** CSV datasets (Kaggle)  
- **Storage:** MySQL (Raw/Staging)  
- **Transformation:** dbt (staging → intermediate → final)  
- **Forecasting:** Python ML script  
- **Orchestration:** Airflow  
- **Visualization:** Dash  

---

## 🧰 Setup & Execution

### 1. Environment Setup
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
mysql -u admin -p < sql/create_tables.sql
python sql/load_data.py
```

### 3. Run dbt Models
```bash
cd dbt
source ~/venv/bin/activate
dbt debug
dbt run
```

### 4. Run Forecasting
```bash
python forecasting/model_forecast.py
```

### 5. Launch Dashboard
```bash
python dash/app.py
```

### 6. Airflow DAG
```bash
airflow standalone
```

---

## 🗂️ Deliverables
- ✅ Source Code Repository (structured as above)
- ✅ Technical Documentation (this file)
- ✅ Data Flow & Architecture Diagram (`docs/architecture_diagram.png`)
- ✅ dbt Model Lineage Graph
- ✅ Forecasting Script & Dashboard
