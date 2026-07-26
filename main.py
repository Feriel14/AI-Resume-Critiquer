import streamlit as st
import PyPDF2
import io
import os
import json
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from theme import inject_theme, render_brand

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

inject_theme()

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    render_brand()
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

default_score = 0
default_suggestions = [
    {"text": "Improve impact verbs", "status": "warn"},
    {"text": "Quantify achievements", "status": "warn"},
    {"text": "Add more skills", "status": "warn"},
    {"text": "Optimize for ATS", "status": "warn"},
]

result_state = st.session_state.get("result")
personal_info = st.session_state.get("personal_info")

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
        display_name = personal_info["full_name"] if personal_info and personal_info.get("full_name") else result_state["file_name"]
        display_role = personal_info["job_title"] if personal_info and personal_info.get("job_title") else (job_role if job_role else "General Application")

        st.markdown('<div class="resume-card">', unsafe_allow_html=True)
        st.markdown(f'<h2>{display_name}</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="resume-role">{display_role}</div>', unsafe_allow_html=True)

        if personal_info:
            meta_bits = []
            if personal_info.get("email"):
                meta_bits.append(f'✉️ {personal_info["email"]}')
            if personal_info.get("phone"):
                meta_bits.append(f'📞 {personal_info["phone"]}')
            if personal_info.get("location"):
                meta_bits.append(f'📍 {personal_info["location"]}')
            if personal_info.get("linkedin"):
                meta_bits.append(f'🔗 {personal_info["linkedin"]}')
            if meta_bits:
                spans = "".join(f"<span>{b}</span>" for b in meta_bits)
                st.markdown(f'<div class="resume-meta">{spans}</div>', unsafe_allow_html=True)

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