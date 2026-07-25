import streamlit as st
import PyPDF2
import io
import os
import json
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resumate AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------------------------------------------------------------------
# Theme / CSS  (purple dashboard look)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        :root {
            --purple: #7C3AED;
            --purple-light: #A78BFA;
            --purple-soft: rgba(124, 58, 237, 0.12);
            --bg-dark: #12101B;
            --bg-panel: #1B1830;
            --border: rgba(255,255,255,0.08);
            --text-dim: #9895AC;
        }

        .stApp {
            background-color: var(--bg-dark);
        }

        /* Sidebar = dark navy/purple nav rail */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #16132A 0%, #1B1733 100%);
            border-right: 1px solid var(--border);
        }
        section[data-testid="stSidebar"] * {
            color: #E9E7F5;
        }

        .brand {
            font-size: 1.3rem;
            font-weight: 800;
            padding: 0.4rem 0 1.2rem 0;
        }
        .brand span {
            color: var(--purple-light);
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.55rem 0.8rem;
            border-radius: 10px;
            margin-bottom: 0.25rem;
            font-size: 0.93rem;
            color: #B7B4CC;
        }
        .nav-item.active {
            background: var(--purple);
            color: white !important;
            font-weight: 600;
        }

        /* Cards */
        .panel {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.4rem 1.5rem;
            margin-bottom: 1.1rem;
        }
        .panel h4 {
            margin-top: 0;
            color: #D9D6EC;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 700;
        }

        /* Score gauge */
        .gauge-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0.6rem 0 0.3rem 0;
        }
        .gauge {
            width: 170px;
            height: 170px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .gauge-inner {
            width: 132px;
            height: 132px;
            border-radius: 50%;
            background: var(--bg-panel);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .gauge-score {
            font-size: 2.1rem;
            font-weight: 800;
            color: #F1EFFB;
        }
        .gauge-label {
            font-size: 0.85rem;
            font-weight: 700;
            margin-top: 0.6rem;
            padding: 0.15rem 0.9rem;
            border-radius: 999px;
        }

        /* Suggestions list */
        .suggestion-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.55rem 0;
            border-bottom: 1px solid var(--border);
            font-size: 0.93rem;
            color: #DDDAEE;
        }
        .suggestion-row:last-child { border-bottom: none; }
        .badge-good { color: #4ADE80; font-weight: 700; }
        .badge-warn { color: #FBBF24; font-weight: 700; }

        /* Resume preview panel (right side, mimics the resume card) */
        .resume-card {
            background: #FBFAFF;
            color: #1a1a2e;
            border-radius: 16px;
            padding: 1.8rem 2rem;
            border: 1px solid var(--border);
        }
        .resume-card h2 { margin-bottom: 0; color: #14121f; }
        .resume-role { color: var(--purple); font-weight: 700; margin-top: 0.1rem; }
        .resume-meta { color: #6b6880; font-size: 0.85rem; margin: 0.6rem 0 1rem 0; }
        .resume-section-title {
            color: var(--purple);
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 1.1rem 0 0.4rem 0;
        }
        .resume-body { font-size: 0.9rem; line-height: 1.55; white-space: pre-wrap; color: #2b2942; }

        /* Buttons */
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.65rem 1rem;
            font-weight: 700;
            border: none;
            background: linear-gradient(135deg, #7C3AED, #A78BFA);
            color: white;
        }
        div.stButton > button:hover {
            box-shadow: 0 6px 18px rgba(124, 58, 237, 0.4);
            color: white;
        }

        h1, h2, h3, p, label, .stMarkdown { color: #E9E7F5; }
        .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar — nav rail (styled like the mockup)
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">Resumate <span>AI</span></div>', unsafe_allow_html=True)

    nav_items = [
        ("🏠", "Dashboard", True),
        ("👤", "Personal Info", False),
        ("💼", "Experience", False),
        ("🎓", "Education", False),
        ("⭐", "Skills", False),
        ("📁", "Projects", False),
        ("📄", "Templates", False),
        ("⚙️", "Settings", False),
    ]
    for icon, label, active in nav_items:
        cls = "nav-item active" if active else "nav-item"
        st.markdown(f'<div class="{cls}">{icon} &nbsp; {label}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📎 Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or TXT)",
        type=["pdf", "txt"],
        label_visibility="collapsed",
    )
    job_role = st.text_input(
        "Target job role (optional)",
        placeholder="e.g. Software Engineer",
    )
    analyze = st.button("✨ Enhance with AI", disabled=not GROQ_API_KEY)

    if not GROQ_API_KEY:
        st.warning("Set GROQ_API_KEY in your .env file.")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(file.read()))
    return file.read().decode("utf-8")


def gauge_html(score: int) -> str:
    score = max(0, min(100, score))
    if score >= 85:
        label, label_bg, label_color = "Excellent", "rgba(74,222,128,0.15)", "#4ADE80"
    elif score >= 65:
        label, label_bg, label_color = "Good", "rgba(251,191,36,0.15)", "#FBBF24"
    else:
        label, label_bg, label_color = "Needs Work", "rgba(248,113,113,0.15)", "#F87171"

    deg = score * 3.6
    return f"""
    <div class="gauge-wrap">
        <div class="gauge" style="background: conic-gradient(#7C3AED 0deg, #A78BFA {deg}deg, #2A2640 {deg}deg 360deg);">
            <div class="gauge-inner">
                <div class="gauge-score">{score}%</div>
            </div>
        </div>
        <div class="gauge-label" style="background:{label_bg}; color:{label_color};">{label}</div>
    </div>
    """


def suggestions_html(suggestions):
    rows = ""
    for s in suggestions:
        text = s.get("text", "")
        status = s.get("status", "good")
        badge = "✅" if status == "good" else "⚠️"
        badge_cls = "badge-good" if status == "good" else "badge-warn"
        rows += f'<div class="suggestion-row"><span>{text}</span><span class="{badge_cls}">{badge}</span></div>'
    return f'<div class="panel"><h4>AI Suggestions</h4>{rows}</div>'


def parse_ai_json(raw_text: str):
    cleaned = re.sub(r"```json|```", "", raw_text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


# ----------------------------------------------------------------------------
# Main layout
# ----------------------------------------------------------------------------
st.markdown("### Dashboard")
st.caption("Upload a resume in the sidebar, then click **Enhance with AI** to generate your score and feedback.")

left_col, right_col = st.columns([1, 1.6], gap="medium")

# Defaults shown before any analysis has run
default_score = 0
default_suggestions = [
    {"text": "Improve impact verbs", "status": "warn"},
    {"text": "Quantify achievements", "status": "warn"},
    {"text": "Add more skills", "status": "warn"},
    {"text": "Optimize for ATS", "status": "warn"},
]

result_state = st.session_state.get("result")

with left_col:
    st.markdown('<div class="panel"><h4>Resume Score</h4>', unsafe_allow_html=True)
    score_to_show = result_state["score"] if result_state else default_score
    st.markdown(gauge_html(score_to_show), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    suggestions_to_show = result_state["suggestions"] if result_state else default_suggestions
    st.markdown(suggestions_html(suggestions_to_show), unsafe_allow_html=True)

with right_col:
    if uploaded_file is None and not result_state:
        st.markdown(
            '<div class="panel" style="text-align:center; padding: 3rem 1rem; color:#9895AC;">'
            "📄 Upload a resume in the sidebar to see it here."
            "</div>",
            unsafe_allow_html=True,
        )
    elif result_state:
        st.markdown('<div class="resume-card">', unsafe_allow_html=True)
        st.markdown(f'<h2>{result_state["file_name"]}</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="resume-role">{job_role if job_role else "General Application"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="resume-section-title">AI Feedback</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="resume-body">{result_state["feedback"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            "⬇️ Download Feedback as TXT",
            data=result_state["feedback"],
            file_name="resume_feedback.txt",
            mime="text/plain",
        )
    elif uploaded_file is not None:
        st.markdown(
            '<div class="panel" style="text-align:center; padding: 3rem 1rem; color:#9895AC;">'
            f'📎 <b>{uploaded_file.name}</b> ready — click <b>Enhance with AI</b> in the sidebar.'
            "</div>",
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------------------------
# Analysis flow
# ----------------------------------------------------------------------------
if analyze:
    if not uploaded_file:
        st.error("📎 Please upload a resume file first.")
        st.stop()

    try:
        with st.spinner("Analyzing resume..."):
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("The uploaded file doesn't contain any readable text.")
                st.stop()

            prompt = f"""You are an expert resume reviewer. Analyze the resume below and respond with ONLY a valid JSON object
(no markdown fences, no preamble) with exactly these fields:

{{
  "score": <integer 0-100 representing overall resume quality>,
  "suggestions": [
    {{"text": "<short improvement suggestion, 3-5 words>", "status": "good" or "warn"}},
    ... exactly 4 items ...
  ],
  "feedback": "<detailed markdown-formatted feedback covering content clarity, skills presentation, experience descriptions, and improvements for {job_role if job_role else 'general job applications'}>"
}}

Resume content:
{file_content}
"""

            client = ChatGroq(
                api_key=GROQ_API_KEY,
                model="llama-3.1-8b-instant",
                temperature=0.5,
                max_tokens=1500,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

            messages = [
                {"role": "system", "content": "You are an expert resume reviewer. You always respond with strictly valid JSON only."},
                {"role": "user", "content": prompt},
            ]

            response = client.invoke(messages)

            try:
                parsed = parse_ai_json(response.content)
                st.session_state["result"] = {
                    "score": int(parsed.get("score", 70)),
                    "suggestions": parsed.get("suggestions", default_suggestions),
                    "feedback": parsed.get("feedback", response.content),
                    "file_name": uploaded_file.name,
                }
            except (json.JSONDecodeError, ValueError, AttributeError):
                # Fallback: JSON mode failed for some reason — still show the
                # raw response as feedback instead of blocking the user.
                st.session_state["result"] = {
                    "score": 70,
                    "suggestions": default_suggestions,
                    "feedback": response.content,
                    "file_name": uploaded_file.name,
                }
                st.toast("Feedback generated, but the score/checklist formatting fell back to defaults.", icon="⚠️")

        st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")