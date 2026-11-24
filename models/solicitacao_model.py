# -- coding: utf-8 --
"""
[MODEL] Entidade Solicitação / Reserva.

Unifica validação de horários e conflitos com persistência no Firestore
isolada por instituicao_id.
"""
from utils.datetime_utils import agora_str
from datetime import datetime
import streamlit as st

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_SOLICITACOES = "solicitacoes"

SLOTS = [("08:00", "10:00"), ("10:00", "12:00"), ("12:00", "14:00"),
         ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")]


def _validar_horario(inicio: str, fim: str) -> None:
    """Valida os horários e garante que o término seja posterior ao início."""
    try:
        inicio_hora = datetime.strptime(inicio, "%H:%M").time()
        fim_hora = datetime.strptime(fim, "%H:%M").time()
    except (TypeError, ValueError):
        raise ValueError("Informe horários válidos no formato HH:MM.")

    if fim_hora <= inicio_hora:
        raise ValueError(
            "O horário de término deve ser posterior ao de início.")


def _now_str() -> str:
    return agora_str()


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, sol_id: int) -> str:
    return f"{instituicao_id}_{sol_id}"


def listar_solicitacoes_firestore(instituicao_id: str | None = None) -> tuple[list, int]:
    """Busca todas as solicitações da instituição no Firestore."""
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
    """Cria uma solicitação, verifica conflitos de horário e persiste no Firestore."""
    if tem_conflito(
        solicitacoes,
        kwargs["sala"],
        kwargs["data"],
        kwargs["inicio"],
        kwargs["fim"],
    ):
        raise ValueError("Já existe uma reserva ou solicitação neste horário.")

    inst_id = _get_instituicao_id()
    sol = dict(kwargs)
    sol["id"] = next_id
    sol["instituicao_id"] = inst_id
    sol["createdAt"] = _now_str()

    db = _get_db()
    if db:
        db.collection(COLECAO_SOLICITACOES).document(
            _doc_id(inst_id, next_id)).set(sol)

    solicitacoes.append(sol)
    return sol, next_id + 1


def aprovar_solicitacao(solicitacoes: list, sol_id: int, aprovado_por: str, obs: str | None = None) -> None:
    inst_id = _get_instituicao_id()
    for s in solicitacoes:
        if s["id"] == sol_id:
            if tem_conflito(
                solicitacoes,
                s["sala"],
                s["data"],
                s["inicio"],
                s["fim"],
                ignorar_id=sol_id,
            ):
                raise ValueError(
                    "Não é possível aprovar: já existe uma reserva neste horário.")

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
                db.collection(COLECAO_SOLICITACOES).document(
                    _doc_id(inst_id, sol_id)).update(updates)
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

def minhas_solicitacoes(
    solicitacoes: list, nome_usuario: str, usuario_uid: str | None = None
) -> list:
    """Retorna todas as reservas/solicitações do usuário (independente do status)."""
    nome_norm = (nome_usuario or "").strip().lower()
    resultado = []
    for s in solicitacoes:
        uid_sol = s.get("solicitanteUid")
        nome_sol = (s.get("solicitante") or "").strip().lower()

        if (usuario_uid and uid_sol == usuario_uid) or (nome_norm and nome_sol == nome_norm):
            resultado.append(s)
    return resultado


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
        inicio_slot = datetime.strptime(si, "%H:%M").time()
        fim_slot = datetime.strptime(fi, "%H:%M").time()

        ocupado = next(
            (
                s for s in solicitacoes
                if s["sala"] == sala_nome
                and s["data"] == data_ptbr
                and s["status"] not in ("Cancelado", "Recusado")
                and datetime.strptime(s["inicio"], "%H:%M").time() < fim_slot
                and datetime.strptime(s["fim"], "%H:%M").time() > inicio_slot
            ),
            None,
        )

        rows.append({
            "Horário": f"{si}–{fi}",
            "Status": f"Ocupado · {ocupado['solicitante']}" if ocupado else "Disponível",
        })

    return rows


def tem_conflito(
    solicitacoes: list,
    sala: str,
    data: str,
    inicio: str,
    fim: str,
    ignorar_id: int | None = None,
) -> bool:
    """Verifica sobreposição com outra solicitação ativa da mesma sala e data."""
    _validar_horario(inicio, fim)
    inicio_novo = datetime.strptime(inicio, "%H:%M").time()
    fim_novo = datetime.strptime(fim, "%H:%M").time()

    for s in solicitacoes:
        if s["sala"] != sala or s["data"] != data:
            continue

        if s["status"] in ("Cancelado", "Recusado"):
            continue

        if ignorar_id is not None and s["id"] == ignorar_id:
            continue

        inicio_existente = datetime.strptime(s["inicio"], "%H:%M").time()
        fim_existente = datetime.strptime(s["fim"], "%H:%M").time()

        if inicio_novo < fim_existente and fim_novo > inicio_existente:
            return True

    return False
