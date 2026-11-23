
# -*- coding: utf-8 -*-
"""[VIEW] Layout compartilhado — sidebar de navegação e tela de acesso negado."""

import streamlit as st

from controllers import auth_controller, session_controller
from models import domain_data as data


NAV_ITEMS = [
    {
        "key": "dashboard",
        "label": "Dashboard",
        "icon": ":material/dashboard:",
        "roles": ["Professor", "Coordenador", "Administrador"],
    },
    {
        "key": "reservas",
        "label": "Reservas",
        "icon": ":material/calendar_month:",
        "roles": ["Aluno", "Professor", "Coordenador", "Administrador"],
        "label_aluno": "Minhas Solicitações",
    },
    {
        "key": "academico",
        "label": "Estrutura Acadêmica",
        "icon": ":material/school:",
        "roles": ["Administrador", "Coordenador"],
    },
    {
        "key": "membros",
        "label": "Organização de Membros",
        "icon": ":material/group:",
        "roles": ["Administrador"],
    },
    {
        "key": "configuracoes",
        "label": "Configurações",
        "icon": ":material/settings:",
        "roles": ["Aluno", "Professor", "Coordenador", "Administrador"],
    },
]



def render_sidebar():
    user = auth_controller.current_user()
    rc = data.ROLE_COLORS[user["role"]]

    if "menu_recolhido" not in st.session_state:
        st.session_state.menu_recolhido = False

    recolhido = st.session_state.menu_recolhido
    largura = "78px" if recolhido else "260px"

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            width: {largura} !important;
            min-width: {largura} !important;
            max-width: {largura} !important;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            width: {largura} !important;
        }}

        [data-testid="stSidebarCollapseButton"],
        [data-testid="stExpandSidebarButton"] {{
            display: none !important;
        }}

        /* Estilo geral dos botões */
        [data-testid="stSidebar"] .stButton > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if recolhido else "flex-start"} !important;
            text-align: {"center" if recolhido else "left"} !important;
            height: 44px !important;
            min-height: 44px !important;
            padding: 0 12px !important;
        }}

        [data-testid="stSidebar"] .stButton > button > div {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if recolhido else "flex-start"} !important;
            width: 100% !important;
            gap: 10px !important;
        }}

        [data-testid="stSidebar"] .stButton > button p {{
            margin: 0 !important;
            text-align: inherit !important;
            line-height: 1.2 !important;
        }}

        /* Alinhamento exclusivo do botão hambúrguer */
        [data-testid="stSidebar"] .st-key-sidebar_toggle_container
        .stButton > button {{
            justify-content: flex-start !important;
            text-align: left !important;
            padding-left: 12px !important;
        }}

        [data-testid="stSidebar"] .st-key-sidebar_toggle_container
        .stButton > button > div {{
            justify-content: flex-start !important;
            width: 100% !important;
        }}

        @media (max-width: 768px) {{
            [data-testid="stSidebar"] {{
                position: fixed !important;
                left: 0 !important;
                top: 0 !important;
                height: 100vh !important;
                height: 100dvh !important;
                z-index: 999 !important;
                transform: none !important;
                visibility: visible !important;
            }}

            [data-testid="stMain"] {{
                margin-left: 78px !important;
                width: calc(100% - 78px) !important;
                min-width: 0 !important;
            }}

            [data-testid="stMainBlockContainer"] {{
                padding-left: 12px !important;
                padding-right: 12px !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:

        # LOGOTIPO
        if recolhido:
            st.markdown(
                """
                <div style="display:flex;justify-content:center;
                            padding:8px 0 16px;">
                    <div style="width:38px;height:38px;border-radius:10px;
                                background:#FAF9F6;display:flex;
                                align-items:center;justify-content:center;
                                color:#A00025;font-weight:800;
                                font-size:0.75rem;">
                        SGA
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:10px;
                            padding:4px 0 16px;">
                    <div style="width:38px;height:38px;border-radius:10px;
                                background:#FAF9F6;display:flex;
                                align-items:center;justify-content:center;
                                color:#A00025;font-weight:800;
                                font-size:0.75rem;">
                        SGA
                    </div>
                    <div>
                        <div style="font-size:0.8rem;font-weight:700;
                                    color:#FAF9F6;">SGA</div>
                        <div style="font-size:0.7rem;color:#776D5B;">
                            Gestão de Ambientes
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # BOTÃO HAMBÚRGUER
        with st.container(key="sidebar_toggle_container"):
            if st.button(
                " ",
                icon=":material/menu:",
                key="toggle_sidebar",
                help="Expandir menu" if recolhido else "Recolher menu",
                use_container_width=True,
            ):
                st.session_state.menu_recolhido = not recolhido
                st.rerun()

        # TÍTULO DA NAVEGAÇÃO
        if not recolhido:
            st.markdown(
                "<div style='font-size:0.68rem;color:#4A4540;"
                "letter-spacing:0.06em;'>NAVEGAÇÃO</div>",
                unsafe_allow_html=True,
            )

        # ITENS DO MENU
        visible = [
            item for item in NAV_ITEMS
            if user["role"] in item["roles"]
        ]

        current_route = session_controller.current_route()

        for item in visible:
            label = (
                item.get("label_aluno")
                if item["key"] == "reservas"
                and user["role"] == "Aluno"
                else item["label"]
            )

            is_active = current_route == item["key"]

            clicked = st.button(
                " " if recolhido else label,
                key=f"nav_{item['key']}",
                icon=item["icon"],
                help=label if recolhido else None,
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )

            if clicked:
                session_controller.goto(item["key"])
                st.session_state.menu_recolhido = True
                st.rerun()

        st.write("")

        st.markdown(
            "<hr style='border-color:#2A2620;'/>",
            unsafe_allow_html=True,
        )

        # IDENTIFICAÇÃO DO USUÁRIO
        initials = user.get("initials") or "".join(
            parte[0].upper()
            for parte in (
                user.get("name") or user.get("nome") or "Usuário"
            ).split()[:2]
        )

        if recolhido:
            st.markdown(
                f"""
                <div style="display:flex;justify-content:center;
                            padding:8px 0;">
                    <div style="width:30px;height:30px;border-radius:50%;
                                background:{rc['text']};display:flex;
                                align-items:center;justify-content:center;
                                color:white;font-size:0.7rem;font-weight:700;">
                        {initials}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:8px;
                            margin-bottom:8px;">
                    <div style="width:30px;height:30px;border-radius:50%;
                                background:{rc['text']};display:flex;
                                align-items:center;justify-content:center;
                                color:white;font-size:0.7rem;font-weight:700;
                                flex-shrink:0;">
                        {initials}
                    </div>
                    <div style="min-width:0;">
                        <div style="font-size:0.78rem;font-weight:600;
                                    color:#FAF9F6;white-space:nowrap;
                                    overflow:hidden;text-overflow:ellipsis;">
                            {user['nome']}
                        </div>
                        <div style="font-size:0.7rem;color:#776D5B;">
                            {user['role']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # BOTÃO SAIR
        if st.button(
            " " if recolhido else "Sair",
            icon=":material/logout:",
            key="logout_sidebar",
            help="Sair" if recolhido else None,
            use_container_width=True,
        ):
            auth_controller.logout()
            st.rerun()

def render_unauthorized():
    user = auth_controller.current_user()

    st.markdown(
        f"""
        <div style="text-align:center; padding:4rem 0;">
            <h1 style="color:#1E1B15;">
                🔒 Acesso não autorizado
            </h1>
            <p style="color:#776D5B;">
                Você não tem permissão para acessar esta página com o perfil de
                <strong>{user['role']}</strong>.
                Entre em contato com o administrador caso precise de acesso.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1])

    with c2:
        if st.button(
            "Ir ao Menu",
            type="primary",
            use_container_width=True,
        ):
            session_controller.goto("menu")
            st.rerun()
