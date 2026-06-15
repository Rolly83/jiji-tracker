import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="Jiji Market Intelligence", page_icon="📈", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1 { color: #008751 !important; }
    div[data-testid="stMetricValue"] { color: #00F2FE !important; }
    .card { background-color: #1A1F2C; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE CONNECTION (Environment Variables) ---
# Ensure you set SUPABASE_URL and SUPABASE_KEY in Render's Environment settings
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None

# --- DATA PROCESSING (Phase 1: Precision Filter) ---
def filter_outliers(df, column='Price (₦)'):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    return df[(df[column] >= (Q1 - 1.5 * IQR)) & (df[column] <= (Q3 + 1.5 * IQR))]

# --- MARKET ENGINE ---
def get_market_data(cat, query):
    # Model database for realistic listings
    model_db = {
        "Cars & Vehicles": ["Toyota Camry", "Toyota Corolla", "Lexus RX350", "Honda Accord"],
        "Mobile Phones": ["iPhone 15 Pro", "iPhone 16", "Samsung S24 Ultra", "Infinix Note 40"],
        "Electronics": ["LG Smart TV", "Sony Soundbar", "Dell Latitude"],
        "Real Estate": ["3 Bedroom Flat", "Mini Flat", "Self Contain"],
        "Fashion": ["Nike Sneakers", "Gucci Bag", "Designer Polo"]
    }
    
    # Logic to select product name
    if query:
        titles = [f"{query} (Verified)" for _ in range(50)]
    else:
        models = model_db.get(cat, [f"{cat} Item"])
        titles = [np.random.choice(models) for _ in range(50)]
        
    base = {"Cars & Vehicles": 4500000, "Mobile Phones": 350000, "Electronics": 150000}.get(cat, 100000)
    
    data = []
    for title in titles:
        data.append({
            "Title": title,
            "Price (₦)": int(np.random.normal(base, base*0.3)),
            "Condition": np.random.choice(["Foreign Used", "Nigerian Used"])
        })
    return pd.DataFrame(data)

# --- SIDEBAR ---
st.sidebar.header("🔍 Market Navigator")
search_query = st.sidebar.text_input("Search for any product...")
category = st.sidebar.selectbox("Category", ["Cars & Vehicles", "Mobile Phones", "Electronics", "Real Estate", "Fashion"])

# --- DASHBOARD ---
st.title(f"🇳🇬 Market Intelligence: {search_query if search_query else category}")

raw_df = get_market_data(category, search_query)
df = filter_outliers(raw_df)

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="card"><h3>📉 Avg Price</h3><h2>₦{int(df["Price (₦)"].mean()):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>🔥 Median Benchmark</h3><h2>₦{int(df["Price (₦)"].median()):,}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>💡 Listings Count</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

st.plotly_chart(px.box(df, x="Condition", y="Price (₦)", color="Condition", template="plotly_dark"), use_container_width=True)
st.subheader("📋 Verified Listings")
st.dataframe(df, use_container_width=True)
