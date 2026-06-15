import streamlit as st
import anthropic
import json
import re
from datetime import datetime

# ── page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="JijiTrack — Nigeria Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@400;500&display=swap');

/* ── reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background-color: #08090A !important;
    color: #E8EAED !important;
}

/* ── hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0F1012; }
::-webkit-scrollbar-thumb { background: #2A2D32; border-radius: 4px; }

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #0A0B0D !important;
    border-right: 1px solid #1A1D22 !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* ── inputs ── */
.stTextInput > div > div > input {
    background: #0F1114 !important;
    border: 1.5px solid #1E2227 !important;
    border-radius: 12px !important;
    color: #E8EAED !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    caret-color: #00D68F !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D68F !important;
    box-shadow: 0 0 0 3px #00D68F1A !important;
}
.stTextInput > div > div > input::placeholder { color: #3D4248 !important; }

/* ── selectbox ── */
.stSelectbox > div > div {
    background: #0F1114 !important;
    border: 1.5px solid #1E2227 !important;
    border-radius: 12px !important;
    color: #E8EAED !important;
    font-size: 14px !important;
}
.stSelectbox [data-baseweb="select"] { background: #0F1114 !important; }

/* ── primary button ── */
.stButton > button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, #00D68F 0%, #00B87A 100%) !important;
    color: #08090A !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: -0.01em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 4px 15px #00D68F25 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00FFAA 0%, #00D68F 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #00D68F35 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── metrics ── */
[data-testid="stMetric"] {
    background: #0D0F12 !important;
    border: 1px solid #1A1D22 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stMetric"]:hover { border-color: #2A2D32 !important; }
[data-testid="stMetricLabel"] {
    color: #4B5563 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color: #E8EAED !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── spinner ── */
.stSpinner > div {
    border-top-color: #00D68F !important;
    border-right-color: #00D68F33 !important;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0D0F12 !important;
    border: 1px solid #1A1D22 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #4B5563 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: #1A1D22 !important;
    color: #E8EAED !important;
}

/* ── divider ── */
hr { border-color: #1A1D22 !important; margin: 20px 0 !important; }

/* ── progress ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00D68F, #00B87A) !important;
    border-radius: 4px !important;
}
.stProgress > div > div > div {
    background: #1A1D22 !important;
    border-radius: 4px !important;
}

/* ── expander ── */
details {
    background: #0D0F12 !important;
    border: 1px solid #1A1D22 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
summary {
    color: #9CA3AF !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 14px 18px !important;
}

/* ── animations ── */
@keyframes fadeIn  { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }
@keyframes pulse   { 0%,100%{opacity:1} 50%{opacity:0.4} }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
@keyframes spin    { to{transform:rotate(360deg)} }

.fade-in { animation: fadeIn 0.4s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def ngn(n):
    try: return f"₦{int(n):,}"
    except: return "₦—"

def demand_meta(score):
    if score >= 80: return ("🔥", "Very High", "#EF4444", "#EF444418")
    if score >= 60: return ("📈", "High",      "#F59E0B", "#F59E0B18")
    if score >= 40: return ("〰", "Moderate",  "#3B82F6", "#3B82F618")
    return               ("📉", "Low",        "#6B7280", "#6B728018")

def comp_badge(level):
    colors = {"Low":"#00D68F","Moderate":"#F59E0B","High":"#F97316","Very High":"#EF4444"}
    c = colors.get(level, "#6B7280")
    return f'<span style="color:{c};background:{c}18;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">● {level}</span>'

def sparkline(prices, w=110, h=34):
    if not prices or len(prices) < 2: return ""
    mn, mx = min(prices), max(prices)
    rng = mx - mn or 1
    p = 4
    pts = " ".join(
        f"{(p + i/(len(prices)-1)*(w-p*2)):.1f},{(p + (mx-v)/rng*(h-p*2)):.1f}"
        for i, v in enumerate(prices)
    )
    rising = prices[-1] >= prices[0]
    stroke = "#00D68F" if rising else "#EF4444"
    fill_pts = pts + f" {w-p},{h-p} {p},{h-p}"
    lx, ly = pts.split()[-1].split(",")
    return f"""<svg width="{w}" height="{h}" style="display:block;overflow:visible">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{stroke}" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="{stroke}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <polygon points="{fill_pts}" fill="url(#sg)"/>
      <polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="{lx}" cy="{ly}" r="3.5" fill="{stroke}" stroke="#08090A" stroke-width="1.5"/>
    </svg>"""

def demand_ring(score):
    _, _, color, _ = demand_meta(score)
    r = 20; circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    return f"""<svg width="52" height="52" style="transform:rotate(-90deg);flex-shrink:0">
      <circle cx="26" cy="26" r="{r}" fill="none" stroke="#1A1D22" stroke-width="3.5"/>
      <circle cx="26" cy="26" r="{r}" fill="none" stroke="{color}" stroke-width="3.5"
        stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"/>
      <text x="26" y="26" text-anchor="middle" dominant-baseline="central"
        style="fill:{color};font-size:10px;font-weight:800;font-family:monospace;
               transform:rotate(90deg);transform-origin:26px 26px">{score}</text>
    </svg>"""

def render_product_card(item, idx):
    icon, label, color, bg = demand_meta(item.get("demandScore", 0))
    trend = item.get("priceTrend", 0)
    trend_str  = "Stable" if trend == 0 else (f"▲ {trend}%" if trend > 0 else f"▼ {abs(trend)}%")
    trend_color = "#6B7280" if trend == 0 else ("#EF4444" if trend > 0 else "#00D68F")
    spark = sparkline(item.get("sparkPrices", []))
    ring  = demand_ring(item.get("demandScore", 0))
    insight = item.get("insight", "")

    st.markdown(f"""
    <div class="fade-in" style="
        background: linear-gradient(145deg, #0F1114 0%, #0D0F12 100%);
        border: 1px solid #1A1D22;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 12px;
        animation-delay: {idx * 0.06}s;
        transition: border-color 0.2s, transform 0.2s;
        position: relative;
        overflow: hidden;
    ">
      <!-- subtle top accent line -->
      <div style="position:absolute;top:0;left:24px;right:24px;height:1px;
                  background:linear-gradient(90deg,transparent,{color}44,transparent)"></div>

      <!-- header row -->
      <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:18px">
        {ring}
        <div style="flex:1;min-width:0">
          <div style="font-size:15px;font-weight:700;color:#F3F4F6;line-height:1.3;
                      margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
            {item.get("title","—")}
          </div>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <span style="font-size:11px;color:{color};background:{bg};padding:3px 10px;
                         border-radius:20px;font-weight:700;letter-spacing:0.02em">
              {icon} {label}
            </span>
            <span style="font-size:11px;color:#4B5563;font-weight:500">
              {item.get("listingCount","—")} active listings
            </span>
          </div>
        </div>
      </div>

      <!-- price row -->
      <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-end;margin-bottom:16px">
        <div>
          <div style="font-size:10px;color:#4B5563;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Average price</div>
          <div style="font-size:26px;font-weight:900;color:#00D68F;
                      font-family:'DM Mono',monospace;letter-spacing:-0.03em;line-height:1">
            {ngn(item.get("avgPrice",0))}
          </div>
        </div>
        <div>
          <div style="font-size:10px;color:#4B5563;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Price range</div>
          <div style="font-size:13px;color:#9CA3AF;font-family:'DM Mono',monospace;font-weight:500">
            {ngn(item.get("minPrice",0))} → {ngn(item.get("maxPrice",0))}
          </div>
        </div>
        <div style="margin-left:auto;text-align:right">
          <div style="font-size:10px;color:#4B5563;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Price trend</div>
          <div style="font-size:15px;font-weight:800;color:{trend_color};
                      font-family:'DM Mono',monospace">{trend_str}</div>
          <div style="margin-top:6px">{spark}</div>
        </div>
      </div>

      <!-- insight -->
      {"" if not insight else f'''
      <div style="background:linear-gradient(135deg,#00D68F0A,#00D68F05);
                  border:1px solid #00D68F20;
                  border-radius:10px;padding:12px 16px;
                  font-size:12.5px;color:#00C47E;line-height:1.6;font-weight:500">
        <span style="color:#00D68F;font-weight:700;margin-right:6px">💡</span>{insight}
      </div>'''}
    </div>
    """, unsafe_allow_html=True)

def search_jiji(query, category):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    cat_hint = f' in "{category}"' if category != "All categories" else ""
    prompt = f"""You are a Nigerian market intelligence analyst. Search Jiji.ng for current listings of: "{query}"{cat_hint}.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "totalListings": <integer>,
  "overallDemandScore": <0-100>,
  "avgMarketPrice": <naira integer>,
  "priceRange": {{ "min": <integer>, "max": <integer> }},
  "marketSummary": "<2 sentence overview for Nigerian resellers>",
  "competitionLevel": "<Low|Moderate|High|Very High>",
  "bestTimeToSell": "<brief timing advice>",
  "hotKeywords": ["<kw1>","<kw2>","<kw3>","<kw4>","<kw5>"],
  "items": [
    {{
      "title": "<specific variant/model>",
      "avgPrice": <naira integer>,
      "minPrice": <naira integer>,
      "maxPrice": <naira integer>,
      "listingCount": <integer>,
      "demandScore": <0-100>,
      "priceTrend": <integer percent, positive=rising>,
      "sparkPrices": [<5 naira integers showing recent price history>],
      "insight": "<1 sentence actionable tip for a Nigerian reseller>"
    }}
  ]
}}

Include 4-7 distinct items. All prices in Nigerian Naira. Use real Jiji.ng data from web search."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if hasattr(b, "text"))
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No data returned — try a different search term.")
    return json.loads(match.group())

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 20px 16px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
        <div style="width:36px;height:36px;border-radius:10px;
                    background:linear-gradient(135deg,#00D68F,#00956A);
                    display:flex;align-items:center;justify-content:center;font-size:18px">
          📊
        </div>
        <div>
          <div style="font-size:16px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em">JijiTrack</div>
          <div style="font-size:10px;color:#3D4248;font-weight:500;letter-spacing:0.05em;text-transform:uppercase">Nigeria Market Intel</div>
        </div>
      </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,#1A1D22,transparent);margin:0 20px 20px"></div>
    """, unsafe_allow_html=True)

    # live badge
    st.markdown("""
    <div style="padding:0 20px 16px">
      <div style="background:#00D68F0D;border:1px solid #00D68F20;border-radius:10px;
                  padding:10px 14px;display:flex;align-items:center;gap:10px">
        <div style="width:7px;height:7px;border-radius:50%;background:#00D68F;
                    box-shadow:0 0 6px #00D68F;flex-shrink:0;animation:pulse 2s infinite"></div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#00D68F">Live data</div>
          <div style="font-size:10px;color:#3D4248">Powered by Jiji.ng</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 20px"><div style="font-size:10px;color:#3D4248;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:10px">Quick searches</div></div>', unsafe_allow_html=True)

    QUICK = [
        ("📱", "iPhone 15 Pro Max"),
        ("⚡", "Honda Generator"),
        ("💻", "MacBook Pro M3"),
        ("🚗", "Tokunbo Camry 2018"),
        ("📲", "Tecno Camon 30"),
        ("📺", "LG Plasma 43 inch"),
        ("🎧", "AirPods Pro"),
        ("🖨️", "HP LaserJet Printer"),
    ]

    for emoji, label in QUICK:
        if st.button(f"{emoji}  {label}", key=f"qs_{label}", use_container_width=True):
            st.session_state["queued_query"] = label
            st.rerun()

    st.markdown('<div style="height:1px;background:#1A1D22;margin:16px 20px"></div>', unsafe_allow_html=True)

    # search history
    if st.session_state.get("history"):
        st.markdown('<div style="padding:0 20px"><div style="font-size:10px;color:#3D4248;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:10px">Recent searches</div></div>', unsafe_allow_html=True)
        for h in reversed(st.session_state["history"][-6:]):
            if st.button(f"🕐  {h}", key=f"hist_{h}", use_container_width=True):
                st.session_state["queued_query"] = h
                st.rerun()

    # bottom
    st.markdown("""
    <div style="position:fixed;bottom:0;width:260px;padding:16px 20px;
                border-top:1px solid #1A1D22;background:#0A0B0D">
      <div style="font-size:10px;color:#2A2D32;line-height:1.6">
        Data sourced from Jiji.ng<br>
        For research purposes only<br>
        🇳🇬 Built for Nigeria
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════
CATEGORIES = [
    "All categories", "Phones & Tablets", "Electronics",
    "Laptops & Computers", "Vehicles", "Fashion",
    "Home & Garden", "Health & Beauty", "Sports & Outdoors", "Real Estate",
]

if "history" not in st.session_state:
    st.session_state["history"] = []
if "results" not in st.session_state:
    st.session_state["results"] = None

# pick up queued query from sidebar
default_query = st.session_state.pop("queued_query", "")

# ── nav bar ────────────────────────────────────────────────────
st.markdown("""
<div style="background:#08090AEE;backdrop-filter:blur(16px);
            border-bottom:1px solid #1A1D22;
            padding:14px 32px;display:flex;align-items:center;gap:12px;
            position:sticky;top:0;z-index:99">
  <div style="font-size:15px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em">
    Market Intelligence
  </div>
  <div style="margin-left:auto;display:flex;gap:10px;align-items:center">
    <span style="font-size:11px;color:#00D68F;background:#00D68F15;
                 padding:4px 12px;border-radius:20px;font-weight:700;letter-spacing:0.05em">
      ● LIVE
    </span>
    <span style="font-size:11px;color:#2A2D32;background:#0D0F12;
                 border:1px solid #1A1D22;padding:4px 12px;border-radius:8px">
      jiji.ng
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── hero (before first search) ─────────────────────────────────
if not st.session_state["results"]:
    st.markdown("""
    <div style="padding:60px 40px 40px;text-align:center;max-width:680px;margin:0 auto">
      <div style="display:inline-block;font-size:10px;color:#00D68F;font-weight:700;
                  letter-spacing:0.2em;text-transform:uppercase;
                  background:#00D68F0D;border:1px solid #00D68F20;
                  padding:5px 16px;border-radius:20px;margin-bottom:24px">
        Real-time · Jiji.ng · Nigeria
      </div>
      <h1 style="font-size:clamp(32px,5vw,54px);font-weight:900;letter-spacing:-0.04em;
                 line-height:1.05;margin-bottom:18px;color:#FFFFFF">
        Know what sells.<br>
        <span style="background:linear-gradient(135deg,#00D68F,#00FFAA);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     b
