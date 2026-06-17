# FMCG AI Assistant

An AI-powered conversational analytics assistant for Fast-Moving Consumer Goods (FMCG) beverage sales and inventory operations.

This application allows supply chain managers, brand directors, and business analysts to query complex relational datasets in plain English. It converts natural language queries into optimized SQLite code, queries the database locally, and translates raw metrics into executive-level business insights using Google Gemini 2.5 Flash.

---

## Architecture Flow

```
   User Question (Natural Language)
               │
               ▼
┌──────────────────────────────┐
│     Gemini Text-to-SQL       │ (Generates SQLite statement based on schema)
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       SQLite Database        │ (Executes generated SQL on local fmcg.db)
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Gemini Insight Synthesizer  │ (Translates query results to business text)
└──────────────┬───────────────┘
               │
               ▼
   Executive Insights & Visual Charts (Streamlit Interface)
```

---

## Features

- **Natural Language Analytics**: Translate business questions directly to SQL queries.
- **Interactive KPI Metrics**: Instantly view Total Revenue, Units Sold, Promotional Revenue Share, and Stockout Counts.
- **Dynamic Visualizations**: View Regional Revenue breakdown, Category Sales Performance, and Promotion Efficiency charts using Plotly.
- **Dual API Key Entry**: Input your `GEMINI_API_KEY` either via a local `.env` configuration file or securely within the Streamlit sidebar.

---

## Database Schema

The SQLite database (`database/fmcg.db`) contains four tables:

1. **`product_master`**: SKU metadata (beverage name, brand, category, sub-category, pack size, price).
2. **`store_master`**: Outlet profiles (name, region, city, retail format).
3. **`sales_promotions`**: Weekly sales transactions detailing units sold, revenue, promo active flag, type of promotion (`Discount`, `BOGO`, `Display Space`), and discount %.
4. **`inventory`**: Supply chain metrics tracking weekly `opening_stock`, `units_received` (replenishment logs), `units_sold`, `closing_stock`, and whether a `stockout_flag` occurred.

---

## Setup and Run Instructions

### Prerequisites
Make sure Python 3.10+ is installed on your local machine.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root folder:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Generate Mock FMCG Datasets
Generate the 24-week synthetic datasets:
```bash
python generate_data.py
```
This writes four CSV files to the `data/` folder.

### 4. Setup and Populate Database
Load the generated CSV data into the SQLite relational tables:
```bash
python database.py
```
This builds `database/fmcg.db`.

### 5. Launch the Streamlit Dashboard
Start the web server locally:
```bash
streamlit run app.py
```

---

## Sample Questions to Try in the Chat Box

- **Regional Sales**: `"Which region generated the highest revenue?"`
- **Promo Efficiency**: `"What promotion type worked best in terms of units sold?"`
- **Supply Chain**: `"Which products experienced the most stockout incidents?"`
- **Trend Comparison**: `"Compare North and South regions' weekly revenue trends."`
- **Rankings**: `"Show top 5 products by revenue and their brand."`
- **Financial Analysis**: `"What is the average discount percent by brand?"`
