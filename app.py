import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analysis_engine import get_product_list, get_forecast, run_waste_simulation

# Page configuration
st.set_page_config(
    page_title="Inventory Forecasting & Waste Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Inventory Forecasting & Waste Simulation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered demand forecasting and promotional impact analysis</div>', unsafe_allow_html=True)

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'base_forecast_7_days' not in st.session_state:
    st.session_state.base_forecast_7_days = None
if 'selected_sku' not in st.session_state:
    st.session_state.selected_sku = None

# Sidebar
with st.sidebar:
    st.markdown("### Configuration")
    st.markdown("---")
    
    # Load product list
    try:
        product_dict = get_product_list()
        product_names = list(product_dict.keys())
        
        # Product selection dropdown
        st.markdown("**Product Selection**")
        selected_product_name = st.selectbox(
            "Choose a product",
            options=product_names,
            index=0,
            help="Choose a product to analyze",
            label_visibility="collapsed"
        )
        
        # Get corresponding SKU
        selected_sku = product_dict[selected_product_name]
        st.session_state.selected_sku = selected_sku
        
        # Display selected SKU
        st.markdown(f"""
            <div style='background-color: #e3f2fd; padding: 0.75rem; border-radius: 0.375rem; margin: 1rem 0;'>
                <div style='font-size: 0.75rem; color: #1976d2; font-weight: 600; margin-bottom: 0.25rem;'>SELECTED SKU</div>
                <div style='font-size: 1rem; font-weight: 700; color: #0d47a1;'>{selected_sku}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Forecast button
        generate_forecast_btn = st.button(
            "Generate Forecast",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Additional info
        st.markdown("""
            <div style='font-size: 0.85rem; color: #666; margin-top: 2rem;'>
                <strong>How to use:</strong>
                <ol style='margin-top: 0.5rem; padding-left: 1.25rem;'>
                    <li>Select a product</li>
                    <li>Generate forecast</li>
                    <li>Run promotion simulation</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading product list: {str(e)}")
        generate_forecast_btn = False

# Main content area
col1, col2 = st.columns([2, 1], gap="large")

# Forecast Section
with col1:
    st.markdown('<div class="section-header">Demand Forecast</div>', unsafe_allow_html=True)
    
    if generate_forecast_btn:
        with st.spinner("Generating forecast..."):
            try:
                # Call get_forecast
                model, forecast_df, total_forecast_7_days = get_forecast(selected_sku)
                
                # Store in session state
                st.session_state.forecast_data = forecast_df
                st.session_state.base_forecast_7_days = total_forecast_7_days
                
                st.success("Forecast generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
    
    # Display forecast if available
    if st.session_state.forecast_data is not None:
        forecast_df = st.session_state.forecast_data
        total_forecast = st.session_state.base_forecast_7_days
        
        # Show total forecasted demand in a styled card
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 1.5rem; color: white;'>
                <div style='font-size: 0.875rem; font-weight: 600; opacity: 0.9; margin-bottom: 0.25rem;'>
                    TOTAL FORECASTED DEMAND (NEXT 7 DAYS)
                </div>
                <div style='font-size: 2.5rem; font-weight: 700;'>
                    {total_forecast:.2f} kg
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create interactive Plotly chart
        fig = go.Figure()
        
        # Add yhat (forecast line)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast (yhat)',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>Forecast:</b> %{y:.2f} kg<extra></extra>'
        ))
        
        # Add confidence interval (upper bound)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            mode='lines',
            name='Upper Bound',
            line=dict(color='rgba(31, 119, 180, 0.3)', width=0),
            showlegend=True,
            hovertemplate='<b>Upper:</b> %{y:.2f} kg<extra></extra>'
        ))
        
        # Add confidence interval (lower bound) with fill
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            mode='lines',
            name='Lower Bound',
            line=dict(color='rgba(31, 119, 180, 0.3)', width=0),
            fillcolor='rgba(31, 119, 180, 0.2)',
            fill='tonexty',
            showlegend=True,
            hovertemplate='<b>Lower:</b> %{y:.2f} kg<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Demand Forecast: {selected_product_name}",
                font=dict(size=18, family="Arial, sans-serif", color="#2c3e50")
            ),
            xaxis_title="Date",
            yaxis_title="Quantity (kg)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e0e0e0",
                borderwidth=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # Add gridlines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show forecast table for next 7 days
        with st.expander("View Detailed Forecast Table (Next 7 Days)"):
            next_7_days = forecast_df.tail(7)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            next_7_days.columns = ['Date', 'Forecast (kg)', 'Lower Bound (kg)', 'Upper Bound (kg)']
            next_7_days['Date'] = pd.to_datetime(next_7_days['Date']).dt.strftime('%Y-%m-%d')
            
            # Format numeric columns
            for col in ['Forecast (kg)', 'Lower Bound (kg)', 'Upper Bound (kg)']:
                next_7_days[col] = next_7_days[col].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(
                next_7_days, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Forecast (kg)": st.column_config.TextColumn("Forecast (kg)", width="medium"),
                    "Lower Bound (kg)": st.column_config.TextColumn("Lower Bound (kg)", width="medium"),
                    "Upper Bound (kg)": st.column_config.TextColumn("Upper Bound (kg)", width="medium"),
                }
            )
    
    else:
        st.info("Click 'Generate Forecast' in the sidebar to view demand predictions")

# Promotion Simulation Section
with col2:
    st.markdown('<div class="section-header">Promotion Simulation</div>', unsafe_allow_html=True)
    
    if st.session_state.base_forecast_7_days is not None:
        st.markdown("**Simulation Parameters**")
        st.markdown("")
        
        # Discount percentage input
        discount_percentage = st.slider(
            "Discount Percentage",
            min_value=0,
            max_value=80,
            value=15,
            step=5,
            help="Enter discount percentage (0-80%)",
            format="%d%%"
        )
        
        # Convert to decimal
        discount_decimal = discount_percentage / 100.0
        
        st.markdown("")
        
        # Run simulation button
        run_simulation_btn = st.button(
            "Run Simulation",
            type="secondary",
            use_container_width=True
        )
        
        if run_simulation_btn:
            with st.spinner("Running simulation..."):
                try:
                    # Call run_waste_simulation
                    simulation_results = run_waste_simulation(
                        sku_id=st.session_state.selected_sku,
                        base_forecast_days=st.session_state.base_forecast_7_days,
                        discount_percentage=discount_decimal
                    )
                    
                    st.markdown("---")
                    st.markdown("###  Simulation Results")
                    
                    # Display metrics in a nice layout
                    st.metric(
                        label=" Current Stock",
                        value=f"{simulation_results['current_stock']:.2f} kg",
                        help="Current inventory on hand"
                    )
                    
                    st.metric(
                        label=" Days to Expire",
                        value=f"{simulation_results['days_to_expire']} days",
                        help="Remaining shelf life"
                    )
                    
                    st.markdown("---")
                    
                    # Waste comparison
                    col_waste1, col_waste2 = st.columns(2)
                    
                    with col_waste1:
                        st.metric(
                            label=" Base Waste",
                            value=f"{simulation_results['base_waste_kg']:.2f} kg",
                            help="Expected waste without discount"
                        )
                    
                    with col_waste2:
                        waste_delta = simulation_results['promo_waste_kg'] - simulation_results['base_waste_kg']
                        st.metric(
                            label="Promo Waste",
                            value=f"{simulation_results['promo_waste_kg']:.2f} kg",
                            delta=f"{waste_delta:.2f} kg",
                            delta_color="inverse",
                            help="Expected waste with discount"
                        )
                    
                    st.markdown("---")
                    
                    # Revenue comparison
                    col_rev1, col_rev2 = st.columns(2)
                    
                    with col_rev1:
                        st.metric(
                            label=" Base Revenue",
                            value=f"{simulation_results['base_revenue']:,.0f} VND",
                            help="Expected revenue without discount"
                        )
                    
                    with col_rev2:
                        revenue_delta = simulation_results['promo_revenue'] - simulation_results['base_revenue']
                        st.metric(
                            label=" Promo Revenue",
                            value=f"{simulation_results['promo_revenue']:,.0f} VND",
                            delta=f"{revenue_delta:,.0f} VND",
                            help="Expected revenue with discount"
                        )
                    
                    st.markdown("---")
                    
                    # Analysis
                    st.markdown("###  Analysis")
                    waste_reduction = simulation_results['base_waste_kg'] - simulation_results['promo_waste_kg']
                    waste_reduction_pct = (waste_reduction / simulation_results['base_waste_kg'] * 100) if simulation_results['base_waste_kg'] > 0 else 0
                    
                    if waste_reduction > 0:
                        st.success(f" Waste reduced by **{waste_reduction:.2f} kg** ({waste_reduction_pct:.1f}%)")
                    elif waste_reduction < 0:
                        st.warning(f" Waste increased by **{abs(waste_reduction):.2f} kg**")
                    else:
                        st.info("No change in waste")
                    
                    if revenue_delta > 0:
                        st.success(f" Revenue increased by **{revenue_delta:,.0f} VND**")
                    elif revenue_delta < 0:
                        st.error(f" Revenue decreased by **{abs(revenue_delta):,.0f} VND**")
                    else:
                        st.info(" No change in revenue")
                    
                except Exception as e:
                    st.error(f"Error running simulation: {str(e)}")
    else:
        st.info(" Generate a forecast first to run simulations")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; padding: 1rem 0;'>
        <div style='font-size: 0.875rem; font-weight: 500;'>Inventory Forecasting & Waste Simulation</div>
        <div style='font-size: 0.75rem; margin-top: 0.25rem;'>Powered by Prophet & Streamlit</div>
    </div>
    """,
    unsafe_allow_html=True
)
