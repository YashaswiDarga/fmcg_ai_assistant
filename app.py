import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from sql_agent import generate_sql, explain_results

# Load environment variables from .env
load_dotenv()

# Set streamlit page config
st.set_page_config(
    page_title="FMCG Conversational Analytics AI",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a highly premium, clean dark-mode dashboard
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Base layout settings */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif;
    background-color: #080b11;
    color: #e2e8f0;
}

/* Hide default streamlit banner and minimize header */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stToolbar"] {
    right: 2rem;
}

/* Sidebar design */
[data-testid="stSidebar"] {
    background-color: #05070a;
    border-right: 1px solid rgba(255, 255, 255, 0.03);
}

/* Clean KPI Card layouts */
.kpi-card {
    background: rgba(17, 24, 39, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(8px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 15px;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}
.kpi-icon-container {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.kpi-content {
    display: flex;
    flex-direction: column;
}
.kpi-title {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 2px;
}
.kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.2;
}

/* Sidebar connection status indicator */
.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 9999px;
    width: fit-content;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 15px;
}
.status-online {
    background: rgba(16, 185, 129, 0.08);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.15);
}
.status-offline {
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.15);
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: currentColor;
    box-shadow: 0 0 8px currentColor;
}

/* Redesign chat bubble for User questions */
.user-query-container {
    background: rgba(14, 165, 233, 0.06);
    border: 1px solid rgba(14, 165, 233, 0.12);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 20px 0;
}
.query-header {
    font-size: 11px;
    font-weight: 700;
    color: #0ea5e9;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.query-text {
    font-size: 16px;
    font-weight: 500;
    color: #f1f5f9;
}

/* Style streamlit's native border container to look like glassmorphism panels */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(17, 24, 39, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15) !important;
}

/* Header typography */
.main-title {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
    letter-spacing: -0.02em;
}
.subtitle {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 25px;
    font-weight: 400;
}

/* Custom styled scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}
</style>
""", unsafe_allow_html=True)

# Database helper
def get_db_connection():
    db_file = "database/fmcg.db"
    return sqlite3.connect(db_file)

# Plotly theme styling helper
def style_plotly_fig(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Outfit, sans-serif',
        font_color='#94a3b8',
        title_font_color='#f8fafc',
        title_font_size=15,
        title_font_family='Outfit, sans-serif',
        title_x=0.05,
        legend_font_color='#94a3b8',
        margin=dict(t=45, b=20, l=15, r=15),
    )
    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.02)',
        zerolinecolor='rgba(255,255,255,0.04)',
        tickfont=dict(color='#64748b', size=11),
        title_font=dict(size=12, color='#64748b')
    )
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.02)',
        zerolinecolor='rgba(255,255,255,0.04)',
        tickfont=dict(color='#64748b', size=11),
        title_font=dict(size=12, color='#64748b')
    )
    return fig

# Sidebar configuration
st.sidebar.markdown("### 🥤 FMCG Analytics AI")
st.sidebar.markdown("Conversational decision support for beverage retail and logistics inventory.")

# Check API Configuration
api_key = os.getenv("GEMINI_API_KEY")
api_key_configured = True

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    api_key_configured = False
    st.sidebar.error("❌ Gemini API Key not found in `.env`")
else:
    st.sidebar.success("🔑 Gemini API Key configured")
    genai.configure(api_key=api_key)

# Connection Health Check
db_connected = False
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    if len(tables) >= 4:
        db_connected = True
except Exception:
    pass

if db_connected:
    st.sidebar.markdown('<div class="status-indicator status-online"><span class="status-dot"></span>Database Connected</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-indicator status-offline"><span class="status-dot"></span>Database Missing</div>', unsafe_allow_html=True)
    st.sidebar.warning("Please run setup scripts: \n`python generate_data.py` \n`python database.py`")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Database Inventory Details:**
* `product_master`: SKU detail logs
* `store_master`: Outlet location logs
* `sales_promotions`: Transaction logs
* `inventory`: Reorder stock logs
""")

# Dashboard main headers
st.markdown('<div class="main-title">🥤 FMCG AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Natural language query engine & analytics dashboard for FMCG beverage retail operations</div>', unsafe_allow_html=True)

if db_connected:
    # 1. Load KPI statistics
    try:
        conn = get_db_connection()
        kpi_data = pd.read_sql_query("""
        SELECT 
            (SELECT SUM(revenue) FROM sales_promotions) as total_revenue,
            (SELECT SUM(units_sold) FROM sales_promotions) as total_units,
            (SELECT SUM(CASE WHEN promotion_flag = 1 THEN revenue ELSE 0 END) * 100.0 / SUM(revenue) FROM sales_promotions) as promo_share,
            (SELECT SUM(stockout_flag) FROM inventory) as stockouts
        """, conn)
        
        # Monthly trend and regional summary queries
        df_region = pd.read_sql_query("""
            SELECT region, SUM(revenue) as revenue
            FROM sales_promotions
            GROUP BY region
        """, conn)
        
        df_category = pd.read_sql_query("""
            SELECT p.category, SUM(s.revenue) as revenue
            FROM sales_promotions s
            JOIN product_master p ON s.product_id = p.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
        """, conn)
        
        df_promo = pd.read_sql_query("""
            SELECT p.category, s.promotion_flag, AVG(s.units_sold) as avg_units
            FROM sales_promotions s
            JOIN product_master p ON s.product_id = p.product_id
            GROUP BY p.category, s.promotion_flag
        """, conn)
        
        conn.close()
        
        # Format KPI values
        total_rev = kpi_data['total_revenue'].iloc[0] or 0.0
        total_uni = kpi_data['total_units'].iloc[0] or 0
        p_share = kpi_data['promo_share'].iloc[0] or 0.0
        stkouts = kpi_data['stockouts'].iloc[0] or 0
        
        # Render beautiful KPI cards with color-coded containers
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-container" style="background: rgba(6, 182, 212, 0.08); color: #06b6d4;">💰</div>
                <div class="kpi-content">
                    <div class="kpi-title">Total Revenue</div>
                    <div class="kpi-value">${total_rev/1e6:.2f}M</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-container" style="background: rgba(139, 92, 246, 0.08); color: #8b5cf6;">📦</div>
                <div class="kpi-content">
                    <div class="kpi-title">Units Sold</div>
                    <div class="kpi-value">{total_uni/1e3:.1f}k</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-container" style="background: rgba(236, 72, 153, 0.08); color: #ec4899;">📣</div>
                <div class="kpi-content">
                    <div class="kpi-title">Promo Share</div>
                    <div class="kpi-value">{p_share:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon-container" style="background: rgba(245, 158, 11, 0.08); color: #f59e0b;">⚠️</div>
                <div class="kpi-content">
                    <div class="kpi-title">Stockouts</div>
                    <div class="kpi-value">{stkouts:,}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. Charts Section
        chart_col1, chart_col2 = st.columns([1, 1])
        
        with chart_col1:
            fig_region = px.pie(
                df_region, 
                values='revenue', 
                names='region', 
                hole=0.55,
                title="Revenue Distribution by Region",
                color_discrete_sequence=px.colors.sequential.Tealgrn_r
            )
            style_plotly_fig(fig_region)
            fig_region.update_layout(height=260, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_region, use_container_width=True)
            
        with chart_col2:
            df_category = df_category.sort_values(by="revenue", ascending=True)
            fig_category = px.bar(
                df_category,
                x='revenue',
                y='category',
                orientation='h',
                title="Sales Revenue by Product Category",
                color='revenue',
                color_continuous_scale='Tealgrn'
            )
            style_plotly_fig(fig_category)
            fig_category.update_layout(height=260, coloraxis_showscale=False, yaxis_title=None, xaxis_title="Revenue ($)")
            st.plotly_chart(fig_category, use_container_width=True)
            
        # Promotion Efficiency Chart
        df_promo['Promotion'] = df_promo['promotion_flag'].map({0: 'No Promo', 1: 'Promo Active'})
        fig_promo = px.bar(
            df_promo,
            x='category',
            y='avg_units',
            color='Promotion',
            barmode='group',
            title="Promotion Performance: Average Weekly Units Sold per SKU",
            color_discrete_map={'No Promo': '#475569', 'Promo Active': '#0ea5e9'}
        )
        style_plotly_fig(fig_promo)
        fig_promo.update_layout(height=280, xaxis_title=None, yaxis_title="Average Units Sold")
        st.plotly_chart(fig_promo, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")
else:
    st.info("💡 Please complete the Database Connection Setup in the sidebar to unlock Dashboard Analytics.")

# 3. AI Chat Box Section
st.write("---")
st.markdown("### 💬 AI Business Analyst Chat")
st.markdown("Ask natural language business questions about beverage sales, promotion lifts, and stockout impacts.")

# Suggest standard business queries
st.markdown("**Suggested Queries:**")
sample_queries = [
    "Which region generated the highest revenue?",
    "What promotion type worked best in terms of units sold?",
    "Which products experienced the most stockout incidents?",
    "Compare North and South regions' weekly revenue trends.",
    "Show top 5 products by revenue and their brand.",
    "What is the average discount percent by brand?"
]

# Render clean suggested questions as outline-styled tags using st.columns
cols_queries = st.columns(3)
for idx, sq in enumerate(sample_queries):
    c_idx = idx % 3
    if cols_queries[c_idx].button(sq, key=f"sq_btn_{idx}", use_container_width=True):
        st.session_state.active_query = sq

# Chat input from user
user_input = st.chat_input("Ask a business question about the FMCG data...")
if user_input:
    st.session_state.active_query = user_input

# Check if we have an active query to run
if "active_query" in st.session_state and st.session_state.active_query:
    query = st.session_state.active_query
    st.session_state.active_query = None  # Reset session state query
    
    # Custom styled user query bubble
    st.markdown(f"""
    <div class="user-query-container">
        <div class="query-header">👤 Business User</div>
        <div class="query-text">{query}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not api_key_configured:
        st.error("Please configure your Gemini API Key in the sidebar or `.env` file first.")
    elif not db_connected:
        st.error("The SQLite database must be configured and connected first.")
    else:
        # Step A: Translate Text to SQL
        with st.spinner("Translating question into SQL query..."):
            try:
                sql_query = generate_sql(query)
            except Exception as ex:
                st.error(f"Error calling Gemini API: {ex}")
                sql_query = None
        
        if sql_query:
            # Render using modern Streamlit Container with overrides
            with st.container(border=True):
                st.markdown("### ✨ AI Analyst Response")
                
                # Expandable SQL Block
                with st.expander("🛠️ Show SQL Query", expanded=True):
                    st.code(sql_query, language="sql")
                
                # Step B: Run SQLite Query
                with st.spinner("Executing query on SQLite..."):
                    try:
                        conn = get_db_connection()
                        df_results = pd.read_sql_query(sql_query, conn)
                        conn.close()
                        
                        st.markdown(f"#### 📊 Query Results ({len(df_results)} rows)")
                        st.dataframe(df_results, use_container_width=True)
                        
                        # Step C: Summarize Business Insights
                        with st.spinner("Synthesizing executive business insights..."):
                            executive_summary = explain_results(query, sql_query, df_results)
                            st.markdown("#### 💡 AI Analyst Insights")
                            st.markdown(executive_summary)
                            
                    except Exception as ex:
                        st.error(f"Database Execution Error: {ex}")
                        st.warning("The generated SQL query might have invalid syntax. Try rephrasing your question.")
