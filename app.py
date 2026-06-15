import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="Jiji Market Intelligence", page_icon="📈", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1 { color: #008751 !important; }
    div[data-testid="stMetricValue"] { color: #00F2FE !important; }
    .card { background-color: #1A1F2C; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATOR ---
st.sidebar.header("🔍 Market Search")
# Global Search Bar
search_query = st.sidebar.text_input("Search for any product...")

st.sidebar.header("📊 Category Filters")
category = st.sidebar.selectbox("Select Product Category", 
                                ["Cars & Vehicles", "Mobile Phones", "Electronics", "Real Estate", "Fashion"])

# --- DATA PROCESSING (PHASE 1: FILTERING) ---
def filter_outliers(df, column='Price (₦)'):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    return df[(df[column] >= (Q1 - 1.5 * IQR)) & (df[column] <= (Q3 + 1.5 * IQR))]

# --- MARKET ENGINE ---
def get_market_data(cat, query):
    base = {"Cars & Vehicles": 4500000, "Mobile Phones": 350000, "Electronics": 150000}.get(cat, 100000)
    # Simulate data - using 'Foreign Used' instead of 'Tokunbo'
    data = [{"Title": f"{query if query else cat} Item", 
             "Price (₦)": int(np.random.normal(base, base*0.3)), 
             "Condition": np.random.choice(["Foreign Used", "Nigerian Used"])} for _ in range(50)]
    return pd.DataFrame(data)

# --- MAIN DASHBOARD ---
st.title(f"🇳🇬 Market Intelligence: {search_query if search_query else category}")

raw_df = get_market_data(category, search_query)
df = filter_outliers(raw_df)

# CARD LAYOUT
c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="card"><h3>📉 Avg Price</h3><h2>₦{int(df["Price (₦)"].mean()):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>🔥 Median Benchmark</h3><h2>₦{int(df["Price (₦)"].median()):,}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>💡 Listings Count</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.plotly_chart(px.box(df, x="Condition", y="Price (₦)", color="Condition", template="plotly_dark"), use_container_width=True)

st.subheader("📋 Verified Listings")
st.dataframe(df, use_container_width=True)
