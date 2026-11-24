# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Membro (usuário da instituição).

Mantém compatibilidade com a interface de listas usada por membros_controller,
sincronizando cada operação com o Firestore isolada por instituicao_id.
"""
from datetime import datetime
from utils import auth_utils
import streamlit as st
from utils.datetime_utils import agora_br

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_MEMBROS = "membros"
COLECAO_USUARIOS = "usuarios"
MAPA_FUNCAO_ROLE = {
    "Aluno": "usuario",
    "Professor": "professor",
    "Coordenador": "Coordenador",
    "Administrador": "admin",
}
MAPA_ROLE_FUNCAO = {
    "admin": "Administrador",
    "Administrador": "Administrador",
    "Coordenador": "Coordenador",
    "coordenador": "Coordenador",
    "professor": "Professor",
    "Professor": "Professor",
    "usuario": "Aluno",
    "Aluno": "Aluno",
}


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, member_id: int) -> str:
    return f"{instituicao_id}_{member_id}"


def _sincronizar_status_usuario(db, email: str, inst_id: str, ativo: bool) -> None:
    """Reflete ativação/desativação na coleção usuarios para bloquear/liberar o login."""
    if not db or not email:
        return
    docs = (
        db.collection(COLECAO_USUARIOS)
        .where("email", "==", email.strip())
        .where("instituicao_id", "==", inst_id)
        .limit(1)
        .stream()
    )
    user_doc = next(docs, None)
    if user_doc:
        db.collection(COLECAO_USUARIOS).document(user_doc.id).update({"ativo": ativo})


def _excluir_usuario_completo(db, alvo: dict, inst_id: str) -> None:
    """Remove o usuário do Firebase Authentication e da coleção usuarios."""
    if not db or not alvo:
        return

    uid = alvo.get("uid")
    email = (alvo.get("email") or "").strip()

    if not uid and email:
        docs = (
            db.collection(COLECAO_USUARIOS)
            .where("email", "==", email)
            .where("instituicao_id", "==", inst_id)
            .limit(1)
            .stream()
        )
        user_doc = next(docs, None)
        if user_doc:
            uid = user_doc.id

    if uid:
        auth_utils.deletar_usuario_auth(uid)
        db.collection(COLECAO_USUARIOS).document(uid).delete()


def listar_membros_firestore(instituicao_id: str | None = None) -> tuple[list, int]:
    """
    Busca todos os membros da instituição no Firestore, importa automaticamente
    usuários da coleção 'usuarios' que ainda não possuam registro em 'membros'
    e devolve (lista, proximo_id).
    """
    db = _get_db()
    if not db:
        return [], 1

    inst_id = instituicao_id or _get_instituicao_id()
    docs = (
        db.collection(COLECAO_MEMBROS)
        .where("instituicao_id", "==", inst_id)
        .stream()
    )

    membros = [doc.to_dict() for doc in docs]
    emails_existentes = {
        (m.get("email") or "").strip().lower() for m in membros
    }
    next_id = max((m.get("id", 0) for m in membros), default=0) + 1

    # Sincroniza usuários da coleção 'usuarios' que ainda não estão em 'membros'
    for u_doc in db.collection(COLECAO_USUARIOS).stream():
        u = u_doc.to_dict() or {}
        u_inst = u.get("instituicao_id")

        # Se for usuário antigo sem instituicao_id na instituição padrão, vincula agora
        if not u_inst and inst_id == INSTITUICAO_PADRAO_ID:
            u_inst = inst_id
            db.collection(COLECAO_USUARIOS).document(u_doc.id).update({
                "instituicao_id": inst_id
            })

        if u_inst != inst_id:
            continue

        email_u = (u.get("email") or "").strip().lower()
        if email_u and email_u not in emails_existentes:
            nome_u = (u.get("nome") or email_u.split("@")[0]).strip()
            novo_membro = {
                "id": next_id,
                "uid": u.get("uid") or u_doc.id,
                "nome": nome_u,
                "email": (u.get("email") or "").strip(),
                "funcao": MAPA_ROLE_FUNCAO.get(u.get("role", ""), "Aluno"),
                "status": "Ativo" if u.get("ativo", True) else "Inativo",
                "instituicao_id": inst_id,
                "initials": make_initials(nome_u),
                "source": "existing",
                "nucleo": u.get("nucleo"),
                "turma": u.get("turma"),
            }
            db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, next_id)).set(novo_membro)
            membros.append(novo_membro)
            emails_existentes.add(email_u)
            next_id += 1

    membros.sort(key=lambda m: m.get("id", 0))
    next_id = max((m.get("id", 0) for m in membros), default=0) + 1
    return membros, next_id


def make_initials(nome: str) -> str:
    words = [w for w in nome.split(" ") if w and w[0].isalpha()]
    return "".join(w[0] for w in words[:2]).upper()


def email_exists(members: list, email: str, exclude_id: int = None) -> bool:
    email = email.strip().lower()

    for member in members:
        if member.get("email", "").strip().lower() == email:
            if member["id"] != exclude_id:
                return True

    return False


def add_member_directly(members: list, next_id: int, m: dict) -> tuple[dict, int]:
    if email_exists(members, m["email"]):
        raise ValueError("Este e-mail já está cadastrado.")

    inst_id = _get_instituicao_id()
    email = m["email"].strip()
    nome = m["nome"].strip()
    funcao = m.get("funcao", "Aluno")
    role_firestore = MAPA_FUNCAO_ROLE.get(funcao, "usuario")

    # 1. Gera senha temporária aleatória e cria conta no Firebase Auth
    senha_temp = auth_utils.gerar_senha_temporaria()
    uid = None
    db = _get_db()

    if db:
        sucesso_auth, uid, msg_auth = auth_utils.registrar_usuario(email, senha_temp)
        if not sucesso_auth:
            raise ValueError(msg_auth)

        try:
            # 2. Cria perfil pré-cadastrado na coleção usuarios/{uid}
            perfil_usuario = {
                "uid": uid,
                "nome": nome,
                "email": email,
                "role": role_firestore,
                "instituicao_id": inst_id,
                "ativo": m.get("status", "Ativo") == "Ativo",
                "email_verificado": False,
                "primeiro_acesso": True,
                "criado_em": agora_br(),
            }
            db.collection(COLECAO_USUARIOS).document(uid).set(perfil_usuario)

            # 3. Envia automaticamente o e-mail com a senha temporária
            enviado, msg_email = auth_utils.enviar_email_primeiro_acesso(
                email, nome, senha_temp
            )
            if not enviado:
                st.warning(f"Membro cadastrado, mas o e-mail não foi enviado: {msg_email}")

        except Exception as e:
            if uid:
                auth_utils.deletar_usuario_auth(uid)
            raise ValueError(f"Erro ao salvar pré-cadastro no Firestore: {e}")

    novo = dict(m)
    novo["email"] = email
    novo["id"] = next_id
    novo["uid"] = uid
    novo["instituicao_id"] = inst_id
    novo["initials"] = make_initials(nome)
    novo["source"] = "existing"
    novo["senhaTemporaria"] = senha_temp
    novo["primeiroAcesso"] = True

    if db:
        db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, next_id)).set(novo)
        st.session_state["ultimo_membro_criado_info"] = {
            "nome": nome,
            "email": email,
            "senha_temporaria": senha_temp,
        }

    members.append(novo)
    return novo, next_id + 1


def add_pending_member(members: list, next_id: int, m: dict) -> tuple[dict, int]:
    inst_id = _get_instituicao_id()
    novo = dict(m)
    novo["id"] = next_id
    novo["instituicao_id"] = inst_id
    novo["status"] = "Pendente"
    novo["initials"] = make_initials(novo["nome"])
    novo["source"] = "request"

    db = _get_db()
    if db:
        db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, next_id)).set(novo)

    members.append(novo)
    return novo, next_id + 1


def approve_member(members: list, member_id: int) -> None:
    inst_id = _get_instituicao_id()
    for m in members:
        if m["id"] == member_id:
            m["status"] = "Ativo"
            m.pop("motivoRejeicao", None)
            m.pop("motivoCorrecao", None)

            db = _get_db()
            if db:
                db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).set(m)
                _sincronizar_status_usuario(db, m.get("email", ""), inst_id, True)
            return


def reject_member(members: list, member_id: int) -> list:
    inst_id = _get_instituicao_id()
    alvo = next((m for m in members if m["id"] == member_id), None)

    db = _get_db()
    if db and alvo:
        db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).delete()
        _excluir_usuario_completo(db, alvo, inst_id)

    return [m for m in members if m["id"] != member_id]


def remove_member(members: list, member_id: int) -> list:
    inst_id = _get_instituicao_id()
    alvo = next((m for m in members if m["id"] == member_id), None)

    db = _get_db()
    if db and alvo:
        db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).delete()
        _excluir_usuario_completo(db, alvo, inst_id)

    return [m for m in members if m["id"] != member_id]


def solicitar_correcao(members: list, member_id: int, motivo: str) -> None:
    inst_id = _get_instituicao_id()
    for m in members:
        if m["id"] == member_id:
            m["status"] = "Aguardando Correção"
            m["motivoCorrecao"] = motivo

            db = _get_db()
            if db:
                db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).update({
                    "status": "Aguardando Correção",
                    "motivoCorrecao": motivo,
                })
            return


def toggle_member_status(members: list, member_id: int) -> None:
    inst_id = _get_instituicao_id()
    for m in members:
        if m["id"] == member_id:
            novo_status = "Inativo" if m["status"] == "Ativo" else "Ativo"
            m["status"] = novo_status

            db = _get_db()
            if db:
                db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).update({
                    "status": novo_status
                })
                _sincronizar_status_usuario(
                    db, m.get("email", ""), inst_id, novo_status == "Ativo"
                )
            return


def update_member(members: list, member_id: int, data_new: dict) -> None:
    dados_atualizados = dict(data_new)

    if "email" in dados_atualizados:
        email = dados_atualizados["email"].strip()

        if email_exists(members, email, exclude_id=member_id):
            raise ValueError("Este e-mail já está cadastrado.")

        dados_atualizados["email"] = email

    inst_id = _get_instituicao_id()
    for m in members:
        if m["id"] == member_id:
            m.update(dados_atualizados)
            m["instituicao_id"] = inst_id

            if "nome" in dados_atualizados:
                m["initials"] = make_initials(dados_atualizados["nome"])

            db = _get_db()
            if db:
                db.collection(COLECAO_MEMBROS).document(_doc_id(inst_id, member_id)).set(m)
            return


# ── Consultas / filtros ──────────────────────────────────────────────────────

def pending_requests(members: list) -> list:
    return [m for m in members if m["source"] == "request" and m["status"] != "Ativo"]


def filter_members(members: list, search: str, funcao: str, status: str, nucleo: str) -> list:
    filtered = []
    for m in members:
        if search and search.lower() not in m["nome"].lower() and search.lower() not in m["email"].lower():
            continue
        if funcao != "Todos" and m["funcao"] != funcao:
            continue
        if status != "Todos" and m["status"] != status:
            continue
        if nucleo == "Global" and m.get("nucleo"):
            continue
        elif nucleo not in ("Todos", "Global") and m.get("nucleo") != nucleo:
            continue
        filtered.append(m)
    return filtered