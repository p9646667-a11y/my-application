import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import io

# ---------------------------------------------------------
# Page Configuration & Metadata
# ---------------------------------------------------------
st.set_page_config(
    page_title="CashFlow IQ | Financial Intelligence & Visualizer",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Modern UI/UX Styles (Ultra-Crisp Contrast Theme)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
    }
    
    /* Main View Container */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(145deg, #0b0f19 0%, #0f172a 60%, #111827 100%) !important;
        color: #f8fafc !important;
    }

    /* Sidebar Background & Text */
    [data-testid="stSidebar"] {
        background-color: #0d121f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #f8fafc !important;
    }

    /* Metric Card Styling */
    .metric-card {
        background: #1e293b !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.45);
        border-radius: 16px;
        padding: 20px 18px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.6) !important;
        box-shadow: 0 12px 30px 0 rgba(99, 102, 241, 0.25);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #38bdf8);
    }
    
    .metric-title {
        color: #94a3b8 !important;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #ffffff !important;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .delta-positive { color: #10b981 !important; }
    .delta-negative { color: #f43f5e !important; }
    .delta-neutral { color: #38bdf8 !important; }

    /* Custom Hero Header Banner */
    .hero-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #172554 50%, #0f172a 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    .hero-title {
        margin: 0;
        color: #ffffff !important;
        font-weight: 800;
        font-size: 2.1rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        margin: 6px 0 0 0;
        color: #cbd5e1 !important;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Sleek High-Contrast Section Header Pill */
    .section-title {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.12) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        padding: 8px 18px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    /* Tab bar styling for bold, high contrast visibility */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 41, 59, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border-radius: 10px;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #6366f1 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* General text and headings contrast */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
    }
    p, span, label {
        color: #e2e8f0;
    }
    .stCaption {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Default Preset Data Profiles
# ---------------------------------------------------------
PRESETS = {
    "💼 Tech Professional ($8,500/mo)": [
        {"type": "Income", "source": "Salary (Senior SWE)", "target": "Net Income", "amount": 7500, "category": "Income"},
        {"type": "Income", "source": "Stock Dividends", "target": "Net Income", "amount": 600, "category": "Income"},
        {"type": "Income", "source": "Freelance Consulting", "target": "Net Income", "amount": 400, "category": "Income"},
        {"type": "Expense", "source": "Net Income", "target": "Needs", "amount": 3700, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Wants", "amount": 2100, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Savings & Investments", "amount": 2700, "category": "Bucket"},
        {"type": "Expense", "source": "Needs", "target": "Apartment Rent", "amount": 2400, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Organic Groceries", "amount": 650, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Utilities & High-Speed Internet", "amount": 250, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Car Insurance & Transit", "amount": 400, "category": "Needs"},
        {"type": "Expense", "source": "Wants", "target": "Fine Dining & Cafes", "amount": 800, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Travel & Weekend Escapes", "amount": 750, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Fitness & Tech Gadgets", "amount": 350, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Digital Subscriptions (AI/SaaS)", "amount": 200, "category": "Wants"},
        {"type": "Expense", "source": "Savings & Investments", "target": "S&P 500 ETF (VOO)", "amount": 1400, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Roth IRA (Retirement)", "amount": 550, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "High Yield Savings Account", "amount": 500, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Crypto / BTC", "amount": 250, "category": "Savings"},
    ],
    "🎓 Student / Early Career ($3,200/mo)": [
        {"type": "Income", "source": "Junior Role Salary", "target": "Net Income", "amount": 2800, "category": "Income"},
        {"type": "Income", "source": "Tutoring / Gig", "target": "Net Income", "amount": 400, "category": "Income"},
        {"type": "Expense", "source": "Net Income", "target": "Needs", "amount": 1800, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Wants", "amount": 800, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Savings & Investments", "amount": 600, "category": "Bucket"},
        {"type": "Expense", "source": "Needs", "target": "Shared Rent", "amount": 1100, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Groceries", "amount": 400, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Bus/Train Pass & Phone", "amount": 150, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Utilities", "amount": 150, "category": "Needs"},
        {"type": "Expense", "source": "Wants", "target": "Eating Out / Fast Food", "amount": 400, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Concerts / Nightlife", "amount": 250, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Streaming & Gaming", "amount": 150, "category": "Wants"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Emergency Fund", "amount": 400, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Index Funds", "amount": 200, "category": "Savings"},
    ],
    "🏡 Family Household ($11,000/mo)": [
        {"type": "Income", "source": "Primary Salary", "target": "Net Income", "amount": 6500, "category": "Income"},
        {"type": "Income", "source": "Partner Salary", "target": "Net Income", "amount": 4000, "category": "Income"},
        {"type": "Income", "source": "Rental Property", "target": "Net Income", "amount": 500, "category": "Income"},
        {"type": "Expense", "source": "Net Income", "target": "Needs", "amount": 6200, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Wants", "amount": 2600, "category": "Bucket"},
        {"type": "Expense", "source": "Net Income", "target": "Savings & Investments", "amount": 2200, "category": "Bucket"},
        {"type": "Expense", "source": "Needs", "target": "Home Mortgage", "amount": 3200, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Family Groceries", "amount": 1400, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Childcare & Education", "amount": 900, "category": "Needs"},
        {"type": "Expense", "source": "Needs", "target": "Health & Auto Insurance", "amount": 700, "category": "Needs"},
        {"type": "Expense", "source": "Wants", "target": "Family Vacations", "amount": 1200, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Dining & Entertainment", "amount": 800, "category": "Wants"},
        {"type": "Expense", "source": "Wants", "target": "Hobbies & Shopping", "amount": 600, "category": "Wants"},
        {"type": "Expense", "source": "Savings & Investments", "target": "College Fund (529)", "amount": 800, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Retirement Portfolio", "amount": 1000, "category": "Savings"},
        {"type": "Expense", "source": "Savings & Investments", "target": "Liquid Savings", "amount": 400, "category": "Savings"},
    ]
}

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(PRESETS["💼 Tech Professional ($8,500/mo)"])

if "starting_net_worth" not in st.session_state:
    st.session_state.starting_net_worth = 25000

# ---------------------------------------------------------
# Sidebar Controls & Settings
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 12px 0 20px 0;">
            <div style="font-size: 2.4rem;">🌊 💸</div>
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800; font-size: 1.5rem;">CashFlow IQ</h2>
            <p style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">Smart Financial & Sankey Visualizer</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("⚡ Quick Load Preset")
    selected_preset = st.selectbox(
        "Choose Financial Archetype:",
        list(PRESETS.keys())
    )
    
    if st.button("Apply Selected Preset", use_container_width=True, type="primary"):
        st.session_state.transactions = pd.DataFrame(PRESETS[selected_preset])
        st.toast(f"Loaded: {selected_preset}", icon="🚀")
        st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Baseline Setup")
    curr_savings = st.number_input(
        "Current Total Savings/Net Worth ($)",
        min_value=0,
        max_value=10000000,
        value=st.session_state.starting_net_worth,
        step=1000
    )
    st.session_state.starting_net_worth = curr_savings

    st.markdown("---")
    st.subheader("📥 Export & Backup")
    csv_buffer = io.StringIO()
    st.session_state.transactions.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download Financial Plan (.CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"cashflow_iq_plan_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("Upload Plan CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            required_cols = {"type", "source", "target", "amount", "category"}
            if required_cols.issubset(uploaded_df.columns):
                st.session_state.transactions = uploaded_df
                st.success("Plan uploaded successfully!")
            else:
                st.error("CSV format requires: type, source, target, amount, category")
        except Exception as e:
            st.error(f"Error loading file: {e}")

# ---------------------------------------------------------
# Core Data Calculation Helpers
# ---------------------------------------------------------
df = st.session_state.transactions

# Total Income
income_df = df[df["type"] == "Income"]
total_income = income_df["amount"].sum()

# Specific itemized expenses (exclude bucket transfers)
itemized_df = df[(df["type"] == "Expense") & (df["source"].isin(["Needs", "Wants", "Savings & Investments"]))]

needs_total = itemized_df[itemized_df["category"] == "Needs"]["amount"].sum()
wants_total = itemized_df[itemized_df["category"] == "Wants"]["amount"].sum()
savings_total = itemized_df[itemized_df["category"] == "Savings"]["amount"].sum()

total_expenses = needs_total + wants_total
net_cash_left = total_income - (total_expenses + savings_total)
savings_rate = (savings_total / total_income * 100) if total_income > 0 else 0
burn_rate_daily = (total_expenses / 30) if total_expenses > 0 else 0
runway_months = (st.session_state.starting_net_worth / total_expenses) if total_expenses > 0 else 999

# Financial Health Score (0-100)
# Formula: 40% Savings rate, 30% Needs within 50%, 20% Wants within 30%, 10% Runway
score_sr = min(40, (savings_rate / 20) * 40)
needs_ratio = (needs_total / total_income) if total_income > 0 else 1
score_needs = 30 if needs_ratio <= 0.50 else max(0, 30 - ((needs_ratio - 0.50) * 100))
wants_ratio = (wants_total / total_income) if total_income > 0 else 1
score_wants = 20 if wants_ratio <= 0.30 else max(0, 20 - ((wants_ratio - 0.30) * 80))
score_runway = min(10, (runway_months / 6) * 10)
health_score = int(np.clip(score_sr + score_needs + score_wants + score_runway, 0, 100))

# ---------------------------------------------------------
# Top Hero Header Banner
# ---------------------------------------------------------
st.markdown(f"""
<div class="hero-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 2.1rem; letter-spacing: -0.02em;">
                💸 CashFlow IQ Dashboard
            </h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 0.95rem;">
                Live Financial Intelligence, Flow Visualization & 12-Month Projections
            </p>
        </div>
        <div style="text-align: right; background: rgba(15, 23, 42, 0.6); padding: 12px 20px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Financial Health Score</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {'#10b981' if health_score >= 80 else '#fbbf24' if health_score >= 60 else '#f43f5e'};">
                {health_score} / 100
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI Metric Cards Row
# ---------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Monthly Inflow</div>
        <div class="metric-value">${total_income:,.0f}</div>
        <div class="metric-delta delta-positive">▲ Across {len(income_df)} sources</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Essential Needs (50%)</div>
        <div class="metric-value">${needs_total:,.0f}</div>
        <div class="metric-delta {( 'delta-positive' if (needs_total/total_income*100 <= 50) else 'delta-negative' )}">
            {(needs_total / total_income * 100) if total_income > 0 else 0:.1f}% of Inflow
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Discretionary (30%)</div>
        <div class="metric-value">${wants_total:,.0f}</div>
        <div class="metric-delta {( 'delta-positive' if (wants_total/total_income*100 <= 30) else 'delta-negative' )}">
            {(wants_total / total_income * 100) if total_income > 0 else 0:.1f}% of Inflow
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Savings & Invest (20%)</div>
        <div class="metric-value">${savings_total:,.0f}</div>
        <div class="metric-delta {( 'delta-positive' if savings_rate >= 20 else 'delta-negative' )}">
            {savings_rate:.1f}% Savings Rate
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Emergency Runway</div>
        <div class="metric-value">{runway_months:.1f} <span style="font-size: 1rem; color: #94a3b8;">mo</span></div>
        <div class="metric-delta delta-neutral">🛡️ At ${burn_rate_daily:.0f}/day burn</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Interactive Tabbed Visualizer Experience
# ---------------------------------------------------------
tabs = st.tabs([
    "🌊 CashFlow Sankey Stream", 
    "📊 Category Breakdown & Treemap", 
    "📈 12-Month Net Worth Simulator", 
    "🎯 50/30/20 Rule Audit",
    "📝 Transaction & Budget Planner"
])

# ---------------------------------------------------------
# TAB 1: Sankey Flow Diagram
# ---------------------------------------------------------
with tabs[0]:
    st.markdown("<div class='section-title'>🌊 Dynamic Cashflow Sankey Stream</div>", unsafe_allow_html=True)
    st.caption("Trace the continuous stream of every dollar from origin income to target buckets and final spending/investing endpoints.")
    
    # Dynamically update the main bucket sums from itemized rows to guarantee clean balanced flow
    plot_df = df.copy()
    
    # Calculate unique node mapping
    all_nodes = list(dict.fromkeys(plot_df["source"].tolist() + plot_df["target"].tolist()))
    node_map = {node: i for i, node in enumerate(all_nodes)}
    
    # Define aesthetic node color palette
    node_colors = []
    for node in all_nodes:
        if node == "Net Income":
            node_colors.append("rgba(99, 102, 241, 0.9)")  # Indigo
        elif node == "Needs":
            node_colors.append("rgba(59, 130, 246, 0.9)")  # Blue
        elif node == "Wants":
            node_colors.append("rgba(245, 158, 11, 0.9)")  # Amber
        elif node == "Savings & Investments":
            node_colors.append("rgba(168, 85, 247, 0.9)")  # Purple
        elif node in income_df["source"].values:
            node_colors.append("rgba(16, 185, 129, 0.85)") # Emerald
        elif node in itemized_df[itemized_df["category"] == "Needs"]["target"].values:
            node_colors.append("rgba(96, 165, 250, 0.75)") # Light Blue
        elif node in itemized_df[itemized_df["category"] == "Wants"]["target"].values:
            node_colors.append("rgba(251, 191, 36, 0.75)") # Light Amber
        else:
            node_colors.append("rgba(192, 132, 252, 0.75)") # Light Purple

    # Link colors with transparency
    link_colors = []
    for _, row in plot_df.iterrows():
        cat = row["category"]
        if cat == "Income":
            link_colors.append("rgba(16, 185, 129, 0.35)")
        elif cat == "Bucket":
            if row["target"] == "Needs":
                link_colors.append("rgba(59, 130, 246, 0.35)")
            elif row["target"] == "Wants":
                link_colors.append("rgba(245, 158, 11, 0.35)")
            else:
                link_colors.append("rgba(168, 85, 247, 0.35)")
        elif cat == "Needs":
            link_colors.append("rgba(96, 165, 250, 0.30)")
        elif cat == "Wants":
            link_colors.append("rgba(251, 191, 36, 0.30)")
        else:
            link_colors.append("rgba(192, 132, 252, 0.30)")

    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=22,
            line=dict(color="rgba(255, 255, 255, 0.2)", width=0.8),
            label=all_nodes,
            color=node_colors,
            hovertemplate='<b>%{label}</b><br>Total Flow: $%{value:,.0f}<extra></extra>'
        ),
        link=dict(
            source=[node_map[s] for s in plot_df["source"]],
            target=[node_map[t] for t in plot_df["target"]],
            value=plot_df["amount"],
            color=link_colors,
            hovertemplate='<b>%{source.label}</b> ➔ <b>%{target.label}</b><br>Amount: $%{value:,.0f}<extra></extra>'
        )
    )])

    fig_sankey.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=13, color="#e2e8f0"),
        height=520,
        margin=dict(l=10, r=10, t=20, b=20)
    )

    st.plotly_chart(fig_sankey, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: Category Breakdown & Treemap
# ---------------------------------------------------------
with tabs[1]:
    st.markdown("<div class='section-title'>📊 Hierarchical Treemap & Donut Distribution</div>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([3, 2])
    
    with col_t1:
        st.subheader("Interactive Expense Hierarchy (Treemap)")
        fig_treemap = px.treemap(
            itemized_df,
            path=["category", "target"],
            values="amount",
            color="category",
            color_discrete_map={
                "Needs": "#3b82f6",
                "Wants": "#f59e0b",
                "Savings": "#a855f7"
            },
            hover_data={"amount": ":$,.0f"}
        )
        fig_treemap.update_traces(
            textinfo="label+value+percent entry",
            textfont=dict(size=14, family="Plus Jakarta Sans"),
            marker=dict(cornerradius=6)
        )
        fig_treemap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc"),
            margin=dict(l=0, r=0, t=10, b=0),
            height=430
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        
    with col_t2:
        st.subheader("Budget Bucket Split")
        bucket_summary = pd.DataFrame({
            "Bucket": ["Needs", "Wants", "Savings & Investments"],
            "Amount": [needs_total, wants_total, savings_total]
        })
        
        fig_donut = px.pie(
            bucket_summary,
            names="Bucket",
            values="Amount",
            hole=0.62,
            color="Bucket",
            color_discrete_map={
                "Needs": "#3b82f6",
                "Wants": "#f59e0b",
                "Savings & Investments": "#a855f7"
            }
        )
        fig_donut.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=12, color="#cbd5e1"),
            marker=dict(line=dict(color="#0f172a", width=2))
        )
        fig_donut.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#f8fafc"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=430,
            annotations=[dict(text=f"${total_income:,.0f}<br><span style='font-size:12px;color:#94a3b8;'>Total Inflow</span>", x=0.5, y=0.5, font_size=18, showarrow=False, font_color="#ffffff")]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: 12-Month Net Worth Simulator
# ---------------------------------------------------------
with tabs[2]:
    st.markdown("<div class='section-title'>📈 12-Month Net Worth & Growth Simulator</div>", unsafe_allow_html=True)
    st.caption("Forecast how your wealth compounds over the next year using dynamic monthly savings and investment returns.")
    
    sim_c1, sim_c2, sim_c3 = st.columns(3)
    with sim_c1:
        annual_return = st.slider("Expected Annual Investment Return (%)", 0.0, 20.0, 8.0, 0.5)
    with sim_c2:
        inflation_rate = st.slider("Expected Annual Inflation (%)", 0.0, 10.0, 3.0, 0.5)
    with sim_c3:
        extra_monthly_boost = st.number_input("Optional Monthly Extra Contribution ($)", 0, 5000, 0, 50)
        
    # Generate 12-month projections
    months = ["Current"] + [(datetime.now() + timedelta(days=30*i)).strftime("%b %Y") for i in range(1, 13)]
    
    monthly_return_rate = ((1 + (annual_return / 100)) ** (1/12)) - 1
    monthly_effective_savings = savings_total + extra_monthly_boost
    
    # Conservative (4%), Expected, and Aggressive (12%) scenarios
    net_worth_expected = [st.session_state.starting_net_worth]
    net_worth_conservative = [st.session_state.starting_net_worth]
    net_worth_aggressive = [st.session_state.starting_net_worth]
    
    for _ in range(12):
        # Expected
        prev = net_worth_expected[-1]
        growth = prev * monthly_return_rate
        net_worth_expected.append(prev + growth + monthly_effective_savings)
        
        # Conservative
        prev_c = net_worth_conservative[-1]
        growth_c = prev_c * (((1 + 0.03)**(1/12)) - 1)
        net_worth_conservative.append(prev_c + growth_c + monthly_effective_savings)
        
        # Aggressive
        prev_a = net_worth_aggressive[-1]
        growth_a = prev_a * (((1 + 0.12)**(1/12)) - 1)
        net_worth_aggressive.append(prev_a + growth_a + monthly_effective_savings)

    forecast_df = pd.DataFrame({
        "Month": months,
        "Conservative (3%)": net_worth_conservative,
        "Expected Plan": net_worth_expected,
        "Aggressive (12%)": net_worth_aggressive
    })

    fig_forecast = go.Figure()
    
    # Aggressive
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df["Month"],
        y=forecast_df["Aggressive (12%)"],
        mode="lines",
        line=dict(color="rgba(52, 211, 153, 0.5)", width=1.5, dash="dot"),
        name="Aggressive Market (12%)"
    ))
    
    # Expected with filled area
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df["Month"],
        y=forecast_df["Expected Plan"],
        mode="lines+markers",
        line=dict(color="#6366f1", width=3.5),
        marker=dict(size=6, color="#a855f7"),
        fill='tonexty',
        fillcolor="rgba(99, 102, 241, 0.12)",
        name=f"Expected ({annual_return}%)"
    ))
    
    # Conservative
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df["Month"],
        y=forecast_df["Conservative (3%)"],
        mode="lines",
        line=dict(color="rgba(148, 163, 184, 0.6)", width=1.5, dash="dash"),
        fill='tonexty',
        fillcolor="rgba(244, 63, 94, 0.05)",
        name="Conservative (3%)"
    ))
    
    fig_forecast.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#e2e8f0"),
        height=450,
        hovermode="x unified",
        xaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", showline=False),
        yaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", tickprefix="$", showline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Milestone card
    year_end_expected = net_worth_expected[-1]
    net_increase = year_end_expected - st.session_state.starting_net_worth
    st.info(f"💡 **12-Month Projection Summary:** By maintaining your monthly savings of **${monthly_effective_savings:,.0f}**, your estimated wealth will increase by **+${net_increase:,.0f}** to reach **${year_end_expected:,.0f}** by {months[-1]}.")

# ---------------------------------------------------------
# TAB 4: 50/30/20 Rule Audit & AI Financial Coach
# ---------------------------------------------------------
with tabs[3]:
    st.markdown("<div class='section-title'>🎯 50/30/20 Rule Benchmark & Financial Health Audit</div>", unsafe_allow_html=True)
    
    aud_col1, aud_col2 = st.columns([1, 1])
    
    with aud_col1:
        st.subheader("Budget Benchmark vs Standard")
        
        bench_data = pd.DataFrame({
            "Category": ["Needs", "Wants", "Savings & Investments"],
            "Target %": [50, 30, 20],
            "Actual %": [
                (needs_total / total_income * 100) if total_income > 0 else 0,
                (wants_total / total_income * 100) if total_income > 0 else 0,
                (savings_total / total_income * 100) if total_income > 0 else 0
            ]
        })
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Target (50/30/20)",
            x=bench_data["Category"],
            y=bench_data["Target %"],
            marker_color="rgba(148, 163, 184, 0.4)",
            text=bench_data["Target %"].apply(lambda x: f"{x}%"),
            textposition="auto"
        ))
        fig_bar.add_trace(go.Bar(
            name="Your Current Budget",
            x=bench_data["Category"],
            y=bench_data["Actual %"],
            marker_color=["#3b82f6", "#f59e0b", "#a855f7"],
            text=bench_data["Actual %"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto"
        ))
        
        fig_bar.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#e2e8f0"),
            height=380,
            yaxis=dict(ticksuffix="%", gridcolor="rgba(255, 255, 255, 0.06)"),
            xaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with aud_col2:
        st.subheader("💡 Financial Coach Insights")
        
        # Personalized automated insights
        if needs_ratio > 0.50:
            st.warning(f"⚠️ **Needs Alert:** Your essential needs account for **{(needs_ratio*100):.1f}%** of income (target: ≤50%). Consider reviewing high fixed costs like rent or auto expenses.")
        else:
            st.success(f"✅ **Needs Optimized:** Essential spending is well-controlled at **{(needs_ratio*100):.1f}%**.")

        if wants_ratio > 0.30:
            st.warning(f"⚠️ **Discretionary Spending:** Wants take up **{(wants_ratio*100):.1f}%** of income (target: ≤30%). Trimming dining out or unused subscriptions can boost savings.")
        else:
            st.success(f"✅ **Wants In Check:** Discretionary lifestyle spending is healthy at **{(wants_ratio*100):.1f}%**.")

        if savings_rate >= 20:
            st.success(f"🌟 **Outstanding Savings Rate:** You are saving **{savings_rate:.1f}%** of income! You are on an accelerated path to financial independence.")
        else:
            st.info(f"💡 **Savings Growth Opportunity:** Current savings rate is **{savings_rate:.1f}%**. Aiming for 20% would add **${(total_income*0.20 - savings_total):,.0f}/mo** to investments.")

        if runway_months < 3:
            st.error(f"🚨 **Emergency Fund Priority:** Your liquid emergency buffer lasts **{runway_months:.1f} months**. Prioritize building at least a 3 to 6-month buffer.")
        elif runway_months >= 6:
            st.success(f"🛡️ **Fortress Runway:** You have **{runway_months:.1f} months** of living expenses secured.")

# ---------------------------------------------------------
# TAB 5: Interactive Transaction & Budget Planner
# ---------------------------------------------------------
with tabs[4]:
    st.markdown("<div class='section-title'>📝 Transaction & Budget Planner</div>", unsafe_allow_html=True)
    st.caption("Add, edit, or customize any income stream or expense item. All charts update in real-time.")
    
    col_add, col_table = st.columns([1, 2])
    
    with col_add:
        st.subheader("➕ Add New Item")
        with st.form("new_entry_form", clear_on_submit=True):
            entry_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
            
            if entry_type == "Income":
                name = st.text_input("Income Source Name", placeholder="e.g. Dividend Yield")
                category = "Income"
                source = name if name else "New Income"
                target = "Net Income"
            else:
                name = st.text_input("Expense Item Name", placeholder="e.g. Gym Membership")
                category = st.selectbox("Category Bucket", ["Needs", "Wants", "Savings"])
                source = "Needs" if category == "Needs" else "Wants" if category == "Wants" else "Savings & Investments"
                target = name if name else "New Expense"
                
            amount = st.number_input("Monthly Amount ($)", min_value=1.0, value=100.0, step=25.0)
            submitted = st.form_submit_button("Add to Financial Plan", type="primary", use_container_width=True)
            
            if submitted:
                if name.strip():
                    new_row = pd.DataFrame([{
                        "type": entry_type,
                        "source": source,
                        "target": target,
                        "amount": float(amount),
                        "category": category
                    }])
                    st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                    st.toast(f"Added {name} (${amount:,.0f})", icon="✅")
                    st.rerun()
                else:
                    st.error("Please provide a valid name.")
                    
    with col_table:
        st.subheader("📋 Active Transactions (Editable Table)")
        edited_df = st.data_editor(
            st.session_state.transactions,
            num_rows="dynamic",
            use_container_width=True,
            height=380,
            column_config={
                "amount": st.column_config.NumberColumn("Amount ($)", format="$%d"),
                "type": st.column_config.SelectboxColumn("Type", options=["Income", "Expense"]),
                "category": st.column_config.SelectboxColumn("Category", options=["Income", "Bucket", "Needs", "Wants", "Savings"])
            }
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Save Table Edits", use_container_width=True, type="primary"):
                st.session_state.transactions = edited_df
                st.success("Changes saved!")
                st.rerun()
        with col_btn2:
            if st.button("🔄 Reset to Default Template", use_container_width=True):
                st.session_state.transactions = pd.DataFrame(PRESETS["💼 Tech Professional ($8,500/mo)"])
                st.rerun()

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; color: #64748b; font-size: 0.85rem; border-top: 1px solid rgba(255, 255, 255, 0.05);">
    CashFlow IQ • Built with Python & Streamlit • Interactive Visualizations powered by Plotly
</div>
""", unsafe_allow_html=True)
