import streamlit as st
from login import (login_user, register_user, save_assessment_result, get_assessment_history, save_roadmap, get_latest_roadmap)
from fetch_content import content_generation
from assessment import call_gemini

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
    page_icon="P",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Global styles ----------
st.markdown("""
<style>
    /* Reset & base */
    #MainMenu, footer, header { visibility: hidden; }
    * { box-sizing: border-box; }

    .stApp {
        background: #ffffff;
        color: #2d3339;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Layout shell */
    .block-container {
        max-width: 1100px !important;
        padding: 0 2rem 4rem !important;
        margin: 0 auto;
    }

    /* Top nav */
    .nav-divider {
        height: 1px;
        background: #e2e5e9;
        margin: 0.5rem 0 2.25rem;
    }

    /* Hero section */
    .hero-wrap {
        padding: 4rem 0 2.75rem;
        text-align: center;
    }
    .hero-title {
        font-size: 2.1rem;
        line-height: 1.3;
        font-weight: 700;
        color: #1f2328;
        margin: 0;
        letter-spacing: -0.01em;
    }

    /* Auth form area (no card/box treatment, just plain fields) */
    .auth-card {
        max-width: 420px;
        margin: 0 auto;
    }
    .auth-card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1f2328;
        margin-bottom: .3rem;
    }
    .auth-card-sub {
        font-size: 0.88rem;
        color: #57606a;
        margin-bottom: 1.75rem;
    }

    /* Form elements */
    .stTextInput > label, .stSelectbox > label {
        color: #57606a !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        margin-bottom: .3rem !important;
    }
    .stTextInput input {
        background: #ffffff !important;
        border: 1px solid #d8dee4 !important;
        border-radius: 6px !important;
        color: #1f2328 !important;
        font-size: 0.93rem !important;
        padding: .55rem .8rem !important;
        transition: border-color .15s !important;
    }
    .stTextInput input:focus {
        border-color: #2c5f8a !important;
        box-shadow: 0 0 0 2px rgba(44,95,138,0.15) !important;
    }
    .stTextInput input::placeholder { color: #9aa3ab !important; }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid #d8dee4 !important;
        border-radius: 6px !important;
        color: #1f2328 !important;
        font-size: 0.93rem !important;
    }

    /* Buttons */
    .stButton > button {
        background: #2c5f8a;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: .6rem 1.3rem;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
        transition: background .15s ease;
    }
    .stButton > button:hover {
        background: #244d70;
        color: #ffffff;
    }
    .stButton > button:active { opacity: 0.9; }
    .stButton > button p { color: inherit !important; }

    /* Secondary ghost button — wrap in .ghost-btn div */
    .ghost-btn .stButton > button {
        background: #ffffff;
        color: #1f2328;
        border: 1px solid #d8dee4;
    }
    .ghost-btn .stButton > button:hover {
        background: #f2f4f6;
        color: #1f2328;
    }

    /* Danger ghost — wrap in .danger-btn div */
    .danger-btn .stButton > button {
        background: #ffffff;
        color: #b3261e;
        border: 1px solid #e7b3ae;
    }
    .danger-btn .stButton > button:hover {
        background: #fbeceb;
        color: #b3261e;
    }

    /* Radio tabs */
    .stRadio [data-testid="stHorizontalBlock"] {
        background: #f2f4f6;
        border: 1px solid #d8dee4;
        border-radius: 6px;
        padding: .25rem;
        gap: .25rem !important;
    }
    .stRadio label {
        background: transparent;
        border-radius: 5px;
        padding: .42rem .9rem;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #57606a !important;
        transition: all .15s;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    .stRadio label[data-selected="true"], .stRadio input:checked + label {
        background: #2c5f8a !important;
        color: #ffffff !important;
    }

    /* Dashboard layout */
    .dashboard-header {
        padding: 1.5rem 0 1.75rem;
        border-bottom: 1px solid #e2e5e9;
        margin-bottom: 2.25rem;
    }
    .greeting-eyebrow {
        font-size: 0.85rem;
        font-weight: 600;
        color: #2c5f8a;
        margin-bottom: .4rem;
    }
    .greeting-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1f2328;
        margin: 0 0 .35rem;
        letter-spacing: -0.01em;
    }
    .greeting-sub {
        font-size: 0.92rem;
        color: #57606a;
    }

    /* Stat cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2.25rem;
    }
    .stat-card {
        background: #fafbfc;
        border: 1px solid #e2e5e9;
        border-radius: 8px;
        padding: 1.2rem 1.3rem;
    }
    .stat-label {
        font-size: 0.74rem;
        color: #57606a;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
        margin-bottom: .4rem;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f2328;
    }

    /* Section headers */
    .section-hd {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1f2328;
        margin: 1.9rem 0 0.9rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e2e5e9;
    }

    /* Skill chips */
    .chip-wrap { display: flex; flex-wrap: wrap; gap: .45rem; margin-bottom: .5rem; }
    .chip {
        background: #eef3f7;
        color: #2c5f8a;
        border: 1px solid #c9dbe8;
        border-radius: 5px;
        font-size: 0.82rem;
        font-weight: 500;
        padding: .28rem .7rem;
        letter-spacing: 0.01em;
    }
    .chip.tool {
        background: #f1edf7;
        color: #6b4fa0;
        border-color: #d9cdec;
    }

    /* Action cards (CTA area) */
    .cta-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    .cta-card {
        background: #ffffff;
        border: 1px solid #d8dee4;
        border-radius: 8px;
        padding: 1.5rem 1.6rem;
        transition: border-color .15s;
    }
    .cta-card:hover {
        border-color: #2c5f8a;
    }
    .cta-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1f2328;
        margin-bottom: .35rem;
    }
    .cta-card-desc {
        font-size: 0.85rem;
        color: #57606a;
        line-height: 1.55;
    }

    /* Assessment page */
    .assessment-header {
        padding: 1.5rem 0 1.75rem;
    }
    .progress-bar-wrap {
        background: #e2e5e9;
        border-radius: 99px;
        height: 6px;
        margin-bottom: 2.25rem;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: #2c5f8a;
        border-radius: 99px;
        transition: width .4s ease;
    }

    .question-card {
        background: #fafbfc;
        border: 1px solid #e2e5e9;
        border-radius: 8px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1rem;
    }
    .q-number {
        font-size: 0.72rem;
        font-weight: 700;
        color: #2c5f8a;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: .55rem;
    }
    .q-text {
        font-size: 0.97rem;
        font-weight: 600;
        color: #1f2328;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    .stRadio > label { display: none; }
    div[role="radiogroup"] label {
        background: #ffffff;
        border: 1px solid #d8dee4;
        border-radius: 6px;
        padding: .6rem .85rem;
        margin-bottom: .35rem;
        color: #2d3339 !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        transition: border-color .15s, background .15s;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    div[role="radiogroup"] label:hover {
        border-color: #2c5f8a;
        background: #f2f6f9;
        color: #1f2328 !important;
    }

    /* Report page */
    .report-header {
        padding: 1.5rem 0 1.75rem;
    }
    .score-summary {
        display: flex;
        gap: 2rem;
        align-items: center;
        background: #fafbfc;
        border: 1px solid #e2e5e9;
        border-radius: 8px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.75rem;
    }
    .score-big {
        font-size: 2.6rem;
        font-weight: 700;
        color: #2c5f8a;
        line-height: 1;
        letter-spacing: -0.01em;
    }
    .score-label { font-size: 0.85rem; color: #57606a; margin-top: .3rem; }

    .skill-row {
        margin-bottom: 1rem;
    }
    .skill-row-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: .4rem;
    }
    .skill-name { font-size: 0.9rem; color: #2d3339; font-weight: 500; }
    .skill-pct  { font-size: 0.88rem; font-weight: 700; }
    .skill-pct.good   { color: #2f7a3c; }
    .skill-pct.warn   { color: #a15c07; }
    .skill-pct.danger { color: #b3261e; }
    .skill-track {
        background: #e2e5e9;
        border-radius: 99px;
        height: 6px;
        overflow: hidden;
    }
    .skill-fill { height: 100%; border-radius: 99px; }
    .fill-good   { background: #2f7a3c; }
    .fill-warn   { background: #a15c07; }
    .fill-danger { background: #b3261e; }

    .result-badge {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        font-size: 0.8rem;
        font-weight: 600;
        padding: .28rem .75rem;
        border-radius: 5px;
    }
    .badge-strong { background: #eaf5ec; color: #2f7a3c; border: 1px solid #bfe2c5; }
    .badge-weak   { background: #faf1e2; color: #a15c07; border: 1px solid #ecd6ab; }

    /* Progress overrides */
    .stProgress { display: none !important; }

    /* Metric overrides (hide native, we use custom) */
    div[data-testid="stMetric"] { display: none !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #2c5f8a !important; }
    .stSpinner p { color: #57606a !important; font-size: 0.88rem !important; }

    /* Alerts */
    .stAlert {
        background: #eef3f7 !important;
        border: 1px solid #c9dbe8 !important;
        border-radius: 6px !important;
        color: #1f2328 !important;
    }
    .stSuccess { background: #eaf5ec !important; border: 1px solid #bfe2c5 !important; border-radius: 6px !important; }
    .stError   { background: #fbeceb !important; border: 1px solid #e7b3ae !important; border-radius: 6px !important; }
    .stSuccess p, .stError p, .stAlert p { font-size: 0.88rem !important; color: #1f2328 !important; }

    /* Horizontal rule */
    hr { border-color: #e2e5e9 !important; margin: 1.6rem 0 !important; }

    /* Spacer util */
    .sp { height: 1rem; }
    .sp2 { height: 1.75rem; }
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
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None

# ── Shared nav bar ──
def render_nav(show_user=None):
    if show_user:
        _, right = st.columns([6, 1])
        with right:
            st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("Sign out", key="nav_signout_btn"):
                st.session_state.user = None
                st.session_state.page = "dashboard"
                st.session_state.assessment_questions = None
                st.session_state.assessment_report = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)


# ============================================================
# ROUTING
# ============================================================

# ──────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────
if st.session_state.user is None:

    st.markdown("""
    <div class="hero-wrap">
        <h1 class="hero-title">Adaptive Learning Pathway</h1>
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
            <span class="greeting-eyebrow">Assessment</span>
            <h1 class="greeting-title">Skill Evaluation</h1>
            <p class="greeting-sub">
                Questions tailored for <strong style="color:#2c5f8a;">{user[4]}</strong>
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
    total = len(questions["questions"])

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
            format_func=lambda x, q=q: f"{x}. {q['options'][x]}",
            key=f"question_{i}",
            index=None,  # No option selected initially
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sp2'></div>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1.2, 1, 2])
    with c1:
        if st.button("Submit assessment →"):

            unanswered = []

            for i in range(total):
                if st.session_state.get(f"question_{i}") is None:
                    unanswered.append(i + 1)

            if unanswered:
                st.error(
                    f"Please answer all questions before submitting. Missing: {', '.join(map(str, unanswered))}"
                )
                st.stop()

            for i, q in enumerate(questions["questions"]):
                q["user answer"] = st.session_state.get(
                    f"question_{i}"
                )

            report = skill_gap(questions)

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
            <span class="greeting-eyebrow">Results</span>
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
                    <span class="result-badge badge-strong">{len(strong)} strong skills</span>
                    &nbsp;
                    <span class="result-badge badge-weak">{len(weak)} need work</span>
                </div>
                <div style="font-size:0.85rem; color:#57606a;">
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
            st.markdown("<p style='color:#57606a;font-size:0.88rem;'>Keep practicing — no strong areas yet.</p>", unsafe_allow_html=True)

    with col_w:
        st.markdown('<div class="section-hd">Needs Improvement</div>', unsafe_allow_html=True)
        if weak:
            items_html = "".join(
                f'<span class="chip tool">{s}</span>' for s in weak
            )
            st.markdown(f'<div class="chip-wrap">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#2f7a3c;font-size:0.88rem;'>Excellent — no weak areas found!</p>", unsafe_allow_html=True)

    st.markdown("<div class='sp2'></div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns([1.2, 1.2, 1])
    with a1:
        if st.button("Generate roadmap →"):

            with st.spinner(
                "Generating roadmap..."
            ):

                roadmap_prompt = content_generation(
                    {
                        "target_role": user[4],
                        "timelines": user[5]
                    },
                    st.session_state.assessment_report
                )

                client = genai.Client(
                    api_key=os.getenv(
                        "GEMINI_API_KEY"
                    )
                )

                roadmap = call_gemini(
                    client,
                    roadmap_prompt
                )

                print("ROADMAP =", roadmap)

                if roadmap is None:

                    st.error(
                        "Roadmap generation failed."
                    )
                    st.stop()

                st.session_state.roadmap = roadmap

                # SAVE ROADMAP TO DATABASE
                save_roadmap(
                    user[0],
                    roadmap
                )

                st.session_state.page = "roadmap"

                st.rerun()
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

# ─────────────────────────────
# ROADMAP
# ─────────────────────────────

elif st.session_state.page == "roadmap":

    #roadmap = st.session_state.roadmap
    roadmap = st.session_state.get(
        "roadmap",
        None
    )

    st.title(
        "Personalized Learning Roadmap"
    )

    if roadmap is None:

        st.error(
            "Roadmap generation failed."
        )

    else:

        st.success(
            f"{roadmap['timeline_weeks']} Week Learning Plan"
        )

        weeks = {}

        for skill in roadmap["learning_path"]:

            if "weekly_plan" not in skill:
                continue

            for week in skill["weekly_plan"]:

                wk = week["week"]

                if wk not in weeks:
                    weeks[wk] = []

                weeks[wk].append({
                    "skill": skill["skill"],
                    "focus": week["focus"],
                    "tasks": week["TASK"]
                })

        for week_no in sorted(weeks.keys()):

            st.markdown(
                f"## Week {week_no}"
            )

            for item in weeks[week_no]:

                st.subheader(
                    item["skill"]
                )

                st.write(
                    f"Focus: {item['focus']}"
                )

                for task in item["tasks"]:

                    st.write(
                        f"• {task}"
                    )

            st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Retake Assessment"
        ):

            st.session_state.assessment_questions = None

            st.session_state.assessment_report = None

            st.session_state.page = "assessment"

            st.rerun()

    with c2:

        if st.button(
            "Back To Dashboard"
        ):

            st.session_state.page = "dashboard"

            st.rerun()

# ─────────────────────────────
# JOB READY PAGE
# ─────────────────────────────

elif st.session_state.page == "job_ready":

    st.balloons()

    st.success(
        "Congratulations!"
    )

    st.markdown(
        """
# You Are Job Ready

You have successfully completed your learning pathway.

Your assessment results indicate that you are ready to begin applying for roles.

Recommended next steps:

• Update your Resume

• Build Projects

• Apply for Jobs

• Continue Advanced Learning
"""
    )

    if st.button(
        "Back To Dashboard"
    ):

        st.session_state.page = "dashboard"

        st.rerun()
        
# ──────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────
else:
    user   = st.session_state.user
    history = get_assessment_history(user[0])
    saved_roadmap = get_latest_roadmap(user[0])
    skills = [s.strip() for s in user[7].split(",") if s.strip()]
    tools  = []
    if len(user) > 8 and user[8]:
        tools = [t.strip() for t in user[8].split(",") if t.strip()]

    render_nav(show_user=user[1])

    # Dashboard header
    st.markdown(
        f"""<div class="dashboard-header">
            <div class="greeting-eyebrow">Good to see you</div>
            <h1 class="greeting-title">{user[1].split()[0]}'s Learning Hub</h1>
            <p class="greeting-sub">
                Working toward <strong style="color:#2c5f8a;">{user[4]}</strong>
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
        st.markdown("<p style='color:#57606a;font-size:0.88rem;'>No skills added yet. Edit your profile to add some.</p>", unsafe_allow_html=True)

    # Tools
    st.markdown('<div class="section-hd">Tools & Technologies</div>', unsafe_allow_html=True)
    if tools:
        chips_html = "".join(f'<span class="chip tool">{t}</span>' for t in tools)
        st.markdown(f'<div class="chip-wrap">{chips_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#57606a;font-size:0.88rem;'>No tools added yet.</p>", unsafe_allow_html=True)

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
                    f"Assessment #{attempt_no}\n\n{status}"
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
                <div class="cta-card-title">Start Assessment</div>
                <div class="cta-card-desc">
                    Take an adaptive skill evaluation to find your gaps and strengths
                    relative to your target role.
                </div>
            </div>
            <div class="cta-card" id="view-roadmap">
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
    b1, _ = st.columns([1, 3])
    with b1:

        if saved_roadmap:

            if st.button("View Roadmap →"):

                st.session_state.roadmap = saved_roadmap

                st.session_state.page = "roadmap"

                st.rerun()

        else:

            if st.button("Start assessment →"):

                st.session_state.page = "assessment"

                st.rerun()