# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║        WildHeart Nonprofit — Donor & Volunteer Management Hub               ║
# ║        Built with Claude for Claude Corps Fellowship                         ║
# ║        Full single-file Streamlit app  •  app.py                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io, json, random, math, requests
from datetime import datetime, timedelta
from fpdf import FPDF

# ──────────────────────────────────────────────────────────────────────────────
# 1.  PAGE CONFIG  (must come first)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WildHeart Nonprofit Hub",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# 2.  GLOBAL CSS  —  green / teal nonprofit palette
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:wght@700&display=swap');

/* ─── tokens ─── */
:root{
  --g900:#064E3B; --g700:#047857; --g500:#10B981; --g300:#6EE7B7; --g100:#D1FAE5;
  --b700:#1D4ED8; --b500:#3B82F6; --b100:#DBEAFE;
  --sand:#F9FAFB; --white:#FFFFFF;
  --ink:#111827; --muted:#6B7280; --border:#E5E7EB;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.05);
}

/* ─── base ─── */
html,body,.stApp{background:var(--sand)!important;font-family:'Inter',sans-serif;color:var(--ink);}

/* ─── sidebar ─── */
section[data-testid="stSidebar"]{background:var(--g900)!important;}
section[data-testid="stSidebar"] *{color:#ECFDF5!important;}
section[data-testid="stSidebar"] hr{border-color:#065F46!important;}
section[data-testid="stSidebar"] .stRadio > div{gap:.35rem;}
section[data-testid="stSidebar"] .stRadio label{
  padding:.55rem .9rem; border-radius:8px; font-size:.92rem; font-weight:500;
  transition:background .15s;
}
section[data-testid="stSidebar"] .stRadio label:hover{background:rgba(255,255,255,.12)!important;}

/* ─── metric card ─── */
.card{
  background:var(--white); border-radius:14px; padding:1.3rem 1.5rem;
  box-shadow:var(--shadow); border-top:4px solid var(--g500);
}
.card.blue{border-top-color:var(--b500);}
.card.teal{border-top-color:#0D9488;}
.card.amber{border-top-color:#F59E0B;}
.card-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:.4rem;}
.card-value{font-size:2rem;font-weight:700;color:var(--ink);line-height:1.1;}
.card-sub{font-size:.78rem;color:var(--g700);margin-top:.35rem;font-weight:500;}

/* ─── page heading ─── */
.ph-wrap{margin-bottom:1.6rem;}
.ph-title{font-family:'Merriweather',serif;font-size:1.75rem;color:var(--g900);margin:0;}
.ph-sub{font-size:.9rem;color:var(--muted);margin:.3rem 0 0;}

/* ─── section label ─── */
.sec-label{font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;
  color:var(--g700);margin:1.6rem 0 .7rem;}

/* ─── ai / email output ─── */
.ai-card{
  background:var(--white);border-radius:12px;padding:1.5rem 1.7rem;
  border:1px solid var(--border);white-space:pre-wrap;
  font-size:.9rem;line-height:1.8;color:var(--ink);
  box-shadow:var(--shadow);
}

/* ─── email preview ─── */
.email-card{
  background:#F0FDF4;border-radius:12px;padding:1.4rem 1.6rem;
  border:1px solid var(--g300);font-size:.88rem;line-height:1.75;
  color:var(--ink);white-space:pre-wrap;
}

/* ─── rule ─── */
.rule{border:none;border-top:1px solid var(--border);margin:1.5rem 0;}

/* ─── primary button ─── */
.stButton>button{
  background:var(--g700)!important;color:#fff!important;
  border:none!important;border-radius:9px!important;
  font-weight:600!important;font-size:.88rem!important;
  padding:.5rem 1.4rem!important;transition:background .15s!important;
}
.stButton>button:hover{background:var(--g900)!important;}

/* ─── download button ─── */
.stDownloadButton>button{
  background:var(--b700)!important;color:#fff!important;
  border:none!important;border-radius:9px!important;
  font-weight:600!important;font-size:.88rem!important;
}

/* ─── footer ─── */
.footer{
  text-align:center;padding:1.5rem 0 .8rem;
  color:var(--muted);font-size:.78rem;border-top:1px solid var(--border);
  margin-top:3rem;
}
.footer b{color:var(--g700);}

/* ─── badge ─── */
.badge{
  display:inline-block;padding:.18rem .65rem;border-radius:999px;
  font-size:.72rem;font-weight:600;
}
.badge-green{background:var(--g100);color:var(--g700);}
.badge-blue{background:var(--b100);color:var(--b700);}

/* ─── search box ─── */
.stTextInput>div>div>input{border-radius:9px!important;}

/* ─── dataframe ─── */
.stDataFrame{border-radius:10px;overflow:hidden;}

/* ─── expander ─── */
.streamlit-expanderHeader{font-weight:600!important;font-size:.9rem!important;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 3.  SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULTS = dict(
    df            = None,   # main dataframe
    insights_md   = "",     # cached AI insights text
    emails        = [],     # list of generated email dicts
    pdf_bytes     = None,   # cached PDF bytes
)
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ──────────────────────────────────────────────────────────────────────────────
# 4.  SAMPLE DATA GENERATOR  (used when no file is uploaded)
# ──────────────────────────────────────────────────────────────────────────────
def make_sample_data(n: int = 200) -> pd.DataFrame:
    """Generate realistic-looking nonprofit donor/volunteer records."""
    rng = random.Random(42)
    names_f = ["Amara Osei","Sofia Reyes","Priya Nair","Yuki Tanaka","Elena Vasquez",
               "Fatima Al-Rashid","Grace Liu","Hannah Müller","Ingrid Svensson","Jia Chen"]
    names_m = ["David Okafor","Marco Ferretti","Arjun Patel","Kenji Yamamoto","Carlos Mendez",
               "Omar Hassan","Wei Zhang","Tobias Becker","Lars Andersen","Raj Krishnan"]
    campaigns  = ["Rescue Orphaned Gorillas","Marine Mammal Defense Mission",
                  "Wildlife Rescue Van Drive","Habitat for Hope",
                  "Defend the Great Apes","Jungle Education Project","Reforest the Sanctuary"]
    countries  = ["USA"]*35+["UK"]*18+["France"]*12+["Germany"]*10+["Canada"]*9+["Australia"]*8+["India"]*5+["Brazil"]*3
    sectors    = ["Healthcare","Technology","Finance/Banking","Education","Retail",
                  "Government","Nonprofit","Science & Research","Law","Agriculture"]
    channels   = ["Website","Online advertising","Newsletter","Word of mouth","Social Media","Local event"]
    methods    = ["Credit Card","Bank Transfer","PayPal","Cheque"]
    types      = ["Donor"]*70 + ["Volunteer"]*30

    rows = []
    start = datetime(2023, 6, 1)
    end   = datetime(2025, 6, 17)
    span  = (end - start).days

    for i in range(n):
        gender  = rng.choice(["Female","Male","Other"])
        pool    = names_f if gender == "Female" else names_m
        name    = rng.choice(pool)
        role    = rng.choice(types)
        amount  = round(rng.uniform(5, 500), 2) if role == "Donor" else 0.0
        date    = start + timedelta(days=rng.randint(0, span))
        rows.append({
            "donor_id":         f"SMP-{i+1:04d}",
            "name":             name,
            "email":            f"{name.lower().replace(' ','.')}{rng.randint(1,999)}@example.org",
            "gender":           gender,
            "age_group":        rng.choice(["18-29","30-49","50-65","66-80"]),
            "country":          rng.choice(countries),
            "sector":           rng.choice(sectors),
            "campaign":         rng.choice(campaigns),
            "donation_type":    "Monthly" if rng.random() < .35 else "One-time",
            "donation_amount":  amount,
            "donation_date":    date.strftime("%Y-%m-%d"),
            "payment_method":   rng.choice(methods),
            "newsletter_opt_in":rng.choice([True, False]),
            "referral_channel": rng.choice(channels),
            "type":             role,
            "volunteer_hours":  rng.randint(2, 80) if role == "Volunteer" else 0,
            "notes":            "",
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────────
# 5.  DATA LOADING & NORMALISATION
# ──────────────────────────────────────────────────────────────────────────────
COL_MAP = {
    # source column         canonical name
    "donor_id":             "donor_id",
    "name":                 "name",
    "email":                "email",
    "gender":               "gender",
    "age_group":            "age_group",
    "country":              "country",
    "sector":               "sector",
    "campaign":             "campaign",
    "donation_type":        "donation_type",
    "donation_amount":      "donation_amount",
    "donation_date":        "donation_date",
    "payment_method":       "payment_method",
    "newsletter_opt_in":    "newsletter_opt_in",
    "referral_channel":     "referral_channel",
    # allow pre-renamed columns through too
    "amount":               "donation_amount",
    "date":                 "donation_date",
    "type":                 "type",
}

def normalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k: v for k, v in COL_MAP.items() if k in df.columns})
    if "donation_date" in df.columns:
        df["donation_date"] = pd.to_datetime(df["donation_date"], errors="coerce")
    if "donation_amount" in df.columns:
        df["donation_amount"] = pd.to_numeric(df["donation_amount"], errors="coerce").fillna(0)
    if "type" not in df.columns:
        df["type"] = "Donor"
    if "volunteer_hours" not in df.columns:
        df["volunteer_hours"] = 0
    if "donation_date" in df.columns and df["donation_date"].notna().any():
        df["month_str"] = df["donation_date"].dt.to_period("M").astype(str)
    return df

def load_file(file) -> pd.DataFrame:
    n = file.name.lower()
    df = pd.read_excel(file) if n.endswith((".xlsx",".xls")) else pd.read_csv(file)
    return normalise(df)

def get_df() -> pd.DataFrame:
    if st.session_state.df is None:
        st.session_state.df = normalise(make_sample_data())
    return st.session_state.df


# ──────────────────────────────────────────────────────────────────────────────
# 6.  ANTHROPIC API
# ──────────────────────────────────────────────────────────────────────────────
def claude(system: str, user: str, max_tokens: int = 900) -> str:
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model":      "claude-sonnet-4-6",
                "max_tokens": max_tokens,
                "system":     system,
                "messages":   [{"role":"user","content":user}],
            },
            timeout=60,
        )
        data = r.json()
        if "content" in data:
            return "".join(b.get("text","") for b in data["content"] if b.get("type")=="text")
        return data.get("error",{}).get("message","No response.")
    except Exception as e:
        return f"⚠️ API error: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# 7.  PDF EXPORT — Fixed Version (No Special Characters)
# ──────────────────────────────────────────────────────────────────────────────
def build_pdf(df: pd.DataFrame, title: str = "Donor Report") -> bytes:
    """Safe PDF generator without special characters"""
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # Clean title
    clean_title = str(title).replace("—", "-").replace("’", "'").replace("“", '"').replace("”", '"')

    # Title
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(6, 78, 59)
    pdf.cell(0, 12, clean_title[:90], ln=True, align="C")
    
    # Subtitle - NO bullet character
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated on {datetime.today().strftime('%B %d, %Y')} - {len(df):,} records", 
             ln=True, align="C")
    pdf.ln(10)

    # Columns
    cols = [c for c in ["name","email","type","campaign","donation_amount",
                       "donation_date","country"] if c in df.columns]
    
    if not cols:
        cols = list(df.columns[:7])

    col_width = max(24, int(270 / len(cols)))

    # Header
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(6, 78, 59)
    pdf.set_text_color(255, 255, 255)
    for c in cols:
        header = str(c).replace("_", " ").title()[:22]
        pdf.cell(col_width, 9, header, border=0, fill=True, align="C")
    pdf.ln()

    # Rows
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(0, 0, 0)
    for i, (_, row) in enumerate(df.head(300).iterrows()):
        fill = i % 2 == 0
        pdf.set_fill_color(230, 255, 240) if fill else pdf.set_fill_color(255, 255, 255)
        
        for c in cols:
            val = "" if pd.isna(row.get(c)) else str(row[c])
            val = val.replace("—", "-").replace("\n", " ")[:32]
            pdf.cell(col_width, 7, val, border=0, fill=True, align="C")
        pdf.ln()

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Built with Claude for Claude Corps Fellowship", align="C")

    return bytes(pdf.output())


# ──────────────────────────────────────────────────────────────────────────────
# 8.  CHART THEME
# ──────────────────────────────────────────────────────────────────────────────
GREEN_SEQ  = ["#064E3B","#065F46","#047857","#059669","#10B981","#34D399","#6EE7B7","#A7F3D0"]
MIXED_PAL  = ["#10B981","#3B82F6","#F59E0B","#8B5CF6","#EF4444","#06B6D4","#EC4899","#14B8A6"]
LAYOUT_BASE = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Inter", color="#374151"),
    title_font=dict(family="Merriweather", color="#064E3B", size=14),
    margin=dict(t=46, b=24, l=18, r=18),
    legend=dict(font=dict(size=11)),
)

def _fig(fig):
    fig.update_layout(**LAYOUT_BASE)
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB")
    fig.update_yaxes(gridcolor="#F3F4F6", linecolor="#E5E7EB")
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# 9.  SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.1rem 0 1.4rem'>
      <div style='font-size:2.6rem'>🐾</div>
      <div style='font-family:Merriweather,serif;font-size:1.25rem;font-weight:700;
                  margin-top:.3rem;letter-spacing:-.01em'>WildHeart</div>
      <div style='font-size:.68rem;opacity:.65;letter-spacing:.1em;
                  margin-top:.15rem'>NONPROFIT DONOR HUB</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Dashboard",
        "🔍  Data Explorer",
        "💡  AI Insights",
        "✉️  Email Generator",
        "📊  Reports",
    ], label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:.78rem;font-weight:600;letter-spacing:.05em;opacity:.6;margin-bottom:.5rem'>UPLOAD DATA</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV or Excel file", type=["csv","xlsx","xls"], label_visibility="collapsed")
    if uploaded:
        with st.spinner("Loading…"):
            st.session_state.df          = load_file(uploaded)
            st.session_state.insights_md = ""
            st.session_state.emails      = []
            st.session_state.pdf_bytes   = None
        st.success(f"✅ {len(st.session_state.df):,} rows loaded")

    st.markdown("<hr>", unsafe_allow_html=True)

    df_meta = get_df()
    st.markdown(f"""
    <div style='font-size:.78rem;opacity:.75;line-height:1.9'>
      📋 <b>{len(df_meta):,}</b> records<br>
      👥 <b>{df_meta['type'].value_counts().get('Donor', df_meta['type'].value_counts().get('Donor',len(df_meta))):,}</b> donors<br>
      🤝 <b>{df_meta['type'].value_counts().get('Volunteer',0):,}</b> volunteers<br>
      📅 <b>{datetime.today().strftime('%b %d, %Y')}</b>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 10.  HELPER: page header
# ──────────────────────────────────────────────────────────────────────────────
def page_header(title: str, sub: str):
    st.markdown(f"""
    <div class="ph-wrap">
      <h1 class="ph-title">{title}</h1>
      <p class="ph-sub">{sub}</p>
    </div>""", unsafe_allow_html=True)


def section(label: str):
    st.markdown(f'<p class="sec-label">{label}</p>', unsafe_allow_html=True)


def rule():
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in page:
    df = get_df()
    page_header("🏠 Dashboard", "Real-time snapshot of your donors, volunteers, and campaigns.")

    # ── date range filter
    if "donation_date" in df.columns and df["donation_date"].notna().any():
        lo = df["donation_date"].min().date()
        hi = df["donation_date"].max().date()
        fa, fb = st.columns(2)
        with fa: d_from = st.date_input("From", lo, key="d_from")
        with fb: d_to   = st.date_input("To",   hi, key="d_to")
        dff = df[(df["donation_date"].dt.date >= d_from) & (df["donation_date"].dt.date <= d_to)].copy()
    else:
        dff = df.copy()

    donors     = dff[dff["type"]=="Donor"]
    volunteers = dff[dff["type"]=="Volunteer"]
    total_amt  = donors["donation_amount"].sum()
    avg_gift   = donors["donation_amount"].mean() if len(donors) else 0
    monthly_ct = len(donors[donors.get("donation_type","")=="Monthly"]) if "donation_type" in donors.columns else 0
    opt_pct    = (dff["newsletter_opt_in"].sum()/len(dff)*100) if "newsletter_opt_in" in dff.columns and len(dff) else 0

    # ── KPI cards
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f"""<div class="card">
      <div class="card-label">Total Donors</div>
      <div class="card-value">{len(donors):,}</div>
      <div class="card-sub">↑ Unique individuals</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="card amber">
      <div class="card-label">Total Raised</div>
      <div class="card-value">${total_amt:,.0f}</div>
      <div class="card-sub">Avg gift ${avg_gift:,.2f}</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="card blue">
      <div class="card-label">Total Volunteers</div>
      <div class="card-value">{len(volunteers):,}</div>
      <div class="card-sub">{volunteers['volunteer_hours'].sum():,} hrs logged</div></div>""", unsafe_allow_html=True)
    with c4: st.markdown(f"""<div class="card teal">
      <div class="card-label">Monthly Supporters</div>
      <div class="card-value">{monthly_ct:,}</div>
      <div class="card-sub">Newsletter opt-in {opt_pct:.1f}%</div></div>""", unsafe_allow_html=True)

    rule()

    # ── Row 1 charts
    r1a, r1b = st.columns(2)

    with r1a:
        if "month_str" in dff.columns and "donation_amount" in dff.columns:
            ts = donors.groupby("month_str")["donation_amount"].sum().reset_index()
            ts.columns = ["Month","Raised ($)"]
            ts = ts.sort_values("Month")
            fig = _fig(px.area(ts, x="Month", y="Raised ($)", title="Monthly Donations",
                               color_discrete_sequence=["#10B981"]))
            fig.update_traces(fill="tozeroy", fillcolor="rgba(16,185,129,.15)", line_width=2.5)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    with r1b:
        if "campaign" in dff.columns and "donation_amount" in dff.columns:
            camp = donors.groupby("campaign")["donation_amount"].sum().sort_values().reset_index()
            fig = _fig(px.bar(camp, x="donation_amount", y="campaign", orientation="h",
                              title="Raised per Campaign",
                              color="donation_amount",
                              color_continuous_scale=["#6EE7B7","#064E3B"],
                              labels={"donation_amount":"Amount ($)","campaign":""}))
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2 charts
    r2a, r2b, r2c = st.columns(3)

    with r2a:
        if "referral_channel" in dff.columns:
            ref = dff["referral_channel"].value_counts().reset_index()
            ref.columns = ["Channel","Count"]
            fig = _fig(px.pie(ref, values="Count", names="Channel",
                              title="Referral Channels", hole=.52,
                              color_discrete_sequence=GREEN_SEQ))
            st.plotly_chart(fig, use_container_width=True)

    with r2b:
        if "age_group" in dff.columns and "donation_amount" in dff.columns:
            age = donors.groupby("age_group")["donation_amount"].sum().reset_index()
            fig = _fig(px.bar(age, x="age_group", y="donation_amount",
                              title="Donations by Age Group",
                              color="age_group", color_discrete_sequence=MIXED_PAL,
                              labels={"age_group":"Age Group","donation_amount":"Amount ($)"}))
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with r2c:
        if "payment_method" in dff.columns:
            pm = dff["payment_method"].value_counts().reset_index()
            pm.columns = ["Method","Count"]
            fig = _fig(px.pie(pm, values="Count", names="Method",
                              title="Payment Methods", hole=.52,
                              color_discrete_sequence=MIXED_PAL))
            st.plotly_chart(fig, use_container_width=True)

    # ── Top 10 donors table
    rule()
    section("🏆 Top 10 Donors by Total Giving")
    if "donation_amount" in donors.columns and "name" in donors.columns:
        top10 = (donors.groupby(["name","email","campaign","country"])["donation_amount"]
                 .sum().reset_index()
                 .sort_values("donation_amount", ascending=False)
                 .head(10)
                 .rename(columns={"donation_amount":"Total ($)","name":"Name",
                                  "email":"Email","campaign":"Campaign","country":"Country"}))
        top10["Total ($)"] = top10["Total ($)"].map("${:,.2f}".format)
        st.dataframe(top10.reset_index(drop=True), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif "Explorer" in page:
    df = get_df()
    page_header("🔍 Data Explorer", "Search, filter, and inspect every record in your dataset.")

    # ── filter bar
    ex1, ex2, ex3, ex4 = st.columns(4)
    with ex1:
        search = st.text_input("🔍 Search name / email", "")
    with ex2:
        type_opts = ["All"] + sorted(df["type"].dropna().unique().tolist())
        ftype = st.selectbox("Type", type_opts)
    with ex3:
        camp_opts = ["All"] + (sorted(df["campaign"].dropna().unique().tolist()) if "campaign" in df.columns else [])
        fcamp = st.selectbox("Campaign", camp_opts)
    with ex4:
        ctry_opts = ["All"] + (sorted(df["country"].dropna().unique().tolist()) if "country" in df.columns else [])
        fctry = st.selectbox("Country", ctry_opts)

    ex5, ex6, _ = st.columns([1,1,2])
    with ex5:
        if "donation_date" in df.columns and df["donation_date"].notna().any():
            d_lo = st.date_input("From", df["donation_date"].min().date(), key="ex_lo")
    with ex6:
        if "donation_date" in df.columns and df["donation_date"].notna().any():
            d_hi = st.date_input("To",   df["donation_date"].max().date(), key="ex_hi")

    # apply filters
    fdf = df.copy()
    if search:
        fdf = fdf[
            fdf.get("name",pd.Series(dtype=str)).astype(str).str.contains(search,case=False,na=False) |
            fdf.get("email",pd.Series(dtype=str)).astype(str).str.contains(search,case=False,na=False)
        ]
    if ftype != "All":     fdf = fdf[fdf["type"]==ftype]
    if fcamp != "All" and "campaign" in fdf.columns: fdf = fdf[fdf["campaign"]==fcamp]
    if fctry != "All" and "country"  in fdf.columns: fdf = fdf[fdf["country"] ==fctry]
    if "donation_date" in fdf.columns and fdf["donation_date"].notna().any():
        fdf = fdf[(fdf["donation_date"].dt.date >= d_lo) & (fdf["donation_date"].dt.date <= d_hi)]

    st.caption(f"**{len(fdf):,}** records match your filters  ·  {len(df):,} total")

    # ── summary chips
    if len(fdf):
        sc1,sc2,sc3,sc4 = st.columns(4)
        with sc1: st.metric("Records", f"{len(fdf):,}")
        with sc2:
            amt = fdf["donation_amount"].sum() if "donation_amount" in fdf.columns else 0
            st.metric("Total Raised", f"${amt:,.0f}")
        with sc3:
            avg = fdf["donation_amount"].mean() if "donation_amount" in fdf.columns and len(fdf) else 0
            st.metric("Avg Gift", f"${avg:,.2f}")
        with sc4:
            uniq = fdf["donor_id"].nunique() if "donor_id" in fdf.columns else len(fdf)
            st.metric("Unique IDs", f"{uniq:,}")

    rule()
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=460)

    # quick pivot
    rule()
    section("📐 Quick Pivot")
    pv1, pv2 = st.columns(2)
    with pv1:
        grp_col = st.selectbox("Group by", [c for c in ["campaign","country","age_group","gender","referral_channel","payment_method","sector"] if c in fdf.columns])
    with pv2:
        agg_col = st.selectbox("Aggregate", [c for c in ["donation_amount","newsletter_opt_in","volunteer_hours"] if c in fdf.columns])

    if grp_col and agg_col:
        pivot = fdf.groupby(grp_col)[agg_col].agg(["sum","mean","count"]).round(2).reset_index()
        pivot.columns = [grp_col,"Sum","Mean","Count"]
        st.dataframe(pivot.sort_values("Sum",ascending=False), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif "Insights" in page:
    df = get_df()
    page_header("💡 AI Insights", "Claude analyses your data...")
    
    st.info("💡 AI responses are mock demonstrations for portfolio purposes. Real integration with Claude is shown in the code.", icon="ℹ️")
    
    # build a rich summary string to feed to the model
    def data_summary(df: pd.DataFrame) -> str:
        donors = df[df["type"]=="Donor"] if "type" in df.columns else df
        vols   = df[df["type"]=="Volunteer"] if "type" in df.columns else pd.DataFrame()
        lines  = [f"Total records: {len(df):,}"]
        lines += [f"Donors: {len(donors):,}",
                  f"Volunteers: {len(vols):,}"]
        if "donation_amount" in donors.columns:
            lines += [f"Total raised: ${donors['donation_amount'].sum():,.2f}",
                      f"Avg gift: ${donors['donation_amount'].mean():.2f}",
                      f"Median gift: ${donors['donation_amount'].median():.2f}",
                      f"Max single gift: ${donors['donation_amount'].max():.2f}"]
        if "campaign" in df.columns and "donation_amount" in df.columns:
            top_camps = donors.groupby("campaign")["donation_amount"].sum().sort_values(ascending=False).head(3)
            lines.append(f"Top campaigns: {top_camps.to_dict()}")
        if "referral_channel" in df.columns:
            lines.append(f"Referral channels: {df['referral_channel'].value_counts().to_dict()}")
        if "age_group" in df.columns:
            lines.append(f"Age groups: {df['age_group'].value_counts().to_dict()}")
        if "country" in df.columns:
            lines.append(f"Top countries: {df['country'].value_counts().head(5).to_dict()}")
        if "donation_type" in df.columns:
            lines.append(f"Recurring vs one-time: {df['donation_type'].value_counts().to_dict()}")
        if "newsletter_opt_in" in df.columns:
            lines.append(f"Newsletter opt-in: {df['newsletter_opt_in'].mean()*100:.1f}%")
        if "donation_date" in df.columns and df["donation_date"].notna().any():
            lines.append(f"Date range: {df['donation_date'].min().date()} → {df['donation_date'].max().date()}")
        return "\n".join(lines)

    # show summary collapsible
    with st.expander("📄 Data summary sent to Claude", expanded=False):
        st.code(data_summary(df), language=None)

    # focus selector
    focus = st.selectbox("Analysis focus", [
        "Full overview — trends, risks, and opportunities",
        "Donor retention & recurring giving",
        "Top campaigns & underperformers",
        "Referral & acquisition channels",
        "Demographics & geographic patterns",
        "Volunteer engagement strategy",
    ])

    if st.button("✨ Generate AI Insights", use_container_width=False):
        with st.spinner("Claude is analysing your data…"):
            system = (
                "You are a senior nonprofit fundraising strategist and data analyst "
                "specialising in wildlife and animal welfare organisations. "
                "Your writing is concise, warm, and action-oriented. "
                "Always cite the actual numbers from the data summary provided. "
                "Structure every response with exactly these four sections using markdown headers:\n"
                "## 📊 Key Findings\n## 📈 Trends\n## ✅ Top 5 Recommendations\n## ⚡ Quick Win This Week"
            )
            user = (
                f"Data summary:\n{data_summary(df)}\n\n"
                f"Analysis focus: {focus}\n\n"
                "Generate a thorough, specific analysis using the four required sections. "
                "Each recommendation must be actionable and reference the data."
            )
            result = claude(system, user, max_tokens=950)
            st.session_state.insights_md = result

    if st.session_state.insights_md:
        rule()
        section("🌿 Claude's Analysis")
        st.markdown(st.session_state.insights_md)
        rule()
        st.download_button(
            "⬇️ Download Insights (.txt)",
            data=st.session_state.insights_md,
            file_name="wildheart_insights.txt",
            mime="text/plain",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EMAIL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Email" in page:
    df = get_df()
    page_header("✉️ Email Generator", "Select recipients...")
    
    st.info("💡 AI responses are mock demonstrations for portfolio purposes. Real integration with Claude is shown in the code.", icon="ℹ️")

    # ── Step 1: Filter
    section("Step 1 — Filter Recipients")
    sf1, sf2, sf3 = st.columns(3)
    with sf1:
        camp_opts = ["All"] + (sorted(df["campaign"].dropna().unique().tolist()) if "campaign" in df.columns else [])
        e_camp = st.selectbox("Campaign", camp_opts, key="e_camp")
    with sf2:
        type_opts = ["All","Donor","Volunteer"]
        e_type = st.selectbox("Type", type_opts, key="e_type")
    with sf3:
        e_opt = st.selectbox("Newsletter opt-in", ["All","Yes","No"], key="e_opt")

    efdf = df.copy()
    if e_camp != "All" and "campaign" in efdf.columns: efdf = efdf[efdf["campaign"]==e_camp]
    if e_type != "All": efdf = efdf[efdf["type"]==e_type]
    if e_opt == "Yes" and "newsletter_opt_in" in efdf.columns: efdf = efdf[efdf["newsletter_opt_in"]==True]
    if e_opt == "No"  and "newsletter_opt_in" in efdf.columns: efdf = efdf[efdf["newsletter_opt_in"]==False]

    st.caption(f"{len(efdf):,} matching records")

    # ── Step 2: Pick rows
    section("Step 2 — Select Recipients (click rows)")
    show_cols = [c for c in ["name","email","type","campaign","donation_amount","country"] if c in efdf.columns]
    sel = st.dataframe(
        efdf[show_cols].reset_index(drop=True).head(300),
        use_container_width=True,
        height=280,
        on_select="rerun",
        selection_mode="multi-row",
        key="email_sel_tbl",
    )
    sel_rows = sel.selection.rows if hasattr(sel,"selection") else []
    st.caption(f"**{len(sel_rows)} selected**  (max 10 generated per run)")

    # ── Step 3: Template & tone
    section("Step 3 — Template & Settings")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        template = st.selectbox("Email template", [
            "Thank You — First Gift",
            "Thank You — Monthly Supporter",
            "Campaign Update & Impact",
            "Year-End Giving Appeal",
            "Lapsed Donor Re-engagement",
            "Volunteer Appreciation",
            "Newsletter Welcome",
        ])
    with tc2:
        tone = st.selectbox("Tone", ["Warm & personal","Professional & formal","Urgent & inspiring"])
    with tc3:
        org_name = st.text_input("Organisation name", "WildHeart Animal Charity")

    extra = st.text_area("Extra context / talking points (optional)",
                         placeholder="e.g. We just rescued 3 baby gorillas in Uganda — mention this!",
                         height=70)

    # ── Step 4: Generate
    if st.button("✉️ Generate Emails", use_container_width=False):
        if not sel_rows:
            st.warning("Select at least one row in the table above.")
        else:
            chosen = efdf.iloc[sel_rows[:10]]
            results = []
            system = (
                f"You are an expert fundraising copywriter for {org_name}, a wildlife/animal charity. "
                f"Write emails that are {tone.lower()}. "
                "Each email must feel genuinely personal — use the donor's name and specific campaign/amount details. "
                "Keep emails under 180 words. Output ONLY the email body starting with 'Dear [Name],' "
                "and ending with a warm closing. No subject line."
            )
            prog = st.progress(0, "Generating…")
            for i, (_, row) in enumerate(chosen.iterrows()):
                ctx = {c: str(row.get(c,"")) for c in show_cols if c in row}
                prompt = (
                    f"Template: {template}\n"
                    f"Recipient data: {json.dumps(ctx, indent=2)}\n"
                    f"Extra notes: {extra or 'None'}\n"
                    f"Organisation: {org_name}\n\n"
                    "Write the personalised email body now."
                )
                body = claude(system, prompt, max_tokens=350)
                results.append({
                    "name":  row.get("name","Donor"),
                    "email": row.get("email",""),
                    "body":  body,
                    "template": template,
                })
                prog.progress((i+1)/len(chosen), f"Generating {i+1}/{len(chosen)}…")
            prog.empty()
            st.session_state.emails = results
            st.success(f"✅ {len(results)} email(s) generated.")

    # ── Preview & copy
    if st.session_state.emails:
        rule()
        section(f"📬 {len(st.session_state.emails)} Generated Email(s)")
        all_txt = ""
        for i, em in enumerate(st.session_state.emails):
            with st.expander(f"📧  {em['name']}  ·  {em['email']}  ·  {em['template']}", expanded=(i==0)):
                st.markdown(f'<div class="email-card">{em["body"]}</div>', unsafe_allow_html=True)
                st.code(em["body"], language=None)
            all_txt += f"TO: {em['email']}\nNAME: {em['name']}\nTEMPLATE: {em['template']}\n\n{em['body']}\n\n{'─'*64}\n\n"

        st.download_button(
            "⬇️ Download All Emails (.txt)",
            data=all_txt,
            file_name="wildheart_emails.txt",
            mime="text/plain",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif "Reports" in page:
    df = get_df()
    page_header("📊 Reports & Exports", "Filter your data, view summary statistics, and export to CSV or PDF.")

    # ── Filters
    section("Filters")
    rf1, rf2, rf3 = st.columns(3)
    with rf1:
        r_camp = st.multiselect("Campaign(s)",
            options=sorted(df["campaign"].dropna().unique().tolist()) if "campaign" in df.columns else [])
    with rf2:
        r_type = st.multiselect("Type", ["Donor","Volunteer"])
    with rf3:
        r_ctry = st.multiselect("Country",
            options=sorted(df["country"].dropna().unique().tolist()) if "country" in df.columns else [])

    rf4, rf5 = st.columns(2)
    if "donation_date" in df.columns and df["donation_date"].notna().any():
        with rf4: r_from = st.date_input("From", df["donation_date"].min().date(), key="rp_lo")
        with rf5: r_to   = st.date_input("To",   df["donation_date"].max().date(), key="rp_hi")
    else:
        r_from = r_to = None

    rdf = df.copy()
    if r_camp: rdf = rdf[rdf["campaign"].isin(r_camp)]
    if r_type: rdf = rdf[rdf["type"].isin(r_type)]
    if r_ctry: rdf = rdf[rdf["country"].isin(r_ctry)]
    if r_from and "donation_date" in rdf.columns:
        rdf = rdf[(rdf["donation_date"].dt.date >= r_from) & (rdf["donation_date"].dt.date <= r_to)]

    st.caption(f"**{len(rdf):,} records** match your filters")
    st.dataframe(rdf.reset_index(drop=True), use_container_width=True, height=320)

    # ── Summary stats
    rule()
    section("Summary Statistics")
    ss1,ss2,ss3,ss4 = st.columns(4)
    total_r = rdf["donation_amount"].sum() if "donation_amount" in rdf.columns else 0
    avg_r   = rdf["donation_amount"].mean() if "donation_amount" in rdf.columns and len(rdf) else 0
    uniq_r  = rdf["donor_id"].nunique() if "donor_id" in rdf.columns else len(rdf)
    with ss1: st.metric("Records",      f"{len(rdf):,}")
    with ss2: st.metric("Total Raised", f"${total_r:,.2f}")
    with ss3: st.metric("Avg Gift",     f"${avg_r:,.2f}")
    with ss4: st.metric("Unique Donors",f"{uniq_r:,}")

    # Campaign breakdown
    if "campaign" in rdf.columns and "donation_amount" in rdf.columns:
        rule()
        section("Campaign Breakdown")
        cbk = (rdf.groupby("campaign")
                  .agg(Donors   =("donor_id","nunique"),
                       Donations =("donation_amount","count"),
                       Total     =("donation_amount","sum"),
                       Average   =("donation_amount","mean"))
                  .round(2).sort_values("Total",ascending=False).reset_index())
        cbk.columns = ["Campaign","Donors","Donations","Total ($)","Avg ($)"]
        cbk["Total ($)"] = cbk["Total ($)"].map("${:,.2f}".format)
        cbk["Avg ($)"]   = cbk["Avg ($)"].map("${:,.2f}".format)
        st.dataframe(cbk, use_container_width=True, hide_index=True)

    # ── Exports
    rule()
    section("Export")
    ex_a, ex_b = st.columns(2)

    with ex_a:
        csv_bytes = rdf.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_bytes,
            file_name=f"wildheart_report_{datetime.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ex_b:
        if st.button("📄 Build PDF Report", use_container_width=True):
            with st.spinner("Building PDF…"):
                st.session_state.pdf_bytes = build_pdf(rdf, f"WildHeart Donor Report — {datetime.today().strftime('%B %d, %Y')}")
            st.success("PDF ready!")
        if st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"wildheart_report_{datetime.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Built with <b>Claude</b> for the <b>Claude Corps Fellowship</b> &nbsp;·&nbsp;
  WildHeart Nonprofit Hub &nbsp;·&nbsp;
  🐾 Every record counts
</div>
""", unsafe_allow_html=True)