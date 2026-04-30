import streamlit as st


def inject_css():
    """Inject comprehensive CSS styling for dark luxury aesthetic."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Outfit:wght@300;400;500;600&display=swap');

    :root {
        --bg: #080C14;
        --surface: #0F1623;
        --border: #1E2D45;
        --accent: #E8A93C;
        --text: #F0F4FF;
        --muted: #6B7FA3;
        --green: #22C55E;
        --orange: #F97316;
        --red: #EF4444;
    }

    * {
        scroll-behavior: smooth;
    }

    html {
        scroll-behavior: smooth;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }

    /* Global Streamlit overrides */
    .appViewContainer {
        background-color: var(--bg);
    }

    /* Hide header/footer if desired - optional */
    header {
        background-color: var(--bg);
        border-bottom: 1px solid var(--border);
    }

    /* Button styling */
    button {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    button:hover {
        transform: translateY(-2px);
    }

    /* Primary button (Streamlit's default blue override) */
    .stButton > button {
        background-color: var(--accent);
        color: var(--bg);
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        background-color: #f0b847;
        box-shadow: 0 8px 24px rgba(232, 169, 60, 0.3);
    }

    .stButton > button:focus {
        background-color: #f0b847;
    }

    /* Text area styling */
    [data-testid="stTextArea"] textarea {
        font-family: 'Outfit', sans-serif;
        background-color: var(--surface);
        border: 1.5px solid var(--border);
        color: var(--text);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.3s ease;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(232, 169, 60, 0.1);
    }

    /* Animations */
    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 0.4;
            transform: translateY(0);
        }
        50% {
            opacity: 1;
            transform: translateY(6px);
        }
    }

    .animated {
        animation: fadeUp 0.6s ease forwards;
    }

    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }
    .delay-5 { animation-delay: 0.5s; }

    /* Hero section */
    .hero-section {
        min-height: 100vh;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        padding-bottom: 40px;
        background: linear-gradient(135deg, rgba(15, 22, 35, 0.4) 0%, rgba(8, 12, 20, 0.8) 100%);
    }

    .scroll-indicator {
        animation: pulse 2s ease-in-out infinite;
        font-size: 24px;
        color: var(--muted);
        cursor: pointer;
    }

    /* Skill badges */
    .skill-badge {
        display: inline-block;
        background: transparent;
        border: 1.5px solid var(--accent);
        color: var(--text);
        border-radius: 12px;
        padding: 6px 14px;
        margin: 4px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.9em;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .skill-badge:hover {
        background-color: rgba(232, 169, 60, 0.1);
        border-color: var(--accent);
    }

    /* Match badges */
    .match-badge {
        display: inline-block;
        color: white;
        border-radius: 8px;
        padding: 6px 12px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.85em;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    .match-badge.strong {
        background-color: var(--green);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
    }

    .match-badge.moderate {
        background-color: var(--orange);
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.2);
    }

    .match-badge.weak {
        background-color: var(--red);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
    }

    /* Cards */
    .compass-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }

    .compass-card:hover {
        border-color: var(--accent);
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(232, 169, 60, 0.15);
    }

    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 32px;
        padding: 0 20px;
    }

    .step-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: var(--border);
        transition: all 0.3s ease;
    }

    .step-dot.active {
        background-color: var(--accent);
        box-shadow: 0 0 12px rgba(232, 169, 60, 0.5);
        transform: scale(1.3);
    }

    /* Headings */
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5em;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 12px;
        letter-spacing: -1px;
    }

    .page-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1em;
        color: var(--muted);
        margin-bottom: 32px;
        font-weight: 400;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--accent);
        border-radius: 4px;
    }

    .stProgress {
        margin: 16px 0;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        background-color: var(--surface);
        margin: 12px 0;
    }

    [data-testid="stExpander"] button {
        font-family: 'Outfit', sans-serif;
        color: var(--text);
        font-weight: 600;
    }

    [data-testid="stExpander"] button:hover {
        background-color: rgba(232, 169, 60, 0.05);
    }

    /* Info/Warning boxes */
    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--border);
        background-color: var(--surface);
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: var(--accent);
        color: var(--bg);
        border: none;
    }

    .stDownloadButton > button:hover {
        background-color: #f0b847;
        box-shadow: 0 8px 24px rgba(232, 169, 60, 0.3);
    }

    /* Container widths */
    .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Caption/small text */
    .caption {
        font-family: 'Outfit', sans-serif;
        color: var(--muted);
        font-size: 0.9em;
        margin-top: 8px;
    }

    /* Divider */
    .stDivider {
        border-color: var(--border);
        margin: 24px 0;
    }

    /* Landing page specific */
    .landing-hero {
        text-align: center;
        margin: 60px 0;
    }

    .landing-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5em;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 16px;
        letter-spacing: -2px;
        background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .landing-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2em;
        color: var(--muted);
        margin-bottom: 48px;
        font-weight: 300;
    }

    .step-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin: 16px;
        text-align: left;
        transition: all 0.3s ease;
    }

    .step-card:hover {
        border-color: var(--accent);
        box-shadow: 0 8px 24px rgba(232, 169, 60, 0.1);
    }

    .step-card h3 {
        font-family: 'Outfit', sans-serif;
        color: var(--accent);
        font-size: 1.1em;
        margin-bottom: 8px;
    }

    .step-card p {
        font-family: 'Outfit', sans-serif;
        color: var(--muted);
        font-size: 0.95em;
        line-height: 1.6;
    }

    /* Utility classes */
    .text-center {
        text-align: center;
    }

    .mt-4 {
        margin-top: 32px;
    }

    .mb-2 {
        margin-bottom: 16px;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .landing-title {
            font-size: 2.5em;
        }

        .page-title {
            font-size: 2em;
        }

        .hero-section {
            min-height: 80vh;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
