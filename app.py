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

# Custom CSS - Clean, modern design inspired by Prediko
st.markdown("""
    <style>
    /* Global styles */
    .main {
        background-color: #fafbfc;
    }
    
    /* Header styles */
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    /* Card styles */
    .info-card {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .metric-card-large {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.15);
        margin-bottom: 1.5rem;
    }
    
    /* SKU display */
    .sku-badge {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        font-weight: 500;
        color: #374151;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        letter-spacing: 0.025em;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">SKU Demand Forecasting</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Predict demand, optimize inventory, and reduce waste with AI-powered forecasting</div>', unsafe_allow_html=True)

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'base_forecast_7_days' not in st.session_state:
    st.session_state.base_forecast_7_days = None
if 'selected_sku' not in st.session_state:
    st.session_state.selected_sku = None

# Sidebar
with st.sidebar:
    st.markdown("### Product Selection")
    
    # Load product list
    try:
        product_dict = get_product_list()
        product_names = list(product_dict.keys())
        
        # Product selection dropdown
        selected_product_name = st.selectbox(
            "Select Product",
            options=product_names,
            index=0,
            help="Choose a product variant to forecast"
        )
        
        # Get corresponding SKU
        selected_sku = product_dict[selected_product_name]
        st.session_state.selected_sku = selected_sku
        
        # Display selected SKU with cleaner design
        st.markdown(f"""
            <div class='sku-badge'>
                <div style='font-size: 0.75rem; color: #3b82f6; font-weight: 600; margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing: 0.5px;'>SKU</div>
                <div style='font-size: 1.125rem; font-weight: 600; color: #1a1a1a;'>{selected_sku}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Forecast button
        generate_forecast_btn = st.button(
            "Generate Forecast",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<div style='margin: 2rem 0; border-top: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
        
        # Additional info with cleaner design
        st.markdown("""
            <div style='font-size: 0.875rem; color: #6b7280;'>
                <div style='font-weight: 600; color: #374151; margin-bottom: 0.75rem;'>Quick Guide</div>
                <div style='margin-bottom: 0.5rem;'>1. Select a product variant</div>
                <div style='margin-bottom: 0.5rem;'>2. Click Generate Forecast</div>
                <div style='margin-bottom: 0.5rem;'>3. Adjust discount & run simulation</div>
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
            <div class='metric-card-large'>
                <div style='font-size: 0.8rem; font-weight: 500; opacity: 0.95; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;'>
                    7-Day Demand Forecast
                </div>
                <div style='font-size: 2.25rem; font-weight: 600; margin-bottom: 0.25rem;'>
                    {total_forecast:.2f} kg
                </div>
                <div style='font-size: 0.875rem; opacity: 0.9;'>
                    Total expected demand for next 7 days
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
        
        # Update layout with cleaner design
        fig.update_layout(
            title=dict(
                text=f"Daily Demand Projection",
                font=dict(size=16, family="Arial, sans-serif", color="#1a1a1a", weight=600)
            ),
            xaxis_title="Date",
            yaxis_title="Daily Demand (kg)",
            hovermode='x unified',
            template='plotly_white',
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="#e5e7eb",
                borderwidth=1,
                font=dict(size=11)
            ),
            plot_bgcolor='rgba(250,251,252,0.5)',
            paper_bgcolor='white',
            margin=dict(l=60, r=20, t=80, b=60)
        )
        
        # Add gridlines with lighter color
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(229,231,235,0.8)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(229,231,235,0.8)')
        
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
    st.markdown('<div class="section-header">Discount Impact Simulator</div>', unsafe_allow_html=True)
    
    if st.session_state.base_forecast_7_days is not None:
        # Discount percentage input
        discount_percentage = st.slider(
            "Discount Rate",
            min_value=0,
            max_value=80,
            value=15,
            step=5,
            help="Adjust discount to see impact on waste and revenue",
            format="%d%%"
        )
        
        # Convert to decimal
        discount_decimal = discount_percentage / 100.0
        
        # Run simulation button
        run_simulation_btn = st.button(
            "Run Simulation",
            type="primary",
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
                    
                    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
                    st.markdown("#### Current Inventory Status")
                    
                    # Display metrics in a nice layout
                    st.metric(
                        label="Stock on Hand",
                        value=f"{simulation_results['current_stock']:.2f} kg",
                        help="Current inventory quantity"
                    )
                    
                    st.metric(
                        label="Shelf Life Remaining",
                        value=f"{simulation_results['days_to_expire']} days",
                        help="Days until product expires"
                    )
                    
                    st.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
                    
                    # Waste comparison
                    st.markdown("#### Waste Projection")
                    col_waste1, col_waste2 = st.columns(2)
                    
                    with col_waste1:
                        st.metric(
                            label="No Discount",
                            value=f"{simulation_results['base_waste_kg']:.2f} kg",
                            help="Expected waste without promotion"
                        )
                    
                    with col_waste2:
                        waste_delta = simulation_results['promo_waste_kg'] - simulation_results['base_waste_kg']
                        st.metric(
                            label="With Discount",
                            value=f"{simulation_results['promo_waste_kg']:.2f} kg",
                            delta=f"{waste_delta:.2f} kg",
                            delta_color="inverse",
                            help="Expected waste with promotion"
                        )
                    
                    st.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
                    
                    # Revenue comparison
                    st.markdown("#### Revenue Projection")
                    col_rev1, col_rev2 = st.columns(2)
                    
                    with col_rev1:
                        st.metric(
                            label="No Discount",
                            value=f"{simulation_results['base_revenue']:,.0f} VND",
                            help="Expected revenue without promotion"
                        )
                    
                    with col_rev2:
                        revenue_delta = simulation_results['promo_revenue'] - simulation_results['base_revenue']
                        st.metric(
                            label="With Discount",
                            value=f"{simulation_results['promo_revenue']:,.0f} VND",
                            delta=f"{revenue_delta:,.0f} VND",
                            help="Expected revenue with promotion"
                        )
                    
                    st.markdown("<div style='margin: 1.5rem 0; border-top: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
                    
                    # Analysis with cleaner design
                    st.markdown("#### Impact Summary")
                    waste_reduction = simulation_results['base_waste_kg'] - simulation_results['promo_waste_kg']
                    waste_reduction_pct = (waste_reduction / simulation_results['base_waste_kg'] * 100) if simulation_results['base_waste_kg'] > 0 else 0
                    
                    # Create summary card
                    if waste_reduction > 0 and revenue_delta > 0:
                        summary_color = "#10b981"
                        summary_bg = "#d1fae5"
                        summary_text = f"Discount reduces waste by **{waste_reduction:.2f} kg** ({waste_reduction_pct:.1f}%) and increases revenue by **{revenue_delta:,.0f} VND**"
                    elif waste_reduction > 0 and revenue_delta <= 0:
                        summary_color = "#f59e0b"
                        summary_bg = "#fef3c7"
                        summary_text = f"Discount reduces waste by **{waste_reduction:.2f} kg** but decreases revenue by **{abs(revenue_delta):,.0f} VND**"
                    elif waste_reduction <= 0 and revenue_delta > 0:
                        summary_color = "#f59e0b"
                        summary_bg = "#fef3c7"
                        summary_text = f"Discount increases revenue by **{revenue_delta:,.0f} VND** but waste remains at **{simulation_results['promo_waste_kg']:.2f} kg**"
                    else:
                        summary_color = "#ef4444"
                        summary_bg = "#fee2e2"
                        summary_text = f"Discount decreases revenue by **{abs(revenue_delta):,.0f} VND** with waste at **{simulation_results['promo_waste_kg']:.2f} kg**"
                    
                    st.markdown(f"""
                        <div style='background: {summary_bg}; border-left: 3px solid {summary_color}; 
                                    padding: 1rem; border-radius: 6px; font-size: 0.875rem; color: #1a1a1a;'>
                            {summary_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error running simulation: {str(e)}")
    else:
        st.info("Generate a forecast first to enable simulation")

# Footer
st.markdown("<div style='margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #6b7280; padding: 1rem 0;'>
        <div style='font-size: 0.8rem;'>SKU Demand Forecasting & Waste Reduction Tool</div>
        <div style='font-size: 0.75rem; margin-top: 0.25rem; color: #9ca3af;'>Powered by Prophet ML & Streamlit</div>
    </div>
    """,
    unsafe_allow_html=True
)
