# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Sala (ambiente).

Unifica as regras de validação de sala com a persistência no Firestore
isolada por instituicao_id e disparo de notificações aos afetados.
"""

import streamlit as st
from models import notificacao_model

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_SALAS = "salas"
STATUS_SALA = ("Disponível", "Manutenção", "Inativa")


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, sala_id: int) -> str:
    return f"{instituicao_id}_{sala_id}"


def _validar_sala(sala: dict) -> None:
    """Valida os campos essenciais e o status de uma sala."""
    for campo in ("nome", "bloco", "numero"):
        if not str(sala.get(campo, "")).strip():
            raise ValueError("Preencha nome, bloco e localização da sala.")

    try:
        capacidade = int(sala.get("capacidade", 0))
    except (TypeError, ValueError):
        raise ValueError("Informe uma capacidade válida para a sala.")

    if capacidade < 1:
        raise ValueError("A capacidade da sala deve ser maior que zero.")

    if sala.get("status") not in STATUS_SALA:
        raise ValueError("Status de sala inválido.")


def listar_salas_firestore(instituicao_id: str | None = None) -> list:
    """Busca todas as salas da instituição no Firestore ordenadas por id."""
    db = _get_db()
    if not db:
        return []

    inst_id = instituicao_id or _get_instituicao_id()
    docs = db.collection(COLECAO_SALAS).where(
        "instituicao_id", "==", inst_id).stream()

    salas = [doc.to_dict() for doc in docs]
    salas.sort(key=lambda s: s.get("id", 0))
    return salas


def add_sala(salas: list, sala: dict) -> dict:
    """Valida, cria uma nova sala com id autoincremental e persiste no Firestore."""
    _validar_sala(sala)
    new_id = (max((s["id"] for s in salas), default=0)) + 1
    inst_id = _get_instituicao_id()

    novo = dict(sala)
    novo["id"] = new_id
    novo["instituicao_id"] = inst_id

    db = _get_db()
    if db:
        db.collection(COLECAO_SALAS).document(
            _doc_id(inst_id, new_id)).set(novo)

    salas.append(novo)
    return novo


def update_sala(salas: list, sala_id: int, data_new: dict) -> int:
    """Atualiza a sala; se mudou para Manutenção, cancela reservas ativas e notifica."""
    _validar_sala(data_new)
    inst_id = _get_instituicao_id()
    notificados = 0

    for i, s in enumerate(salas):
        if s["id"] == sala_id:
            status_anterior = s.get("status")
            nome_anterior = s.get("nome", "")
            atualizado = {**data_new, "id": sala_id, "instituicao_id": inst_id}
            salas[i] = atualizado

            db = _get_db()
            if db:
                db.collection(COLECAO_SALAS).document(
                    _doc_id(inst_id, sala_id)).set(atualizado)

            if status_anterior != "Manutenção" and atualizado.get("status") == "Manutenção":
                notificados = notificacao_model.notificar_reservas_afetadas(
                    st.session_state.get("solicitacoes", []),
                    nome_anterior,
                    acao="manutencao",
                )
            return notificados
    return 0


def toggle_manutencao(salas: list, sala_id: int) -> int:
    """Alterna Disponível/Manutenção; uma sala Inativa volta a Disponível."""
    inst_id = _get_instituicao_id()
    notificados = 0

    for s in salas:
        if s["id"] == sala_id:
            novo_status = "Manutenção" if s["status"] == "Disponível" else "Disponível"
            s["status"] = novo_status

            db = _get_db()
            if db:
                db.collection(COLECAO_SALAS).document(_doc_id(inst_id, sala_id)).update({
                    "status": novo_status
                })

            if novo_status == "Manutenção":
                notificados = notificacao_model.notificar_reservas_afetadas(
                    st.session_state.get("solicitacoes", []),
                    s["nome"],
                    acao="manutencao",
                )
            return notificados
    return 0


def delete_sala(salas: list, solicitacoes: list, sala_id: int) -> int:
    """Exclui a sala do Firestore/sessão, cancela reservas ativas nela e notifica."""
    inst_id = _get_instituicao_id()
    sala = get_sala_by_id(salas, sala_id)
    if not sala:
        return 0

    notificados = notificacao_model.notificar_reservas_afetadas(
        solicitacoes, sala["nome"], acao="excluida"
    )

    salas[:] = [s for s in salas if s["id"] != sala_id]

    db = _get_db()
    if db:
        db.collection(COLECAO_SALAS).document(_doc_id(inst_id, sala_id)).delete()

    return notificados


def get_sala_by_id(salas: list, sala_id: int) -> dict | None:
    return next((s for s in salas if s["id"] == sala_id), None)


def salas_disponiveis(salas: list) -> list:
    return [s for s in salas if s["status"] == "Disponível"]