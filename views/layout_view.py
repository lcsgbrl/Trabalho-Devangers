
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

    with st.sidebar:

        # Cabeçalho original
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:10px; padding:4px 0 18px;
                        border-bottom:1px solid #2A2620; margin-bottom:14px;">
                <div style="width:38px;height:38px;border-radius:10px;background:#FAF9F6;
                            display:flex;align-items:center;justify-content:center;
                            color:{data.ROLE_COLORS['Administrador']['text']};
                            font-weight:800;font-size:0.75rem;">
                    SGA
                </div>
                <div>
                    <div style="font-size:0.8rem;font-weight:700;color:#FAF9F6;">
                        SGA
                    </div>
                    <div style="font-size:0.7rem;color:#776D5B;">
                        Gestão de Ambientes
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Alinhamento dos botões de navegação
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] .stButton > button {
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                text-align: left !important;
                height: 44px !important;
                min-height: 44px !important;
                padding: 0 12px !important;
            }

            [data-testid="stSidebar"] .stButton > button > div {
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                width: 100% !important;
                gap: 10px !important;
            }

            [data-testid="stSidebar"] .stButton > button p {
                text-align: left !important;
                margin: 0 !important;
                line-height: 1.2 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='font-size:0.68rem;color:#4A4540;letter-spacing:0.06em;'>NAVEGAÇÃO</div>",
            unsafe_allow_html=True,
        )

        visible = [
            item for item in NAV_ITEMS
            if user["role"] in item["roles"]
        ]

        current_route = session_controller.current_route()

        for item in visible:

            label = (
                item.get("label_aluno")
                if item["key"] == "reservas" and user["role"] == "Aluno"
                else item["label"]
            )

            is_active = current_route == item["key"]

            clicked = st.button(
                label,
                key=f"nav_{item['key']}",
                icon=item["icon"],
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )

            if clicked:
                session_controller.goto(item["key"])
                st.rerun()

        st.markdown(
            "<div style='margin-top:auto;'></div>",
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown("<hr style='border-color:#2A2620;'/>", unsafe_allow_html=True)

        # Identificação original do usuário
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <div style="width:30px;height:30px;border-radius:50%;background:{rc['text']};
                            display:flex;align-items:center;justify-content:center;color:white;
                            font-size:0.7rem;font-weight:700;flex-shrink:0;">
                    {user['initials']}
                </div>
                <div style="min-width:0;">
                    <div style="font-size:0.78rem;font-weight:600;color:#FAF9F6;
                                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
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

        if st.button("↩ Sair", use_container_width=True):
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