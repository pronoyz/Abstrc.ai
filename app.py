"""
Abstrc.ai — AI Video / Audio Summarizer
Streamlit UI  •  Black & White  •  English / বাংলা  •  Dark / Light Mode
"""

import streamlit as st
import os
import sys
import tempfile
import time
import io
from pathlib import Path
from datetime import datetime

# ── Environment ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Core imports ─────────────────────────────────────────────────────────────
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_questions
from core.rag_engine import build_rag_chain, ask_question

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Abstrc.ai — AI Summarizer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "en": {
        "app_title": "Abstrc.ai",
        "app_subtitle": "AI-Powered Video & Audio Summarizer",
        "sidebar_title": "⚙️ Settings",
        "language_label": "Interface Language",
        "theme_label": "Theme",
        "dark": "Dark",
        "light": "Light",
        "input_section": "📥 Input Source",
        "input_method": "Choose input method",
        "youtube_url": "YouTube URL",
        "file_upload": "Upload File",
        "youtube_placeholder": "Paste a YouTube URL here…",
        "upload_prompt": "Upload an audio or video file",
        "upload_help": "Supported: MP3, WAV, MP4, MKV, WEBM, OGG, FLAC, M4A",
        "transcription_lang": "Transcription Language",
        "english": "English",
        "banglish": "Bangla (Banglish)",
        "process_btn": "⚡ Process",
        "processing": "Processing…",
        "step_downloading": "Downloading & preparing audio…",
        "step_transcribing": "Transcribing audio…",
        "step_title": "Generating title…",
        "step_summary": "Summarizing transcript…",
        "step_questions": "Extracting open questions…",
        "step_rag": "Building knowledge base…",
        "step_done": "Done!",
        "results_title": "📊 Results",
        "tab_summary": "📋 Summary",
        "tab_questions": "❓ Open Questions",
        "tab_transcript": "📝 Full Transcript",
        "tab_chat": "💬 Chat with AI",
        "chat_title": "Chat with the Video",
        "chat_placeholder": "Ask anything about the video…",
        "chat_thinking": "Thinking…",
        "export_title": "📤 Export",
        "export_txt": "Download as TXT",
        "export_info": "Download the full analysis report.",
        "no_input_warning": "Please provide a YouTube URL or upload a file.",
        "about_title": "About",
        "about_text": (
            "**Abstrc.ai** uses AI to transcribe, summarize, "
            "and analyze video/audio content. Ask questions about "
            "your media using the built-in RAG chat."
        ),
        "footer": "Built with ❤️ by Abstrc.ai",
        "new_session": "🔄 New Session",
        "clear_confirm": "Start a new analysis?",
    },
    "bn": {
        "app_title": "Abstrc.ai",
        "app_subtitle": "AI-চালিত ভিডিও ও অডিও সংক্ষেপণ",
        "sidebar_title": "⚙️ সেটিংস",
        "language_label": "ইন্টারফেস ভাষা",
        "theme_label": "থিম",
        "dark": "ডার্ক",
        "light": "লাইট",
        "input_section": "📥 ইনপুট সোর্স",
        "input_method": "ইনপুট পদ্ধতি বাছুন",
        "youtube_url": "ইউটিউব URL",
        "file_upload": "ফাইল আপলোড",
        "youtube_placeholder": "এখানে ইউটিউব URL পেস্ট করুন…",
        "upload_prompt": "একটি অডিও বা ভিডিও ফাইল আপলোড করুন",
        "upload_help": "সমর্থিত: MP3, WAV, MP4, MKV, WEBM, OGG, FLAC, M4A",
        "transcription_lang": "ট্রান্সক্রিপশন ভাষা",
        "english": "ইংরেজি",
        "banglish": "বাংলা (বাংলিশ)",
        "process_btn": "⚡ প্রক্রিয়া শুরু",
        "processing": "প্রক্রিয়াকরণ চলছে…",
        "step_downloading": "অডিও ডাউনলোড ও প্রস্তুত করা হচ্ছে…",
        "step_transcribing": "অডিও ট্রান্সক্রাইব করা হচ্ছে…",
        "step_title": "শিরোনাম তৈরি করা হচ্ছে…",
        "step_summary": "সারাংশ তৈরি করা হচ্ছে…",
        "step_questions": "অমীমাংসিত প্রশ্ন বের করা হচ্ছে…",
        "step_rag": "জ্ঞানভাণ্ডার তৈরি করা হচ্ছে…",
        "step_done": "সম্পন্ন!",
        "results_title": "📊 ফলাফল",
        "tab_summary": "📋 সারাংশ",
        "tab_questions": "❓ অমীমাংসিত প্রশ্ন",
        "tab_transcript": "📝 সম্পূর্ণ ট্রান্সক্রিপ্ট",
        "tab_chat": "💬 AI-এর সাথে চ্যাট",
        "chat_title": "ভিডিও নিয়ে প্রশ্ন করুন",
        "chat_placeholder": "ভিডিও সম্পর্কে যেকোনো প্রশ্ন করুন…",
        "chat_thinking": "চিন্তা করা হচ্ছে…",
        "export_title": "📤 এক্সপোর্ট",
        "export_txt": "TXT হিসাবে ডাউনলোড",
        "export_info": "সম্পূর্ণ বিশ্লেষণ রিপোর্ট ডাউনলোড করুন।",
        "no_input_warning": "অনুগ্রহ করে একটি ইউটিউব URL দিন অথবা ফাইল আপলোড করুন।",
        "about_title": "সম্পর্কে",
        "about_text": (
            "**Abstrc.ai** এ AI ব্যবহার করে ভিডিও/অডিও কন্টেন্ট "
            "ট্রান্সক্রাইব, সারাংশ ও বিশ্লেষণ করা হয়। বিল্ট-ইন RAG চ্যাট "
            "ব্যবহার করে আপনার মিডিয়া সম্পর্কে প্রশ্ন করুন।"
        ),
        "footer": "Team Abstrc দিয়ে তৈরি — Abstrc.ai",
        "new_session": "🔄 নতুন সেশন",
        "clear_confirm": "নতুন বিশ্লেষণ শুরু করবেন?",
    },
}


def t(key: str) -> str:
    """Return translated string for current language."""
    lang = st.session_state.get("ui_lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ═══════════════════════════════════════════════════════════════════════════════
# THEME CSS
# ═══════════════════════════════════════════════════════════════════════════════
def inject_css():
    """Inject black-and-white theme CSS with dark/light mode support."""
    mode = st.session_state.get("theme_mode", "dark")
    is_dark = mode == "dark"

    # ── Color palette ────────────────────────────────────────────────────────
    bg = "#0a0a0a" if is_dark else "#fafafa"
    bg_secondary = "#111111" if is_dark else "#f0f0f0"
    bg_card = "#161616" if is_dark else "#ffffff"
    bg_card_hover = "#1c1c1c" if is_dark else "#f5f5f5"
    bg_input = "#1a1a1a" if is_dark else "#ffffff"
    border = "#2a2a2a" if is_dark else "#e0e0e0"
    border_focus = "#555555" if is_dark else "#888888"
    text_primary = "#ffffff" if is_dark else "#0a0a0a"
    text_secondary = "#999999" if is_dark else "#666666"
    text_muted = "#555555" if is_dark else "#aaaaaa"
    accent = "#ffffff" if is_dark else "#000000"
    accent_subtle = "#333333" if is_dark else "#dddddd"
    btn_bg = "#ffffff" if is_dark else "#0a0a0a"
    btn_text = "#000000" if is_dark else "#ffffff"
    btn_hover = "#e0e0e0" if is_dark else "#222222"
    scrollbar_thumb = "#333333" if is_dark else "#cccccc"
    scrollbar_track = "#111111" if is_dark else "#f0f0f0"
    shadow = "0 4px 24px rgba(0,0,0,0.5)" if is_dark else "0 4px 24px rgba(0,0,0,0.08)"
    shadow_sm = "0 2px 8px rgba(0,0,0,0.3)" if is_dark else "0 2px 8px rgba(0,0,0,0.05)"
    glow = "0 0 20px rgba(255,255,255,0.03)" if is_dark else "0 0 20px rgba(0,0,0,0.02)"

    css = f"""
    <style>
    /* ── Import font ───────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+Bengali:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root / Global ─────────────────────────────────────────────────── */
    :root {{
        color-scheme: {"dark" if is_dark else "light"};
    }}

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {{
        background-color: {bg} !important;
        color: {text_primary} !important;
        font-family: 'Inter', 'Noto Sans Bengali', -apple-system, sans-serif !important;
    }}

    /* ── Scrollbar ─────────────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {scrollbar_track}; }}
    ::-webkit-scrollbar-thumb {{ background: {scrollbar_thumb}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {border_focus}; }}

    /* ── Header bar ────────────────────────────────────────────────────── */
    header[data-testid="stHeader"] {{
        background-color: {bg} !important;
        border-bottom: 1px solid {border} !important;
        backdrop-filter: blur(12px);
    }}

    /* ── Sidebar ───────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background-color: {bg_secondary} !important;
        border-right: 1px solid {border} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stSelectbox label {{
        color: {text_secondary} !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.7rem !important;
    }}

    /* ── Text elements ─────────────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
        font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }}
    p, span, li, div {{
        color: {text_primary} !important;
    }}
    a {{ color: {text_secondary} !important; text-decoration: none !important; }}
    a:hover {{ color: {text_primary} !important; }}

    /* ── Buttons ────────────────────────────────────────────────────────── */
    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.6rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: {shadow_sm} !important;
    }}
    .stButton > button:hover {{
        background-color: {btn_hover} !important;
        transform: translateY(-1px) !important;
        box-shadow: {shadow} !important;
    }}
    .stButton > button:active {{
        transform: translateY(0px) !important;
    }}

    /* ── Download button ───────────────────────────────────────────────── */
    .stDownloadButton > button {{
        background-color: transparent !important;
        color: {text_primary} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {accent_subtle} !important;
        border-color: {border_focus} !important;
    }}

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    .stTextInput input,
    .stTextArea textarea {{
        background-color: {bg_input} !important;
        color: {text_primary} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        padding: 0.7rem 1rem !important;
        font-family: 'Inter', 'Noto Sans Bengali', sans-serif !important;
        transition: border-color 0.2s ease !important;
    }}
    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {border_focus} !important;
        box-shadow: 0 0 0 2px {"rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.05)"} !important;
    }}

    /* ── Chat input ────────────────────────────────────────────────────── */
    .stChatInput {{
        border-color: {border} !important;
    }}
    .stChatInput textarea {{
        background-color: {bg_input} !important;
        color: {text_primary} !important;
    }}

    /* ── Chat messages ─────────────────────────────────────────────────── */
    [data-testid="stChatMessage"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
    }}

    /* ── Tabs ───────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px !important;
        background-color: {bg_secondary} !important;
        border-radius: 10px !important;
        padding: 4px !important;
        border: 1px solid {border} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: {text_secondary} !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {text_primary} !important;
        background-color: {"rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.04)"} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        box-shadow: {shadow_sm} !important;
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ── File uploader ─────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {{
        background-color: {bg_card} !important;
        border: 2px dashed {border} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: border-color 0.3s ease !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: {border_focus} !important;
    }}

    /* ── Selectbox / Radio ─────────────────────────────────────────────── */
    [data-baseweb="select"] {{
        background-color: {bg_input} !important;
    }}
    [data-baseweb="select"] * {{
        color: {text_primary} !important;
    }}
    [data-baseweb="popover"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border} !important;
    }}
    [data-baseweb="menu"] {{
        background-color: {bg_card} !important;
    }}
    [data-baseweb="menu"] li {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    [data-baseweb="menu"] li:hover {{
        background-color: {accent_subtle} !important;
    }}
    .stRadio [data-baseweb="radio"] {{
        background-color: transparent !important;
    }}

    /* ── Expander ───────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    .streamlit-expanderContent {{
        background-color: {bg_card} !important;
        border: 1px solid {border} !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }}

    /* ── Alerts ─────────────────────────────────────────────────────────── */
    .stAlert {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
    }}

    /* ── Spinner ────────────────────────────────────────────────────────── */
    .stSpinner > div {{
        border-top-color: {accent} !important;
    }}

    /* ── Progress bar ──────────────────────────────────────────────────── */
    .stProgress > div > div > div {{
        background-color: {accent} !important;
        border-radius: 4px !important;
    }}
    .stProgress > div > div {{
        background-color: {accent_subtle} !important;
        border-radius: 4px !important;
    }}

    /* ── Divider ────────────────────────────────────────────────────────── */
    hr {{
        border-color: {border} !important;
        opacity: 0.5;
    }}

    /* ── Card class ─────────────────────────────────────────────────────── */
    .result-card {{
        background-color: {bg_card};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: {glow};
        transition: all 0.25s ease;
    }}
    .result-card:hover {{
        border-color: {border_focus};
        box-shadow: {shadow};
    }}

    /* ── Hero header ───────────────────────────────────────────────────── */
    .hero-title {{
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, {text_primary} 0%, {text_secondary} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        color: {text_secondary};
        font-weight: 400;
        letter-spacing: 0.01em;
        margin-bottom: 2rem;
    }}

    /* ── Status badge ──────────────────────────────────────────────────── */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: {accent_subtle};
        color: {text_primary};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }}

    /* ── Section header ────────────────────────────────────────────────── */
    .section-header {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {text_muted};
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {border};
    }}

    /* ── Stats row ─────────────────────────────────────────────────────── */
    .stat-card {{
        background-color: {bg_card};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.2s ease;
    }}
    .stat-card:hover {{
        border-color: {border_focus};
    }}
    .stat-number {{
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: {text_primary};
    }}
    .stat-label {{
        font-size: 0.72rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {text_muted};
        margin-top: 4px;
    }}

    /* ── Footer ─────────────────────────────────────────────────────────── */
    .footer {{
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: {text_muted};
        font-size: 0.8rem;
        letter-spacing: 0.02em;
        border-top: 1px solid {border};
        margin-top: 3rem;
    }}

    /* ── Animations ─────────────────────────────────────────────────────── */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0);   }}
    }}
    .animate-in {{
        animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50%      {{ opacity: 0.5; }}
    }}
    .pulse {{
        animation: pulse 2s ease-in-out infinite;
    }}

    /* ── Hide Streamlit branding ───────────────────────────────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER — build export text
# ═══════════════════════════════════════════════════════════════════════════════
def build_export_text(result: dict) -> str:
    """Build a plain-text report from the analysis results."""

    def to_str(val):
        if isinstance(val, list):
            return "\n".join(f"  - {item}" for item in val) if val else "N/A"
        return str(val) if val else "N/A"

    key_points = result.get("key_points", [])
    key_points_text = to_str(key_points)

    lines = [
        "═" * 60,
        f"  Abstrc.ai — Analysis Report",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "═" * 60,
        "",
        f"📌 TITLE",
        f"   {result.get('title', 'N/A')}",
        "",
        "─" * 60,
        "📋 SUMMARY",
        "─" * 60,
        to_str(result.get("summary")),
        "",
        "─" * 60,
        "🔑 KEY POINTS",
        "─" * 60,
        key_points_text,
        "",
        "─" * 60,
        "❓ OPEN QUESTIONS",
        "─" * 60,
        to_str(result.get("open_questions")),
        "",
        "─" * 60,
        "📝 FULL TRANSCRIPT",
        "─" * 60,
        to_str(result.get("transcript")),
        "",
        "═" * 60,
        f"  End of Report",
        "═" * 60,
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
defaults = {
    "ui_lang": "en",
    "theme_mode": "dark",
    "result": None,
    "rag_chain": None,
    "chat_history": [],
    "processed": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"### {t('sidebar_title')}")
    st.markdown("---")

    # ── Language toggle ──────────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">{t("language_label")}</div>', unsafe_allow_html=True)
    lang_choice = st.radio(
        t("language_label"),
        options=["en", "bn"],
        format_func=lambda x: "English" if x == "en" else "বাংলা",
        index=0 if st.session_state.ui_lang == "en" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if lang_choice != st.session_state.ui_lang:
        st.session_state.ui_lang = lang_choice
        st.rerun()

    st.markdown("")

    # ── Theme toggle ─────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">{t("theme_label")}</div>', unsafe_allow_html=True)
    theme_choice = st.radio(
        t("theme_label"),
        options=["dark", "light"],
        format_func=lambda x: t(x),
        index=0 if st.session_state.theme_mode == "dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if theme_choice != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_choice
        st.rerun()

    st.markdown("---")

    # ── About ────────────────────────────────────────────────────────────────
    st.markdown(f"#### {t('about_title')}")
    st.markdown(t("about_text"))

    st.markdown("---")

    # ── New session button ───────────────────────────────────────────────────
    if st.session_state.processed:
        if st.button(t("new_session"), use_container_width=True):
            for key in ["result", "rag_chain", "chat_history", "processed"]:
                st.session_state[key] = defaults[key]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# INJECT CSS (after sidebar sets theme)
# ═══════════════════════════════════════════════════════════════════════════════
inject_css()


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"""
    <div class="animate-in" style="margin-bottom: 0.5rem;">
        <div class="hero-title">{t("app_title")}</div>
        <div class="hero-subtitle">{t("app_subtitle")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SECTION  (only shown when no result yet)
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.processed:

    st.markdown(f'<div class="section-header">{t("input_section")}</div>', unsafe_allow_html=True)

    col_input, col_settings = st.columns([3, 1], gap="large")

    with col_input:
        input_method = st.radio(
            t("input_method"),
            options=["youtube", "upload"],
            format_func=lambda x: t("youtube_url") if x == "youtube" else t("file_upload"),
            horizontal=True,
            label_visibility="collapsed",
        )

        source = None

        if input_method == "youtube":
            url = st.text_input(
                t("youtube_url"),
                placeholder=t("youtube_placeholder"),
                label_visibility="collapsed",
            )
            if url:
                source = url.strip()
        else:
            uploaded_file = st.file_uploader(
                t("upload_prompt"),
                type=["mp3", "wav", "mp4", "mkv", "webm", "ogg", "flac", "m4a"],
                help=t("upload_help"),
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                # Save to temp file
                suffix = Path(uploaded_file.name).suffix
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="downloads")
                tmp.write(uploaded_file.read())
                tmp.close()
                source = tmp.name

    with col_settings:
        st.markdown(f'<div class="section-header">{t("transcription_lang")}</div>', unsafe_allow_html=True)
        trans_lang = st.radio(
            t("transcription_lang"),
            options=["english", "banglish"],
            format_func=lambda x: t("english") if x == "english" else t("banglish"),
            label_visibility="collapsed",
        )

    st.markdown("")

    # ── Process button ───────────────────────────────────────────────────────
    process_col1, process_col2, process_col3 = st.columns([1, 1, 1])
    with process_col2:
        process_clicked = st.button(t("process_btn"), use_container_width=True, type="primary")

    if process_clicked:
        if not source:
            st.warning(t("no_input_warning"))
        else:
            # ── Pipeline execution ───────────────────────────────────────────
            progress_bar = st.progress(0)
            status_text = st.empty()

            steps = [
                ("step_downloading", 0.05),
                ("step_transcribing", 0.20),
                ("step_title", 0.45),
                ("step_summary", 0.60),
                ("step_questions", 0.80),
                ("step_rag", 0.94),
            ]

            try:
                # Step 1 — Download / prepare
                status_text.markdown(f'<div class="status-badge pulse">⏳ {t("step_downloading")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[0][1])
                chunks = process_input(source)

                # Step 2 — Transcribe
                status_text.markdown(f'<div class="status-badge pulse">🎙️ {t("step_transcribing")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[1][1])
                transcript = transcribe_all(chunks, trans_lang)

                # Step 3 — Title
                status_text.markdown(f'<div class="status-badge pulse">📌 {t("step_title")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[2][1])
                title = generate_title(transcript)

                # Step 4 — Summary
                status_text.markdown(f'<div class="status-badge pulse">📋 {t("step_summary")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[3][1])
                summary_result = summarize(transcript)
                summary = summary_result.get("summary", "") if isinstance(summary_result, dict) else summary_result
                key_points = summary_result.get("key_points", []) if isinstance(summary_result, dict) else []

                # Step 5 — Questions
                status_text.markdown(f'<div class="status-badge pulse">❓ {t("step_questions")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[4][1])
                questions_result = extract_questions(transcript)

                # Step 6 — RAG
                status_text.markdown(f'<div class="status-badge pulse">🧠 {t("step_rag")}</div>', unsafe_allow_html=True)
                progress_bar.progress(steps[5][1])
                rag_chain = build_rag_chain(transcript)

                # Done!
                progress_bar.progress(1.0)
                status_text.markdown(f'<div class="status-badge">✅ {t("step_done")}</div>', unsafe_allow_html=True)

                # Store results
                st.session_state.result = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "key_points": key_points,
                    "open_questions": questions_result,
                }
                st.session_state.rag_chain = rag_chain
                st.session_state.processed = True
                st.session_state.chat_history = []

                time.sleep(0.8)
                st.rerun()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS SECTION
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.processed and st.session_state.result:
    result = st.session_state.result

    # ── Title display ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="result-card animate-in" style="text-align:center; margin-bottom: 1.5rem;">
            <div style="font-size: 0.72rem; font-weight:600; letter-spacing:0.06em;
                        text-transform:uppercase; opacity:0.5; margin-bottom:0.4rem;">
                {"শিরোনাম" if st.session_state.ui_lang == "bn" else "GENERATED TITLE"}
            </div>
            <div style="font-size:1.5rem; font-weight:800; letter-spacing:-0.02em;">
                {result['title']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick stats ──────────────────────────────────────────────────────────
    word_count = len(result["transcript"].split())
    char_count = len(result["transcript"])
    chunk_est = max(1, word_count // 500)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f'<div class="stat-card animate-in"><div class="stat-number">{word_count:,}</div>'
            f'<div class="stat-label">{"শব্দ" if st.session_state.ui_lang == "bn" else "Words"}</div></div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div class="stat-card animate-in"><div class="stat-number">{char_count:,}</div>'
            f'<div class="stat-label">{"অক্ষর" if st.session_state.ui_lang == "bn" else "Characters"}</div></div>',
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f'<div class="stat-card animate-in"><div class="stat-number">{chunk_est}</div>'
            f'<div class="stat-label">{"খণ্ড" if st.session_state.ui_lang == "bn" else "Chunks"}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        t("tab_summary"),
        t("tab_questions"),
        t("tab_transcript"),
        t("tab_chat"),
    ])

    # ── Tab: Summary ─────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(
            f'<div class="result-card animate-in">{result["summary"]}</div>',
            unsafe_allow_html=True,
        )

    # ── Tab: Open Questions ──────────────────────────────────────────────────
    with tabs[1]:
        st.markdown(
            f'<div class="result-card animate-in">{result["open_questions"]}</div>',
            unsafe_allow_html=True,
        )

    # ── Tab: Full Transcript ─────────────────────────────────────────────────
    with tabs[2]:
        with st.expander(
            f"{'সম্পূর্ণ ট্রান্সক্রিপ্ট দেখুন' if st.session_state.ui_lang == 'bn' else 'View full transcript'}",
            expanded=False,
        ):
            st.text(result["transcript"])

    # ── Tab: Chat ────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown(f"#### {t('chat_title')}")

        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input(t("chat_placeholder")):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑"):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner(t("chat_thinking")):
                    try:
                        answer = ask_question(st.session_state.rag_chain, prompt)
                    except Exception as e:
                        answer = f"❌ Error: {e}"
                st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f'<div class="section-header">{t("export_title")}</div>', unsafe_allow_html=True)

    export_text = build_export_text(result)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in result.get("title", "report"))

    exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 1])
    with exp_col2:
        st.download_button(
            label=t("export_txt"),
            data=export_text,
            file_name=f"{safe_title}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption(t("export_info"))


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="footer">{t("footer")}</div>', unsafe_allow_html=True)
