import streamlit as st

CSS = """
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

        /* Style Streamlit's native multipage nav to look like the nav rail */
        [data-testid="stSidebarNav"] {
            padding-top: 0.6rem;
        }
        [data-testid="stSidebarNav"] a {
            color: #B7B4CC !important;
            border-radius: 10px !important;
            padding: 0.5rem 0.9rem !important;
            margin: 0 0.6rem 0.15rem 0.6rem !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background: rgba(124, 58, 237, 0.18) !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: var(--purple) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        .brand {
            font-size: 1.3rem;
            font-weight: 800;
            padding: 0.4rem 0 1rem 0;
        }
        .brand span {
            color: var(--purple-light);
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

        /* Resume / preview card (light card on dark bg, like the mockup) */
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
        .resume-meta span { margin-right: 1rem; }
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

        /* Form inputs on dark panels */
        .panel .stTextInput input, .panel .stTextArea textarea {
            background: #241F3D;
            color: #F1EFFB;
            border: 1px solid var(--border);
            border-radius: 8px;
        }

        h1, h2, h3, p, label, .stMarkdown { color: #E9E7F5; }
        .block-container { padding-top: 1.5rem; }
    </style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def render_brand():
    st.markdown('<div class="brand">Resumate <span>AI</span></div>', unsafe_allow_html=True)