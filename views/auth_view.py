# -*- coding: utf-8 -*-
"""Tela unificada de autenticação do SGA."""

import streamlit as st

from controllers import auth_controller
from views.components import BORDER, PRIMARY, TEXT_DARK, TEXT_MUTED


def _inject_auth_css():
    """Define os estilos locais da tela sem alterar o tema das páginas internas."""
    st.markdown(
        f"""
        <style>
        .block-container {{
            max-width: none !important;
            padding: 0 !important;
        }}

        /* Fundo contínuo na proporção exata das colunas [1, 1.03] em telas desktop */
        @media (min-width: 801px) {{
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main,
            section[data-testid="stMain"] {{
                background: linear-gradient(
                    90deg,
                    #6B0014 0%,
                    {PRIMARY} 49.26%,
                    #FAF9F6 49.26%,
                    #FAF9F6 100%
                ) !important;
            }}

            /* Camada fixa na metade esquerda: mantém o gradiente, brilhos e detalhes geométricos contínuos mesmo ao rolar */
            section[data-testid="stMain"]::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 49.26%;
                height: 100vh;
                pointer-events: none;
                z-index: 0;
                background:
                    radial-gradient(circle at 86% 16%, rgba(255, 225, 230, 0.16) 0%, rgba(255, 225, 230, 0) 36%),
                    radial-gradient(circle at 14% 86%, rgba(42, 0, 8, 0.48) 0%, rgba(42, 0, 8, 0) 46%),
                    radial-gradient(circle at 75% 78%, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0) 32%),
                    radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                    linear-gradient(155deg, #A3001F 0%, {PRIMARY} 52%, #5C0011 100%);
                background-size: auto, auto, auto, 24px 24px, auto;
            }}
        }}

        @media (max-width: 800px) {{
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > .main,
            section[data-testid="stMain"] {{
                background: #FAF9F6 !important;
            }}
        }}

        .auth-panel-marker {{ display: block; color-scheme: light; }}

        /* Estica o bloco horizontal e ambas as colunas */
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) {{
            align-items: stretch !important;
            min-height: 100vh !important;
            gap: 0 !important;
            position: relative;
            z-index: 1;
        }}

        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="stColumn"]:first-child,
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="column"]:first-child {{
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            background: transparent !important;
        }}

        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="stColumn"]:first-child > div,
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="column"]:first-child > div,
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="column"]:first-child [data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="stColumn"]:first-child [data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.auth-panel-marker) > div[data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] {{
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
        }}

        div[data-testid="stColumn"]:has(.auth-panel-marker),
        div[data-testid="column"]:has(.auth-panel-marker) {{
            background-color: #FAF9F6 !important;
            color: {TEXT_DARK};
            color-scheme: light;
            padding: 3.2rem clamp(2rem, 6.5vw, 6.5rem) 3.5rem !important;
            box-sizing: border-box;
        }}

        /* Conteúdo e detalhes geométricos da marca na esquerda */
        .auth-brand {{
            flex: 1 1 auto;
            width: 100%;
            height: 100%;
            min-height: 100vh;
            box-sizing: border-box;
            padding: 3.4rem 3.5rem;
            background: transparent;
            color: #FFFFFF;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}

        /* Anéis decorativos em camadas (acompanham a coluna inteira) */
        .auth-brand::before {{
            content: "";
            position: absolute;
            width: 360px;
            height: 360px;
            left: -120px;
            top: 26%;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: radial-gradient(circle, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0) 70%);
            pointer-events: none;
        }}
        .auth-brand::after {{
            content: "";
            position: absolute;
            width: 300px;
            height: 300px;
            right: -70px;
            bottom: 42px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: 0 0 0 36px rgba(255, 255, 255, 0.03);
            background: radial-gradient(circle, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0) 72%);
            pointer-events: none;
        }}

        .auth-brand-mark {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 800;
            font-size: 1rem;
        }}
        .auth-brand-icon {{
            width: 80px;
            height: 80px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #FFFFFF;
            color: {PRIMARY};
            border-radius: 14px;
            font-weight: 900;
            font-size: 1.35rem;
            box-shadow: 0 10px 24px rgba(35, 0, 7, 0.28);
        }}
        .auth-brand-copy {{
            position: relative;
            z-index: 1;
            max-width: 530px;
            padding-bottom: 1rem;
        }}
        .auth-kicker {{
            display: inline-flex;
            align-items: center;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #FFFFFF;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
        }}
        .auth-brand h1 {{
            color: #FFFFFF;
            font-size: clamp(2.25rem, 4vw, 3.25rem);
            line-height: 1.08;
            margin: 0 0 1.1rem;
        }}
        .auth-brand p {{
            color: rgba(255, 255, 255, 0.92);
            font-size: 1rem;
            line-height: 1.6;
            margin: 0;
            max-width: 440px;
        }}

        .auth-label {{
            color: {TEXT_MUTED};
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }}
        .auth-card-title {{
            color: {TEXT_DARK};
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0;
        }}
        .auth-card-subtitle {{
            color: {TEXT_MUTED};
            font-size: 0.9rem;
            margin: 0.25rem 0 1.5rem;
        }}
        .first-access {{
            margin: 2.2rem 0 0.5rem;
            padding-top: 1.4rem;
            border-top: 1px solid {BORDER};
        }}
        .first-access p {{
            color: {TEXT_MUTED};
            font-size: 0.82rem;
            margin: 0 0 0.7rem;
        }}

        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input {{
            background: #F5F2EB;
            border-color: {BORDER};
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input:focus,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input:focus {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
            caret-color: {TEXT_DARK} !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input::placeholder {{
            color: {TEXT_MUTED} !important;
            -webkit-text-fill-color: {TEXT_MUTED} !important;
            opacity: 1 !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] label,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stTextInput"] label *,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stSelectbox"] label,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stSelectbox"] label *,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stMultiSelect"] label,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stMultiSelect"] label *,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stCheckbox"] label,
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stCheckbox"] label * {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) [data-baseweb="select"] > div,
        div[data-testid="column"]:has(.auth-panel-marker) [data-baseweb="select"] > div {{
            background-color: #F5F2EB !important;
            border-color: {BORDER} !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) .stButton button[kind="primary"],
        div[data-testid="stColumn"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) .stButton button[kind="primary"] *,
        div[data-testid="stColumn"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) div[data-testid="stForm"] {{
            border: 0;
            padding: 0;
        }}
        div[data-testid="stColumn"]:has(.auth-panel-marker) .stButton button,
        div[data-testid="column"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button {{
            min-height: 2.6rem;
        }}

        @media (max-width: 800px) {{
            .auth-brand {{
                min-height: auto;
                padding: 2rem 1.5rem 3rem;
                gap: 5rem;
                background:
                    radial-gradient(circle at 86% 16%, rgba(255, 225, 230, 0.16) 0%, rgba(255, 225, 230, 0) 36%),
                    radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                    linear-gradient(155deg, #A3001F 0%, {PRIMARY} 52%, #5C0011 100%);
                background-size: auto, 24px 24px, auto;
            }}
            .auth-brand h1 {{ font-size: 2.2rem; }}
            div[data-testid="stColumn"]:has(.auth-panel-marker),
            div[data-testid="column"]:has(.auth-panel-marker) {{
                padding: 2.5rem 1.25rem 3rem !important;
            }}
        }}
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stCheckbox"] label {{
            color: {TEXT_DARK} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand():
    st.markdown(
        """
        <div class="auth-brand">
            <div class="auth-brand-mark">
                <span class="auth-brand-icon">SGA</span>
                <span>SGA</span>
            </div>
            <div class="auth-brand-copy">
                <div class="auth-kicker">&#8226;&nbsp; Sistema Institucional</div>
                <h1>Sistema de Gestão<br>de Ambientes</h1>
                <p>Plataforma integrada para gerenciamento de reservas, controle de ambientes e organização de membros da instituição.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login():
    st.markdown('<div class="auth-label">Acesso à conta</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-card-title">Bem-vindo de volta</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-card-subtitle">Acesse sua conta para continuar.</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="Sua senha")
        st.checkbox("Lembrar de mim")
        submitted = st.form_submit_button("Entrar", type="primary", width="stretch")

    if submitted:
        if not email.strip() or not senha:
            st.error("Preencha o e-mail e a senha.")
        else:
            with st.spinner("Verificando..."):
                sucesso, mensagem = auth_controller.fazer_login(email.strip(), senha)
                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)


def _render_first_access_form():
    st.markdown('<div class="auth-label">Ativação institucional</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-card-title">Primeiro Acesso</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-card-subtitle">Informe seu nome e e-mail do pré-cadastro para identificar seu perfil e ativar sua conta.</div>',
        unsafe_allow_html=True,
    )

    nome = st.text_input("Nome completo", key="fa_nome", placeholder="Ex.: Mirela Silva")
    col_email, col_btn = st.columns([3, 1.2])
    with col_email:
        email = st.text_input("E-mail institucional", key="fa_email", placeholder="seu@email.com")
    with col_btn:
        st.markdown("<div style='height: 1.72rem;'></div>", unsafe_allow_html=True)
        buscar_clicked = st.button("Verificar perfil", key="fa_verificar_btn", width="stretch")

    email_normalizado = (email or "").strip().lower()
    if buscar_clicked or (email_normalizado and st.session_state.get("fa_email_consultado") != email_normalizado):
        if email_normalizado:
            info_perfil = auth_controller.consultar_perfil_primeiro_acesso(nome, email_normalizado)
            st.session_state["fa_perfil_info"] = info_perfil
            st.session_state["fa_email_consultado"] = email_normalizado
            if info_perfil.get("encontrado"):
                acad_data = auth_controller.carregar_academico_primeiro_acesso(
                    info_perfil.get("instituicao_id")
                )
                st.session_state["fa_acad_data"] = acad_data
        else:
            st.session_state["fa_perfil_info"] = None

    info_perfil = st.session_state.get("fa_perfil_info")
    role_norm = info_perfil.get("role_normalizado") if info_perfil and info_perfil.get("encontrado") else None

    if info_perfil:
        if info_perfil.get("encontrado"):
            st.info(info_perfil.get("mensagem"))
        else:
            st.warning(info_perfil.get("mensagem"))

    col1, col2 = st.columns(2)
    with col1:
        senha_temp = st.text_input(
            "Senha temporária",
            type="password",
            key="fa_senha_temp",
            placeholder="Recebida por e-mail",
        )
    with col2:
        nova_senha = st.text_input(
            "Nova senha definitiva",
            type="password",
            key="fa_nova_senha",
            placeholder="Mínimo 6 caracteres",
        )
        st.caption(
            "⚠ Dica para criar uma senha mais segura: combine letras maiúsculas, "
            "letras minúsculas, números e caracteres especiais."
        )

    confirmar_senha = st.text_input(
        "Confirmar nova senha",
        type="password",
        key="fa_confirmar_senha",
        placeholder="Repita a nova senha",
    )

    cursos_ids_selecionados: list[int] = []
    turma_id_selecionada: int | None = None
    disciplinas_ids_selecionadas: list[int] = []

    acad_data = st.session_state.get("fa_acad_data") or {}
    cursos_ativos = [c for c in acad_data.get("cursos", []) if c.get("ativo", True)]
    turmas_ativas = [t for t in acad_data.get("turmas", []) if t.get("ativo", True)]
    disciplinas_lista = acad_data.get("disciplinas", [])

    if role_norm == "professor":
        st.markdown("**Vínculo acadêmico do professor**")
        st.caption("As disciplinas serão atribuídas posteriormente pelo coordenador.")
        if not cursos_ativos:
            st.warning("Nenhum curso ativo encontrado para esta instituição.")
        else:
            cursos_ids_selecionados = st.multiselect(
                "Cursos (selecione um ou mais)",
                options=[c["id"] for c in cursos_ativos],
                format_func=lambda cid: next((c["nome"] for c in cursos_ativos if c["id"] == cid), str(cid)),
                key="fa_prof_cursos",
                placeholder="Escolha os cursos...",
            )

    elif role_norm == "aluno":
        st.markdown("**Vínculo acadêmico do aluno**")
        if not cursos_ativos:
            st.warning("Nenhum curso ativo encontrado para esta instituição.")
        else:
            curso_id_escolhido = st.selectbox(
                "Curso",
                options=[c["id"] for c in cursos_ativos],
                format_func=lambda cid: next((c["nome"] for c in cursos_ativos if c["id"] == cid), str(cid)),
                key="fa_aluno_curso",
            )
            cursos_ids_selecionados = [curso_id_escolhido] if curso_id_escolhido is not None else []

            curso_obj = next((c for c in cursos_ativos if c["id"] == curso_id_escolhido), None)
            turmas_do_curso = [t for t in turmas_ativas if t.get("cursoId") == curso_id_escolhido]

            if not turmas_do_curso:
                st.warning("Nenhuma turma ativa vinculada a este curso.")
            else:
                turma_id_selecionada = st.selectbox(
                    "Turma",
                    options=[t["id"] for t in turmas_do_curso],
                    format_func=lambda tid: next(
                        (f"{t['nome']} ({t['turno']})" if t.get("turno") else t["nome"] for t in turmas_do_curso if t["id"] == tid),
                        str(tid),
                    ),
                    key="fa_aluno_turma",
                )

                discs_da_turma = [
                    d for d in disciplinas_lista if turma_id_selecionada in (d.get("turmasIds") or [])
                ]
                if not discs_da_turma:
                    nucleo_ref = (
                        next((t.get("nucleoId") for t in turmas_do_curso if t["id"] == turma_id_selecionada), None)
                        or (curso_obj.get("nucleoId") if curso_obj else None)
                    )
                    if nucleo_ref is not None:
                        discs_da_turma = [d for d in disciplinas_lista if d.get("nucleoId") == nucleo_ref]
                    else:
                        discs_da_turma = disciplinas_lista

                if not discs_da_turma:
                    st.warning("Nenhuma disciplina disponível para esta turma.")
                else:
                    disciplinas_ids_selecionadas = st.multiselect(
                        "Disciplinas / Matérias (selecione uma ou mais)",
                        options=[d["id"] for d in discs_da_turma],
                        format_func=lambda did: next(
                            (f"{d['codigo']} — {d['nome']}" if d.get("codigo") else d["nome"] for d in discs_da_turma if d["id"] == did),
                            str(did),
                        ),
                        key="fa_aluno_disciplinas",
                        placeholder="Escolha as disciplinas...",
                    )

    submitted = st.button(
        "Concluir primeiro acesso",
        type="primary",
        key="fa_submit_btn",
        width="stretch",
    )

    if submitted:
        if not all([(nome or "").strip(), email_normalizado, senha_temp, nova_senha]):
            st.error("Preencha nome, e-mail, senha temporária e nova senha.")
        elif not info_perfil or not info_perfil.get("encontrado"):
            st.error("Não foi possível validar o seu pré-cadastro. Verifique seu e-mail.")
        elif nova_senha != confirmar_senha:
            st.error("A nova senha e a confirmação não conferem.")
        elif role_norm == "professor" and not cursos_ids_selecionados:
            st.error("Selecione pelo menos um curso.")
        elif role_norm == "aluno" and (
            not cursos_ids_selecionados or turma_id_selecionada is None or not disciplinas_ids_selecionadas
        ):
            st.error("Selecione curso, turma e pelo menos uma disciplina.")
        else:
            with st.spinner("Validando pré-cadastro..."):
                sucesso, mensagem = auth_controller.concluir_primeiro_acesso(
                    nome=nome,
                    email=email_normalizado,
                    senha_temporaria=senha_temp,
                    nova_senha=nova_senha,
                    cursos_ids=cursos_ids_selecionados,
                    turma_id=turma_id_selecionada,
                    disciplinas_ids=disciplinas_ids_selecionadas,
                )
            if sucesso:
                st.success(mensagem)
                st.session_state.pop("fa_perfil_info", None)
                st.session_state.pop("fa_email_consultado", None)
                st.session_state.pop("fa_acad_data", None)
                st.session_state.auth_tab = "login"
                st.rerun()
            else:
                st.error(mensagem)

    if st.button("Voltar ao login", key="fa_voltar_btn", width="stretch"):
        st.session_state.pop("fa_perfil_info", None)
        st.session_state.pop("fa_email_consultado", None)
        st.session_state.pop("fa_acad_data", None)
        st.session_state.auth_tab = "login"
        st.rerun()


def _render_first_access():
    st.markdown(
        '<div class="first-access"><div class="auth-label">Primeiro acesso</div>'
        '<p>Recebeu um pré-cadastro da sua instituição com senha temporária?</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Primeiro Acesso", type="primary", width="stretch"):
        st.session_state.auth_tab = "primeiro_acesso"
        st.rerun()


def render():
    """Renderiza a tela única de login e primeiro acesso."""
    _inject_auth_css()

    left, right = st.columns([1, 1.03], gap="small")
    with left:
        _render_brand()

    with right:
        st.markdown('<span class="auth-panel-marker"></span>', unsafe_allow_html=True)
        tab = st.session_state.get("auth_tab", "login")
        if tab == "primeiro_acesso":
            _render_first_access_form()
        else:
            _render_login()
            _render_first_access()


def render_user_menu():
    """Renderiza o menu do usuário logado na barra lateral."""
    if not auth_controller.is_logged_in():
        return

    info = auth_controller.obter_info_usuario()
    st.markdown("---")
    st.subheader(info.get("nome") or "Usuário")
    st.caption(info.get("email") or "")
    st.caption(f"Papel: **{(info.get('role') or 'usuario').upper()}**")

    if st.button("Perfil", width="stretch"):
        st.session_state.route = "perfil"
        st.rerun()
    if st.button("Sair", width="stretch"):
        auth_controller.fazer_logout()
        st.session_state.route = "login"
        st.rerun()