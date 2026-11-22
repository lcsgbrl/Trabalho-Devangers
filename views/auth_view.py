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
        .block-container {{ max-width: none !important; padding: 0 !important; }}
        [data-testid="stAppViewContainer"] > .main {{ background: #FAF9F6; }}
        .auth-panel-marker {{ display: block; color-scheme: light; }}
        div[data-testid="column"]:has(.auth-panel-marker) {{ color: {TEXT_DARK}; color-scheme: light; }}
        .auth-layout {{ min-height: 100vh; }}
        .auth-brand {{
            min-height: 100vh; box-sizing: border-box; padding: 3.4rem 3.5rem;
            background: {PRIMARY}; color: #FFFFFF; display: flex;
            flex-direction: column; justify-content: space-between; position: relative;
            overflow: hidden;
        }}
        .auth-brand::after {{
            content: ""; position: absolute; width: 260px; height: 260px;
            right: -55px; bottom: 60px; border-radius: 50%;
            background: rgba(255,255,255,0.05);
        }}
        .auth-brand-mark {{ display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 1rem; }}
        .auth-brand-icon {{
            width: 80px; height: 80px; display: inline-flex; align-items: center;
            justify-content: center; background: #FFFFFF; color: {PRIMARY};
            border-radius: 12px; font-weight: 900; font-size: 1.35rem;
        }}
        .auth-brand-copy {{ position: relative; z-index: 1; max-width: 530px; padding-bottom: 1rem; }}
        .auth-kicker {{
            display: inline-flex; padding: 0.45rem 0.8rem; border-radius: 999px;
            background: rgba(255,255,255,0.12); color: #FFFFFF; font-size: 0.72rem;
            font-weight: 700; margin-bottom: 1.5rem;
        }}
        .auth-brand h1 {{ color: #FFFFFF; font-size: clamp(2.25rem, 4vw, 3.25rem); line-height: 1.08; margin: 0 0 1.1rem; }}
        .auth-brand p {{ color: rgba(255,255,255,0.9); font-size: 1rem; line-height: 1.6; margin: 0; max-width: 440px; }}
        div[data-testid="column"]:has(.auth-panel-marker) {{
            padding: 3.5rem clamp(2rem, 8vw, 8rem) 4rem; box-sizing: border-box;
        }}
        .auth-label {{
            color: {TEXT_MUTED}; font-size: 0.72rem; font-weight: 700;
            letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.6rem;
        }}
        .auth-card-title {{ color: {TEXT_DARK}; font-size: 1.55rem; font-weight: 800; margin: 0; }}
        .auth-card-subtitle {{ color: {TEXT_MUTED}; font-size: 0.9rem; margin: 0.25rem 0 1.5rem; }}
        .first-access {{ margin: 2.2rem 0 0.5rem; padding-top: 1.4rem; border-top: 1px solid {BORDER}; }}
        .first-access p {{ color: {TEXT_MUTED}; font-size: 0.82rem; margin: 0 0 0.7rem; }}
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input {{ background: #F5F2EB; border-color: {BORDER}; }}
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input:focus {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
            caret-color: {TEXT_DARK} !important;
        }}
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] input::placeholder {{
            color: {TEXT_MUTED} !important;
            -webkit-text-fill-color: {TEXT_MUTED} !important;
            opacity: 1 !important;
        }}
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] label,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stTextInput"] label *,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stCheckbox"] label,
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stCheckbox"] label * {{
            color: {TEXT_DARK} !important;
            -webkit-text-fill-color: {TEXT_DARK} !important;
        }}
        div[data-testid="column"]:has(.auth-panel-marker) .stButton button[kind="primary"],
        div[data-testid="column"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        div[data-testid="column"]:has(.auth-panel-marker) .stButton button[kind="primary"] *,
        div[data-testid="column"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button * {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}
        div[data-testid="column"]:has(.auth-panel-marker) div[data-testid="stForm"] {{ border: 0; padding: 0; }}
        div[data-testid="column"]:has(.auth-panel-marker) .stButton button,
        div[data-testid="column"]:has(.auth-panel-marker) [data-testid="stFormSubmitButton"] button {{ min-height: 2.6rem; }}
        @media (max-width: 800px) {{
            .auth-brand {{ min-height: auto; padding: 2rem 1.5rem 3rem; gap: 5rem; }}
            .auth-brand h1 {{ font-size: 2.2rem; }}
            div[data-testid="column"]:has(.auth-panel-marker) {{ padding: 2.5rem 1.25rem 3rem; }}
        }}
        div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label,
        div[data-testid="stCheckbox"] label {{ color: {TEXT_DARK} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand():
    st.markdown(
        """
        <div class="auth-brand">
            <div class="auth-brand-mark"><span class="auth-brand-icon">SGA</span><span>SGA</span></div>
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
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

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
        '<div class="auth-card-subtitle">Informe os dados recebidos no seu pré-cadastro, defina sua nova senha e vincule seu curso, turma e matéria.</div>',
        unsafe_allow_html=True,
    )

    with st.form("primeiro_acesso_form"):
        nome = st.text_input("Nome completo", placeholder="Ex.: Mirela Silva")
        email = st.text_input("E-mail institucional", placeholder="seu@email.com")
        col1, col2 = st.columns(2)
        with col1:
            senha_temp = st.text_input("Senha temporária", type="password", placeholder="Recebida por e-mail")
        with col2:
            nova_senha = st.text_input("Nova senha definitiva", type="password", placeholder="Mínimo 6 caracteres")

        confirmar_senha = st.text_input("Confirmar nova senha", type="password", placeholder="Repita a nova senha")

        col_c, col_t = st.columns(2)
        with col_c:
            curso = st.text_input("Curso", placeholder="Ex.: Engenharia de Software")
        with col_t:
            turma = st.text_input("Turma", placeholder="Ex.: ESW-2026-1")

        materia = st.text_input("Matéria / Disciplina", placeholder="Ex.: Banco de Dados")
        submitted = st.form_submit_button("Concluir primeiro acesso", type="primary", use_container_width=True)

    if submitted:
        if not all([nome.strip(), email.strip(), senha_temp, nova_senha, curso.strip(), turma.strip(), materia.strip()]):
            st.error("Preencha todos os campos obrigatórios.")
        elif nova_senha != confirmar_senha:
            st.error("A nova senha e a confirmação não conferem.")
        else:
            with st.spinner("Validando pré-cadastro..."):
                sucesso, mensagem = auth_controller.concluir_primeiro_acesso(
                    nome=nome,
                    email=email,
                    senha_temporaria=senha_temp,
                    nova_senha=nova_senha,
                    curso=curso,
                    turma=turma,
                    materia=materia,
                )
            if sucesso:
                st.success(mensagem)
                st.session_state.auth_tab = "login"
                st.rerun()
            else:
                st.error(mensagem)

    if st.button("Voltar ao login", use_container_width=True):
        st.session_state.auth_tab = "login"
        st.rerun()


def _render_first_access():
    st.markdown(
        '<div class="first-access"><div class="auth-label">Primeiro acesso</div>'
        '<p>Recebeu um pré-cadastro da sua instituição com senha temporária?</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Primeiro Acesso", type="primary", use_container_width=True):
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

    if st.button("Perfil", use_container_width=True):
        st.session_state.route = "perfil"
        st.rerun()
    if st.button("Sair", use_container_width=True):
        auth_controller.fazer_logout()
        st.session_state.route = "login"
        st.rerun()
