import streamlit as st

from theme import inject_theme, render_brand

st.set_page_config(
    page_title="Personal Info · Resumate AI",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

with st.sidebar:
    render_brand()
    st.markdown("---")
    st.caption("Fill in your details here — they'll be used to personalize your resume analysis on the Dashboard.")

st.markdown("### Personal Info")
st.caption("This information powers the header shown on your Dashboard results.")

# Load any previously saved values so the form doesn't reset on rerun/navigation
saved = st.session_state.get("personal_info", {})

left_col, right_col = st.columns([1, 1.2], gap="medium")

with left_col:
    st.markdown('<div class="panel"><h4>Your Details</h4>', unsafe_allow_html=True)

    full_name = st.text_input("Full Name", value=saved.get("full_name", ""), placeholder="Jonathan Smith")
    job_title = st.text_input("Job Title", value=saved.get("job_title", ""), placeholder="Software Engineer")

    c1, c2 = st.columns(2)
    with c1:
        email = st.text_input("Email", value=saved.get("email", ""), placeholder="jonathan.smith@email.com")
    with c2:
        phone = st.text_input("Phone", value=saved.get("phone", ""), placeholder="(123) 456-7890")

    c3, c4 = st.columns(2)
    with c3:
        location = st.text_input("Location", value=saved.get("location", ""), placeholder="New York, NY")
    with c4:
        linkedin = st.text_input("LinkedIn", value=saved.get("linkedin", ""), placeholder="linkedin.com/in/jonathansmith")

    summary = st.text_area(
        "Professional Summary",
        value=saved.get("summary", ""),
        placeholder="Innovative Software Engineer with 5+ years of experience building scalable web applications...",
        height=130,
    )

    save = st.button("💾 Save Personal Info")

    st.markdown("</div>", unsafe_allow_html=True)

    if save:
        st.session_state["personal_info"] = {
            "full_name": full_name,
            "job_title": job_title,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "summary": summary,
        }
        st.success("Saved! This will now appear on your Dashboard.")

with right_col:
    st.markdown('<div class="resume-card">', unsafe_allow_html=True)
    st.markdown(f'<h2>{full_name if full_name else "Your Name"}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="resume-role">{job_title if job_title else "Job Title"}</div>', unsafe_allow_html=True)

    meta_bits = []
    if email:
        meta_bits.append(f"✉️ {email}")
    if phone:
        meta_bits.append(f"📞 {phone}")
    if location:
        meta_bits.append(f"📍 {location}")
    if linkedin:
        meta_bits.append(f"🔗 {linkedin}")
    if meta_bits:
        spans = "".join(f"<span>{b}</span>" for b in meta_bits)
        st.markdown(f'<div class="resume-meta">{spans}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="resume-meta">Fill in the form to see a live preview</div>', unsafe_allow_html=True)

    if summary:
        st.markdown('<div class="resume-section-title">Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="resume-body">{summary}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)