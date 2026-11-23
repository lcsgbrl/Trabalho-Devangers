# -*- coding: utf-8 -*-
"""[VIEW] Membros — equivalente a src/pages/Membros.tsx."""

import re
import streamlit as st

from controllers import academico_controller, auth_controller, membros_controller as mc
from models import domain_data as data
from views.components import badge_html


@st.dialog("Membro")
def member_modal(member=None):
    editing = member is not None
    funcoes_permitidas = mc.allowed_funcoes()

    if not funcoes_permitidas:
        st.error("Você não tem permissão para gerenciar membros.")
        return

    st.markdown(f"##### {'Editar Membro' if editing else 'Adicionar Membro'}")
    nome = st.text_input("Nome completo *", value=member["nome"] if editing else "")
    email = st.text_input("E-mail *", value=member["email"] if editing else "")
    c1, c2 = st.columns(2)

    if editing and member["funcao"] in funcoes_permitidas:
        default_idx = funcoes_permitidas.index(member["funcao"])
    elif "Professor" in funcoes_permitidas and len(funcoes_permitidas) == 1:
        default_idx = 0
    elif "Aluno" in funcoes_permitidas:
        default_idx = funcoes_permitidas.index("Aluno")
    else:
        default_idx = 0

    funcao = c1.selectbox(
        "Função",
        funcoes_permitidas,
        index=default_idx,
        disabled=(len(funcoes_permitidas) == 1),
    )
    depto = c2.text_input("Departamento", value=member.get("depto", "") if editing else "")
    nucleo_opts = ["— Global (sem restrição) —"] + [n["nome"] for n in academico_controller.list_nucleos() if n["ativo"]]
    cur_nucleo = member.get("nucleo") if editing else None
    nucleo_sel = st.selectbox(
        "Núcleo",
        nucleo_opts,
        index=nucleo_opts.index(cur_nucleo) if cur_nucleo in nucleo_opts else 0,
    )
    status = st.radio(
        "Status",
        ["Ativo", "Inativo"],
        index=0 if not editing or member["status"] == "Ativo" else 1,
        horizontal=True,
    )

    if st.button("Salvar" if editing else "Adicionar", type="primary", use_container_width=True):
        nome = nome.strip()
        email = email.strip()

        if len(nome) < 3:
            st.error("Informe um nome com pelo menos 3 caracteres.")
        elif len(email) > 254 or not re.fullmatch(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+",
            email,
        ):
            st.error("Informe um endereço de e-mail válido.")
        else:
            payload = {
                "nome": nome,
                "email": email,
                "funcao": funcao,
                "depto": depto.strip(),
                "nucleo": None if nucleo_sel.startswith("—") else nucleo_sel,
                "status": status,
            }

            if editing:
                try:
                    mc.update_member(member["id"], payload)
                except (ValueError, PermissionError) as erro:
                    st.error(str(erro))
                else:
                    st.toast("Membro atualizado com sucesso!")
                    st.rerun()
            else:
                try:
                    mc.add_member_directly(payload)
                except (ValueError, PermissionError) as erro:
                    st.error(str(erro))
                else:
                    st.toast(f"{nome} adicionado(a) com sucesso!")
                    st.rerun()


@st.dialog("Remover membro?")
def confirm_delete_modal(member):
    st.warning(f"**{member['nome']}** será removido permanentemente do sistema. Esta ação não pode ser desfeita.")
    c1, c2 = st.columns(2)
    if c1.button("Cancelar", use_container_width=True):
        st.rerun()
    if c2.button("Remover", type="primary", use_container_width=True):
        try:
            mc.remove_member(member["id"])
        except (ValueError, PermissionError) as erro:
            st.error(str(erro))
        else:
            st.toast("Membro removido.", icon="✅")
            st.rerun()


def render():
    is_admin = auth_controller.is_admin()
    funcoes_permitidas = mc.allowed_funcoes()
    pode_criar = len(funcoes_permitidas) > 0

    st.markdown('<div class="sga-eyebrow">EQUIPE</div>', unsafe_allow_html=True)
    hc1, hc2 = st.columns([3, 1])
    hc1.markdown("<div class='sga-title'>Organização de Membros</div>", unsafe_allow_html=True)
    if is_admin:
        hc1.caption("Gerencie os membros e organize as informações da equipe.")
    else:
        hc1.caption("Gerencie os professores vinculados à instituição.")

    if pode_criar:
        btn_label = "➕ Adicionar Membro" if is_admin else "➕ Adicionar Professor"
        if st.button(btn_label, type="primary"):
            member_modal()

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    search = c1.text_input("Buscar por nome ou e-mail", key="mem_search")

    if len(funcoes_permitidas) > 1:
        filtro_funcao = c2.selectbox("Função", ["Todos"] + funcoes_permitidas, key="mem_funcao")
    elif len(funcoes_permitidas) == 1:
        filtro_funcao = c2.selectbox("Função", funcoes_permitidas, key="mem_funcao", disabled=True)
    else:
        filtro_funcao = "Todos"

    filtro_status = c3.selectbox("Status", ["Todos", "Ativo", "Inativo"], key="mem_status")
    nucleos = [n["nome"] for n in academico_controller.list_nucleos() if n["ativo"]]
    filtro_nucleo = c4.selectbox("Núcleo", ["Todos", "Global"] + nucleos, key="mem_nucleo")

    filtered = mc.filter_members(search, filtro_funcao, filtro_status, filtro_nucleo)

    st.caption(f"{len(filtered)} membro(s)")

    for m in filtered:
        f_badge = data.FUNCAO_BADGE.get(m["funcao"], {"bg": "#F3EFEA", "text": "#776D5B"})
        s_badge = data.MEMBER_STATUS_BADGE.get(m["status"], data.MEMBER_STATUS_BADGE["Ativo"])
        pode_gerenciar_item = mc.can_manage_role(m["funcao"])

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([2.2, 1, 1, 1, 1.4])
            with c1:
                st.markdown(f"**{m['nome']}**")
                st.caption(m["email"])
            with c2:
                st.markdown(badge_html(m["funcao"], f_badge["bg"], f_badge["text"]), unsafe_allow_html=True)
            with c3:
                st.caption(m.get("nucleo") or "Global")
            with c4:
                st.caption(m.get("turma") or "—")
            with c5:
                st.markdown(
                    badge_html(m["status"], s_badge["bg"], s_badge["text"], s_badge["dot"]),
                    unsafe_allow_html=True,
                )

            if pode_gerenciar_item:
                ac1, ac2, ac3 = st.columns(3)
                if ac1.button("Editar", key=f"editm_{m['id']}", use_container_width=True):
                    member_modal(m)
                toggle_label = "Desativar" if m["status"] == "Ativo" else "Ativar"
                if ac2.button(toggle_label, key=f"togm_{m['id']}", use_container_width=True):
                    try:
                        mc.toggle_member_status(m["id"])
                    except (ValueError, PermissionError) as erro:
                        st.error(str(erro))
                    else:
                        st.rerun()
                if ac3.button("Remover", key=f"delm_{m['id']}", use_container_width=True):
                    confirm_delete_modal(m)

    if not filtered:
        st.info("Nenhum membro encontrado. Tente ajustar os filtros de busca.")