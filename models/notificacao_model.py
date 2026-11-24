# -*- coding: utf-8 -*-
"""
[MODEL] Notificações do sistema.
Persiste alertas de status, salas e lembretes de reservas no Firestore,
isolados por instituicao_id e destinatário, com destino de navegação direta.
"""

from datetime import datetime, timedelta
import streamlit as st
from utils.datetime_utils import agora_br, agora_str, hoje_br

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_NOTIFICACOES = "notificacoes"


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def criar_notificacao(
    destinatario_uid: str | None,
    destinatario_nome: str,
    titulo: str,
    mensagem: str,
    tipo: str = "info",
    chave_unica: str | None = None,
    rota: str = "reservas",
    aba: str = "minhas",
) -> dict | None:
    """
    Cria uma notificação no Firestore para um usuário específico.
    Se `chave_unica` for informada, usa como sufixo do doc_id para evitar duplicatas.
    """
    db = _get_db()
    if not db:
        return None

    inst_id = _get_instituicao_id()
    if chave_unica:
        doc_id = f"{inst_id}_{chave_unica}"
        doc_ref = db.collection(COLECAO_NOTIFICACOES).document(doc_id)
        if doc_ref.get().exists:
            return None
    else:
        doc_ref = db.collection(COLECAO_NOTIFICACOES).document()

    notif = {
        "id": doc_ref.id,
        "instituicao_id": inst_id,
        "destinatario_uid": (destinatario_uid or "").strip(),
        "destinatario_nome": (destinatario_nome or "").strip(),
        "titulo": titulo,
        "mensagem": mensagem,
        "tipo": tipo,
        "rota": rota,
        "aba": aba,
        "lida": False,
        "createdAt": agora_str(),
    }
    doc_ref.set(notif)
    return notif


# ── Gatilhos de Solicitações ──────────────────────────────────────────────────

def notificar_evento_solicitacao(sol: dict, evento: str, ator: str = "", motivo: str = "") -> None:
    """
    Notifica o solicitante sobre mudanças na sua solicitação/reserva.
    Eventos: 'aprovada', 'recusada', 'cancelada', 'excluida'
    """
    uid = sol.get("solicitanteUid")
    nome = sol.get("solicitante", "Usuário")
    sala = sol.get("sala", "")
    data_str = sol.get("data", "")
    horario = f"{sol.get('inicio', '')}–{sol.get('fim', '')}"

    if evento == "aprovada":
        titulo = f"✅ Reserva aprovada: {sala}"
        mensagem = (
            f"Sua solicitação para {sala} no dia {data_str} ({horario}) "
            f"foi aprovada por {ator}."
        )
        tipo = "sucesso"

    elif evento == "recusada":
        titulo = f"❌ Solicitação recusada: {sala}"
        obs_txt = f" Motivo: {motivo}" if motivo else ""
        mensagem = (
            f"Sua solicitação para {sala} no dia {data_str} ({horario}) "
            f"foi recusada por {ator}.{obs_txt}"
        )
        tipo = "erro"

    elif evento == "cancelada":
        titulo = f"⚠️ Reserva cancelada: {sala}"
        obs_txt = f" ({motivo})" if motivo else ""
        mensagem = (
            f"A reserva da sala {sala} no dia {data_str} ({horario}) foi cancelada{obs_txt}."
        )
        tipo = "alerta"

    elif evento == "excluida":
        titulo = f"🗑️ Reserva removida: {sala}"
        mensagem = (
            f"O registro da sua reserva para {sala} no dia {data_str} ({horario}) "
            f"foi removido pelo administrador."
        )
        tipo = "alerta"

    else:
        return

    criar_notificacao(
        uid,
        nome,
        titulo,
        mensagem,
        tipo=tipo,
        rota="reservas",
        aba="minhas",
    )


def notificar_novo_pedido_aprovador(sol: dict) -> None:
    """
    Quando um aluno pede reserva ao professor, notifica o professor responsável.
    """
    if sol.get("tipo") == "aluno_para_professor" and sol.get("professorResponsavel"):
        criar_notificacao(
            destinatario_uid="",
            destinatario_nome=sol["professorResponsavel"],
            titulo=f"📩 Nova solicitação de aluno: {sol['sala']}",
            mensagem=(
                f"{sol['solicitante']} solicitou {sol['sala']} para "
                f"{sol['data']} ({sol['inicio']}–{sol['fim']})."
            ),
            tipo="info",
            rota="reservas",
            aba="aprovacoes",
        )


# ── Gatilhos de Salas ─────────────────────────────────────────────────────────

def notificar_reservas_afetadas(solicitacoes: list, sala_nome: str, acao: str) -> int:
    """
    Cancela reservas ativas na sala excluída/em manutenção e notifica os usuários.
    """
    db = _get_db()
    inst_id = _get_instituicao_id()
    status_ativos = ("Pendente", "Em análise", "Aprovado")
    notificados = 0

    for s in solicitacoes:
        if s.get("sala") != sala_nome or s.get("status") not in status_ativos:
            continue

        motivo = (
            f"Sala '{sala_nome}' foi excluída pelo administrador."
            if acao == "excluida"
            else f"Sala '{sala_nome}' entrou em manutenção."
        )
        s["status"] = "Cancelado"
        s["observacao"] = motivo

        if db:
            db.collection("solicitacoes").document(f"{inst_id}_{s['id']}").update({
                "status": "Cancelado",
                "observacao": motivo,
            })

        titulo = (
            f"🗑️ Sala excluída: {sala_nome}"
            if acao == "excluida"
            else f"🔧 Sala em manutenção: {sala_nome}"
        )
        mensagem = (
            f"Sua reserva do dia {s['data']} ({s['inicio']}–{s['fim']}) "
            f"foi cancelada porque a sala {sala_nome} "
            f"{'foi excluída do sistema' if acao == 'excluida' else 'entrou em manutenção'}."
        )

        criar_notificacao(
            destinatario_uid=s.get("solicitanteUid"),
            destinatario_nome=s.get("solicitante", "Usuário"),
            titulo=titulo,
            mensagem=mensagem,
            tipo="alerta",
            rota="reservas",
            aba="minhas",
        )
        notificados += 1

    return notificados


# ── Lembretes Automáticos de Reservas Próximas ────────────────────────────────

def verificar_lembretes_proximos(
    solicitacoes: list, usuario_uid: str | None, usuario_nome: str
) -> None:
    """
    Verifica reservas Aprovadas do usuário que acontecem hoje ou amanhã
    e gera lembretes únicos no Firestore.
    """
    agora = agora_br()
    hoje = hoje_br()
    amanha = hoje + timedelta(days=1)

    nome_norm = (usuario_nome or "").strip().lower()
    uid_norm = (usuario_uid or "").strip()

    for s in solicitacoes:
        if s.get("status") != "Aprovado":
            continue

        sol_uid = (s.get("solicitanteUid") or "").strip()
        sol_nome = (s.get("solicitante") or "").strip().lower()
        if not ((uid_norm and sol_uid == uid_norm) or (nome_norm and sol_nome == nome_norm)):
            continue

        try:
            data_res = datetime.strptime(s["data"], "%d/%m/%Y").date()
            hora_ini = datetime.strptime(s["inicio"], "%H:%M").time()
        except (ValueError, KeyError):
            continue

        if data_res == amanha:
            criar_notificacao(
                destinatario_uid=usuario_uid,
                destinatario_nome=usuario_nome,
                titulo=f"📅 Lembrete: reserva amanhã ({s['sala']})",
                mensagem=(
                    f"Você tem uma reserva confirmada para amanhã ({s['data']}) "
                    f"das {s['inicio']} às {s['fim']} em {s['sala']}."
                ),
                tipo="lembrete",
                chave_unica=f"lembrete_amanha_{s['id']}",
                rota="reservas",
                aba="minhas",
            )

        elif data_res == hoje and hora_ini >= agora.time():
            criar_notificacao(
                destinatario_uid=usuario_uid,
                destinatario_nome=usuario_nome,
                titulo=f"⏰ É hoje! Reserva em {s['sala']}",
                mensagem=(
                    f"Sua reserva em {s['sala']} começa hoje às {s['inicio']} "
                    f"(término às {s['fim']})."
                ),
                tipo="lembrete",
                chave_unica=f"lembrete_hoje_{s['id']}",
                rota="reservas",
                aba="minhas",
            )


# ── Consultas e Leitura ───────────────────────────────────────────────────────

def listar_minhas_notificacoes(usuario_uid: str | None, usuario_nome: str) -> list:
    db = _get_db()
    if not db:
        return []

    inst_id = _get_instituicao_id()
    docs = (
        db.collection(COLECAO_NOTIFICACOES)
        .where("instituicao_id", "==", inst_id)
        .stream()
    )

    uid_norm = (usuario_uid or "").strip()
    nome_norm = (usuario_nome or "").strip().lower()
    resultado = []

    for doc in docs:
        n = doc.to_dict()
        n["id"] = doc.id
        dest_uid = (n.get("destinatario_uid") or "").strip()
        dest_nome = (n.get("destinatario_nome") or "").strip().lower()

        if (uid_norm and dest_uid == uid_norm) or (not dest_uid and nome_norm and dest_nome == nome_norm):
            resultado.append(n)

    resultado.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return resultado


def marcar_como_lida(notif_id: str) -> None:
    db = _get_db()
    if db:
        db.collection(COLECAO_NOTIFICACOES).document(notif_id).update({"lida": True})


def marcar_todas_como_lidas(notif_ids: list[str]) -> None:
    db = _get_db()
    if not db:
        return
    for nid in notif_ids:
        db.collection(COLECAO_NOTIFICACOES).document(nid).update({"lida": True})