# -*- coding: utf-8 -*-
"""
[CONTROLLER] Salas (ambientes) e Solicitações/Reservas.
"""

import streamlit as st

from models import sala_model, solicitacao_model

SLOTS = solicitacao_model.SLOTS


# ── Salas ──

def list_salas() -> list:
    return st.session_state.salas


def salas_disponiveis() -> list:
    return sala_model.salas_disponiveis(st.session_state.salas)


def add_sala(sala: dict) -> dict:
    return sala_model.add_sala(st.session_state.salas, sala)


def update_sala(sala_id: int, data_new: dict) -> None:
    sala_model.update_sala(st.session_state.salas, sala_id, data_new)


def toggle_manutencao(sala_id: int) -> None:
    sala_model.toggle_manutencao(st.session_state.salas, sala_id)


# ── Persistência das Reservas ──

def carregar_solicitacoes() -> None:
    ss = st.session_state
    uid = ss.get("user_uid")

    if not uid:
        return

    if ss.get("reservas_carregadas_uid") == uid:
        return

    db = ss.get("firestore_db")
    if db is None:
        raise RuntimeError("Não foi possível conectar ao Firestore.")

    documentos = db.collection("reservas").stream()

    solicitacoes = []
    for doc in documentos:
        dados = doc.to_dict()
        dados["id"] = doc.id
        solicitacoes.append(dados)

    ss.solicitacoes = solicitacoes
    ss.reservas_carregadas_uid = uid


def _salvar_solicitacao(sol: dict) -> None:
    db = st.session_state.get("firestore_db")

    if db is None:
        raise RuntimeError("Não foi possível conectar ao Firestore.")

    dados = {chave: valor for chave, valor in sol.items() if chave != "id"}

    db.collection("reservas").document(str(sol["id"])).set(dados)


def _buscar_solicitacao(sol_id: str) -> dict:
    for sol in st.session_state.solicitacoes:
        if str(sol["id"]) == str(sol_id):
            return sol

    raise ValueError("Solicitação não encontrada.")


# ── Solicitações / Reservas ──

def list_solicitacoes() -> list:
    return st.session_state.solicitacoes


def add_solicitacao(**kwargs) -> dict:
    ss = st.session_state

    sol, ss._next_sol_id = solicitacao_model.add_solicitacao(
        ss.solicitacoes, ss._next_sol_id, **kwargs
    )

    try:
        db = ss.get("firestore_db")
        if db is None:
            raise RuntimeError("Não foi possível conectar ao Firestore.")

        documento = db.collection("reservas").document()
        sol["id"] = documento.id

        _salvar_solicitacao(sol)

    except Exception:
        ss.solicitacoes.remove(sol)
        raise

    return sol


def aprovar_solicitacao(sol_id: str, aprovado_por: str, obs: str | None = None) -> None:
    solicitacao_model.aprovar_solicitacao(
        st.session_state.solicitacoes, sol_id, aprovado_por, obs
    )
    sol = _buscar_solicitacao(sol_id)
    _salvar_solicitacao(sol)


def recusar_solicitacao(sol_id: str, aprovado_por: str, obs: str) -> None:
    solicitacao_model.recusar_solicitacao(
        st.session_state.solicitacoes, sol_id, aprovado_por, obs
    )
    sol = _buscar_solicitacao(sol_id)
    _salvar_solicitacao(sol)


def cancelar_solicitacao(sol_id: str) -> None:
    solicitacao_model.cancelar_solicitacao(
        st.session_state.solicitacoes, sol_id
    )
    sol = _buscar_solicitacao(sol_id)
    _salvar_solicitacao(sol)


def minhas_solicitacoes(nome_usuario: str, usuario_uid: str = None) -> list:
    return solicitacao_model.minhas_solicitacoes(
        st.session_state.solicitacoes, nome_usuario, usuario_uid
    )


def pendentes_para_professor(nome_professor: str) -> list:
    return solicitacao_model.pendentes_para_professor(
        st.session_state.solicitacoes, nome_professor
    )


def solicitacoes_de_alunos_do_professor(nome_professor: str) -> list:
    return solicitacao_model.solicitacoes_de_alunos_do_professor(
        st.session_state.solicitacoes, nome_professor
    )


def auth_requests_do_nucleo(nucleo: str | None) -> list:
    return solicitacao_model.auth_requests_do_nucleo(
        st.session_state.solicitacoes, nucleo
    )


def pendentes(lista: list) -> list:
    return solicitacao_model.pendentes(lista)


def disponibilidade_da_sala(sala_nome: str, data_ptbr: str) -> list:
    return solicitacao_model.disponibilidade_da_sala(
        st.session_state.solicitacoes, sala_nome, data_ptbr
    )
