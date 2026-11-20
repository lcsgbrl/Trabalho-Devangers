# -*- coding: utf-8 -*-
"""
[CONTROLLER] Sessão e navegação.

Responsável por inicializar as coleções de trabalho em st.session_state,
carregar os dados persistidos da instituição no Firestore e controlar a rota atual.
"""

import streamlit as st


def init_state() -> None:
    """Inicializa as coleções operacionais vazias para a sessão."""
    ss = st.session_state
    if ss.get("_sga_initialized") == 2:
        return

    ss.current_user = None
    ss.route = "login"
    ss.logged_in = False
    ss.instituicao_id = "inst_001"

    ss.salas = []
    ss.solicitacoes = []
    ss._next_sol_id = 1

    ss.members = []
    ss._next_member_id = 1

    ss.nucleos = []
    ss.cursos = []
    ss.turmas = []
    ss.disciplinas = []
    ss._next_acad_id = 0

    ss._sga_initialized = 2


def carregar_dados_instituicao(instituicao_id: str | None = None) -> None:
    """
    Carrega salas e solicitações da instituição ativa a partir do Firestore
    para st.session_state, mantendo retrocompatibilidade com todas as views.
    """
    from models import sala_model, solicitacao_model

    ss = st.session_state
    inst_id = instituicao_id or ss.get("instituicao_id") or "inst_001"
    ss.instituicao_id = inst_id

    try:
        ss.salas = sala_model.listar_salas_firestore(inst_id)
    except Exception as e:
        st.warning(f"Não foi possível carregar salas do banco: {e}")

    try:
        sols, next_id = solicitacao_model.listar_solicitacoes_firestore(inst_id)
        ss.solicitacoes = sols
        ss._next_sol_id = next_id
    except Exception as e:
        st.warning(f"Não foi possível carregar solicitações do banco: {e}")


def limpar_dados_sessao() -> None:
    """Limpa os dados operacionais ao fazer logout."""
    ss = st.session_state
    ss.instituicao_id = "inst_001"
    ss.salas = []
    ss.solicitacoes = []
    ss._next_sol_id = 1
    ss.members = []
    ss._next_member_id = 1
    ss.nucleos = []
    ss.cursos = []
    ss.turmas = []
    ss.disciplinas = []
    ss._next_acad_id = 0


def current_route() -> str:
    return st.session_state.route


def is_logged_in() -> bool:
    return bool(st.session_state.logged_in)


def goto(route: str) -> None:
    st.session_state.route = route