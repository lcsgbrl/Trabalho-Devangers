# -*- coding: utf-8 -*-
"""
[CONTROLLER] Membros da instituição e controle de autorização por perfil.

Conecta a View "membros_view" ao Model membro_model, validando permissões
de escopo (Admin -> todos; Coordenador -> apenas Professores) antes de
qualquer leitura ou escrita.
"""

import streamlit as st

from models import membro_model as m
from models import permissions_model as pm


def _current_role() -> str:
    return st.session_state.get("user_role") or ""


def allowed_funcoes() -> list[str]:
    """Devolve as funções que o usuário logado pode visualizar e gerenciar."""
    return pm.allowed_member_roles(_current_role())


def can_manage_role(target_funcao: str) -> bool:
    """Indica se o usuário logado pode gerenciar membros com `target_funcao`."""
    return pm.can_manage_member_role(_current_role(), target_funcao)


def _assert_can_manage(target_funcao: str) -> None:
    """Bloqueia operações não autorizadas diretamente na camada de negócio."""
    role = _current_role()
    if not pm.can_manage_member_role(role, target_funcao):
        if pm.is_coordinator_role(role):
            raise PermissionError("Coordenadores só têm permissão para gerenciar perfis de Professores.")
        raise PermissionError("Você não tem permissão para gerenciar este perfil de usuário.")


def _find_member(member_id: int) -> dict | None:
    return next((item for item in st.session_state.members if item["id"] == member_id), None)


def list_members() -> list:
    permitidas = set(allowed_funcoes())
    if not permitidas:
        return []
    return [item for item in st.session_state.members if item.get("funcao") in permitidas]


def filter_members(search: str, funcao: str, status: str, nucleo: str) -> list:
    visiveis = list_members()
    return m.filter_members(visiveis, search, funcao, status, nucleo)


def pending_requests() -> list:
    permitidas = set(allowed_funcoes())
    return [
        item for item in m.pending_requests(st.session_state.members)
        if item.get("funcao") in permitidas
    ]


def add_member_directly(payload: dict) -> None:
    _assert_can_manage(payload.get("funcao", ""))
    ss = st.session_state
    _, ss._next_member_id = m.add_member_directly(ss.members, ss._next_member_id, payload)


def update_member(member_id: int, payload: dict) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    # Valida tanto o perfil atual do membro quanto o novo perfil enviado
    _assert_can_manage(alvo.get("funcao", ""))
    _assert_can_manage(payload.get("funcao", alvo.get("funcao", "")))
    m.update_member(st.session_state.members, member_id, payload)


def remove_member(member_id: int) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    _assert_can_manage(alvo.get("funcao", ""))
    ss = st.session_state
    ss.members = m.remove_member(ss.members, member_id)


def toggle_member_status(member_id: int) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    _assert_can_manage(alvo.get("funcao", ""))
    m.toggle_member_status(st.session_state.members, member_id)


def approve_member(member_id: int) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    _assert_can_manage(alvo.get("funcao", ""))
    m.approve_member(st.session_state.members, member_id)


def reject_member(member_id: int) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    _assert_can_manage(alvo.get("funcao", ""))
    ss = st.session_state
    ss.members = m.reject_member(ss.members, member_id)


def solicitar_correcao(member_id: int, motivo: str) -> None:
    alvo = _find_member(member_id)
    if not alvo:
        raise ValueError("Membro não encontrado.")
    _assert_can_manage(alvo.get("funcao", ""))
    m.solicitar_correcao(st.session_state.members, member_id, motivo)