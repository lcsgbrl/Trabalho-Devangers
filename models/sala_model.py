# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Sala (ambiente).

Mantém compatibilidade com a interface de listas usada pelos controllers,
sincronizando cada operação com o Firestore isolada por instituicao_id.
"""

import streamlit as st

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_SALAS = "salas"


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, sala_id: int) -> str:
    return f"{instituicao_id}_{sala_id}"


def listar_salas_firestore(instituicao_id: str | None = None) -> list:
    """Busca todas as salas da instituição no Firestore ordenadas por id."""
    db = _get_db()
    if not db:
        return []

    inst_id = instituicao_id or _get_instituicao_id()
    docs = db.collection(COLECAO_SALAS).where("instituicao_id", "==", inst_id).stream()

    salas = [doc.to_dict() for doc in docs]
    salas.sort(key=lambda s: s.get("id", 0))
    return salas


def add_sala(salas: list, sala: dict) -> dict:
    """Cria uma nova sala com id autoincremental, persiste no Firestore e insere na lista."""
    new_id = (max((s["id"] for s in salas), default=0)) + 1
    inst_id = _get_instituicao_id()

    novo = dict(sala)
    novo["id"] = new_id
    novo["instituicao_id"] = inst_id

    db = _get_db()
    if db:
        db.collection(COLECAO_SALAS).document(_doc_id(inst_id, new_id)).set(novo)

    salas.append(novo)
    return novo


def update_sala(salas: list, sala_id: int, data_new: dict) -> None:
    inst_id = _get_instituicao_id()
    for i, s in enumerate(salas):
        if s["id"] == sala_id:
            atualizado = {**data_new, "id": sala_id, "instituicao_id": inst_id}
            salas[i] = atualizado

            db = _get_db()
            if db:
                db.collection(COLECAO_SALAS).document(_doc_id(inst_id, sala_id)).set(atualizado)
            return


def toggle_manutencao(salas: list, sala_id: int) -> None:
    inst_id = _get_instituicao_id()
    for s in salas:
        if s["id"] == sala_id:
            novo_status = "Disponível" if s["status"] == "Manutenção" else "Manutenção"
            s["status"] = novo_status

            db = _get_db()
            if db:
                db.collection(COLECAO_SALAS).document(_doc_id(inst_id, sala_id)).update({
                    "status": novo_status
                })
            return


def get_sala_by_id(salas: list, sala_id: int) -> dict | None:
    return next((s for s in salas if s["id"] == sala_id), None)


def salas_disponiveis(salas: list) -> list:
    return [s for s in salas if s["status"] == "Disponível"]