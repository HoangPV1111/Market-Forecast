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

# Custom CSS - Prediko-inspired design with data table styling
st.markdown("""
    <style>
    /* Global styles */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styles */
    .main-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
        letter-spacing: -0.3px;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #718096;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Top bar with filters and actions */
    .top-bar {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
    }
    
    /* Metric cards in a row */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        flex: 1;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #718096;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    .metric-subtitle {
        font-size: 0.75rem;
        color: #a0aec0;
        margin-top: 0.25rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-healthy {
        background: #c6f6d5;
        color: #22543d;
    }
    
    .status-risk {
        background: #fed7d7;
        color: #742a2a;
    }
    
    .status-warning {
        background: #feebc8;
        color: #7c2d12;
    }
    
    /* Table container */
    .table-container {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        font-weight: 500;
        color: #4a5568;
        font-size: 0.875rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        letter-spacing: 0.025em;
        font-size: 0.875rem;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: #718096;
        font-weight: 500;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border: none;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Demand Planning</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Review your past sales data and plan for the year ahead</div>', unsafe_allow_html=True)

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'base_forecast_7_days' not in st.session_state:
    st.session_state.base_forecast_7_days = None
if 'selected_sku' not in st.session_state:
    st.session_state.selected_sku = None

# Sidebar
with st.sidebar:
    st.markdown("### Filters & Settings")
    
    # Load product list
    try:
        product_dict = get_product_list()
        product_names = list(product_dict.keys())
        
        # Product selection dropdown
        selected_product_name = st.selectbox(
            "Product",
            options=product_names,
            index=0,
            help="Choose a product to analyze"
        )
        
        # Get corresponding SKU
        selected_sku = product_dict[selected_product_name]
        st.session_state.selected_sku = selected_sku
        
        # Display selected SKU
        st.markdown(f"""
            <div style='background: #f7fafc; border: 1px solid #e2e8f0; padding: 0.75rem; border-radius: 6px; margin: 1rem 0;'>
                <div style='font-size: 0.7rem; color: #718096; font-weight: 600; margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing: 0.5px;'>SKU</div>
                <div style='font-size: 1rem; font-weight: 600; color: #2d3748;'>{selected_sku}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Forecast button
        generate_forecast_btn = st.button(
            " Generate Forecast",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<div style='margin: 2rem 0; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("""
            <div style='font-size: 0.875rem; color: #718096;'>
                <div style='font-weight: 600; color: #4a5568; margin-bottom: 0.75rem;'>Quick Actions</div>
                <div style='margin-bottom: 0.5rem;'>• Select product variant</div>
                <div style='margin-bottom: 0.5rem;'>• Generate 7-day forecast</div>
                <div style='margin-bottom: 0.5rem;'>• Simulate discount impact</div>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        generate_forecast_btn = False

# Main content area - Full width layout
# Forecast Section
st.markdown('<div class="section-header">Forecast Overview</div>', unsafe_allow_html=True)

if generate_forecast_btn:
    with st.spinner("Generating forecast..."):
        try:
            # Call get_forecast
            model, forecast_df, total_forecast_7_days = get_forecast(selected_sku)
            
            # Store in session state
            st.session_state.forecast_data = forecast_df
            st.session_state.base_forecast_7_days = total_forecast_7_days
            
            st.success("✓ Forecast generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")

# Display forecast if available
if st.session_state.forecast_data is not None:
    forecast_df = st.session_state.forecast_data
    total_forecast = st.session_state.base_forecast_7_days
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Total Forecast</div>
                <div class='metric-value'>{:.1f} kg</div>
                <div class='metric-subtitle'>Next 7 days</div>
            </div>
        """.format(total_forecast), unsafe_allow_html=True)
    
    with col2:
        avg_daily = total_forecast / 7
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Avg Daily Demand</div>
                <div class='metric-value'>{:.1f} kg</div>
                <div class='metric-subtitle'>Per day</div>
            </div>
        """.format(avg_daily), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Product</div>
                <div class='metric-value' style='font-size: 1.1rem;'>{}</div>
                <div class='metric-subtitle'>Selected SKU</div>
            </div>
        """.format(selected_product_name[:20] + "..." if len(selected_product_name) > 20 else selected_product_name), unsafe_allow_html=True)
    
    with col4:
        # Get current stock from inventory
        try:
            inventory_df = pd.read_csv('current_inventory.csv')
            current_stock_row = inventory_df[inventory_df['sku'] == selected_sku]
            if not current_stock_row.empty:
                current_stock = current_stock_row['stock_on_hand_kg'].values[0]
                stock_status = "Healthy" if current_stock > total_forecast else "At Risk"
                status_class = "status-healthy" if current_stock > total_forecast else "status-risk"
            else:
                stock_status = "Unknown"
                status_class = "status-warning"
                current_stock = 0
        except:
            stock_status = "Unknown"
            status_class = "status-warning"
            current_stock = 0
        
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Stock Status</div>
                <div class='metric-value' style='font-size: 1.1rem;'><span class='status-badge {}'>{}</span></div>
                <div class='metric-subtitle'>{:.1f} kg on hand</div>
            </div>
        """.format(status_class, stock_status, current_stock), unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Chart and table layout
    chart_col, table_col = st.columns([2, 1])
    
    with chart_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Daily Demand Projection**")
        
        # Create interactive Plotly chart
        fig = go.Figure()
        
        # Add yhat (forecast line)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='#5a67d8', width=2.5),
            hovertemplate='<b>%{x}</b><br>Forecast: %{y:.2f} kg<extra></extra>'
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            mode='lines',
            name='Upper Bound',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            mode='lines',
            name='Lower Bound',
            line=dict(width=0),
            fillcolor='rgba(90, 103, 216, 0.15)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Demand (kg)",
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(248,249,250,0.3)',
            paper_bgcolor='white',
            margin=dict(l=50, r=20, t=20, b=50),
            font=dict(family="Arial, sans-serif", size=11, color="#4a5568")
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(226,232,240,0.8)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(226,232,240,0.8)')
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with table_col:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.markdown("**7-Day Forecast Detail**")
        
        next_7_days = forecast_df.tail(7)[['ds', 'yhat']].copy()
        next_7_days.columns = ['Date', 'Demand (kg)']
        next_7_days['Date'] = pd.to_datetime(next_7_days['Date']).dt.strftime('%b %d')
        next_7_days['Demand (kg)'] = next_7_days['Demand (kg)'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(
            next_7_days,
            use_container_width=True,
            hide_index=True,
            height=350
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Discount simulation section
    st.markdown('<div class="section-header">Discount Impact Simulator</div>', unsafe_allow_html=True)
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        discount_percentage = st.slider(
            "Discount Rate",
            min_value=0,
            max_value=80,
            value=15,
            step=5,
            help="Adjust discount percentage",
            format="%d%%"
        )
        
        discount_decimal = discount_percentage / 100.0
        
        run_simulation_btn = st.button(
            "⚡ Run Simulation",
            type="primary",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with sim_col2:
        if run_simulation_btn:
            with st.spinner("Running simulation..."):
                try:
                    simulation_results = run_waste_simulation(
                        sku_id=st.session_state.selected_sku,
                        base_forecast_days=st.session_state.base_forecast_7_days,
                        discount_percentage=discount_decimal
                    )
                    
                    st.markdown('<div class="table-container">', unsafe_allow_html=True)
                    
                    # Results in metric cards
                    res_col1, res_col2, res_col3 = st.columns(3)
                    
                    with res_col1:
                        waste_delta = simulation_results['promo_waste_kg'] - simulation_results['base_waste_kg']
                        st.metric(
                            label="Waste Reduction",
                            value=f"{simulation_results['promo_waste_kg']:.1f} kg",
                            delta=f"{waste_delta:.1f} kg",
                            delta_color="inverse"
                        )
                    
                    with res_col2:
                        revenue_delta = simulation_results['promo_revenue'] - simulation_results['base_revenue']
                        st.metric(
                            label="Revenue Impact",
                            value=f"{simulation_results['promo_revenue']:,.0f} VND",
                            delta=f"{revenue_delta:,.0f} VND"
                        )
                    
                    with res_col3:
                        st.metric(
                            label="Stock on Hand",
                            value=f"{simulation_results['current_stock']:.1f} kg",
                            delta=f"{simulation_results['days_to_expire']} days left"
                        )
                    
                    # Impact summary
                    waste_reduction = simulation_results['base_waste_kg'] - simulation_results['promo_waste_kg']
                    waste_reduction_pct = (waste_reduction / simulation_results['base_waste_kg'] * 100) if simulation_results['base_waste_kg'] > 0 else 0
                    
                    if waste_reduction > 0 and revenue_delta > 0:
                        summary_color = "#48bb78"
                        summary_bg = "#f0fff4"
                        summary_text = f"✓ Recommended: Discount reduces waste by {waste_reduction:.1f} kg ({waste_reduction_pct:.0f}%) and increases revenue by {revenue_delta:,.0f} VND"
                    elif waste_reduction > 0 and revenue_delta <= 0:
                        summary_color = "#ed8936"
                        summary_bg = "#fffaf0"
                        summary_text = f"⚠ Caution: Waste reduced by {waste_reduction:.1f} kg but revenue decreases by {abs(revenue_delta):,.0f} VND"
                    else:
                        summary_color = "#f56565"
                        summary_bg = "#fff5f5"
                        summary_text = f"✗ Not recommended: Revenue impact {revenue_delta:,.0f} VND with waste at {simulation_results['promo_waste_kg']:.1f} kg"
                    
                    st.markdown(f"""
                        <div style='background: {summary_bg}; border-left: 3px solid {summary_color}; 
                                    padding: 1rem; border-radius: 6px; font-size: 0.875rem; color: #2d3748; margin-top: 1rem;'>
                            {summary_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Adjust discount rate and click 'Run Simulation' to see impact")

else:
    st.info("Click 'Generate Forecast' in the sidebar to get started")

# Footer
st.markdown("<div style='margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #a0aec0; padding: 1rem 0;'>
        <div style='font-size: 0.75rem;'>Demand Planning & Waste Reduction</div>
        <div style='font-size: 0.7rem; margin-top: 0.25rem;'>Powered by Prophet ML</div>
    </div>
    """,
    unsafe_allow_html=True
)
