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

# Custom CSS - Winmart B2B Professional Dashboard (Red & White Theme)
st.markdown("""
    <style>
    /* Global styles */
    .main {
        background-color: #ffffff;
    }
    
    /* Header styles */
    .main-header {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.4px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .sub-header {
        font-size: 0.9375rem;
        color: #666666;
        margin-bottom: 2rem;
        font-weight: 400;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #d71921;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #d71921;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #e6e6e6;
        flex: 1;
        box-shadow: 0 1px 3px rgba(215, 25, 33, 0.08);
        transition: box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 2px 6px rgba(215, 25, 33, 0.12);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #666666;
        font-weight: 600;
        margin-bottom: 0.625rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #d71921;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        line-height: 1.2;
    }
    
    .metric-subtitle {
        font-size: 0.8125rem;
        color: #999999;
        margin-top: 0.5rem;
        font-weight: 400;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        letter-spacing: 0.3px;
    }
    
    .status-healthy {
        background: #f0f9ff;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    
    .status-risk {
        background: #fff5f5;
        color: #d71921;
        border: 1px solid #fecaca;
    }
    
    .status-warning {
        background: #fffbeb;
        color: #d97706;
        border: 1px solid #fde68a;
    }
    
    /* Table container */
    .table-container {
        background: white;
        border-radius: 4px;
        border: 1px solid #e6e6e6;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(215, 25, 33, 0.08);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 2px solid #d71921;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 0.875rem;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #d71921;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 600;
        letter-spacing: 0.3px;
        font-size: 0.9375rem;
        padding: 0.625rem 1.25rem;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #b91419;
        color: white;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.625rem;
        font-weight: 700;
        color: #d71921;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8125rem;
        color: #666666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #e6e6e6;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 4px;
        border: 1px solid #e6e6e6;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(215, 25, 33, 0.08);
    }
    
    /* Info/Success/Error messages */
    .stAlert {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">Quản Lý Dự Báo Nhu Cầu</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Phân tích dữ liệu bán hàng và lập kế hoạch tồn kho tối ưu</div>', unsafe_allow_html=True)

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'base_forecast_7_days' not in st.session_state:
    st.session_state.base_forecast_7_days = None
if 'selected_sku' not in st.session_state:
    st.session_state.selected_sku = None

# Sidebar
with st.sidebar:
    st.markdown("### Bộ Lọc & Cài Đặt")
    
    # Load product list
    try:
        product_dict = get_product_list()
        product_names = list(product_dict.keys())
        
        # Product selection dropdown
        selected_product_name = st.selectbox(
            "Chọn Sản Phẩm",
            options=product_names,
            index=0,
            help="Chọn sản phẩm để phân tích"
        )
        
        # Get corresponding SKU
        selected_sku = product_dict[selected_product_name]
        st.session_state.selected_sku = selected_sku
        
        # Display selected SKU
        st.markdown(f"""
            <div style='background: white; border: 1px solid #e6e6e6; padding: 0.875rem; border-radius: 4px; margin: 1.25rem 0; box-shadow: 0 1px 2px rgba(215, 25, 33, 0.06);'>
                <div style='font-size: 0.6875rem; color: #666666; font-weight: 600; margin-bottom: 0.375rem; text-transform: uppercase; letter-spacing: 0.8px;'>MÃ SKU</div>
                <div style='font-size: 1.0625rem; font-weight: 700; color: #d71921;'>{selected_sku}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Forecast button
        generate_forecast_btn = st.button(
            "Tạo Dự Báo",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<div style='margin: 2rem 0; border-top: 2px solid #d71921;'></div>", unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("""
            <div style='font-size: 0.875rem; color: #666666; font-family: "Segoe UI", Tahoma, sans-serif;'>
                <div style='font-weight: 600; color: #1a1a1a; margin-bottom: 0.875rem; font-size: 0.9375rem;'>Hướng Dẫn Nhanh</div>
                <div style='margin-bottom: 0.625rem; line-height: 1.6;'>1. Chọn sản phẩm cần phân tích</div>
                <div style='margin-bottom: 0.625rem; line-height: 1.6;'>2. Nhấn "Tạo Dự Báo" để xem kết quả</div>
                <div style='margin-bottom: 0.625rem; line-height: 1.6;'>3. Điều chỉnh giảm giá và mô phỏng</div>
            </div>
        """, unsafe_allow_html=True)
        
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
