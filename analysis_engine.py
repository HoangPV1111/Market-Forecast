import pandas as pd
from prophet import Prophet


def get_product_list():
    """
    Get the list of products from current inventory.
    
    Returns:
        dict[str, str]: Dictionary mapping product_name to sku
    """
    # Read the current inventory CSV
    inventory_df = pd.read_csv('current_inventory.csv')
    
    # Create dictionary with product_name as key and sku as value
    product_dict = dict(zip(inventory_df['product_name'], inventory_df['sku']))
    
    return product_dict


def get_forecast(sku_id, forecast_days=7):
    """
    Generate demand forecast for a given SKU using Prophet.
    
    Args:
        sku_id (str): The SKU identifier (e.g., 'VEG0001')
        forecast_days (int): Number of days to forecast (default: 7)
    
    Returns:
        tuple: (model, forecast_df, total_forecast_days)
            - model: Fitted Prophet model object
            - forecast_df: Full forecast DataFrame
            - total_forecast_days: Sum of predicted sales for forecast period (float)
    """
    # Read the data files
    inventory_df = pd.read_csv('current_inventory.csv')
    sales_df = pd.read_csv('daily_sales.csv')
    
    # Get the product_id for the given sku_id
    product_row = inventory_df[inventory_df['sku'] == sku_id]
    if product_row.empty:
        raise ValueError(f"SKU {sku_id} not found in inventory")
    
    product_id = product_row['product_id'].iloc[0]
    
    # Filter sales data for this product
    product_sales = sales_df[sales_df['product_id'] == product_id].copy()
    
    # Prepare data for Prophet: rename columns to 'ds' and 'y'
    # Convert datetime_id (YYYYMMDD format) to datetime
    product_sales['ds'] = pd.to_datetime(product_sales['datetime_id'].astype(str), format='%Y%m%d')
    product_sales['y'] = product_sales['qty_sold_kg']
    
    # Select only the required columns for Prophet
    prophet_df = product_sales[['ds', 'y']]
    
    # Initialize Prophet model with seasonality settings
    model = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    
    # Fit the model
    model.fit(prophet_df)
    
    # Create future dataframe for specified days ahead
    future = model.make_future_dataframe(periods=forecast_days)
    
    # Generate forecast
    forecast_df = model.predict(future)
    
    # Calculate total forecasted sales for the forecast period
    # Get only the future predictions (last N rows)
    future_predictions = forecast_df.tail(forecast_days)
    total_forecast_days = future_predictions['yhat'].sum()
    
    return model, forecast_df, total_forecast_days


def run_waste_simulation(sku_id, base_forecast_days, discount_percentage, stock_multiplier=1.0):
    """
    Simulate waste and revenue under baseline and promotional scenarios.
    
    Args:
        sku_id (str): The SKU identifier (e.g., 'VEG0001')
        base_forecast_days (float): Total forecasted sales for forecast period from get_forecast()
        discount_percentage (float): Discount percentage as decimal (e.g., 0.15 for 15%)
        stock_multiplier (float): Multiplier for stock levels to simulate overstocking (default: 1.0)
    
    Returns:
        dict: Dictionary containing simulation results with keys:
            - current_stock: Current stock on hand (kg)
            - days_to_expire: Days until product expires
            - base_waste_kg: Waste without discount (kg)
            - promo_waste_kg: Waste with discount (kg)
            - base_revenue: Revenue without discount (VND)
            - promo_revenue: Revenue with discount (VND)
    """
    # Read current inventory
    inventory_df = pd.read_csv('current_inventory.csv')
    
    # Find the row for the given SKU
    product_row = inventory_df[inventory_df['sku'] == sku_id]
    if product_row.empty:
        raise ValueError(f"SKU {sku_id} not found in inventory")
    
    # Extract required values
    base_stock = product_row['stock_on_hand_kg'].iloc[0]
    current_stock = base_stock * stock_multiplier  # Apply multiplier for overstocking scenarios
    shelf_life_days = product_row['shelf_life_days'].iloc[0]
    cost_price = product_row['cost_price'].iloc[0]
    sale_price = product_row['list_price'].iloc[0]  # Use list_price as sale_price
    
    # Calculate days_to_expire
    # Inventory snapshot is dated 2025-12-30, shelf_life_days is the remaining days
    days_to_expire = shelf_life_days
    
    # Define the Price Elasticity Multiplier
    ELASTICITY_MULTIPLIER = 2.5
    
    # Calculate Promo scenario
    sales_uplift = discount_percentage * ELASTICITY_MULTIPLIER
    predicted_sales_with_promo = base_forecast_days * (1 + sales_uplift)
    promo_waste_kg = max(0, current_stock - predicted_sales_with_promo)
    promo_revenue = predicted_sales_with_promo * (sale_price * (1 - discount_percentage))
    
    # Calculate Baseline scenario (0% discount)
    base_waste_kg = max(0, current_stock - base_forecast_days)
    base_revenue = base_forecast_days * sale_price
    
    # Return dictionary with all results
    return {
        "current_stock": current_stock,
        "days_to_expire": days_to_expire,
        "base_waste_kg": base_waste_kg,
        "promo_waste_kg": promo_waste_kg,
        "base_revenue": base_revenue,
        "promo_revenue": promo_revenue
    }
