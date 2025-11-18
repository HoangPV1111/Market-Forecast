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

# Custom CSS - Professional Data-Centric Dashboard (Prediko-inspired, Red & White)
st.markdown("""
    <style>
    /* Global styles - Clean white background with maximum readability */
    .main {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
    }
    
    /* Minimalist header - Less dominant */
    .main-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
        letter-spacing: -0.3px;
    }
    .sub-header {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Filter bar - Compact and integrated */
    .filter-bar {
        background: white;
        padding: 0.875rem 1.25rem;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    
    /* Section headers - Subtle and clean */
    .section-header {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        padding-bottom: 0;
        border-bottom: none;
    }
    
    /* Integrated KPI cards - Tight grouping */
    .metric-card {
        background: white;
        padding: 1.25rem 1.5rem;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        flex: 1;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        transition: box-shadow 0.15s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .metric-label {
        font-size: 0.8125rem;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: none;
        letter-spacing: 0;
    }
    
    .metric-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.2;
    }
    
    .metric-value-red {
        color: #d71921;
    }
    
    .metric-subtitle {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.375rem;
        font-weight: 400;
    }
    
    .metric-trend {
        font-size: 0.8125rem;
        font-weight: 600;
        margin-top: 0.375rem;
    }
    
    .trend-up {
        color: #d71921;
    }
    
    .trend-down {
        color: #9ca3af;
    }
    
    /* Status tags - Rectangular, integrated */
    .status-tag {
        display: inline-block;
        padding: 0.25rem 0.625rem;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    
    .status-healthy {
        background: #e0f2fe;
        color: #0369a1;
    }
    
    .status-risk {
        background: #d71921;
        color: white;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Unified chart container */
    .chart-container {
        background: white;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    
    .chart-title {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    /* Action card - Distinct visual treatment */
    .action-card {
        background: #fafafa;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    
    /* Hide sidebar by default */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Button styling - Red primary action */
    .stButton > button {
        background-color: #d71921;
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.625rem 1.5rem;
        transition: all 0.15s ease;
        box-shadow: 0 1px 2px rgba(215, 25, 33, 0.1);
    }
    
    .stButton > button:hover {
        background-color: #b01419;
        box-shadow: 0 2px 4px rgba(215, 25, 33, 0.2);
    }
    
    /* Streamlit metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8125rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: none;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.8125rem;
        font-weight: 600;
    }
    
    /* Table styling - Clean, minimal lines */
    [data-testid="stDataFrame"] {
        border: none;
    }
    
    /* Slider styling - Red accent */
    .stSlider > div > div > div > div {
        background-color: #d71921;
    }
    
    /* Info/Success/Error messages */
    .stAlert {
        border-radius: 5px;
        border: 1px solid #e5e7eb;
    }
    
    /* Selectbox styling */
    [data-testid="stSelectbox"] label {
        font-size: 0.8125rem;
        color: #374151;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description - More subtle
st.markdown('<div class="main-header">Dự Báo Nhu Cầu</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Phân tích và tối ưu tồn kho</div>', unsafe_allow_html=True)

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'base_forecast_7_days' not in st.session_state:
    st.session_state.base_forecast_7_days = None
if 'selected_sku' not in st.session_state:
    st.session_state.selected_sku = None

# Integrated filter bar (replacing sidebar)
try:
    product_dict = get_product_list()
    product_names = list(product_dict.keys())
    
    # Filter bar layout
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    
    with filter_col1:
        selected_product_name = st.selectbox(
            "Sản phẩm",
            options=product_names,
            index=0,
            help="Chọn sản phẩm để phân tích"
        )
    
    with filter_col2:
        selected_sku = product_dict[selected_product_name]
        st.session_state.selected_sku = selected_sku
        st.markdown(f"""
            <div style='padding-top: 1.75rem;'>
                <span style='font-size: 0.8125rem; color: #6b7280; font-weight: 500;'>SKU: </span>
                <span style='font-size: 0.875rem; color: #d71921; font-weight: 600;'>{selected_sku}</span>
            </div>
        """, unsafe_allow_html=True)
    
    with filter_col3:
        st.markdown("<div style='padding-top: 0.5rem;'></div>", unsafe_allow_html=True)
        generate_forecast_btn = st.button(
            "Tạo Dự Báo",
            type="primary",
            use_container_width=True
        )
    
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"Lỗi tải danh sách sản phẩm: {str(e)}")
    generate_forecast_btn = False

# Main content area - Full width layout
# Forecast Section
st.markdown('<div class="section-header">Tổng Quan Dự Báo</div>', unsafe_allow_html=True)

if generate_forecast_btn:
    with st.spinner("Đang tạo dự báo..."):
        try:
            # Call get_forecast
            model, forecast_df, total_forecast_7_days = get_forecast(selected_sku)
            
            # Store in session state
            st.session_state.forecast_data = forecast_df
            st.session_state.base_forecast_7_days = total_forecast_7_days
            
            st.success("Dự báo đã được tạo thành công!")
            
        except Exception as e:
            st.error(f"Lỗi tạo dự báo: {str(e)}")

# Display forecast if available
if st.session_state.forecast_data is not None:
    forecast_df = st.session_state.forecast_data
    total_forecast = st.session_state.base_forecast_7_days
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Tổng Dự Báo</div>
                <div class='metric-value'>{:.1f} kg</div>
                <div class='metric-subtitle'>7 ngày tới</div>
            </div>
        """.format(total_forecast), unsafe_allow_html=True)
    
    with col2:
        avg_daily = total_forecast / 7
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Nhu Cầu TB/Ngày</div>
                <div class='metric-value'>{:.1f} kg</div>
                <div class='metric-subtitle'>Trung bình mỗi ngày</div>
            </div>
        """.format(avg_daily), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Sản Phẩm</div>
                <div class='metric-value' style='font-size: 1.125rem;'>{}</div>
                <div class='metric-subtitle'>SKU đã chọn</div>
            </div>
        """.format(selected_product_name[:20] + "..." if len(selected_product_name) > 20 else selected_product_name), unsafe_allow_html=True)
    
    with col4:
        # Get current stock from inventory
        try:
            inventory_df = pd.read_csv('current_inventory.csv')
            current_stock_row = inventory_df[inventory_df['sku'] == selected_sku]
            if not current_stock_row.empty:
                current_stock = current_stock_row['stock_on_hand_kg'].values[0]
                stock_status = "Đủ Hàng" if current_stock > total_forecast else "Cần Nhập"
                status_class = "status-healthy" if current_stock > total_forecast else "status-risk"
            else:
                stock_status = "Chưa Rõ"
                status_class = "status-warning"
                current_stock = 0
        except:
            stock_status = "Chưa Rõ"
            status_class = "status-warning"
            current_stock = 0
        
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>Trạng Thái Tồn</div>
                <div class='metric-value' style='font-size: 1.125rem;'><span class='status-badge {}'>{}</span></div>
                <div class='metric-subtitle'>{:.1f} kg tồn kho</div>
            </div>
        """.format(status_class, stock_status, current_stock), unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Chart and table layout
    chart_col, table_col = st.columns([2, 1])
    
    with chart_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**Biểu Đồ Dự Báo Nhu Cầu Theo Ngày**")
        
        # Create interactive Plotly chart with Winmart red theme
        fig = go.Figure()
        
        # Add yhat (forecast line)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Dự báo',
            line=dict(color='#d71921', width=3),
            hovertemplate='<b>%{x}</b><br>Dự báo: %{y:.2f} kg<extra></extra>'
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            mode='lines',
            name='Ngưỡng trên',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            mode='lines',
            name='Ngưỡng dưới',
            line=dict(width=0),
            fillcolor='rgba(215, 25, 33, 0.1)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Ngày",
            yaxis_title="Nhu Cầu (kg)",
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='white',
            margin=dict(l=60, r=20, t=20, b=60),
            font=dict(family="Segoe UI, Tahoma, sans-serif", size=12, color="#1a1a1a")
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230,230,230,1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(230,230,230,1)')
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with table_col:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.markdown("**Chi Tiết Dự Báo 7 Ngày**")
        
        next_7_days = forecast_df.tail(7)[['ds', 'yhat']].copy()
        next_7_days.columns = ['Ngày', 'Nhu Cầu (kg)']
        next_7_days['Ngày'] = pd.to_datetime(next_7_days['Ngày']).dt.strftime('%d/%m')
        next_7_days['Nhu Cầu (kg)'] = next_7_days['Nhu Cầu (kg)'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(
            next_7_days,
            use_container_width=True,
            hide_index=True,
            height=350
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Discount simulation section
    st.markdown('<div class="section-header">Mô Phỏng Tác Động Giảm Giá</div>', unsafe_allow_html=True)
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        discount_percentage = st.slider(
            "Mức Giảm Giá",
            min_value=0,
            max_value=80,
            value=15,
            step=5,
            help="Điều chỉnh % giảm giá",
            format="%d%%"
        )
        
        discount_decimal = discount_percentage / 100.0
        
        run_simulation_btn = st.button(
            "Chạy Mô Phỏng",
            type="primary",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with sim_col2:
        if run_simulation_btn:
            with st.spinner("Đang chạy mô phỏng..."):
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
                            label="Giảm Hao Hụt",
                            value=f"{simulation_results['promo_waste_kg']:.1f} kg",
                            delta=f"{waste_delta:.1f} kg",
                            delta_color="inverse"
                        )
                    
                    with res_col2:
                        revenue_delta = simulation_results['promo_revenue'] - simulation_results['base_revenue']
                        st.metric(
                            label="Tác Động Doanh Thu",
                            value=f"{simulation_results['promo_revenue']:,.0f} VND",
                            delta=f"{revenue_delta:,.0f} VND"
                        )
                    
                    with res_col3:
                        st.metric(
                            label="Tồn Kho Hiện Tại",
                            value=f"{simulation_results['current_stock']:.1f} kg",
                            delta=f"Còn {simulation_results['days_to_expire']} ngày"
                        )
                    
                    # Impact summary
                    waste_reduction = simulation_results['base_waste_kg'] - simulation_results['promo_waste_kg']
                    waste_reduction_pct = (waste_reduction / simulation_results['base_waste_kg'] * 100) if simulation_results['base_waste_kg'] > 0 else 0
                    
                    if waste_reduction > 0 and revenue_delta > 0:
                        summary_color = "#0369a1"
                        summary_bg = "#f0f9ff"
                        summary_text = f"Khuyến nghị: Giảm giá giúp giảm hao hụt {waste_reduction:.1f} kg ({waste_reduction_pct:.0f}%) và tăng doanh thu {revenue_delta:,.0f} VND"
                    elif waste_reduction > 0 and revenue_delta <= 0:
                        summary_color = "#d97706"
                        summary_bg = "#fffbeb"
                        summary_text = f"Cân nhắc: Hao hụt giảm {waste_reduction:.1f} kg nhưng doanh thu giảm {abs(revenue_delta):,.0f} VND"
                    else:
                        summary_color = "#d71921"
                        summary_bg = "#fff5f5"
                        summary_text = f"Không khuyến nghị: Doanh thu thay đổi {revenue_delta:,.0f} VND, hao hụt còn {simulation_results['promo_waste_kg']:.1f} kg"
                    
                    st.markdown(f"""
                        <div style='background: {summary_bg}; border-left: 4px solid {summary_color}; 
                                    padding: 1.125rem; border-radius: 4px; font-size: 0.9375rem; color: #1a1a1a; margin-top: 1.25rem; font-family: "Segoe UI", Tahoma, sans-serif; line-height: 1.6;'>
                            {summary_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")
        else:
            st.info("Điều chỉnh mức giảm giá và nhấn 'Chạy Mô Phỏng' để xem kết quả")

else:
    st.info("Nhấn 'Tạo Dự Báo' ở thanh bên để bắt đầu")

# Footer
st.markdown("<div style='margin-top: 4rem; padding-top: 1.5rem; border-top: 2px solid #d71921;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #999999; padding: 1rem 0; font-family: "Segoe UI", Tahoma, sans-serif;'>
        <div style='font-size: 0.8125rem; color: #666666;'>Hệ Thống Quản Lý Dự Báo & Giảm Hao Hụt</div>
        <div style='font-size: 0.75rem; margin-top: 0.375rem; color: #999999;'>Powered by Prophet ML</div>
    </div>
    """,
    unsafe_allow_html=True
)
