# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Solicitação / Reserva.

Funções puras de criação, aprovação, recusa e cancelamento. O Controller
(reservas_controller) é responsável por buscar a lista em st.session_state,
chamar estas funções e persistir o resultado de volta na sessão.
"""

from datetime import datetime

SLOTS = [("08:00", "10:00"), ("10:00", "12:00"), ("12:00", "14:00"),
         ("14:00", "16:00"), ("16:00", "18:00"), ("18:00", "20:00")]


def _now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def add_solicitacao(solicitacoes: list, next_id: int, **kwargs) -> tuple[dict, int]:
    """Cria uma solicitação e verifica conflitos de horário."""

    if tem_conflito(
        solicitacoes,
        kwargs["sala"],
        kwargs["data"],
        kwargs["inicio"],
        kwargs["fim"],
    ):
        raise ValueError("Já existe uma reserva ou solicitação neste horário.")

    sol = dict(kwargs)
    sol["id"] = next_id
    sol["createdAt"] = _now_str()
    solicitacoes.append(sol)

    return sol, next_id + 1


def aprovar_solicitacao(solicitacoes: list, sol_id: int, aprovado_por: str, obs: str | None = None) -> None:
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
                raise ValueError("Não é possível aprovar: já existe uma reserva neste horário.")

            s["status"] = "Aprovado"
            s["aprovadoPor"] = aprovado_por
            s["dataAprovacao"] = _now_str()

            if obs:
                s["observacao"] = obs

            return


def recusar_solicitacao(solicitacoes: list, sol_id: int, aprovado_por: str, obs: str) -> None:
    for s in solicitacoes:
        if s["id"] == sol_id:
            s["status"] = "Recusado"
            s["aprovadoPor"] = aprovado_por
            s["dataAprovacao"] = _now_str()
            s["observacao"] = obs
            return


def cancelar_solicitacao(solicitacoes: list, sol_id: int) -> None:
    for s in solicitacoes:
        if s["id"] == sol_id:
            s["status"] = "Cancelado"
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


def tem_conflito(solicitacoes: list, sala: str, data: str, inicio: str, fim: str, ignorar_id: int | None = None) -> bool:
    """Verifica se existe outra reserva no mesmo ambiente e horário."""
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
