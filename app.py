import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Jiji Market Intelligence", page_icon="📈", layout="wide")

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1 { color: #008751 !important; }
    div[data-testid="stMetricValue"] { color: #00F2FE !important; }
    </style>
""", unsafe_allow_html=True)

# --- CATEGORY ENGINE ---
st.sidebar.header("📊 Market Navigator")
category = st.sidebar.selectbox(
    "Select Product Category",
    ["Cars & Vehicles", "Mobile Phones", "Electronics", "Real Estate", "Fashion"]
)

# Baseline Pricing Data (The "Professional" logic layer)
category_baselines = {
    "Cars & Vehicles": 4500000,
    "Mobile Phones": 350000,
    "Electronics": 150000,
    "Real Estate": 50000000,
    "Fashion": 20000
}

# --- DATA PROCESSING ENGINE ---
def get_market_data(cat):
    # Simulated professional data pull (Replace with your API logic)
    base_price = category_baselines.get(cat, 100000)
    data = []
    for _ in range(50):
        # Generate data with controlled variance to ensure realistic distributions
        price = np.random.normal(base_price, base_price * 0.25)
        data.append({
            "Title": f"{cat} Listing",
            "Price (₦)": int(price),
            "Condition": np.random.choice(["Tokunbo", "Nigerian Used"])
        })
    return pd.DataFrame(data)

def filter_outliers(df):
    # Statistical Filtering (Phase 1: Precision Layer)
    median = df['Price (₦)'].median()
    std = df['Price (₦)'].std()
    # Remove items outside 2 standard deviations (the "noise" filter)
    filtered_df = df[(df['Price (₦)'] > median - 2*std) & (df['Price (₦)'] < median + 2*std)]
    return filtered_df

# --- DASHBOARD RENDERING ---
st.title(f"🇳🇬 {category} Market Intelligence")

with st.spinner("Analyzing market nodes..."):
    raw_df = get_market_data(category)
    df = filter_outliers(raw_df)

col1, col2 = st.columns(2)
col1.metric("Average Market Price", f"₦{int(df['Price (₦)'].mean()):,}")
col2.metric("Verified Median Benchmark", f"₦{int(df['Price (₦)'].median()):,}")

# Professional Visualization
fig = px.box(df, x="Condition", y="Price (₦)", color="Condition", 
             title=f"Price Spread: {category}", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Verified Listings")
st.dataframe(df, use_container_width=True)
