# -*- coding: utf-8 -*-
"""
[MODEL] Regras de permissão por papel (role).

Funções puras: recebem o papel do usuário e devolvem informações de
permissão, sem tocar em st.session_state. Quem decide "qual é o papel do
usuário logado" é responsabilidade do Controller (auth_controller).
"""

from models import domain_data as data

# Papéis que podem gerenciar membros e quais funções cada um pode manipular
MEMBER_MANAGEMENT_SCOPE = {
    "Administrador": tuple(data.FUNCOES),  # Exclusivo do Administrador
}


def get_permissions(role: str) -> dict:
    """Devolve o dicionário de permissões associado a um papel."""
    return data.PERMISSIONS_MATRIX.get(role, {})


def has_permission(role: str, key: str) -> bool:
    """Verifica se um papel possui a permissão `key`."""
    return bool(get_permissions(role).get(key, False))


def is_admin_role(role: str) -> bool:
    return role == "Administrador"


def is_coordinator_role(role: str) -> bool:
    return role == "Coordenador"


def allowed_member_roles(role: str) -> list[str]:
    """Devolve a lista de funções (perfis) que o papel `role` pode gerenciar."""
    return list(MEMBER_MANAGEMENT_SCOPE.get(role, ()))


def can_manage_member_role(actor_role: str, target_funcao: str) -> bool:
    """Verifica se `actor_role` tem autorização para criar/editar/remover/alterar `target_funcao`."""
    return target_funcao in MEMBER_MANAGEMENT_SCOPE.get(actor_role, ())