# -*- coding: utf-8 -*-
"""
[CONTROLLER] Sessão e navegação.

Responsável por inicializar as coleções de trabalho vazias em st.session_state
e por controlar a rota atual (equivalente
ao roteador de uma aplicação MVC tradicional).
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


def current_route() -> str:
    return st.session_state.route


def is_logged_in() -> bool:
    return bool(st.session_state.logged_in)


def goto(route: str) -> None:
    st.session_state.route = route
