# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Membro (usuário da instituição).

Funções puras de CRUD e de fluxo de aprovação de cadastro. O Controller
(membros_controller) conecta estas funções ao st.session_state.
"""


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

    novo = dict(m)
    novo["email"] = novo["email"].strip()
    novo["id"] = next_id
    novo["initials"] = make_initials(novo["nome"])
    novo["source"] = "existing"
    members.append(novo)
    return novo, next_id + 1


def add_pending_member(members: list, next_id: int, m: dict) -> tuple[dict, int]:
    novo = dict(m)
    novo["id"] = next_id
    novo["status"] = "Pendente"
    novo["initials"] = make_initials(novo["nome"])
    novo["source"] = "request"
    members.append(novo)
    return novo, next_id + 1


def approve_member(members: list, member_id: int) -> None:
    for m in members:
        if m["id"] == member_id:
            m["status"] = "Ativo"
            m.pop("motivoRejeicao", None)
            m.pop("motivoCorrecao", None)
            return


def reject_member(members: list, member_id: int) -> list:
    return [m for m in members if m["id"] != member_id]


def remove_member(members: list, member_id: int) -> list:
    return [m for m in members if m["id"] != member_id]


def solicitar_correcao(members: list, member_id: int, motivo: str) -> None:
    for m in members:
        if m["id"] == member_id:
            m["status"] = "Aguardando Correção"
            m["motivoCorrecao"] = motivo
            return


def toggle_member_status(members: list, member_id: int) -> None:
    for m in members:
        if m["id"] == member_id:
            m["status"] = "Inativo" if m["status"] == "Ativo" else "Ativo"
            return



def update_member(members: list, member_id: int, data_new: dict) -> None:
    dados_atualizados = dict(data_new)

    if "email" in dados_atualizados:
        email = dados_atualizados["email"].strip()

        if email_exists(members, email, exclude_id=member_id):
            raise ValueError("Este e-mail já está cadastrado.")

        dados_atualizados["email"] = email

    for m in members:
        if m["id"] == member_id:
            m.update(dados_atualizados)

            if "nome" in dados_atualizados:
                m["initials"] = make_initials(dados_atualizados["nome"])

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
