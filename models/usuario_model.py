# -*- coding: utf-8 -*-
"""
models/usuario_model.py

Model para gerenciar usuários no Firestore isolados por instituicao_id.
"""

import streamlit as st
from datetime import datetime

INSTITUICAO_PADRAO_ID = "inst_001"


def _get_instituicao_atual(instituicao_id: str = None) -> str:
    """Obtém o instituicao_id passado explicitamente ou da sessão ativa."""
    return (
        instituicao_id
        or st.session_state.get("instituicao_id")
        or INSTITUICAO_PADRAO_ID
    )


def criar_usuario(
    nome: str,
    email: str,
    role: str = "usuario",
    instituicao_id: str = None,
    uid: str = None,
):
    """
    Cria um novo usuário no Firestore vinculado à instituição.
    Usa uid como ID do documento se fornecido, ou email como fallback.
    """
    db = st.session_state.firestore_db
    inst_id = _get_instituicao_atual(instituicao_id)
    doc_id = uid or email

    usuario = {
        "uid": uid or email,
        "nome": nome,
        "email": email,
        "role": role,
        "instituicao_id": inst_id,
        "criado_em": datetime.now(),
        "ativo": True,
    }

    db.collection("usuarios").document(doc_id).set(usuario)
    return usuario


def obter_usuario(identificador: str, instituicao_id: str = None):
    """Busca um usuário por UID/ID de documento ou por e-mail dentro da instituição."""
    db = st.session_state.firestore_db
    inst_id = _get_instituicao_atual(instituicao_id)

    doc = db.collection("usuarios").document(identificador).get()
    if doc.exists:
        dados = doc.to_dict()
        if dados.get("instituicao_id", INSTITUICAO_PADRAO_ID) == inst_id:
            return {**dados, "id": doc.id}
        return None

    # Fallback: buscar pelo campo email dentro da mesma instituição
    query = (
        db.collection("usuarios")
        .where("email", "==", identificador)
        .where("instituicao_id", "==", inst_id)
        .limit(1)
        .stream()
    )
    doc_email = next(query, None)
    if doc_email:
        return {**doc_email.to_dict(), "id": doc_email.id}

    return None


def listar_usuarios(role: str = None, instituicao_id: str = None):
    """
    Lista todos os usuários da instituição ativa.
    """
    db = st.session_state.firestore_db
    inst_id = _get_instituicao_atual(instituicao_id)

    usuarios = []
    query = db.collection("usuarios").where("instituicao_id", "==", inst_id)

    if role:
        query = query.where("role", "==", role)

    for doc in query.stream():
        usuarios.append({**doc.to_dict(), "id": doc.id})

    return usuarios


def atualizar_usuario(identificador: str, dados: dict, instituicao_id: str = None):
    """Atualiza dados de um usuário garantindo que pertence à mesma instituição."""
    usuario = obter_usuario(identificador, instituicao_id)
    if not usuario:
        raise PermissionError("Usuário não encontrado ou pertence a outra instituição.")

    db = st.session_state.firestore_db
    dados_seguros = {k: v for k, v in dados.items() if k != "instituicao_id"}
    db.collection("usuarios").document(usuario["id"]).update({
        **dados_seguros,
        "atualizado_em": datetime.now(),
    })


def deletar_usuario(identificador: str, instituicao_id: str = None):
    """Deleta um usuário garantindo que pertence à mesma instituição."""
    usuario = obter_usuario(identificador, instituicao_id)
    if not usuario:
        raise PermissionError("Usuário não encontrado ou pertence a outra instituição.")

    db = st.session_state.firestore_db
    db.collection("usuarios").document(usuario["id"]).delete()


def usuario_existe(identificador: str, instituicao_id: str = None):
    """Verifica se usuário existe na instituição atual."""
    return obter_usuario(identificador, instituicao_id) is not None