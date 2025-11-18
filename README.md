# Inventory Forecasting & Waste Simulation Dashboard

A complete Streamlit application for inventory demand forecasting and waste simulation using Prophet.

## Features

### 📊 Sidebar
- **Product Selection Dropdown**: Select from available products (populated from `get_product_list()`)
- **SKU Display**: Shows the selected product's SKU code
- **Generate Forecast Button**: Triggers demand forecasting for the next 7 days

### 📈 Forecast Section
- **Total Demand Metric**: Displays sum of forecasted demand for next 7 days
- **Interactive Plotly Chart**: 
  - Line chart showing `yhat` (forecast)
  - Confidence interval bands (`yhat_lower` and `yhat_upper`)
  - Hover tooltips with detailed information
  - X-axis: Date (`ds`)
  - Y-axis: Quantity in kg
- **Forecast Table**: Expandable table showing detailed 7-day forecast

### 💰 Promotion Simulation Section
- **Discount Slider**: Input discount percentage (0-80%)
- **Run Simulation Button**: Executes waste and revenue simulation
- **Results Display using st.metric()**:
  - 📦 **Current Stock**: Inventory on hand
  - ⏰ **Days to Expire**: Remaining shelf life
  - 🗑️ **Base Waste**: Expected waste without discount
  - ♻️ **Promo Waste**: Expected waste with discount (with delta)
  - 💵 **Base Revenue**: Expected revenue without discount
  - 💰 **Promo Revenue**: Expected revenue with discount (with delta)
- **Analysis Summary**: Insights on waste reduction and revenue impact

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Verify data files exist**:
- `current_inventory.csv`
- `daily_sales.csv`

3. **Ensure analysis_engine.py is in the same directory**

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Data Requirements

### analysis_engine.py
Must contain three functions:

1. **`get_product_list()`**
   - Returns: `dict[str, str]` mapping product_name to sku

2. **`get_forecast(sku_id)`**
   - Parameters: `sku_id` (str)
   - Returns: `tuple` (model, forecast_df, total_forecast_7_days)
   - forecast_df must contain columns: `ds`, `yhat`, `yhat_lower`, `yhat_upper`

3. **`run_waste_simulation(sku_id, base_forecast_7_days, discount_percentage)`**
   - Parameters:
     - `sku_id` (str)
     - `base_forecast_7_days` (float)
     - `discount_percentage` (float, e.g., 0.15 for 15%)
   - Returns: `dict` with keys:
     - `current_stock`
     - `days_to_expire`
     - `base_waste_kg`
     - `promo_waste_kg`
     - `base_revenue`
     - `promo_revenue`

### CSV Files

**current_inventory.csv**:
- Required columns: `product_name`, `sku`, `product_id`, `stock_on_hand_kg`, `shelf_life_days`, `cost_price`, `list_price`

**daily_sales.csv**:
- Required columns: `datetime_id`, `product_id`, `qty_sold_kg`

## Usage Workflow

1. Select a product from the sidebar dropdown
2. Click "Generate Forecast" to create 7-day demand prediction
3. Review the forecast chart and metrics
4. Adjust the discount percentage slider
5. Click "Run Simulation" to see waste and revenue impacts
6. Compare base vs. promotional scenarios

## Technical Details

- **Framework**: Streamlit 1.28+
- **Forecasting**: Prophet (Facebook)
- **Visualization**: Plotly
- **Layout**: Wide mode with 2-column design
- **State Management**: Streamlit session state for data persistence
- **Error Handling**: Comprehensive try-except blocks with user-friendly messages

## Features Highlights

✅ **Real-time forecasting** with Prophet  
✅ **Interactive visualizations** with Plotly  
✅ **Responsive layout** with columns  
✅ **Session state management** for data persistence  
✅ **Professional UI** with metrics and deltas  
✅ **Error handling** with helpful messages  
✅ **No placeholder code** - fully functional

## Notes

- The application assumes `analysis_engine.py` is in the same directory
- Forecast is based on historical sales data from `daily_sales.csv`
- Simulation uses a 2.5x price elasticity multiplier
- All monetary values are in VND (Vietnamese Dong)
- Quantities are in kilograms (kg)
