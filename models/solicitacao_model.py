# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Solicitação / Reserva.

Sincroniza criação, aprovação, recusa e cancelamento com o Firestore
isolados por instituicao_id, mantendo compatibilidade total com os controllers.
"""

from datetime import datetime
import streamlit as st

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_SOLICITACOES = "solicitacoes"

SLOTS = [("08:00", "10:00"), ("10:00", "12:00"), ("12:00", "14:00"),
         ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")]


def _now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, sol_id: int) -> str:
    return f"{instituicao_id}_{sol_id}"


def listar_solicitacoes_firestore(instituicao_id: str | None = None) -> tuple[list, int]:
    """
    Busca todas as solicitações da instituição no Firestore.
    Retorna: (lista_solicitacoes, proximo_id_livre)
    """
    db = _get_db()
    if not db:
        return [], 1

    inst_id = instituicao_id or _get_instituicao_id()
    docs = (
        db.collection(COLECAO_SOLICITACOES)
        .where("instituicao_id", "==", inst_id)
        .stream()
    )

    solicitacoes = [doc.to_dict() for doc in docs]
    solicitacoes.sort(key=lambda s: s.get("id", 0))
    next_id = max((s.get("id", 0) for s in solicitacoes), default=0) + 1
    return solicitacoes, next_id


def add_solicitacao(solicitacoes: list, next_id: int, **kwargs) -> tuple[dict, int]:
    """Cria uma nova solicitação, persiste no Firestore e devolve (criada, próximo id livre)."""
    inst_id = _get_instituicao_id()
    sol = dict(kwargs)
    sol["id"] = next_id
    sol["instituicao_id"] = inst_id
    sol["createdAt"] = _now_str()

    db = _get_db()
    if db:
        db.collection(COLECAO_SOLICITACOES).document(_doc_id(inst_id, next_id)).set(sol)

    solicitacoes.append(sol)
    return sol, next_id + 1


def aprovar_solicitacao(solicitacoes: list, sol_id: int, aprovado_por: str, obs: str | None = None) -> None:
    inst_id = _get_instituicao_id()
    for s in solicitacoes:
        if s["id"] == sol_id:
            data_aprov = _now_str()
            s["status"] = "Aprovado"
            s["aprovadoPor"] = aprovado_por
            s["dataAprovacao"] = data_aprov
            updates = {
                "status": "Aprovado",
                "aprovadoPor": aprovado_por,
                "dataAprovacao": data_aprov,
            }
            if obs:
                s["observacao"] = obs
                updates["observacao"] = obs

            db = _get_db()
            if db:
                db.collection(COLECAO_SOLICITACOES).document(_doc_id(inst_id, sol_id)).update(updates)
            return


def recusar_solicitacao(solicitacoes: list, sol_id: int, aprovado_por: str, obs: str) -> None:
    inst_id = _get_instituicao_id()
    for s in solicitacoes:
        if s["id"] == sol_id:
            data_aprov = _now_str()
            s["status"] = "Recusado"
            s["aprovadoPor"] = aprovado_por
            s["dataAprovacao"] = data_aprov
            s["observacao"] = obs

            db = _get_db()
            if db:
                db.collection(COLECAO_SOLICITACOES).document(_doc_id(inst_id, sol_id)).update({
                    "status": "Recusado",
                    "aprovadoPor": aprovado_por,
                    "dataAprovacao": data_aprov,
                    "observacao": obs,
                })
            return


def cancelar_solicitacao(solicitacoes: list, sol_id: int) -> None:
    inst_id = _get_instituicao_id()
    for s in solicitacoes:
        if s["id"] == sol_id:
            s["status"] = "Cancelado"

            db = _get_db()
            if db:
                db.collection(COLECAO_SOLICITACOES).document(_doc_id(inst_id, sol_id)).update({
                    "status": "Cancelado"
                })
            return


# ── Consultas ─────────────────────────────────────────────────────────────────

def minhas_solicitacoes(solicitacoes: list, nome_usuario: str) -> list:
    return [s for s in solicitacoes if s["solicitante"] == nome_usuario]


def pendentes_para_professor(solicitacoes: list, nome_professor: str) -> list:
    return [s for s in solicitacoes if s["tipo"] == "aluno_para_professor"
            and s.get("professorResponsavel") == nome_professor
            and s["status"] in ("Pendente", "Em análise")]


def solicitacoes_de_alunos_do_professor(solicitacoes: list, nome_professor: str) -> list:
    return [s for s in solicitacoes if s.get("professorResponsavel") == nome_professor]


def auth_requests_do_nucleo(solicitacoes: list, nucleo: str | None) -> list:
    return [s for s in solicitacoes if s["tipo"] == "auth_required"
            and (not nucleo or not s.get("nucleoSolicitante") or s.get("nucleoSolicitante") == nucleo)]


def pendentes(lista: list) -> list:
    return [s for s in lista if s["status"] in ("Pendente", "Em análise")]


def disponibilidade_da_sala(solicitacoes: list, sala_nome: str, data_ptbr: str) -> list:
    """Devolve, para cada slot padrão do dia, se está ocupado ou disponível."""
    rows = []
    for si, fi in SLOTS:
        ocupado = next(
            (s for s in solicitacoes
             if s["sala"] == sala_nome and s["data"] == data_ptbr
             and s["status"] not in ("Cancelado", "Recusado") and s["inicio"] == si),
            None,
        )
        rows.append({
            "Horário": f"{si}–{fi}",
            "Status": f"Ocupado · {ocupado['solicitante']}" if ocupado else "Disponível",
        })
    return rows