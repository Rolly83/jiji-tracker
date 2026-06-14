import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from supabase import create_client, Client

# --- ADVANCED CUSTOM BRAND STYLING ---
st.set_page_config(page_title="Jiji Market Tracker", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    h1 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .stMarkdown p {
        color: #A3A8B4 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #00F2FE !important;
        text-shadow: 0px 0px 10px rgba(0, 242, 254, 0.2);
    }
    div[data-testid="stMetricLabel"] {
        color: #E2E8F0 !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1A1F2C !important;
        border-right: 1px solid #2D3748;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Jiji Price & Demand Market Tracker")
st.caption("Empowering buyers and sellers with real-time e-commerce data analytics.")

# --- DATABASE SECURITY CONNECTION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_client():
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

supabase: Client = get_supabase_client()

# --- LIVE REQUESTS & BEAUTIFULSOUP SCRAPER ENGINE ---
def scrape_jiji_live(keyword):
    formatted_query = keyword.replace(" ", "-").lower()
    url = f"https://jiji.ng/search?query={formatted_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    scraped_records = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('div', class_='b-trending-card__template')
            
            for item in listings:
                try:
                    title_elem = item.find('div', class_='b-trending-card__title')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    price_elem = item.find('div', class_='b-trending-card__price')
                    if price_elem:
                        price_str = price_elem.text.strip()
                        cleaned_price = int(re.sub(r'[^\d]', '', price_str))
                    else:
                        continue
                        
                    attr_elem = item.find('div', class_='b-trending-card__item-attr')
                    condition = attr_elem.text.strip() if attr_elem else "Used"
                    
                    scraped_records.append({
                        "Date": datetime.today().strftime('%Y-%m-%d'),
                        "Title": title,
                        "Price (₦)": cleaned_price,
                        "Condition": condition
                    })
                except Exception:
                    continue
    except Exception as e:
        st.error(f"Network processing delay: {e}")
        
    return pd.DataFrame(scraped_records)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔍 Market Search Settings")
search_query = st.sidebar.text_input("Enter Product Keyword:", placeholder="e.g., Toyota Camry 2012")

st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Create Live Price Alert")
alert_email = st.sidebar.text_input("Your Email Address")
target_price = st.sidebar.number_input("Trigger alert if price drops below (₦):", min_value=1000)

if st.sidebar.button("Set Live Alert"):
    if alert_email and search_query:
        if supabase:
            try:
                supabase.table("price_alerts").insert({
                    "email": alert_email,
                    "keyword": search_query,
                    "target_price": int(target_price)
                }).execute()
                st.sidebar.success(f"🚀 Alert saved to database for {alert_email}!")
            except Exception as e:
                st.sidebar.error(f"Database sync issue: {e}")
        else:
            st.sidebar.warning("App running in localized dashboard mode. Input verified.")
    else:
        st.sidebar.error("Please fill in both fields before continuing.")

# --- DATA RENDERING & INTERACTIVE DASHBOARD ---
if search_query:
    with st.spinner(f"Initiating cloud network scan for '{search_query}' on Jiji..."):
        df = scrape_jiji_live(search_query)
        
    if not df.empty:
        avg_price = int(df["Price (₦)"].mean())
        median_price = int(df["Price (₦)"].median())
        
        col1, col2 = st.columns(2)
        col1.metric(label="Real-Time Average Market Price", value=f"₦{avg_price:,}")
        col2.metric(label="Median Price Benchmark", value=f"₦{median_price:,}")
        
        st.markdown("---")
        
        fig = px.box(
            df, 
            x="Condition", 
            y="Price (₦)", 
            color="Condition",
            title=f"Live Price Spread & Valuations for '{search_query}'",
            points="all"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#FFFFFF",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Active Marketplace Listings Captured")
        st.dataframe(df[["Title", "Price (₦)", "Condition"]], use_container_width=True)
        
    else:
        st.warning("⚠️ No active match listings detected on the first page results for this keyword right now. Try adjusting your keyword phrasing (e.g., use 'Camry' instead of 'Camry 2012').")
else:
    st.info("👋 Enter a product keyword in the sidebar menu to launch real-time market discovery metrics.")
