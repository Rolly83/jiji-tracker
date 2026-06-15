import streamlit as st
import anthropic
import json
import re
from datetime import datetime

st.set_page_config(
    page_title="JijiTrack - Nigeria Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (single-quoted strings only, no triple quotes) ─────────
CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900"
    "&family=DM+Mono:wght@400;500&display=swap');"
    "*, *::before, *::after { box-sizing: border-box; }"
    "html, body, [class*='css'] {"
    "  font-family: 'Inter', sans-serif !important;"
    "  background-color: #08090A !important;"
    "  color: #E8EAED !important;"
    "}"
    "#MainMenu, footer, header { visibility: hidden !important; }"
    ".block-container { padding: 0 !important; max-width: 100% !important; }"
    "::-webkit-scrollbar { width: 4px; }"
    "::-webkit-scrollbar-track { background: #0F1012; }"
    "::-webkit-scrollbar-thumb { background: #2A2D32; border-radius: 4px; }"
    "section[data-testid='stSidebar'] {"
    "  background: #0A0B0D !important;"
    "  border-right: 1px solid #1A1D22 !important;"
    "  min-width: 260px !important; max-width: 260px !important;"
    "}"
    "section[data-testid='stSidebar'] > div { padding: 0 !important; }"
    ".stTextInput > div > div > input {"
    "  background: #0F1114 !important;"
    "  border: 1.5px solid #1E2227 !important;"
    "  border-radius: 12px !important;"
    "  color: #E8EAED !important;"
    "  font-family: 'Inter', sans-serif !important;"
    "  font-size: 15px !important;"
    "  padding: 14px 18px !important;"
    "  caret-color: #00D68F !important;"
    "  transition: border-color 0.2s, box-shadow 0.2s !important;"
    "}"
    ".stTextInput > div > div > input:focus {"
    "  border-color: #00D68F !important;"
    "  box-shadow: 0 0 0 3px #00D68F1A !important;"
    "}"
    ".stTextInput > div > div > input::placeholder { color: #3D4248 !important; }"
    ".stSelectbox > div > div {"
    "  background: #0F1114 !important;"
    "  border: 1.5px solid #1E2227 !important;"
    "  border-radius: 12px !important;"
    "  color: #E8EAED !important;"
    "}"
    ".stButton > button {"
    "  background: linear-gradient(135deg, #00D68F 0%, #00B87A 100%) !important;"
    "  color: #08090A !important;"
    "  font-weight: 700 !important;"
    "  font-size: 14px !important;"
    "  border: none !important;"
    "  border-radius: 12px !important;"
    "  padding: 13px 24px !important;"
    "  width: 100% !important;"
    "  transition: all 0.2s !important;"
    "  font-family: 'Inter', sans-serif !important;"
    "  box-shadow: 0 4px 14px #00D68F20 !important;"
    "}"
    ".stButton > button:hover {"
    "  background: linear-gradient(135deg, #00FFAA 0%, #00D68F 100%) !important;"
    "  transform: translateY(-1px) !important;"
    "  box-shadow: 0 6px 20px #00D68F30 !important;"
    "}"
    "[data-testid='stMetric'] {"
    "  background: #0D0F12 !important;"
    "  border: 1px solid #1A1D22 !important;"
    "  border-radius: 14px !important;"
    "  padding: 18px 20px !important;"
    "}"
    "[data-testid='stMetricLabel'] {"
    "  color: #4B5563 !important;"
    "  font-size: 10px !important;"
    "  font-weight: 600 !important;"
    "  text-transform: uppercase !important;"
    "  letter-spacing: 0.1em !important;"
    "}"
    "[data-testid='stMetricValue'] {"
    "  color: #E8EAED !important;"
    "  font-family: 'DM Mono', monospace !important;"
    "  font-size: 20px !important;"
    "  font-weight: 700 !important;"
    "}"
    ".stSpinner > div { border-top-color: #00D68F !important; }"
    "hr { border-color: #1A1D22 !important; margin: 16px 0 !important; }"
    ".stTabs [data-baseweb='tab-list'] {"
    "  background: #0D0F12 !important;"
    "  border: 1px solid #1A1D22 !important;"
    "  border-radius: 12px !important;"
    "  padding: 5px !important;"
    "}"
    ".stTabs [data-baseweb='tab'] {"
    "  background: transparent !important;"
    "  border-radius: 8px !important;"
    "  color: #4B5563 !important;"
    "  font-weight: 600 !important;"
    "}"
    ".stTabs [aria-selected='true'] {"
    "  background: #1A1D22 !important;"
    "  color: #E8EAED !important;"
    "}"
    "@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }"
    "@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }"
)

st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

# ── helpers ────────────────────────────────────────────────────
def ngn(n):
    try:
        return "N{:,}".format(int(n)).replace("N", "₦")
    except Exception:
        return "₦—"

def demand_meta(score):
    if score >= 80:
        return ("🔥", "Very High", "#EF4444", "#EF444418")
    if score >= 60:
        return ("📈", "High", "#F59E0B", "#F59E0B18")
    if score >= 40:
        return ("〰", "Moderate", "#3B82F6", "#3B82F618")
    return ("📉", "Low", "#6B7280", "#6B728018")

def sparkline(prices, w=110, h=34):
    if not prices or len(prices) < 2:
        return ""
    mn = min(prices)
    mx = max(prices)
    rng = mx - mn or 1
    p = 4
    pts = " ".join(
        "{:.1f},{:.1f}".format(
            p + i / (len(prices) - 1) * (w - p * 2),
            p + (mx - v) / rng * (h - p * 2)
        )
        for i, v in enumerate(prices)
    )
    stroke = "#00D68F" if prices[-1] >= prices[0] else "#EF4444"
    last = pts.split()[-1].split(",")
    lx, ly = last[0], last[1]
    fill_pts = pts + " {},{} {},{}".format(w - p, h - p, p, h - p)
    svg = (
        '<svg width="{}" height="{}" style="display:block;overflow:visible">'.format(w, h)
        + '<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
        + '<stop offset="0%" stop-color="{}" stop-opacity="0.18"/>'.format(stroke)
        + '<stop offset="100%" stop-color="{}" stop-opacity="0"/>'.format(stroke)
        + '</linearGradient></defs>'
        + '<polygon points="{}" fill="url(#sg)"/>'.format(fill_pts)
        + '<polyline points="{}" fill="none" stroke="{}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'.format(pts, stroke)
        + '<circle cx="{}" cy="{}" r="3.5" fill="{}" stroke="#08090A" stroke-width="1.5"/>'.format(lx, ly, stroke)
        + '</svg>'
    )
    return svg

def demand_ring(score):
    _, _, color, _ = demand_meta(score)
    r = 20
    circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    return (
        '<svg width="52" height="52" style="transform:rotate(-90deg);flex-shrink:0">'
        + '<circle cx="26" cy="26" r="{}" fill="none" stroke="#1A1D22" stroke-width="3.5"/>'.format(r)
        + '<circle cx="26" cy="26" r="{}" fill="none" stroke="{}" stroke-width="3.5" stroke-dasharray="{:.1f} {:.1f}" stroke-linecap="round"/>'.format(r, color, dash, circ)
        + '<text x="26" y="26" text-anchor="middle" dominant-baseline="central" style="fill:{};font-size:10px;font-weight:800;font-family:monospace;transform:rotate(90deg);transform-origin:26px 26px">{}</text>'.format(color, score)
        + '</svg>'
    )

def card_html(item, idx):
    icon, label, color, bg = demand_meta(item.get("demandScore", 0))
    trend = item.get("priceTrend", 0)
    if trend == 0:
        trend_str = "Stable"
        trend_color = "#6B7280"
    elif trend > 0:
        trend_str = "▲ {}%".format(trend)
        trend_color = "#EF4444"
    else:
        trend_str = "▼ {}%".format(abs(trend))
        trend_color = "#00D68F"

    spark = sparkline(item.get("sparkPrices", []))
    ring = demand_ring(item.get("demandScore", 0))
    insight = item.get("insight", "")

    insight_block = ""
    if insight:
        insight_block = (
            '<div style="background:linear-gradient(135deg,#00D68F0A,#00D68F05);'
            'border:1px solid #00D68F20;border-radius:10px;padding:12px 16px;'
            'font-size:12.5px;color:#00C47E;line-height:1.6;font-weight:500">'
            '<span style="color:#00D68F;font-weight:700;margin-right:6px">💡</span>'
            + insight
            + '</div>'
        )

    return (
        '<div style="background:linear-gradient(145deg,#0F1114,#0D0F12);'
        'border:1px solid #1A1D22;border-radius:16px;padding:22px 24px;'
        'margin-bottom:12px;position:relative;overflow:hidden;'
        'animation:fadeIn 0.4s ease {}s both">'.format(idx * 0.07)
        + '<div style="position:absolute;top:0;left:24px;right:24px;height:1px;'
        'background:linear-gradient(90deg,transparent,{}44,transparent)"></div>'.format(color)
        + '<div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:18px">'
        + ring
        + '<div style="flex:1;min-width:0">'
        + '<div style="font-size:15px;font-weight:700;color:#F3F4F6;line-height:1.3;margin-bottom:8px">'
        + item.get("title", "—")
        + '</div>'
        + '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
        + '<span style="font-size:11px;color:{};background:{};padding:3px 10px;border-radius:20px;font-weight:700">{} {}</span>'.format(color, bg, icon, label)
        + '<span style="font-size:11px;color:#4B5563">{} listings</span>'.format(item.get("listingCount", "—"))
        + '</div></div></div>'
        + '<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-end;margin-bottom:16px">'
        + '<div>'
        + '<div style="font-size:10px;color:#4B5563;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Average price</div>'
        + '<div style="font-size:26px;font-weight:900;color:#00D68F;font-family:DM Mono,monospace;letter-spacing:-0.03em">'
        + ngn(item.get("avgPrice", 0))
        + '</div></div>'
        + '<div>'
        + '<div style="font-size:10px;color:#4B5563;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Price range</div>'
        + '<div style="font-size:13px;color:#9CA3AF;font-family:DM Mono,monospace">'
        + ngn(item.get("minPrice", 0)) + " → " + ngn(item.get("maxPrice", 0))
        + '</div></div>'
        + '<div style="margin-left:auto;text-align:right">'
        + '<div style="font-size:10px;color:#4B5563;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px;font-weight:600">Price trend</div>'
        + '<div style="font-size:15px;font-weight:800;color:{};font-family:DM Mono,monospace">{}</div>'.format(trend_color, trend_str)
        + '<div style="margin-top:6px">' + spark + '</div>'
        + '</div></div>'
        + insight_block
        + '</div>'
    )

def search_jiji(query, category):
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Go to Render dashboard 2192 Environment 2192 add ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    cat_hint = ' in "{}"'.format(category) if category != "All categories" else ""
    prompt = (
        'You are a Nigerian market intelligence analyst. Search Jiji.ng for: "' + query + '"' + cat_hint + '.\n\n'
        'Return ONLY valid JSON:\n'
        '{\n'
        '  "totalListings": <integer>,\n'
        '  "overallDemandScore": <0-100>,\n'
        '  "avgMarketPrice": <naira integer>,\n'
        '  "priceRange": {"min": <integer>, "max": <integer>},\n'
        '  "marketSummary": "<2 sentence overview for Nigerian resellers>",\n'
        '  "competitionLevel": "<Low|Moderate|High|Very High>",\n'
        '  "bestTimeToSell": "<brief timing advice>",\n'
        '  "hotKeywords": ["kw1","kw2","kw3","kw4","kw5"],\n'
        '  "items": [\n'
        '    {\n'
        '      "title": "<variant/model>",\n'
        '      "avgPrice": <naira integer>,\n'
        '      "minPrice": <naira integer>,\n'
        '      "maxPrice": <naira integer>,\n'
        '      "listingCount": <integer>,\n'
        '      "demandScore": <0-100>,\n'
        '      "priceTrend": <integer percent>,\n'
        '      "sparkPrices": [<5 naira integers>],\n'
        '      "insight": "<1 sentence reseller tip>"\n'
        '    }\n'
        '  ]\n'
        '}\n\n'
        'Include 4-7 items. All prices in Nigerian Naira. Use real Jiji.ng data.'
    )
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

CATEGORIES = [
    "All categories", "Phones & Tablets", "Electronics",
    "Laptops & Computers", "Vehicles", "Fashion",
    "Home & Garden", "Health & Beauty", "Sports & Outdoors", "Real Estate",
]

if "history" not in st.session_state:
    st.session_state["history"] = []
if "results" not in st.session_state:
    st.session_state["results"] = None

with st.sidebar:
    st.markdown(
        '<div style="padding:24px 20px 16px">'
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">'
        '<div style="width:36px;height:36px;border-radius:10px;'
        'background:linear-gradient(135deg,#00D68F,#00956A);'
        'display:flex;align-items:center;justify-content:center;font-size:18px">📊</div>'
        '<div>'
        '<div style="font-size:16px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em">JijiTrack</div>'
        '<div style="font-size:10px;color:#3D4248;font-weight:500;letter-spacing:0.05em;text-transform:uppercase">Nigeria Market Intel</div>'
        '</div></div></div>'
        '<div style="height:1px;background:linear-gradient(90deg,transparent,#1A1D22,transparent);margin:0 20px 20px"></div>'
        '<div style="padding:0 20px 16px">'
        '<div style="background:#00D68F0D;border:1px solid #00D68F20;border-radius:10px;'
        'padding:10px 14px;display:flex;align-items:center;gap:10px">'
        '<div style="width:7px;height:7px;border-radius:50%;background:#00D68F;'
        'box-shadow:0 0 6px #00D68F;flex-shrink:0"></div>'
        '<div>'
        '<div style="font-size:11px;font-weight:700;color:#00D68F">Live data</div>'
        '<div style="font-size:10px;color:#3D4248">Powered by Jiji.ng</div>'
        '</div></div></div>'
        '<div style="padding:0 20px">'
        '<div style="font-size:10px;color:#3D4248;text-transform:uppercase;'
        'letter-spacing:0.1em;font-weight:600;margin-bottom:10px">Quick searches</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    for emoji, label in QUICK:
        if st.button("{} {}".format(emoji, label), key="qs_{}".format(label)):
            st.session_state["queued_query"] = label
            st.rerun()

    if st.session_state.get("history"):
        st.markdown(
            '<div style="height:1px;background:#1A1D22;margin:12px 20px"></div>'
            '<div style="padding:0 20px">'
            '<div style="font-size:10px;color:#3D4248;text-transform:uppercase;'
            'letter-spacing:0.1em;font-weight:600;margin-bottom:10px">Recent searches</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        for h in reversed(st.session_state["history"][-5:]):
            if st.button("🕐 {}".format(h), key="hist_{}".format(h)):
                st.session_state["queued_query"] = h
                st.rerun()

    st.markdown(
        '<div style="padding:20px 20px 12px;margin-top:20px;border-top:1px solid #1A1D22">'
        '<div style="font-size:10px;color:#2A2D32;line-height:1.7">'
        'Data from Jiji.ng public listings<br>'
        'For research purposes only<br>'
        '🇳🇬 Built for Nigeria'
        '</div></div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
default_query = st.session_state.pop("queued_query", "")

# nav bar
st.markdown(
    '<div style="background:#08090AEE;backdrop-filter:blur(16px);'
    'border-bottom:1px solid #1A1D22;padding:14px 32px;'
    'display:flex;align-items:center;gap:12px">'
    '<div style="font-size:15px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em">Market Intelligence</div>'
    '<div style="margin-left:auto;display:flex;gap:10px;align-items:center">'
    '<span style="font-size:11px;color:#00D68F;background:#00D68F15;'
    'padding:4px 12px;border-radius:20px;font-weight:700">● LIVE</span>'
    '<span style="font-size:11px;color:#2A2D32;background:#0D0F12;'
    'border:1px solid #1A1D22;padding:4px 12px;border-radius:8px">jiji.ng</span>'
    '</div></div>',
    unsafe_allow_html=True,
)

# hero
if not st.session_state["results"]:
    st.markdown(
        '<div style="padding:56px 40px 40px;text-align:center;max-width:680px;margin:0 auto">'
        '<div style="display:inline-block;font-size:10px;color:#00D68F;font-weight:700;'
        'letter-spacing:0.2em;text-transform:uppercase;background:#00D68F0D;'
        'border:1px solid #00D68F20;padding:5px 16px;border-radius:20px;margin-bottom:24px">'
        'Real-time · Jiji.ng · Nigeria'
        '</div>'
        '<h1 style="font-size:48px;font-weight:900;letter-spacing:-0.04em;'
        'line-height:1.05;margin-bottom:18px;color:#FFFFFF">'
        'Know what sells.<br>'
        '<span style="color:#00D68F">Before your competitors.</span>'
        '</h1>'
        '<p style="font-size:16px;color:#6B7280;max-width:440px;margin:0 auto 48px;line-height:1.75">'
        'Live price ranges, demand scores, and reseller insights pulled directly from Jiji.ng.'
        '</p>'
        '</div>'
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;'
        'max-width:680px;margin:0 auto 48px;padding:0 40px">'
        '<div style="background:#0D0F12;border:1px solid #1A1D22;border-radius:14px;padding:22px 18px">'
        '<div style="font-size:28px;margin-bottom:10px">📉</div>'
        '<div style="font-size:13px;font-weight:700;color:#E8EAED;margin-bottom:6px">Price ranges</div>'
        '<div style="font-size:12px;color:#4B5563;line-height:1.6">Min, max and avg across all listings</div>'
        '</div>'
        '<div style="background:#0D0F12;border:1px solid #1A1D22;border-radius:14px;padding:22px 18px">'
        '<div style="font-size:28px;margin-bottom:10px">🔥</div>'
        '<div style="font-size:13px;font-weight:700;color:#E8EAED;margin-bottom:6px">Demand scores</div>'
        '<div style="font-size:12px;color:#4B5563;line-height:1.6">AI-powered 0-100 demand rating</div>'
        '</div>'
        '<div style="background:#0D0F12;border:1px solid #1A1D22;border-radius:14px;padding:22px 18px">'
        '<div style="font-size:28px;margin-bottom:10px">💡</div>'
        '<div style="font-size:13px;font-weight:700;color:#E8EAED;margin-bottom:6px">Reseller tips</div>'
        '<div style="font-size:12px;color:#4B5563;line-height:1.6">Insights to maximise your margin</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# search bar
st.markdown('<div style="max-width:820px;margin:0 auto;padding:0 32px 32px">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([5, 2.2, 1.5])
with c1:
    query = st.text_input(
        "q", label_visibility="collapsed",
        placeholder="Search any product on Jiji.ng…",
        value=default_query,
        key="main_query",
    )
with c2:
    category = st.selectbox("cat", CATEGORIES, label_visibility="collapsed", key="main_cat")
with c3:
    go = st.button("Analyse →", key="go_btn")

st.markdown('</div>', unsafe_allow_html=True)

# trigger
run_query = query.strip()
if (go or default_query) and run_query:
    with st.spinner("Scanning Jiji.ng for {}...".format(run_query)):
        try:
            data = search_jiji(run_query, category)
            st.session_state["results"] = data
            st.session_state["results_label"] = run_query
            st.session_state["results_time"] = datetime.now().strftime("%I:%M %p")
            if run_query not in st.session_state["history"]:
                st.session_state["history"].append(run_query)
        except Exception as e:
            st.error("Error: {}".format(e))
            st.session_state["results"] = None

# ══════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════
if st.session_state.get("results"):
    data = st.session_state["results"]
    label = st.session_state.get("results_label", "")
    time_ = st.session_state.get("results_time", "")
    items = data.get("items", [])

    st.markdown('<div style="max-width:820px;margin:0 auto;padding:0 32px 60px">', unsafe_allow_html=True)

    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:20px;flex-wrap:wrap;gap:8px">'
        '<div>'
        '<div style="font-size:10px;color:#3D4248;text-transform:uppercase;'
        'letter-spacing:0.12em;font-weight:600;margin-bottom:4px">Market overview</div>'
        '<div style="font-size:20px;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em">'
        + '"' + label + '"'
        + '</div></div>'
        '<div style="font-size:11px;color:#3D4248;background:#0D0F12;'
        'border:1px solid #1A1D22;padding:5px 12px;border-radius:8px">'
        'Updated ' + time_
        + '</div></div>',
        unsafe_allow_html=True,
    )

    # metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Avg Market Price", ngn(data.get("avgMarketPrice", 0)))
    with m2:
        st.metric("Listings Found", "{:,}".format(data.get("totalListings", 0)))
    with m3:
        st.metric("Demand Score", "{}/100".format(data.get("overallDemandScore", 0)))
    with m4:
        st.metric("Competition", data.get("competitionLevel", "—"))

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # demand bar
    demand = data.get("overallDemandScore", 0)
    st.markdown(
        '<div style="background:#0D0F12;border:1px solid #1A1D22;border-radius:14px;'
        'padding:16px 20px;margin-bottom:14px">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
        '<div style="font-size:12px;font-weight:600;color:#9CA3AF">Overall Market Demand</div>'
        '<div style="font-size:14px;font-weight:800;color:#00D68F;font-family:monospace">'
        + str(demand) + '/100'
        + '</div></div>'
        '<div style="height:6px;background:#1A1D22;border-radius:4px;overflow:hidden">'
        '<div style="height:100%;width:' + str(demand) + '%;'
        'background:linear-gradient(90deg,#00D68F,#00FFAA);border-radius:4px"></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # summary
    summary = data.get("marketSummary", "")
    if summary:
        st.markdown(
            '<div style="background:linear-gradient(135deg,#0A1520,#08111E);'
            'border:1px solid #1E3A5F;border-radius:14px;padding:18px 22px;margin-bottom:14px">'
            '<div style="font-size:10px;color:#3B82F6;text-transform:uppercase;'
            'letter-spacing:0.1em;font-weight:700;margin-bottom:8px">📋 Market Summary</div>'
            '<div style="font-size:13.5px;color:#93C5FD;line-height:1.75">' + summary + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # timing + keywords
    t1, t2 = st.columns([1, 1])
    with t1:
        bts = data.get("bestTimeToSell", "")
        if bts:
            st.markdown(
                '<div style="background:#0A140A;border:1px solid #1A3A1A;'
                'border-radius:12px;padding:14px 18px">'
                '<div style="font-size:10px;color:#22C55E;text-transform:uppercase;'
                'letter-spacing:0.1em;font-weight:700;margin-bottom:8px">⏰ Best time to sell</div>'
                '<div style="font-size:13px;color:#86EFAC;line-height:1.6">' + bts + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    with t2:
        kws = data.get("hotKeywords", [])
        if kws:
            kw_html = "".join(
                '<span style="background:#00D68F15;color:#00C47E;padding:5px 12px;'
                'border-radius:20px;font-size:11px;font-weight:600;'
                'border:1px solid #00D68F25;display:inline-block;margin:3px">' + k + '</span>'
                for k in kws
            )
            st.markdown(
                '<div style="background:#0D0F12;border:1px solid #1A1D22;'
                'border-radius:12px;padding:14px 18px">'
                '<div style="font-size:10px;color:#4B5563;text-transform:uppercase;'
                'letter-spacing:0.1em;font-weight:700;margin-bottom:10px">🔍 Trending keywords</div>'
                '<div>' + kw_html + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;color:#3D4248;text-transform:uppercase;'
        'letter-spacing:0.12em;font-weight:700;margin-bottom:12px">'
        + str(len(items)) + ' variants tracked — sorted by demand'
        + '</div>',
        unsafe_allow_html=True,
    )

    sorted_items = sorted(items, key=lambda x: x.get("demandScore", 0), reverse=True)
    for i, item in enumerate(sorted_items):
        st.markdown(card_html(item, i), unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:28px;padding:16px;text-align:center;border-top:1px solid #1A1D22">'
        '<span style="font-size:11px;color:#2A2D32">'
        'Data sourced from Jiji.ng public listings · For research purposes only · 🇳🇬 JijiTrack'
        '</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)
