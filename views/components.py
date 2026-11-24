# -*- coding: utf-8 -*-
"""
[VIEW] Estilos CSS globais e componentes visuais reutilizáveis do SGA.

Puramente apresentação: nenhuma função aqui lê ou grava em st.session_state
nem contém regra de negócio.
"""

import streamlit as st

PRIMARY = "#8B0019"
PRIMARY_DARK = "#700010"
BG = "#FAF9F6"
SIDEBAR_BG = "#14120D"
SIDEBAR_BORDER = "#2A2620"
TEXT_DARK = "#1E1B15"
TEXT_MED = "#3D382E"
TEXT_MUTED = "#776D5B"
TEXT_FAINT = "#A8A09A"
BORDER = "#E7E0D5"
CARD_BG = "#FFFFFF"
SOFT_BG = "#F5F2EB"
DIVIDER = "#F3EFEA"


def inject_css():
    st.markdown(
        f"""
        <style>
        /* Força tema claro institucional mesmo com modo escuro ativado no navegador/SO */
        :root, html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"],
        header[data-testid="stHeader"] {{
            color-scheme: light !important;
            background-color: {BG} !important;
            color: {TEXT_DARK} !important;
        }}

        .stApp {{ background-color: {BG} !important; }}
        section[data-testid="stMain"] {{
            background-color: {BG} !important;
            color: {TEXT_DARK} !important;
            color-scheme: light !important;
        }}

        /* Textos, markdown, captions, métricas e abas na área principal */
        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] span,
        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] strong,
        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] em,
        section[data-testid="stMain"] h1,
        section[data-testid="stMain"] h2,
        section[data-testid="stMain"] h3,
        section[data-testid="stMain"] h4,
        section[data-testid="stMain"] h5,
        section[data-testid="stMain"] h6,
        section[data-testid="stMain"] [data-testid="stMetricValue"],
        section[data-testid="stMain"] [data-testid="stMetricLabel"],
        section[data-testid="stMain"] button[data-baseweb="tab"] {{
            color: {TEXT_DARK} !important;
        }}

        section[data-testid="stMain"] [data-testid="stCaptionContainer"],
        section[data-testid="stMain"] [data-testid="stCaptionContainer"] * {{
            color: {TEXT_MUTED} !important;
        }}

        /* Containers com borda e cards */
        section[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_BG} !important;
            border-color: {BORDER} !important;
        }}

        /* Dropdowns / Popovers / Menus abertos (fora da sidebar) */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        ul[data-baseweb="menu"],
        ul[data-baseweb="menu"] li {{
            background-color: {CARD_BG} !important;
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}

        section[data-testid="stMain"] label {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}
        section[data-testid="stMain"] input,
        section[data-testid="stMain"] textarea,
        section[data-testid="stMain"] select {{
            background-color: {CARD_BG} !important;
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
            caret-color: {TEXT_DARK} !important;
        }}
        section[data-testid="stMain"] input::placeholder,
        section[data-testid="stMain"] textarea::placeholder {{
            color: {TEXT_MUTED} !important;
            -webkit-text-fill-color: {TEXT_MUTED} !important;
            opacity: 1 !important;
        }}
        section[data-testid="stMain"] [data-baseweb="select"] > div,
        section[data-testid="stMain"] [data-baseweb="input"] > div {{
            background-color: {CARD_BG} !important;
            border-color: {BORDER} !important;
        }}
        section[data-testid="stMain"] [data-baseweb="select"] *,
        section[data-testid="stMain"] [data-baseweb="input"] * {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}
        section[data-testid="stMain"] button,
        section[data-testid="stMain"] button:not([kind="primary"]) * {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}
        section[data-testid="stMain"] button:not([kind="primary"]) {{
            background-color: {CARD_BG} !important;
            border-color: {BORDER} !important;
        }}
        section[data-testid="stMain"] button[kind="primary"],
        section[data-testid="stMain"] button[kind="primary"] * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }}

        /* Sidebar look (mantida escura institucional) */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
        }}
        section[data-testid="stSidebar"] * {{ color: #FAF9F6; }}
        section[data-testid="stSidebar"] .stButton button {{
            background-color: transparent;
            color: #C9C3B8;
            border: none;
            text-align: left;
            width: 100%;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            padding: 0.5rem 0.75rem;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background-color: rgba(255,255,255,0.06);
            color: #FAF9F6;
        }}
        section[data-testid="stSidebar"] .nav-active button {{
            background-color: {PRIMARY} !important;
            color: white !important;
        }}

        /* Generic card */
        .sga-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.25rem 1.4rem;
        }}
        .sga-eyebrow {{
            color: {PRIMARY} !important;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        .sga-title {{ color: {TEXT_DARK} !important; font-size: 1.5rem; font-weight: 800; margin: 0; }}
        .sga-subtitle {{ color: {TEXT_MUTED} !important; font-size: 0.85rem; margin-top: 4px; }}

        .badge {{
            display: inline-flex; align-items: center; gap: 6px;
            padding: 3px 10px; border-radius: 999px;
            font-size: 0.72rem; font-weight: 600;
        }}
        .badge-dot {{ width: 6px; height: 6px; border-radius: 50%; display: inline-block; }}

        div[data-testid="stMetric"] {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 16px;
            padding: 1rem 1.1rem;
        }}

        .stButton>button[kind="primary"] {{
            background-color: {PRIMARY} !important;
            border-color: {PRIMARY} !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        .stButton>button[kind="primary"] * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        .stButton>button[kind="primary"]:hover {{
            background-color: {PRIMARY_DARK} !important;
            border-color: {PRIMARY_DARK} !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        hr {{ border-color: {DIVIDER}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge_html(label: str, bg: str, color: str, dot: str | None = None) -> str:
    dot_html = f'<span class="badge-dot" style="background-color:{dot}"></span>' if dot else ""
    return (
        f'<span class="badge" style="background-color:{bg};color:{color}">'
        f'{dot_html}{label}</span>'
    )


def page_header(eyebrow: str, title: str, subtitle: str = ""):
    st.markdown(f'<div class="sga-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sga-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sga-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.write("")


def card_open():
    st.markdown('<div class="sga-card">', unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def toast_ok(msg: str):
    st.toast(msg, icon="✅")


def toast_err(msg: str):
    st.toast(msg, icon="⚠️")