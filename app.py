import streamlit as st
from login import (login_user, register_user, save_assessment_result, get_assessment_history)

from assessment import (
    load_roles,
    match_role,
    build_difficulty_map,
    generate_mcqs,
    skill_gap,
)

from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ---------- Page config ----------
st.set_page_config(
    page_title="Pathwise · Adaptive Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Global styles ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

    /* ── Reset & Base ── */
    #MainMenu, footer, header { visibility: hidden; }
    * { box-sizing: border-box; }

    .stApp {
        background: #0c0e14;
        color: #e8eaf0;
        font-family: 'Inter', sans-serif;
    }

    /* ── Layout shell ── */
    .block-container {
        max-width: 1100px !important;
        padding: 0 2rem 4rem !important;
        margin: 0 auto;
    }

    /* ── Top nav bar ── */
    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.4rem 0 1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 0;
    }
    .nav-logo {
        font-family: 'DM Serif Display', serif;
        font-size: 1.45rem;
        color: #ffffff;
        letter-spacing: -0.01em;
    }
    .nav-logo span { color: #6ee7b7; }
    .nav-pill {
        background: rgba(110,231,183,0.10);
        color: #6ee7b7;
        font-size: 0.75rem;
        font-weight: 600;
        padding: .25rem .75rem;
        border-radius: 20px;
        border: 1px solid rgba(110,231,183,0.25);
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* ── Hero section ── */
    .hero-wrap {
        padding: 5rem 0 3.5rem;
        text-align: center;
        position: relative;
    }
    .hero-eyebrow {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6ee7b7;
        margin-bottom: 1.25rem;
    }
    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 3.2rem;
        line-height: 1.12;
        color: #ffffff;
        margin: 0 0 1.25rem;
        letter-spacing: -0.02em;
    }
    .hero-title em {
        color: #6ee7b7;
        font-style: italic;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 500px;
        margin: 0 auto 2.5rem;
        line-height: 1.65;
        font-weight: 400;
    }

    /* ── Auth card ── */
    .auth-card {
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 2.5rem 2.75rem;
        max-width: 480px;
        margin: 0 auto;
        box-shadow: 0 24px 64px rgba(0,0,0,0.45);
    }
    .auth-card-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: .35rem;
    }
    .auth-card-sub {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .auth-divider {
        display: flex;
        align-items: center;
        gap: .75rem;
        margin: 1.5rem 0;
        color: #334155;
        font-size: 0.8rem;
    }
    .auth-divider::before, .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.07);
    }

    /* ── Form elements ── */
    .stTextInput > label, .stSelectbox > label {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
        margin-bottom: .3rem !important;
    }
    .stTextInput input {
        background: #0c0e14 !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important;
        color: #e8eaf0 !important;
        font-size: 0.93rem !important;
        padding: .65rem .9rem !important;
        transition: border-color .2s !important;
    }
    .stTextInput input:focus {
        border-color: #6ee7b7 !important;
        box-shadow: 0 0 0 3px rgba(110,231,183,0.12) !important;
    }
    .stTextInput input::placeholder { color: #475569 !important; }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #0c0e14 !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important;
        color: #e8eaf0 !important;
        font-size: 0.93rem !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #6ee7b7;
        color: #0c0e14;
        border: none;
        border-radius: 10px;
        padding: .65rem 1.4rem;
        font-weight: 700;
        font-size: 0.9rem;
        width: 100%;
        letter-spacing: 0.01em;
        transition: background .15s ease, transform .12s ease, box-shadow .15s;
        box-shadow: 0 4px 16px rgba(110,231,183,0.18);
    }
    .stButton > button:hover {
        background: #a7f3d0;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(110,231,183,0.28);
        color: #0c0e14;
    }
    .stButton > button:active { transform: translateY(0); }

    /* Secondary ghost button — wrap in .ghost-btn div */
    .ghost-btn .stButton > button {
        background: transparent;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: none;
    }
    .ghost-btn .stButton > button:hover {
        background: rgba(255,255,255,0.05);
        color: #e8eaf0;
        transform: none;
        box-shadow: none;
    }

    /* Danger ghost */
    .danger-btn .stButton > button {
        background: transparent;
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.25);
        box-shadow: none;
    }
    .danger-btn .stButton > button:hover {
        background: rgba(248,113,113,0.08);
        color: #f87171;
        transform: none;
        box-shadow: none;
    }

    /* ── Radio tabs ── */
    .stRadio [data-testid="stHorizontalBlock"] {
        background: #0c0e14;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: .3rem;
        gap: .3rem !important;
    }
    .stRadio label {
        background: transparent;
        border-radius: 8px;
        padding: .45rem 1rem;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #64748b !important;
        transition: all .15s;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    .stRadio label[data-selected="true"], .stRadio input:checked + label {
        background: #6ee7b7 !important;
        color: #0c0e14 !important;
    }

    /* ── Dashboard layout ── */
    .dashboard-header {
        padding: 3rem 0 2rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2.5rem;
    }
    .greeting-eyebrow {
        font-size: 0.78rem;
        font-weight: 600;
        color: #6ee7b7;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: .5rem;
    }
    .greeting-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.4rem;
        color: #ffffff;
        margin: 0 0 .4rem;
        letter-spacing: -0.02em;
    }
    .greeting-sub {
        font-size: 0.92rem;
        color: #64748b;
    }

    /* ── Stat cards ── */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2.5rem;
    }
    .stat-card {
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1.35rem 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6ee7b7, transparent);
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: .5rem;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }

    /* ── Section headers ── */
    .section-hd {
        font-size: 0.78rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 2rem 0 1rem;
        display: flex;
        align-items: center;
        gap: .6rem;
    }
    .section-hd::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.06);
    }

    /* ── Skill chips ── */
    .chip-wrap { display: flex; flex-wrap: wrap; gap: .45rem; margin-bottom: .5rem; }
    .chip {
        background: rgba(110,231,183,0.08);
        color: #6ee7b7;
        border: 1px solid rgba(110,231,183,0.18);
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 500;
        padding: .3rem .75rem;
        letter-spacing: 0.01em;
    }
    .chip.tool {
        background: rgba(139,92,246,0.08);
        color: #c4b5fd;
        border-color: rgba(139,92,246,0.2);
    }

    /* ── Action cards (CTA area) ── */
    .cta-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 2.5rem;
    }
    .cta-card {
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.75rem;
        cursor: pointer;
        transition: border-color .2s, background .2s;
    }
    .cta-card:hover {
        border-color: rgba(110,231,183,0.3);
        background: #15192300;
    }
    .cta-card-icon {
        font-size: 1.6rem;
        margin-bottom: .85rem;
        display: block;
    }
    .cta-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: .35rem;
    }
    .cta-card-desc {
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.55;
    }

    /* ── Assessment page ── */
    .assessment-header {
        padding: 2.5rem 0 2rem;
    }
    .progress-bar-wrap {
        background: rgba(255,255,255,0.06);
        border-radius: 99px;
        height: 5px;
        margin-bottom: 2.5rem;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6ee7b7, #34d399);
        border-radius: 99px;
        transition: width .4s ease;
    }

    .question-card {
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.75rem 1.9rem;
        margin-bottom: 1.1rem;
    }
    .q-number {
        font-size: 0.72rem;
        font-weight: 700;
        color: #6ee7b7;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: .65rem;
    }
    .q-text {
        font-size: 0.97rem;
        font-weight: 600;
        color: #e8eaf0;
        line-height: 1.55;
        margin-bottom: 1.1rem;
    }
    .stRadio > label { display: none; }
    div[role="radiogroup"] label {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 9px;
        padding: .65rem .9rem;
        margin-bottom: .4rem;
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        transition: border-color .15s, background .15s;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    div[role="radiogroup"] label:hover {
        border-color: rgba(110,231,183,0.3);
        background: rgba(110,231,183,0.05);
        color: #e8eaf0 !important;
    }

    /* ── Report page ── */
    .report-header {
        padding: 2.5rem 0 2rem;
    }
    .score-summary {
        display: flex;
        gap: 2rem;
        align-items: center;
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 2rem;
    }
    .score-big {
        font-family: 'DM Serif Display', serif;
        font-size: 3.5rem;
        color: #6ee7b7;
        line-height: 1;
        letter-spacing: -0.03em;
    }
    .score-label { font-size: 0.85rem; color: #64748b; margin-top: .3rem; }

    .skill-row {
        margin-bottom: 1rem;
    }
    .skill-row-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: .45rem;
    }
    .skill-name { font-size: 0.9rem; color: #cbd5e1; font-weight: 500; }
    .skill-pct  { font-size: 0.88rem; font-weight: 700; }
    .skill-pct.good   { color: #6ee7b7; }
    .skill-pct.warn   { color: #fbbf24; }
    .skill-pct.danger { color: #f87171; }
    .skill-track {
        background: rgba(255,255,255,0.06);
        border-radius: 99px;
        height: 5px;
        overflow: hidden;
    }
    .skill-fill { height: 100%; border-radius: 99px; }
    .fill-good   { background: linear-gradient(90deg, #6ee7b7, #34d399); }
    .fill-warn   { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
    .fill-danger { background: linear-gradient(90deg, #f87171, #ef4444); }

    .result-badge {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        font-size: 0.8rem;
        font-weight: 600;
        padding: .3rem .8rem;
        border-radius: 99px;
    }
    .badge-strong { background: rgba(110,231,183,0.12); color: #6ee7b7; border: 1px solid rgba(110,231,183,0.22); }
    .badge-weak   { background: rgba(251,191,36,0.10); color: #fbbf24; border: 1px solid rgba(251,191,36,0.22); }

    /* ── Progress overrides ── */
    .stProgress { display: none !important; }

    /* ── Metric overrides (hide native, we use custom) ── */
    div[data-testid="stMetric"] { display: none !important; }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #6ee7b7 !important; }
    .stSpinner p { color: #64748b !important; font-size: 0.88rem !important; }

    /* ── Alerts ── */
    .stAlert {
        background: rgba(110,231,183,0.07) !important;
        border: 1px solid rgba(110,231,183,0.2) !important;
        border-radius: 10px !important;
        color: #6ee7b7 !important;
    }
    .stSuccess { background: rgba(110,231,183,0.07) !important; border: 1px solid rgba(110,231,183,0.2) !important; border-radius: 10px !important; }
    .stError   { background: rgba(248,113,113,0.07) !important; border: 1px solid rgba(248,113,113,0.2) !important; border-radius: 10px !important; }
    .stSuccess p, .stError p { font-size: 0.88rem !important; }

    /* ── Horizontal rule ── */
    hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.75rem 0 !important; }

    /* Spacer util */
    .sp { height: 1rem; }
    .sp2 { height: 2rem; }
</style>
""", unsafe_allow_html=True)


# ---------- State ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "assessment_questions" not in st.session_state:
    st.session_state.assessment_questions = None
if "assessment_report" not in st.session_state:
    st.session_state.assessment_report = None


# ── Shared nav bar ──
def render_nav(show_user=None):
    st.markdown(
        f"""<div class="nav-bar">
            <span class="nav-logo">Path<span>wise</span></span>
            <span class="nav-pill">{'👤 ' + show_user if show_user else 'Adaptive Learning'}</span>
        </div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# ROUTING
# ============================================================

# ──────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────
if st.session_state.user is None:
    render_nav()

    st.markdown("""
    <div class="hero-wrap">
        <span class="hero-eyebrow">✦ AI-powered career growth</span>
        <h1 class="hero-title">
            Master your next role<br>
            <em>faster than ever.</em>
        </h1>
        <p class="hero-sub">
            Adaptive assessments, personalized learning paths, and real-time skill tracking
            — all built around your goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    mode = st.radio("Mode", ["Login", "Register"],
                    horizontal=True, label_visibility="collapsed")
    st.markdown("<div class='sp'></div>", unsafe_allow_html=True)

    if mode == "Register":
        st.markdown('<p class="auth-card-title">Create your account</p>', unsafe_allow_html=True)
        st.markdown('<p class="auth-card-sub">Set up your profile and start your learning journey.</p>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name", placeholder="Alex Johnson")
        with c2:
            email = st.text_input("Email address", placeholder="alex@example.com")

        password   = st.text_input("Password", type="password", placeholder="Min. 8 characters")
        targetRole = st.text_input("Target role", placeholder="e.g. Senior Data Scientist")
        experience = st.text_input("Relevant experience", placeholder="e.g. 3 years as a data analyst")

        c3, c4 = st.columns(2)
        with c3:
            skills = st.text_input("Skills", placeholder="Python, SQL, ML...")
        with c4:
            tools = st.text_input("Tools", placeholder="dbt, Spark, Airflow...")

        timeline = st.selectbox(
            "Study timeline",
            ["< 1 months", "1-3 months", "3-6 months", "6-12 months", "1+ year"],
        )

        st.markdown("<div class='sp'></div>", unsafe_allow_html=True)
        if st.button("Create account →"):
            ok = register_user(name, email, password, targetRole,
                               timeline, experience, skills, tools)
            if ok:
                st.success("Account created — please log in.")
            else:
                st.error("That email already has an account.")

    else:  # Login
        st.markdown('<p class="auth-card-title">Welcome back</p>', unsafe_allow_html=True)
        st.markdown('<p class="auth-card-sub">Sign in to continue your learning path.</p>', unsafe_allow_html=True)

        email    = st.text_input("Email address", placeholder="alex@example.com")
        password = st.text_input("Password", type="password", placeholder="Your password")

        st.markdown("<div class='sp'></div>", unsafe_allow_html=True)
        if st.button("Sign in →"):
            user = login_user(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Email or password is incorrect.")

    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# ASSESSMENT
# ──────────────────────────────────────────────────────────────
elif st.session_state.page == "assessment":
    user = st.session_state.user
    render_nav(show_user=user[1])

    st.markdown(
        f"""<div class="assessment-header">
            <span class="greeting-eyebrow">📋 Assessment</span>
            <h1 class="greeting-title">Skill Evaluation</h1>
            <p class="greeting-sub">
                Questions tailored for <strong style="color:#e8eaf0;">{user[4]}</strong>
                — answer honestly for the most accurate roadmap.
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.session_state.assessment_questions is None:
        with st.spinner("Generating your personalized assessment…"):
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            roles     = load_roles()
            role_name = match_role(user[4], roles)
            role_data = roles.get(role_name)

            skills_list = []
            if role_data:
                skills_list.extend(role_data["required"])
                skills_list.extend(role_data["preferred"])

            payload = {
                "skills": list(set(skills_list)),
                "difficulty": ["easy", "medium"],
            }
            st.session_state.assessment_questions = generate_mcqs(
                client, payload, role_name
            )

    questions = st.session_state.assessment_questions
    total     = len(questions["questions"])

    # Compute how many have been answered (for progress bar)
    answered = sum(
        1 for i in range(total)
        if st.session_state.get(f"question_{i}")
    )
    pct = int(answered / total * 100) if total else 0

    st.markdown(
        f"""<div class="progress-bar-wrap">
            <div class="progress-fill" style="width:{pct}%;"></div>
        </div>""",
        unsafe_allow_html=True,
    )

    for i, q in enumerate(questions["questions"]):
        st.markdown(
            f"""<div class="question-card">
                <div class="q-number">Question {i+1} of {total}</div>
                <div class="q-text">{q['question']}</div>
            """,
            unsafe_allow_html=True,
        )
        st.radio(
            "Select answer",
            list(q["options"].keys()),
            format_func=lambda x, q=q: f"{x}.  {q['options'][x]}",
            key=f"question_{i}",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sp2'></div>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1.2, 1, 2])
    with c1:
        if st.button("Submit assessment →"):

            for i, q in enumerate(questions["questions"]):
                q["user answer"] = st.session_state.get(
                    f"question_{i}"
                )

            report = skill_gap(
                questions
            )

            save_assessment_result(
                user[0],
                report
            )

            st.session_state.assessment_report = report

            st.session_state.page = "report"

            st.rerun()
    with c2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# REPORT
# ──────────────────────────────────────────────────────────────
elif st.session_state.page == "report":
    user   = st.session_state.user
    report = st.session_state.assessment_report or {}
    render_nav(show_user=user[1])

    strong = [s for s, sc in report.items() if sc >= 75]
    weak   = [s for s, sc in report.items() if sc < 75]
    avg    = (sum(report.values()) / len(report)) if report else 0

    st.markdown(
        f"""<div class="report-header">
            <span class="greeting-eyebrow">📊 Results</span>
            <h1 class="greeting-title">Assessment Report</h1>
            <p class="greeting-sub">Here's how your skills stack up for {user[4]}.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Summary bar
    st.markdown(
        f"""<div class="score-summary">
            <div>
                <div class="score-big">{avg:.0f}%</div>
                <div class="score-label">Overall score</div>
            </div>
            <div style="flex:1; display:flex; flex-direction:column; gap:.5rem;">
                <div>
                    <span class="result-badge badge-strong">✓ {len(strong)} strong skills</span>
                    &nbsp;
                    <span class="result-badge badge-weak">⚠ {len(weak)} need work</span>
                </div>
                <div style="font-size:0.85rem; color:#475569;">
                    {len(report)} skills assessed across your target role requirements.
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Skill breakdown
    st.markdown('<div class="section-hd">Skill Breakdown</div>', unsafe_allow_html=True)

    for skill, score in sorted(report.items(), key=lambda x: -x[1]):
        if score >= 75:
            cls, fcls = "good", "fill-good"
        elif score >= 50:
            cls, fcls = "warn", "fill-warn"
        else:
            cls, fcls = "danger", "fill-danger"

        st.markdown(
            f"""<div class="skill-row">
                <div class="skill-row-meta">
                    <span class="skill-name">{skill}</span>
                    <span class="skill-pct {cls}">{score:.0f}%</span>
                </div>
                <div class="skill-track">
                    <div class="skill-fill {fcls}" style="width:{score}%;"></div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Strengths / Weaknesses
    st.markdown("<div class='sp'></div>", unsafe_allow_html=True)
    col_s, col_w = st.columns(2)

    with col_s:
        st.markdown('<div class="section-hd">Strengths</div>', unsafe_allow_html=True)
        if strong:
            items_html = "".join(
                f'<span class="chip">{s}</span>' for s in strong
            )
            st.markdown(f'<div class="chip-wrap">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#475569;font-size:0.88rem;'>Keep practicing — no strong areas yet.</p>", unsafe_allow_html=True)

    with col_w:
        st.markdown('<div class="section-hd">Needs Improvement</div>', unsafe_allow_html=True)
        if weak:
            items_html = "".join(
                f'<span class="chip tool">{s}</span>' for s in weak
            )
            st.markdown(f'<div class="chip-wrap">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#6ee7b7;font-size:0.88rem;'>Excellent — no weak areas found!</p>", unsafe_allow_html=True)

    st.markdown("<div class='sp2'></div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns([1.2, 1.2, 1])
    with a1:
        if st.button("Generate roadmap →"):
            st.info("Roadmap generation coming soon — hang tight!")
    with a2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Back to dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with a3:
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("Retake assessment"):
            st.session_state.assessment_questions = None
            st.session_state.assessment_report    = None
            st.session_state.page = "assessment"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────
else:
    user   = st.session_state.user
    history = get_assessment_history(user[0])
    skills = [s.strip() for s in user[7].split(",") if s.strip()]
    tools  = []
    if len(user) > 8 and user[8]:
        tools = [t.strip() for t in user[8].split(",") if t.strip()]

    render_nav(show_user=user[1])

    # Dashboard header
    st.markdown(
        f"""<div class="dashboard-header">
            <div class="greeting-eyebrow">👋 Good to see you</div>
            <h1 class="greeting-title">{user[1].split()[0]}'s Learning Hub</h1>
            <p class="greeting-sub">
                Working toward <strong style="color:#e8eaf0;">{user[4]}</strong>
                &nbsp;·&nbsp; {user[5]} timeline
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Stats
    st.markdown(
        f"""<div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Target Role</div>
                <div class="stat-value" style="font-size:1.1rem;">{user[4]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Experience</div>
                <div class="stat-value">{user[6] or "—"}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Skills Listed</div>
                <div class="stat-value">{len(skills)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tools Listed</div>
                <div class="stat-value">{len(tools)}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Skills
    st.markdown('<div class="section-hd">Your Skills</div>', unsafe_allow_html=True)
    if skills:
        chips_html = "".join(f'<span class="chip">{s}</span>' for s in skills)
        st.markdown(f'<div class="chip-wrap">{chips_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#475569;font-size:0.88rem;'>No skills added yet. Edit your profile to add some.</p>", unsafe_allow_html=True)

    # Tools
    st.markdown('<div class="section-hd">Tools & Technologies</div>', unsafe_allow_html=True)
    if tools:
        chips_html = "".join(f'<span class="chip tool">{t}</span>' for t in tools)
        st.markdown(f'<div class="chip-wrap">{chips_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#475569;font-size:0.88rem;'>No tools added yet.</p>", unsafe_allow_html=True)

    # Assessment History
# Assessment History

    st.markdown(
        '<div class="section-hd">Recent Assessments</div>',
        unsafe_allow_html=True
    )

    if history:

        total_attempts = len(history)

        for idx, (date, skill_scores) in enumerate(
            history[:5]
        ):

            scores = json.loads(
                skill_scores
            )

            avg_score = (
                sum(scores.values())
                / len(scores)
            )

            attempt_no = (
                total_attempts - idx
            )

            if avg_score >= 75:

                status = "Strong Performance"

            elif avg_score >= 50:

                status = "Developing Skills"

            else:

                status = "Needs Improvement"

            col1, col2 = st.columns([3,1])

            with col1:

                st.info(
                    f"📋 Assessment #{attempt_no}\n\n{status}"
                )

            with col2:

                st.success(
                    f"{avg_score:.0f}%"
                )

    else:

        st.info(
            "No assessments completed yet."
        )
    
    # Action cards
    st.markdown('<div class="section-hd">Actions</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="cta-row">
            <div class="cta-card" id="start-assessment">
                <span class="cta-card-icon">🎯</span>
                <div class="cta-card-title">Start Assessment</div>
                <div class="cta-card-desc">
                    Take an adaptive skill evaluation to find your gaps and strengths
                    relative to your target role.
                </div>
            </div>
            <div class="cta-card" id="view-roadmap">
                <span class="cta-card-icon">🗺️</span>
                <div class="cta-card-title">View Learning Roadmap</div>
                <div class="cta-card-desc">
                    Get a personalized study plan with curated resources to close skill gaps
                    on your timeline.
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sp2'></div>", unsafe_allow_html=True)
    b1, b2, _ = st.columns([1, 1, 2])
    with b1:
        if st.button("Start assessment →"):
            st.session_state.page = "assessment"
            st.rerun()
    with b2:
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("Sign out"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.assessment_questions = None
            st.session_state.assessment_report    = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)