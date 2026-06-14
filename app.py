import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Jiji Market Tracker", page_icon="📈", layout="wide")

st.title("📈 Jiji Price & Demand Market Tracker")
st.caption("Empowering buyers and sellers with real-time e-commerce data analytics.")

# --- DATABASE CONNECTION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_client():
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

supabase: Client = get_supabase_client()

# --- SIMULATED DATA ENGINE ---
def get_historical_data(keyword):
    np.random.seed(42)
    dates = pd.date_range(start="2026-05-01", end="2026-06-14", freq="D")
    base_price = 4500000 if "camry" in keyword.lower() else 350000
    prices = base_price + np.random.normal(0, base_price * 0.05, len(dates))
    views = np.random.randint(10, 150, len(dates))
    
    return pd.DataFrame({
        "Date": dates,
        "Price (₦)": prices.astype(int),
        "Daily Views": views,
        "Condition": np.random.choice(["Foreign Used", "Nigerian Used"], len(dates))
    })

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔍 Market Search Settings")
search_query = st.sidebar.text_input("Enter Product Keyword:", placeholder="e.g., Toyota Camry 2012")

st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Create Live Price Alert")
alert_email = st.sidebar.text_input("Your Email Address")
target_price = st.sidebar.number_input("Trigger alert if price drops below (₦):", min_value=1000)

if st.sidebar.button("Set Free Alert"):
    if alert_email and search_query:
        if supabase:
            try:
                data, count = supabase.table("price_alerts").insert({
                    "email": alert_email,
                    "keyword": search_query,
                    "target_price": int(target_price)
                }).execute()
                st.sidebar.success(f"🚀 Alert saved to database for {alert_email}!")
            except Exception as e:
                st.sidebar.error(f"Database error: {e}")
        else:
            st.sidebar.warning("Running in offline mode. Alert simulated successfully!")
    else:
        st.sidebar.error("Please provide both an item name and your email.")

# --- MAIN DASHBOARD INTERFACE ---
if search_query:
    data = get_historical_data(search_query)
    avg_price = int(data["Price (₦)"].mean())
    median_price = int(data["Price (₦)"].median())
    
    col1, col2 = st.columns(2)
    col1.metric(label="Average Market Price", value=f"₦{avg_price:,}")
    col2.metric(label="Median Price Benchmark", value=f"₦{median_price:,}")
    
    st.markdown("---")
    fig = px.line(data, x="Date", y="Price (₦)", color="Condition", title=f"Price Trajectory for '{search_query}'")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👋 Enter a product keyword in the sidebar to visualize market velocity and save automated alerts.")
  
