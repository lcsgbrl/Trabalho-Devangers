# -*- coding: utf-8 -*-
"""
[CONTROLLER] Salas (ambientes) e Solicitações/Reservas.

Conecta a View "reservas_view" aos Models sala_model e solicitacao_model,
sincronizados com o Firestore por instituicao_id.
"""

import streamlit as st

from controllers import session_controller
from models import sala_model, solicitacao_model

SLOTS = solicitacao_model.SLOTS


# ── Salas ─────────────────────────────────────────────────────────────────────

def list_salas() -> list:
    return st.session_state.salas


def salas_disponiveis() -> list:
    return sala_model.salas_disponiveis(st.session_state.salas)


def add_sala(sala: dict) -> dict:
    return sala_model.add_sala(st.session_state.salas, sala)


def update_sala(sala_id: int, data_new: dict) -> int:
    return sala_model.update_sala(st.session_state.salas, sala_id, data_new)


def toggle_manutencao(sala_id: int) -> int:
    return sala_model.toggle_manutencao(st.session_state.salas, sala_id)


def delete_sala(sala_id: int) -> int:
    return sala_model.delete_sala(
        st.session_state.salas, st.session_state.solicitacoes, sala_id
    )


# ── Solicitações / Reservas ──────────────────────────────────────────────────

def carregar_solicitacoes() -> None:
    """Garante o carregamento das solicitações/salas da instituição ativa."""
    ss = st.session_state
    uid = ss.get("user_uid")
    if not uid or ss.get("reservas_carregadas_uid") == uid:
        return

    session_controller.carregar_dados_instituicao(ss.get("instituicao_id"))
    ss.reservas_carregadas_uid = uid


def list_solicitacoes() -> list:
    return st.session_state.solicitacoes


def add_solicitacao(**kwargs) -> dict:
    ss = st.session_state
    sol, ss._next_sol_id = solicitacao_model.add_solicitacao(
        ss.solicitacoes, ss._next_sol_id, **kwargs
    )
    return sol


def aprovar_solicitacao(sol_id: int, aprovado_por: str, obs: str | None = None) -> None:
    solicitacao_model.aprovar_solicitacao(
        st.session_state.solicitacoes, sol_id, aprovado_por, obs)


def recusar_solicitacao(sol_id: int, aprovado_por: str, obs: str) -> None:
    solicitacao_model.recusar_solicitacao(
        st.session_state.solicitacoes, sol_id, aprovado_por, obs)


def cancelar_solicitacao(sol_id: int) -> None:
    solicitacao_model.cancelar_solicitacao(
        st.session_state.solicitacoes, sol_id)


def delete_solicitacao(sol_id: int) -> None:
    solicitacao_model.delete_solicitacao(
        st.session_state.solicitacoes, sol_id)


def minhas_solicitacoes(nome_usuario: str, usuario_uid: str | None = None) -> list:
    return solicitacao_model.minhas_solicitacoes(
        st.session_state.solicitacoes, nome_usuario, usuario_uid
    )


def pendentes_para_professor(nome_professor: str) -> list:
    return solicitacao_model.pendentes_para_professor(st.session_state.solicitacoes, nome_professor)


def solicitacoes_de_alunos_do_professor(nome_professor: str) -> list:
    return solicitacao_model.solicitacoes_de_alunos_do_professor(st.session_state.solicitacoes, nome_professor)


def auth_requests_do_nucleo(nucleo: str | None) -> list:
    return solicitacao_model.auth_requests_do_nucleo(st.session_state.solicitacoes, nucleo)


def pendentes(lista: list) -> list:
    return solicitacao_model.pendentes(lista)


def disponibilidade_da_sala(sala_nome: str, data_ptbr: str) -> list:
    return solicitacao_model.disponibilidade_da_sala(st.session_state.solicitacoes, sala_nome, data_ptbr)