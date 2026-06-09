import streamlit as st

GOVAI_CSS = """
<style>
:root {
    --govai-navy: #0B1F3A;
    --govai-azure: #006BFF;
    --govai-teal: #00A7A5;
    --govai-eucalyptus: #3E7C59;
    --govai-mist: #F4F8FB;
    --govai-sand: #F7F1E7;
    --govai-charcoal: #1F2933;
    --govai-border: #CBD5E1;
    --govai-focus: #FFBF47;
}
html, body, [class*="css"] {
    font-family: "Public Sans", "Aptos", Arial, Helvetica, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: var(--govai-mist);
    color: var(--govai-charcoal);
}
[data-testid="stHeader"] {
    background: rgba(244, 248, 251, 0.94);
}
[data-testid="stMainBlockContainer"] {
    max-width: 1280px;
    padding-top: 4.25rem;
    padding-bottom: 3rem;
}
[data-testid="stAppDeployButton"],
[data-testid="stMainMenu"],
[data-testid="stStatusWidget"] {
    display: none;
}
[data-testid="stSidebar"] {
    background: var(--govai-navy);
    border-right: 0;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
[data-testid="stSidebarNav"] a {
    border-radius: 0.5rem;
    margin: 0.15rem 0.5rem;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.10);
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: var(--govai-azure);
    font-weight: 700;
}

/* ── Sidebar access panel ── */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.20);
    border-radius: 0.5rem;
    color: #FFFFFF;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p,
[data-testid="stSidebar"] [data-testid="stAlert"] span,
[data-testid="stSidebar"] [data-testid="stAlert"] div {
    color: #FFFFFF;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown p {
    color: #C9D6E5;
}
[data-testid="stSidebar"] [data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 0.65rem;
    padding: 0.75rem;
}
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="textarea"] > div {
    background: rgba(255, 255, 255, 0.10);
    border-color: rgba(255, 255, 255, 0.25);
    border-radius: 0.4rem;
}
[data-testid="stSidebar"] [data-baseweb="input"] input,
[data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
    color: #FFFFFF;
}
[data-testid="stSidebar"] [data-baseweb="input"] input::placeholder,
[data-testid="stSidebar"] [data-baseweb="textarea"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.45);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #C9D6E5;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button {
    background: var(--govai-azure);
    border: none;
    border-radius: 0.4rem;
    color: #FFFFFF;
    font-weight: 700;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button:hover {
    background: #0056CC;
    color: #FFFFFF;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #FFFFFF;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
}

.govai-masthead {
    align-items: center;
    background: var(--govai-navy);
    border-radius: 0.75rem;
    color: #FFFFFF;
    display: flex;
    justify-content: space-between;
    margin-bottom: 1.75rem;
    min-height: 88px;
    overflow: hidden;
    padding: 1.15rem 1.5rem;
    position: relative;
}
.govai-masthead::after {
    background: repeating-linear-gradient(
        130deg,
        transparent 0,
        transparent 74px,
        rgba(0, 167, 165, 0.12) 76px,
        rgba(0, 167, 165, 0.12) 79px
    );
    content: "";
    inset: 0;
    pointer-events: none;
    position: absolute;
}
.govai-brand, .govai-product {
    position: relative;
    z-index: 1;
}
.govai-brand {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1;
}
.govai-brand::before {
    background: var(--govai-teal);
    border-radius: 50%;
    content: "";
    display: inline-block;
    height: 0.7rem;
    margin-right: 0.6rem;
    width: 0.7rem;
}
.govai-product {
    font-size: 0.95rem;
    font-weight: 600;
    text-align: right;
}
.govai-product span {
    color: #C9D6E5;
    display: block;
    font-size: 0.76rem;
    font-weight: 500;
    margin-top: 0.2rem;
}
.govai-hero {
    background: #FFFFFF;
    border: 1px solid var(--govai-border);
    border-left: 6px solid var(--govai-teal);
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
    padding: 1.5rem 1.75rem;
}
.govai-hero-kicker {
    color: var(--govai-eucalyptus);
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin-bottom: 0.45rem;
    text-transform: uppercase;
}
.govai-hero h1 {
    margin: 0 0 0.5rem 0;
}
.govai-hero p {
    color: #334E68;
    font-size: 1.05rem;
    margin: 0;
    max-width: 780px;
}
h1, h2, h3 {
    color: var(--govai-navy);
    letter-spacing: -0.02em;
}
h1 {
    font-size: clamp(2rem, 4vw, 2.65rem) !important;
    font-weight: 800 !important;
}
h2 {
    font-weight: 750 !important;
}
p, li, label, [data-testid="stCaptionContainer"] {
    line-height: 1.55;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--govai-border);
    border-radius: 0.75rem;
    min-height: 112px;
    padding: 1rem 1.1rem;
}
[data-testid="stMetricValue"] {
    color: var(--govai-navy);
    font-weight: 800;
}
[data-testid="stMetricLabel"] {
    color: #40566E;
    font-weight: 650;
}
[data-testid="stAlert"] {
    border-radius: 0.65rem;
    border-width: 0 0 0 5px;
}
[data-testid="stForm"],
[data-testid="stExpander"],
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    background: #FFFFFF;
    border-color: var(--govai-border);
    border-radius: 0.75rem;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 0.45rem;
    font-weight: 700;
    min-height: 2.65rem;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
    background: var(--govai-azure);
    border-color: var(--govai-azure);
    color: #FFFFFF;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--govai-navy);
    color: var(--govai-navy);
}
.stButton > button[kind="primary"]:hover {
    background: #0056CC;
    color: #FFFFFF;
}
button:focus-visible, a:focus-visible, input:focus-visible,
textarea:focus-visible, [role="combobox"]:focus-visible {
    outline: 3px solid var(--govai-focus) !important;
    outline-offset: 2px !important;
}
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div {
    background: #FFFFFF;
    border-color: #94A3B8;
}
hr {
    border-color: var(--govai-border);
}
@media (max-width: 700px) {
    .govai-masthead {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.75rem;
    }
    .govai-product {
        text-align: left;
    }
    [data-testid="stMainBlockContainer"] {
        padding-top: 4rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
"""

def apply_govai_branding() -> None:
    st.html(GOVAI_CSS)
    st.html(
        """
<div class="govai-masthead">
  <div class="govai-brand">GovAI</div>
  <div class="govai-product">
    UAT feedback dashboard
    <span>Safe, practical and human-reviewed</span>
  </div>
</div>
"""
    )

def page_intro(title: str, description: str, kicker: str = "GovAI service") -> None:
    st.html(
        f"""
<div class="govai-hero">
  <div class="govai-hero-kicker">{kicker}</div>
  <h1>{title}</h1>
  <p>{description}</p>
</div>
"""
    )
