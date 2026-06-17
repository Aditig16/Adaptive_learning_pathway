import streamlit as st
from login import login_user, register_user

from assessment import (
    load_roles,
    match_role,
    build_difficulty_map,
    generate_mcqs
)

from google import genai
from dotenv import load_dotenv
import os

from dotenv import load_dotenv
import os

load_dotenv()

# ---------- Page config ----------
st.set_page_config(
    page_title="Adaptive Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Global styles ----------
st.markdown("""
<style>
    /* Hide default chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* App background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 50%, #e2e8f0 100%);
        color: #0f172a;
    }

    /* Hero / header card */
    .hero {
        background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(14,165,233,0.08));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 20px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 40px -10px rgba(37,99,235,0.15);
    }
    .hero h1 {
        font-size: 2.4rem; font-weight: 800; margin: 0;
        background: linear-gradient(90deg,#2563eb,#0891b2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero p { color:#475569; margin:.35rem 0 0; font-size:1rem;}

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(8px);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px -10px rgba(37,99,235,0.18);
    }
    div[data-testid="stMetricLabel"] p { color:#94a3b8 !important; font-weight:600;}
    div[data-testid="stMetricValue"] { color:#0f172a !important; font-size:1.8rem !important;}
            
    /* Section card */
    .section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(8px);
    }
    .section h3 {
        color:#0f172a; font-weight:700; margin:0 0 1rem 0;
        display:flex; align-items:center; gap:.5rem;
    }

    /* Skill & Tool chips */
    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: .5rem;
    }

    .chip,
    .chip.tool {
        background: linear-gradient(
            135deg,
            #0f766e,
            #14b8a6
        );
        color: white;
        padding: .4rem .9rem;
        border-radius: 999px;
        font-size: .85rem;
        font-weight: 600;
        box-shadow: 0 4px 12px -4px rgba(15,118,110,0.25);
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background: white !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
    }
    .stTextInput input:focus { border-color:#2563eb !important; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg,#2563eb,#0891b2);
        color:white; border:none; border-radius: 12px;
        padding: .6rem 1.4rem; font-weight:700; width:100%;
        transition: all .2s ease;
        box-shadow: 0 6px 20px -6px rgba(37,99,235,0.25);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px -6px rgba(37,99,235,0.25);
    }

    /* Auth container */
    .auth-wrap { 
        max-width: 480px; margin: 1rem auto; 
        background: white; border: 1px solid #e2e8f0; 
        border-radius: 22px; padding: 2.25rem; 
        box-shadow: 0 20px 50px -15px rgba(15,23,42,0.08); 
    }
    .auth-title {
        font-size:1.9rem; font-weight:800; text-align:center; margin-bottom:.3rem;
        background: linear-gradient( 90deg,#2563eb,#0891b2 );
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .auth-sub { text-align:center; color:#64748b; margin-bottom:1.5rem;}
            
    label { color:#334155 !important; font-weight:600 !important;}
</style>
""", unsafe_allow_html=True)


if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "assessment_questions" not in st.session_state:
    st.session_state.assessment_questions = None

def chip_row(items, kind=""):
    html = '<div class="chips">' + "".join(
        f'<span class="chip {kind}">{i}</span>' for i in items if i
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

if (
    st.session_state.user
    and st.session_state.page == "assessment"
):

    st.title("Skill Assessment")

    user = st.session_state.user

    if st.session_state.assessment_questions is None:

        with st.spinner("Generating Assessment..."):

            load_dotenv()

            client = genai.Client(
                api_key=os.getenv(
                    "GEMINI_API_KEY"
                )
            )

            roles = load_roles()

            role_name = match_role(
                user[4],
                roles
            )

            role_data = roles.get(role_name)

            skills = []

            if role_data:

                skills.extend(
                    role_data["required"]
                )

                skills.extend(
                    role_data["preferred"]
                )

            payload = {
                "skills": list(set(skills)),
                "difficulty": [
                    "easy",
                    "medium"
                ]
            }

            result = generate_mcqs(
                client,
                payload,
                role_name
            )

            st.session_state.assessment_questions = result

    questions = st.session_state.assessment_questions

    for i, q in enumerate(
        questions["questions"]
    ):

        st.markdown("---")

        st.write(
            f"### Q{i+1}. {q['question']}"
        )

        st.radio(
            "Select Answer",
            list(
                q["options"].values()
            ),
            key=f"question_{i}"
        )

    if st.button(
        "Submit Assessment"
    ):

        score = 0

        for i, q in enumerate(
            questions["questions"]
        ):

            answer = st.session_state[
                f"question_{i}"
            ]

            if (
                answer.lower().strip()
                ==
                q["correct answer"].lower().strip()
            ):

                score += 1

        st.success(
            f"Score: {score}/{len(questions['questions'])}"
        )

    if st.button(
        "Back To Dashboard"
    ):

        st.session_state.page = "dashboard"

        st.rerun()

    st.stop()

# ============== DASHBOARD ==============
if st.session_state.user:
    user = st.session_state.user
    skills = [s.strip() for s in user[7].split(",") if s.strip()]
    tools = []
    if len(user) > 8 and user[8]:
        tools = [t.strip() for t in user[8].split(",") if t.strip()]

    # Hero
    st.markdown(f"""
    <div class="hero">
        <h1>Welcome back, {user[1]} 👋</h1>
        <p>Target role: <b style="color:#2563eb">{user[4]}</b> · Let's keep building toward your goal.</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🎯 Experience", user[6])
    with c2: st.metric("⏱ Timeline", user[5])
    with c3: st.metric("🧠 Skills", len(skills))
    with c4: st.metric("🛠 Tools", len(tools))

    # Skills section
    st.markdown('<div class="section"><h3>🧠 Your Skills</h3>', unsafe_allow_html=True)
    if skills: chip_row(skills)
    else: st.caption("No skills listed yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Tools section
    st.markdown('<div class="section"><h3>🛠 Tools & Technologies</h3>', unsafe_allow_html=True)
    if tools: chip_row(tools, "tool")
    else: st.caption("No tools listed yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Actions
    a1, a2 = st.columns([3, 1])
    with a1:
        if st.button("🚀 Start Assessment"):
            st.session_state.page = "assessment"
            st.rerun()
    with a2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()


# ============== AUTH ==============
else:
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🎓 Adaptive Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Personalized paths to master your next role</div>', unsafe_allow_html=True)

    mode = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")

    if mode == "Register":
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        targetRole = st.text_input("Target Role")
        experience = st.text_input("Relevant Experience")
        skills = st.text_input("Skills (comma separated)")
        tools = st.text_input("Tools & Technologies (comma separated)")
        timeline = st.selectbox("Study Timeline",
            ["< 1 months", "1-3 months", "3-6 months", "6-12 months", "1+ year"])

        if st.button("Create Account"):
            success = register_user(name, email, password, targetRole,
                                    timeline, experience, skills, tools)
            if success: st.success("✅ Registration successful — please log in.")
            else: st.error("⚠️ Email already exists.")

    else:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    st.markdown('</div>', unsafe_allow_html=True)
