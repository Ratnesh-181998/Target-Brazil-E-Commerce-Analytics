import os
from pathlib import Path
import logging
import warnings

import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from run_target_queries import init_db

# Configure logging
# Configure logging
if 'log_data' not in st.session_state:
    st.session_state['log_data'] = []

class StreamlitLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        st.session_state['log_data'].append(log_entry)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers on rerun
if not logger.handlers:
    # File handler
    file_handler = logging.FileHandler('target_app.log')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Streamlit session state handler
    st_handler = StreamlitLogHandler()
    st_handler.setFormatter(file_formatter)
    logger.addHandler(st_handler)

@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    return init_db()

def run_query(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.execute(sql).fetch_df()

def main() -> None:
    st.set_page_config(
        page_title="Target Brazil E‑Commerce Analytics",
        layout="wide",
        page_icon="🛒",
        initial_sidebar_state="expanded",
    )

    # Enhanced Custom CSS matching Walmart style
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            background-attachment: fixed;
        }
        .block-container {
            background: rgba(17, 24, 39, 0.85);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.7);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(139, 92, 246, 0.2);
        }
        h1 {
            background: linear-gradient(135deg, #a78bfa 0%, #f472b6 50%, #fb923c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 1rem;
            animation: fadeInDown 1s ease-in-out;
            letter-spacing: -1px;
        }
        h2 { 
            color: #f3f4f6 !important; 
            border-bottom: 3px solid #8b5cf6; 
            padding-bottom: 0.5rem; 
            margin-top: 2rem; 
            font-weight: 700 !important;
            text-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);
        }
        h3 { 
            color: #e5e7eb !important; 
            margin-top: 1.5rem; 
            font-weight: 600 !important; 
        }
        p, li, span, div { color: #cbd5e1; }
        
        [data-testid="stMetricValue"] {
            background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 0.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        [data-testid="stMetricLabel"] { 
            color: #9ca3af !important; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.75rem !important;
        }
        
        .stTabs [data-baseweb="tab-list"] { 
            gap: 12px; 
            background-color: rgba(17, 24, 39, 0.5);
            padding: 0.5rem;
            border-radius: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(244, 114, 182, 0.1) 100%);
            color: #a78bfa; 
            border-radius: 10px; 
            padding: 12px 24px; 
            font-weight: 600; 
            transition: all 0.3s ease; 
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .stTabs [data-baseweb="tab"]:hover { 
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(244, 114, 182, 0.2) 100%);
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important; 
            color: white !important; 
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
            transform: translateY(-2px);
        }
        
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); 
            border-right: 1px solid rgba(139, 92, 246, 0.3);
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 { 
            color: white !important; 
            -webkit-text-fill-color: white !important; 
        }
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] li, 
        [data-testid="stSidebar"] span { 
            color: #cbd5e1 !important; 
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); 
            color: white; 
            border-radius: 12px; 
            padding: 0.75rem 2rem; 
            font-weight: 600; 
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); 
            border: none;
            transition: all 0.3s ease;
        }
        .stButton > button:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6); 
            color: white; 
        }
        
        @keyframes fadeInDown { 
            from { opacity: 0; transform: translateY(-30px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        .card {
            padding: 1rem; 
            border-radius: 16px; 
            text-align: center; 
            color: white; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); 
            transition: all 0.4s ease; 
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }
        .card:hover::before {
            left: 100%;
        }
        .card:hover { 
            transform: translateY(-8px) scale(1.02); 
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.4);
        }
        
        .metric-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(244, 114, 182, 0.1) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(244, 114, 182, 0.2) 100%);
            border-color: rgba(139, 92, 246, 0.5);
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
        }
        
        .stExpander {
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
        }
        
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }
        
        .metric-container {
            background: rgba(17, 24, 39, 0.7);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(139, 92, 246, 0.2);
            transition: all 0.3s ease;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .metric-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
            border-color: rgba(139, 92, 246, 0.5);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        .metric-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            background: rgba(139, 92, 246, 0.1);
            width: 50px;
            height: 50px;
            line-height: 50px;
            border-radius: 50%;
            margin: 0 auto 1rem auto;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header with animation
    st.markdown("""
    <div style='position: fixed; top: 3.5rem; right: 1.5rem; z-index: 9999;'>
        <div style='background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); 
                    border-radius: 20px; padding: 0.6rem 1.2rem; 
                    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5);
                    animation: fadeInDown 1s ease-in-out;'>
            <span style='color: white; font-weight: 700; font-size: 0.9rem; letter-spacing: 1.5px;'>
                ✨ Target SQL:By RATNESH SINGH
            </span>
        </div>
    </div>
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 4rem; margin-bottom: 0;'>🛒 Target Brazil E‑Commerce Analytics</h1>
        <p style='font-size: 1.3rem; background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; margin-top: 0.5rem; letter-spacing: 1px;'>
            🎯 Deep Dive into Brazilian E-Commerce Trends
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced Feature Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
            <div style='font-size: 2rem; margin-bottom: 0.25rem;'>📊</div>
            <h3 style='color: white !important; margin: 0.25rem 0; font-size: 1.1rem;'>Data</h3>
            <p style='margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.8);'>8 CSV Files</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div style='font-size: 2rem; margin-bottom: 0.25rem;'>🔍</div>
            <h3 style='color: white !important; margin: 0.25rem 0; font-size: 1.1rem;'>EDA</h3>
            <p style='margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.8);'>Orders & Payments</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'>
            <div style='font-size: 2rem; margin-bottom: 0.25rem;'>🚚</div>
            <h3 style='color: white !important; margin: 0.25rem 0; font-size: 1.1rem;'>Logistics</h3>
            <p style='margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.8);'>Freight & Delivery</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='card' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
            <div style='font-size: 2rem; margin-bottom: 0.25rem;'>💡</div>
            <h3 style='color: white !important; margin: 0.25rem 0; font-size: 1.1rem;'>Insights</h3>
            <p style='margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.8);'>Customer Trends</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar
    BASE_DIR = Path(r"C:\Users\rattu\Downloads\Target SQL")
    DATA_DIR = BASE_DIR / "Target- SQL Business Case ALL 8 CSV"

    with st.sidebar:
        st.markdown("## 📑 Navigation")
        st.markdown("---")
        st.markdown(f"""
        <div style='background: rgba(139, 92, 246, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(139, 92, 246, 0.3);'>
            <h3 style='color: #a78bfa !important; margin-top: 0;'>⚙️ Configuration</h3>
            <p><strong>Data Source:</strong> DuckDB</p>
            <p style='font-size: 0.8rem; word-break: break-all;'>{DATA_DIR}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(244, 114, 182, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(244, 114, 182, 0.3);'>
            <h3 style='color: #f472b6 !important; margin-top: 0;'>🔍 Analysis Modules</h3>
            <ul style='margin: 0; padding-left: 1.2rem;'>
                <li>Orders & Trends</li>
                <li>Geography & Economy</li>
                <li>Delivery & Freight</li>
                <li>Products & Reviews</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    tab_overview, tab_orders, tab_geo, tab_econ, tab_delivery, tab_pay, tab_prod, tab_raw, tab_log = st.tabs(
        [
            "Overview",
            "Orders & Trends",
            "Geography",
            "Economy",
            "Delivery & Freight",
            "Payments",
            "Products & Reviews",
            "Raw Tables",
            "Activity Log",
        ]
    )

    # --- Overview ---
    with tab_overview:
        st.header("📊 Executive Summary")
        logger.info("Rendering Overview tab")
        
        # Time range
        # Time range
        df_time = run_query(
            """
            SELECT
                MIN(order_purchase_timestamp) AS first_order_date,
                MAX(order_purchase_timestamp) AS last_order_date,
                date_diff('day',
                          MIN(order_purchase_timestamp),
                          MAX(order_purchase_timestamp)) AS total_days
            FROM orders;
            """
        )
        
        if not df_time.empty:
            first_date = df_time.at[0, "first_order_date"]
            last_date = df_time.at[0, "last_order_date"]
            total_days = df_time.at[0, "total_days"]
            
            # Handle potential None values if table is empty but query returns a row of Nulls
            if pd.isna(first_date):
                first_date_str = "N/A"
            else:
                first_date_str = str(first_date.date())
                
            if pd.isna(last_date):
                last_date_str = "N/A"
            else:
                last_date_str = str(last_date.date())
                
            if pd.isna(total_days):
                total_days = 0
            else:
                total_days = int(total_days)
        else:
            first_date_str = "N/A"
            last_date_str = "N/A"
            total_days = 0

        # Total orders and customers
        df_counts = run_query(
            """
            SELECT
                (SELECT COUNT(*) FROM orders) AS total_orders,
                (SELECT COUNT(DISTINCT customer_id) FROM customers) AS total_customers,
                (SELECT COUNT(DISTINCT seller_id) FROM sellers) AS total_sellers
            ;
            """
        )
        total_orders = int(df_counts.at[0, "total_orders"])
        total_customers = int(df_counts.at[0, "total_customers"])
        total_sellers = int(df_counts.at[0, "total_sellers"])

        # Row 1: Key Counts
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(102, 126, 234, 0.05));'>
                <div class="metric-icon" style="color: #667eea;">📦</div>
                <div class="metric-value">{total_orders:,}</div>
                <div class="metric-label">Total Orders</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(244, 114, 182, 0.15), rgba(244, 114, 182, 0.05));'>
                <div class="metric-icon" style="color: #f472b6;">👥</div>
                <div class="metric-value">{total_customers:,}</div>
                <div class="metric-label">Unique Customers</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(56, 239, 125, 0.15), rgba(56, 239, 125, 0.05));'>
                <div class="metric-icon" style="color: #38ef7d;">🏪</div>
                <div class="metric-value">{total_sellers:,}</div>
                <div class="metric-label">Unique Sellers</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 2: Time Metrics
        m4, m5, m6 = st.columns(3)
        with m4:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(251, 146, 60, 0.05));'>
                <div class="metric-icon" style="color: #fb923c;">📅</div>
                <div class="metric-value" style="font-size: 1.8rem;">{first_date_str}</div>
                <div class="metric-label">First Order</div>
            </div>
            """, unsafe_allow_html=True)
        with m5:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.05));'>
                <div class="metric-icon" style="color: #8b5cf6;">🏁</div>
                <div class="metric-value" style="font-size: 1.8rem;">{last_date_str}</div>
                <div class="metric-label">Last Order</div>
            </div>
            """, unsafe_allow_html=True)
        with m6:
            st.markdown(f"""
            <div class="metric-container" style='background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(236, 72, 153, 0.05));'>
                <div class="metric-icon" style="color: #ec4899;">⏳</div>
                <div class="metric-value">{total_days}</div>
                <div class="metric-label">Total Days</div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Yearly Order Trend")
        df_year = run_query(
            """
            WITH yearly AS (
                SELECT
                    EXTRACT(year FROM order_purchase_timestamp) AS order_year,
                    COUNT(*) AS total_orders
                FROM orders
                GROUP BY order_year
            )
            SELECT * FROM yearly ORDER BY order_year;
            """
        )
        # Plotly Line Chart
        fig = px.line(df_year, x='order_year', y='total_orders', markers=True, 
                      title='Total Orders per Year')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            xaxis=dict(showgrid=False, title='Year'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Total Orders'),
            hovermode='x unified'
        )
        fig.update_traces(line_color='#8b5cf6', line_width=4, marker_size=10)
        st.plotly_chart(fig, width='stretch')

        st.subheader("Time of Day Distribution")
        df_tod = run_query(
            """
            WITH classified AS (
                SELECT
                    CASE
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 0 AND 6  THEN 'Dawn'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 7 AND 12 THEN 'Morning'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 19 AND 23 THEN 'Night'
                    END AS time_of_day
                FROM orders
            )
            SELECT
                time_of_day,
                COUNT(*) AS order_count
            FROM classified
            GROUP BY time_of_day
            ORDER BY order_count DESC;
            """
        )
        # Plotly Bar Chart
        fig = px.bar(df_tod, x='time_of_day', y='order_count', 
                     color='order_count', color_continuous_scale='RdBu_r',
                     title='Orders by Time of Day')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            xaxis=dict(showgrid=False, title='Time of Day'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Order Count')
        )
        st.plotly_chart(fig, width='stretch')

    # --- Orders & Trends ---
    with tab_orders:
        st.header("📈 Orders & Trends Analysis")
        logger.info("Rendering Orders & Trends tab")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Orders Over Time")
            df_month = run_query(
                """
                SELECT
                    EXTRACT(year  FROM order_purchase_timestamp) AS order_year,
                    EXTRACT(month FROM order_purchase_timestamp) AS order_month,
                    COUNT(*) AS total_orders
                FROM orders
                GROUP BY order_year, order_month
                ORDER BY order_year, order_month;
                """
            )
            
            if not df_month.empty:
                df_month["year_month"] = (
                    df_month["order_year"].astype(int).astype(str)
                    + "-"
                    + df_month["order_month"].astype(int).astype(str).str.zfill(2)
                )
                
                # Plotly Area Chart
                fig = px.area(df_month, x='year_month', y='total_orders',
                              title='Monthly Order Volume',
                              labels={'year_month': 'Month', 'total_orders': 'Orders'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#cbd5e1'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    hovermode='x unified'
                )
                fig.update_traces(line_color='#f472b6', fillcolor='rgba(244, 114, 182, 0.2)')
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No order data available for the selected period.")

        with col2:
            st.subheader("Monthly Data")
            if not df_month.empty:
                st.dataframe(df_month[['year_month', 'total_orders']], width='stretch', height=400)
            else:
                st.write("No data.")

        st.markdown("---")
        
        st.subheader("📊 Year-over-Year Growth")
        df_yoy = run_query(
            """
            WITH yearly AS (
                SELECT
                    EXTRACT(year FROM order_purchase_timestamp) AS order_year,
                    COUNT(*) AS total_orders
                FROM orders
                GROUP BY order_year
            )
            SELECT
                order_year,
                total_orders,
                LAG(total_orders) OVER (ORDER BY order_year) AS previous_year_orders,
                CASE
                    WHEN LAG(total_orders) OVER (ORDER BY order_year) IS NULL THEN NULL
                    ELSE (total_orders - LAG(total_orders) OVER (ORDER BY order_year))
                         * 100.0 / LAG(total_orders) OVER (ORDER BY order_year)
                END AS year_over_year_growth_pct
            FROM yearly
            ORDER BY order_year;
            """
        )
        
        if not df_yoy.empty:
            # Formatted dataframe with styling
            st.dataframe(
                df_yoy.style.format({
                    'year_over_year_growth_pct': '{:.2f}%',
                    'total_orders': '{:,}',
                    'previous_year_orders': '{:,.0f}'
                }).background_gradient(subset=['year_over_year_growth_pct'], cmap='RdYlGn'),
                width='stretch'
            )
        else:
            st.info("No year-over-year data available.")

    # --- Geography ---
    with tab_geo:
        st.header("🗺️ Geographic Distribution")
        logger.info("Rendering Geography tab")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("Customer Distribution by State")
            df_state = run_query(
                """
                WITH counts AS (
                    SELECT
                        customer_state,
                        COUNT(DISTINCT customer_id) AS total_customers
                    FROM customers
                    GROUP BY customer_state
                )
                SELECT
                    customer_state,
                    total_customers,
                    ROUND(total_customers * 100.0 / SUM(total_customers) OVER (), 2) AS percentage
                FROM counts
                ORDER BY total_customers DESC;
                """
            )
            
            if not df_state.empty:
                # Plotly Bar Chart (Horizontal for better readability of states)
                fig = px.bar(df_state, x='total_customers', y='customer_state', orientation='h',
                             title='Customers per State',
                             color='total_customers', color_continuous_scale='viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#cbd5e1'),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Total Customers'),
                    yaxis=dict(showgrid=False, title='State', categoryorder='total ascending'),
                    height=600
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No customer location data available.")

        with col2:
            st.subheader("State Statistics")
            if not df_state.empty:
                st.dataframe(
                    df_state.style.format({
                        'percentage': '{:.2f}%',
                        'total_customers': '{:,}'
                    }).background_gradient(subset=['total_customers'], cmap='viridis'),
                    width='stretch',
                    height=600
                )
            else:
                st.write("No data.")

        st.markdown("---")
        
        st.subheader("Month-on-Month Orders by State")
        df_mom_state = run_query(
            """
            SELECT
                c.customer_state,
                EXTRACT(year  FROM o.order_purchase_timestamp) AS order_year,
                EXTRACT(month FROM o.order_purchase_timestamp) AS order_month,
                COUNT(*) AS total_orders
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_state, order_year, order_month
            ORDER BY c.customer_state, order_year, order_month;
            """
        )
        if not df_mom_state.empty:
            st.dataframe(df_mom_state, width='stretch')
        else:
            st.info("No month-on-month order data by state available.")

    # --- Economy ---
    with tab_econ:
        st.header("💰 Economic Analysis")
        logger.info("Rendering Economy tab")
        
        st.subheader("Cost Increase: 2017 → 2018 (Jan–Aug)")
        df_cost = run_query(
            """
            WITH OrderCosts AS (
                SELECT
                    EXTRACT(year FROM o.order_purchase_timestamp) AS order_year,
                    SUM(p.payment_value) AS total_cost
                FROM orders o
                INNER JOIN payments p ON o.order_id = p.order_id
                WHERE EXTRACT(year FROM o.order_purchase_timestamp) IN (2017, 2018)
                  AND EXTRACT(month FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
                GROUP BY order_year
            )
            SELECT
                (SELECT total_cost FROM OrderCosts WHERE order_year = 2018) AS cost_2018,
                (SELECT total_cost FROM OrderCosts WHERE order_year = 2017) AS cost_2017,
                ROUND(
                    (
                        (SELECT total_cost FROM OrderCosts WHERE order_year = 2018) -
                        (SELECT total_cost FROM OrderCosts WHERE order_year = 2017)
                    ) * 100.0 /
                    (SELECT total_cost FROM OrderCosts WHERE order_year = 2017),
                    2
                ) AS percentage_increase;
            """
        )
        
        if not df_cost.empty:
            cost_2017 = df_cost.at[0, 'cost_2017'] if not pd.isna(df_cost.at[0, 'cost_2017']) else 0
            cost_2018 = df_cost.at[0, 'cost_2018'] if not pd.isna(df_cost.at[0, 'cost_2018']) else 0
            pct_increase = df_cost.at[0, 'percentage_increase'] if not pd.isna(df_cost.at[0, 'percentage_increase']) else 0

            # Custom Metric Cards for Cost Analysis
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-container" style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(102, 126, 234, 0.05));'>
                    <div class="metric-icon" style="color: #667eea;">📉</div>
                    <div class="metric-value">${cost_2017:,.2f}</div>
                    <div class="metric-label">Total Cost 2017 (Jan-Aug)</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-container" style='background: linear-gradient(135deg, rgba(244, 114, 182, 0.15), rgba(244, 114, 182, 0.05));'>
                    <div class="metric-icon" style="color: #f472b6;">📈</div>
                    <div class="metric-value">${cost_2018:,.2f}</div>
                    <div class="metric-label">Total Cost 2018 (Jan-Aug)</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-container" style='background: linear-gradient(135deg, rgba(56, 239, 125, 0.15), rgba(56, 239, 125, 0.05));'>
                    <div class="metric-icon" style="color: #38ef7d;">🚀</div>
                    <div class="metric-value">{pct_increase:.2f}%</div>
                    <div class="metric-label">Increase Percentage</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No cost data available for 2017-2018 comparison.")

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Order Price by State")
            df_price_state = run_query(
                """
                SELECT
                    c.customer_state,
                    SUM(oi.price) AS total_order_price,
                    AVG(oi.price) AS avg_order_price
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                INNER JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_state
                ORDER BY total_order_price DESC;
                """
            )
            if not df_price_state.empty:
                st.dataframe(
                    df_price_state.style.format({
                        'total_order_price': '${:,.2f}',
                        'avg_order_price': '${:,.2f}'
                    }).background_gradient(subset=['total_order_price'], cmap='Blues'),
                    width='stretch',
                    height=400
                )
            else:
                st.write("No data.")
            
        with col2:
            st.subheader("Freight Value by State")
            df_freight_state = run_query(
                """
                SELECT
                    c.customer_state,
                    SUM(oi.freight_value) AS total_freight_value,
                    AVG(oi.freight_value) AS avg_freight_value
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                INNER JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_state
                ORDER BY total_freight_value DESC;
                """
            )
            if not df_freight_state.empty:
                st.dataframe(
                    df_freight_state.style.format({
                        'total_freight_value': '${:,.2f}',
                        'avg_freight_value': '${:,.2f}'
                    }).background_gradient(subset=['total_freight_value'], cmap='Reds'),
                    width='stretch',
                    height=400
                )
            else:
                st.write("No data.")

    # --- Delivery & Freight ---
    with tab_delivery:
        st.header("🚚 Delivery & Freight Analysis")
        logger.info("Rendering Delivery & Freight tab")
        
        st.subheader("Delivery Time vs Estimated")
        df_delivery = run_query(
            """
            SELECT
                date_diff('day', order_purchase_timestamp, order_delivered_customer_date) AS time_to_deliver,
                date_diff('day', order_delivered_customer_date, order_estimated_delivery_date) AS diff_estimated_delivery
            FROM orders
            WHERE order_delivered_customer_date IS NOT NULL
              AND order_estimated_delivery_date IS NOT NULL;
            """
        )
        
        if not df_delivery.empty:
            # Plotly Histogram for Delivery Time
            fig = px.histogram(df_delivery, x='time_to_deliver', nbins=50,
                               title='Distribution of Delivery Times (Days)',
                               color_discrete_sequence=['#8b5cf6'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1'),
                xaxis=dict(showgrid=False, title='Days to Deliver'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Count'),
                bargap=0.1
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No delivery time data available.")

        st.markdown("---")

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top States by Avg Freight")
            df_high_freight = run_query(
                """
                SELECT
                    customer_state,
                    AVG(freight_value) AS avg_freight_value
                FROM (
                    SELECT
                        c.customer_state,
                        oi.freight_value
                    FROM orders o
                    INNER JOIN customers c ON o.customer_id = c.customer_id
                    INNER JOIN order_items oi ON o.order_id = oi.order_id
                )
                GROUP BY customer_state
                ORDER BY avg_freight_value DESC
                LIMIT 5;
                """
            )
            if not df_high_freight.empty:
                st.dataframe(
                    df_high_freight.style.format({
                        'avg_freight_value': '${:,.2f}'
                    }).background_gradient(subset=['avg_freight_value'], cmap='Reds'),
                    width='stretch'
                )
            else:
                st.write("No data.")

        with col2:
            st.subheader("Fastest vs Slowest Delivery")
            df_slowest = run_query(
                """
                SELECT
                    customer_state,
                    AVG(delivery_days) AS avg_delivery_time
                FROM (
                    SELECT
                        c.customer_state,
                        date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
                    FROM orders o
                    INNER JOIN customers c ON o.customer_id = c.customer_id
                    WHERE o.order_delivered_customer_date IS NOT NULL
                )
                GROUP BY customer_state
                ORDER BY avg_delivery_time DESC
                LIMIT 5;
                """
            )
            df_fastest = run_query(
                """
                SELECT
                    customer_state,
                    AVG(delivery_days) AS avg_delivery_time
                FROM (
                    SELECT
                        c.customer_state,
                        date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
                    FROM orders o
                    INNER JOIN customers c ON o.customer_id = c.customer_id
                    WHERE o.order_delivered_customer_date IS NOT NULL
                )
                GROUP BY customer_state
                ORDER BY avg_delivery_time ASC
                LIMIT 5;
                """
            )
            
            tab1, tab2 = st.tabs(["🐢 Slowest States", "🐇 Fastest States"])
            with tab1:
                if not df_slowest.empty:
                    st.dataframe(
                        df_slowest.style.format({'avg_delivery_time': '{:.1f} days'})
                        .background_gradient(subset=['avg_delivery_time'], cmap='Oranges'),
                        width='stretch'
                    )
                else:
                    st.write("No data.")
            with tab2:
                if not df_fastest.empty:
                    st.dataframe(
                        df_fastest.style.format({'avg_delivery_time': '{:.1f} days'})
                        .background_gradient(subset=['avg_delivery_time'], cmap='Greens_r'),
                        width='stretch'
                    )
                else:
                    st.write("No data.")

    # --- Payments ---
    with tab_pay:
        st.header("💳 Payment Analysis")
        logger.info("Rendering Payments tab")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("Monthly Orders by Payment Type")
            df_pay_month = run_query(
                """
                SELECT
                    EXTRACT(year  FROM o.order_purchase_timestamp) AS order_year,
                    EXTRACT(month FROM o.order_purchase_timestamp) AS order_month,
                    p.payment_type,
                    COUNT(DISTINCT o.order_id) AS order_count
                FROM orders o
                INNER JOIN payments p ON o.order_id = p.order_id
                GROUP BY order_year, order_month, p.payment_type
                ORDER BY order_year, order_month, p.payment_type;
                """
            )
            
            if not df_pay_month.empty:
                df_pay_month["year_month"] = (
                    df_pay_month["order_year"].astype(int).astype(str)
                    + "-"
                    + df_pay_month["order_month"].astype(int).astype(str).str.zfill(2)
                )
                
                # Plotly Stacked Bar Chart
                fig = px.bar(df_pay_month, x='year_month', y='order_count', color='payment_type',
                             title='Payment Methods Over Time',
                             labels={'year_month': 'Month', 'order_count': 'Orders', 'payment_type': 'Method'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#cbd5e1'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No payment data available.")

        with col2:
            st.subheader("Installments Distribution")
            df_inst = run_query(
                """
                SELECT
                    payment_installments,
                    COUNT(DISTINCT order_id) AS order_count
                FROM payments
                GROUP BY payment_installments
                ORDER BY payment_installments;
                """
            )
            
            if not df_inst.empty:
                # Plotly Bar Chart
                fig = px.bar(df_inst, x='payment_installments', y='order_count',
                             title='Orders by Installments',
                             color='order_count', color_continuous_scale='Magma')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#cbd5e1'),
                    xaxis=dict(showgrid=False, title='Installments'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Orders')
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.write("No data.")
            
        st.markdown("---")
        if not df_pay_month.empty:
            st.dataframe(df_pay_month, width='stretch')

    # --- Products & Reviews ---
    with tab_prod:
        st.header("⭐ Products & Reviews")
        logger.info("Rendering Products & Reviews tab")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("Top 10 Product Categories")
            try:
                df_prod = run_query(
                    """
                    SELECT
                        COUNT(oi.order_item_id) AS total_items_sold,
                        SUM(oi.price) AS total_revenue
                    FROM order_items oi
                    INNER JOIN products p ON oi.product_id = p.product_id
                    GROUP BY p.product_id
                    ORDER BY total_items_sold DESC
                    LIMIT 10;
                    """
                )
                
                if not df_prod.empty and len(df_prod) > 0:
                    # Plotly Bar Chart
                    fig = px.bar(df_prod, x='total_items_sold', y=df_prod.index, orientation='h',
                                 title='Top Products by Sales Volume',
                                 color='total_revenue', color_continuous_scale='Plasma')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#cbd5e1'),
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Items Sold'),
                        yaxis=dict(showgrid=False, title='Product Rank', categoryorder='total ascending'),
                        height=500
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No product sales data available.")
            except Exception as e:
                st.error(f"Error loading product data: {str(e)}")
                logger.error(f"Product query error: {e}")

        with col2:
            st.subheader("Review Score Distribution")
            try:
                df_reviews = run_query(
                    """
                    WITH counts AS (
                        SELECT
                            review_score,
                            COUNT(*) AS review_count
                        FROM reviews
                        WHERE review_score IS NOT NULL
                        GROUP BY review_score
                    )
                    SELECT
                        review_score,
                        review_count,
                        ROUND(review_count * 100.0 / SUM(review_count) OVER (), 2) AS percentage
                    FROM counts
                    ORDER BY review_score DESC;
                    """
                )
                
                if not df_reviews.empty:
                    # Plotly Donut Chart
                    fig = px.pie(df_reviews, values='review_count', names='review_score',
                                 title='Review Scores Distribution',
                                 color_discrete_sequence=px.colors.sequential.RdBu,
                                 hole=0.4)
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#cbd5e1'),
                        showlegend=True
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, width='stretch')
                    
                    # Display styled dataframe
                    st.dataframe(
                        df_reviews.style.format({
                            'percentage': '{:.2f}%',
                            'review_count': '{:,}'
                        }).background_gradient(subset=['review_count'], cmap='RdYlGn'),
                        width='stretch'
                    )
                else:
                    st.write("No review data.")
            except Exception as e:
                st.error(f"Error loading review data: {str(e)}")
                logger.error(f"Review query error: {e}")
            
        st.markdown("---")
        
        # Additional Product Insights
        st.subheader("📦 Product Performance Metrics")
        try:
            df_prod_stats = run_query(
                """
                SELECT
                    COUNT(DISTINCT oi.product_id) AS unique_products,
                    COUNT(oi.order_item_id) AS total_items_sold,
                    ROUND(AVG(oi.price), 2) AS avg_price,
                    ROUND(SUM(oi.price), 2) AS total_revenue
                FROM order_items oi;
                """
            )
            
            if not df_prod_stats.empty:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="metric-container" style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(102, 126, 234, 0.05));'>
                        <div class="metric-icon" style="color: #667eea;">📦</div>
                        <div class="metric-value">{int(df_prod_stats.at[0, 'unique_products']):,}</div>
                        <div class="metric-label">Unique Products</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-container" style='background: linear-gradient(135deg, rgba(244, 114, 182, 0.15), rgba(244, 114, 182, 0.05));'>
                        <div class="metric-icon" style="color: #f472b6;">🛒</div>
                        <div class="metric-value">{int(df_prod_stats.at[0, 'total_items_sold']):,}</div>
                        <div class="metric-label">Items Sold</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="metric-container" style='background: linear-gradient(135deg, rgba(56, 239, 125, 0.15), rgba(56, 239, 125, 0.05));'>
                        <div class="metric-icon" style="color: #38ef7d;">💵</div>
                        <div class="metric-value">${float(df_prod_stats.at[0, 'avg_price']):,.2f}</div>
                        <div class="metric-label">Avg Price</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m4:
                    st.markdown(f"""
                    <div class="metric-container" style='background: linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(251, 146, 60, 0.05));'>
                        <div class="metric-icon" style="color: #fb923c;">💰</div>
                        <div class="metric-value">${float(df_prod_stats.at[0, 'total_revenue']):,.0f}</div>
                        <div class="metric-label">Total Revenue</div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading product statistics: {str(e)}")
            logger.error(f"Product stats error: {e}")

    # --- Raw Tables ---
    with tab_raw:
        st.header("📋 Raw Data Explorer")
        logger.info("Rendering Raw Tables tab")
        
        st.markdown("""
        <div style='background: rgba(139, 92, 246, 0.1); padding: 1rem; border-radius: 10px; border: 1px solid rgba(139, 92, 246, 0.3); margin-bottom: 1rem;'>
            <p style='margin: 0; color: #cbd5e1;'>
                🔍 <strong>Explore the raw data tables</strong> from the Target Brazil E-Commerce dataset. 
                Select a table below to preview up to 500 rows.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        table_options = ["customers", "sellers", "order_items", "geolocation", "payments", "reviews", "orders", "products"]
        
        with col1:
            selected_option = st.selectbox(
                "📊 Select Table",
                ["ALL TABLES"] + table_options,
                index=0
            )
        
        with col2:
            st.markdown(f"""
            <div style='background: rgba(244, 114, 182, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid rgba(244, 114, 182, 0.3);'>
                <p style='margin: 0; color: #f472b6; font-weight: 600;'>
                    Currently viewing: <span style='color: #fff;'>{selected_option}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        tables_to_show = table_options if selected_option == "ALL TABLES" else [selected_option]
        
        for table in tables_to_show:
            if selected_option == "ALL TABLES":
                st.markdown(f"### 📄 {table}")
            
            try:
                df_raw = run_query(f"SELECT * FROM {table} LIMIT 500;")
                
                if not df_raw.empty:
                    # Display table info
                    info_col1, info_col2, info_col3 = st.columns(3)
                    with info_col1:
                        st.markdown(f"""
                        <div class="metric-container" style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(102, 126, 234, 0.05));'>
                            <div class="metric-icon" style="color: #667eea;">📊</div>
                            <div class="metric-value">{len(df_raw):,}</div>
                            <div class="metric-label">Rows Shown</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with info_col2:
                        st.markdown(f"""
                        <div class="metric-container" style='background: linear-gradient(135deg, rgba(244, 114, 182, 0.15), rgba(244, 114, 182, 0.05));'>
                            <div class="metric-icon" style="color: #f472b6;">📋</div>
                            <div class="metric-value">{len(df_raw.columns)}</div>
                            <div class="metric-label">Columns</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with info_col3:
                        st.markdown(f"""
                        <div class="metric-container" style='background: linear-gradient(135deg, rgba(56, 239, 125, 0.15), rgba(56, 239, 125, 0.05));'>
                            <div class="metric-icon" style="color: #38ef7d;">💾</div>
                            <div class="metric-value">{df_raw.memory_usage(deep=True).sum() / 1024:.1f} KB</div>
                            <div class="metric-label">Memory Usage</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display the dataframe
                    st.dataframe(df_raw, width='stretch', height=400 if selected_option == "ALL TABLES" else 600)
                    
                    # Download button
                    csv = df_raw.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {table} as CSV",
                        data=csv,
                        file_name=f"{table}_export.csv",
                        mime="text/csv",
                        key=f"download_{table}"
                    )
                    
                    if selected_option == "ALL TABLES":
                        st.markdown("---")
                        
                else:
                    st.warning(f"No data found in table: {table}")
            except Exception as e:
                st.error(f"Error loading table data for {table}: {str(e)}")
                logger.error(f"Raw table query error for {table}: {e}")


    # --- Activity Log ---
    with tab_log:
        st.header("📝 Application Activity Log")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Track all application events, data queries, and user interactions.")
        with col2:
            if st.button("🗑️ Clear Logs"):
                st.session_state['log_data'] = []
                st.rerun()
        
        if st.session_state['log_data']:
            # Display logs in a text area
            log_text = "\n".join(st.session_state['log_data'])
            st.text_area("System Logs", value=log_text, height=300, disabled=True)
            
            st.markdown("---")
            
            # Also show as a dataframe for better filtering
            try:
                # Parse logs into a dataframe
                log_entries = []
                for entry in st.session_state['log_data']:
                    # Simple parsing assuming the format: '%(asctime)s - %(levelname)s - %(message)s'
                    parts = entry.split(' - ', 2)
                    if len(parts) == 3:
                        log_entries.append({
                            'Timestamp': parts[0],
                            'Level': parts[1],
                            'Message': parts[2].strip()
                        })
                    else:
                        log_entries.append({
                            'Timestamp': '',
                            'Level': 'INFO',
                            'Message': entry.strip()
                        })
                
                if log_entries:
                    df_logs = pd.DataFrame(log_entries)
                    # Reverse order to show newest first
                    df_logs = df_logs.iloc[::-1]
                    
                    st.subheader("Log Table (Newest First)")
                    
                    def color_level(val):
                        color = '#10b981' # Green for INFO
                        if val == 'ERROR':
                            color = '#ef4444' # Red
                        elif val == 'WARNING':
                            color = '#f59e0b' # Amber
                        return f'color: {color}; font-weight: bold;'
                        
                    st.dataframe(
                        df_logs.style.map(color_level, subset=['Level']),
                        width='stretch',
                        height=400
                    )
            except Exception as e:
                st.error(f"Error parsing logs: {e}")
        else:
            st.info("No activity logs recorded yet.")


if __name__ == "__main__":
    main()



