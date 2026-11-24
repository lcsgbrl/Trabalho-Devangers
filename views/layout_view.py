# -*- coding: utf-8 -*-
"""[VIEW] Layout compartilhado — sidebar de navegação, notificações e tela de acesso negado."""

import streamlit as st

from controllers import auth_controller, session_controller
from models import domain_data as data, notificacao_model


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


def _abrir_destino_notificacao(notif: dict) -> None:
    """Marca a notificação como lida e navega direto para a rota/aba correspondente."""
    if not notif.get("lida") and notif.get("id"):
        notificacao_model.marcar_como_lida(notif["id"])

    rota = notif.get("rota") or "reservas"
    aba = notif.get("aba") or "minhas"

    if rota == "reservas":
        st.session_state.reservas_tab_destino = aba

    st.session_state.menu_recolhido = True
    session_controller.goto(rota)
    st.rerun()


def render_sidebar():
    user = auth_controller.current_user()
    rc = data.ROLE_COLORS[user["role"]]

    if "menu_recolhido" not in st.session_state:
        st.session_state.menu_recolhido = False

    recolhido = st.session_state.menu_recolhido
    largura = "78px" if recolhido else "285px"

    uid = st.session_state.get("user_uid")
    if not st.session_state.get("lembretes_verificados"):
        notificacao_model.verificar_lembretes_proximos(
            st.session_state.get("solicitacoes", []),
            uid,
            user.get("nome", ""),
        )
        st.session_state.lembretes_verificados = True

    notifs = notificacao_model.listar_minhas_notificacoes(uid, user.get("nome", ""))
    nao_lidas = [n for n in notifs if not n.get("lida")]
    qtd_nao_lidas = len(nao_lidas)

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

        /* Estilo geral dos botões e do trigger do popover na sidebar (sem fundo branco) */
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] [data-testid="stPopoverButton"],
        [data-testid="stSidebar"] [data-testid="stPopover"] button {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if recolhido else "flex-start"} !important;
            text-align: {"center" if recolhido else "left"} !important;
            min-height: 44px !important;
            padding: {"6px 8px" if recolhido else "0 12px"} !important;
            width: 100% !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            color: #FAF9F6 !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] [data-testid="stPopoverButton"]:hover,
        [data-testid="stSidebar"] [data-testid="stPopover"] button:hover {{
            background-color: rgba(255, 255, 255, 0.06) !important;
            color: #FAF9F6 !important;
        }}

        [data-testid="stSidebar"] .stButton > button > div,
        [data-testid="stSidebar"] [data-testid="stPopoverButton"] > div,
        [data-testid="stSidebar"] [data-testid="stPopover"] button > div {{
            display: flex !important;
            align-items: center !important;
            justify-content: {"center" if recolhido else "flex-start"} !important;
            width: 100% !important;
            gap: {"4px" if recolhido else "10px"} !important;
        }}

        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] [data-testid="stPopoverButton"] p,
        [data-testid="stSidebar"] [data-testid="stPopover"] button p {{
            margin: 0 !important;
            text-align: inherit !important;
            line-height: 1.2 !important;
            color: #FAF9F6 !important;
        }}

        /* Destaque sutil no sininho quando houver notificações não lidas */
        [data-testid="stSidebar"] .st-key-notif_trigger_container [data-testid="stPopoverButton"],
        [data-testid="stSidebar"] .st-key-notif_trigger_container [data-testid="stPopover"] button {{
            background-color: {"rgba(139, 0, 25, 0.25)" if qtd_nao_lidas else "transparent"} !important;
            border: 1px solid {"#8B0019" if qtd_nao_lidas else "transparent"} !important;
            color: #FAF9F6 !important;
        }}

        /* Estilo do popup flutuante de notificações */
        [data-testid="stPopoverBody"] {{
            background-color: #14120D !important;
            border: 1px solid #2A2620 !important;
            border-radius: 14px !important;
            color: #FAF9F6 !important;
            min-width: 340px !important;
            max-width: 380px !important;
            max-height: 460px !important;
            overflow-y: auto !important;
        }}

        [data-testid="stPopoverBody"] * {{
            color: #FAF9F6 !important;
            -webkit-text-fill-color: #FAF9F6 !important;
        }}

        [data-testid="stPopoverBody"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #1E1B15 !important;
            border: 1px solid #2A2620 !important;
            border-radius: 10px !important;
            padding: 6px !important;
        }}

        [data-testid="stPopoverBody"] .stButton > button {{
            height: 32px !important;
            min-height: 32px !important;
            font-size: 0.76rem !important;
            justify-content: center !important;
            background-color: #2A2620 !important;
            color: #FAF9F6 !important;
            border: 1px solid #3D382E !important;
            border-radius: 8px !important;
            padding: 0 10px !important;
        }}

        [data-testid="stPopoverBody"] .stButton > button:hover {{
            background-color: #8B0019 !important;
            border-color: #8B0019 !important;
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

        # POPUP DO SININHO (Recolhido: ícone + setinha; Expandido: ícone + texto; ao clicar abre popup flutuante)
        bell_icon = (
            ":material/notifications_active:"
            if qtd_nao_lidas
            else ":material/notifications:"
        )
        bell_label = (
            ""
            if recolhido
            else (
                f"Notificações ({qtd_nao_lidas})"
                if qtd_nao_lidas
                else "Notificações"
            )
        )
        bell_help = (
            f"Notificações ({qtd_nao_lidas} não lidas)"
            if qtd_nao_lidas
            else "Notificações"
        )

        with st.container(key="notif_trigger_container"):
            with st.popover(
                bell_label,
                icon=bell_icon,
                help=bell_help,
                use_container_width=True,
            ):
                st.markdown(
                    f"<div style='font-size:0.9rem;font-weight:700;margin-bottom:8px;'>"
                    f"🔔 Notificações ({qtd_nao_lidas} não lida(s))</div>",
                    unsafe_allow_html=True,
                )

                if qtd_nao_lidas:
                    if st.button(
                        "✓ Marcar todas como lidas",
                        key="ler_todas_notifs",
                        use_container_width=True,
                    ):
                        notificacao_model.marcar_todas_como_lidas(
                            [n["id"] for n in nao_lidas]
                        )
                        st.rerun()

                if not notifs:
                    st.caption("Nenhuma notificação no momento.")
                else:
                    for n in notifs[:8]:
                        with st.container(border=True):
                            marcador = "🔴 " if not n.get("lida") else ""
                            st.markdown(
                                f"<div style='font-size:0.8rem;font-weight:700;color:#FAF9F6;margin-bottom:2px;'>"
                                f"{marcador}{n['titulo']}</div>"
                                f"<div style='font-size:0.74rem;color:#C9C3B8;line-height:1.35;margin-bottom:4px;'>"
                                f"{n['mensagem']}</div>"
                                f"<div style='font-size:0.66rem;color:#776D5B;margin-bottom:6px;'>"
                                f"🕒 {n.get('createdAt', '')}</div>",
                                unsafe_allow_html=True,
                            )

                            if not n.get("lida"):
                                b_ir, b_ok = st.columns(2)
                                if b_ir.button(
                                    "Ir até lá →",
                                    key=f"go_notif_{n['id']}",
                                    use_container_width=True,
                                ):
                                    _abrir_destino_notificacao(n)
                                if b_ok.button(
                                    "✓ Lida",
                                    key=f"lida_{n['id']}",
                                    use_container_width=True,
                                ):
                                    notificacao_model.marcar_como_lida(n["id"])
                                    st.rerun()
                            else:
                                if st.button(
                                    "Ir até lá →",
                                    key=f"go_notif_{n['id']}",
                                    use_container_width=True,
                                ):
                                    _abrir_destino_notificacao(n)

        # TÍTULO DA NAVEGAÇÃO
        if not recolhido:
            st.markdown(
                "<div style='font-size:0.68rem;color:#4A4540;"
                "letter-spacing:0.06em;margin-top:8px;'>NAVEGAÇÃO</div>",
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