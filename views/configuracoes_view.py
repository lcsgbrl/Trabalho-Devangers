# -*- coding: utf-8 -*-
"""[VIEW] Configurações — equivalente a src/pages/Configuracoes.tsx."""

import streamlit as st

from controllers import auth_controller
from models import domain_data as data
from utils import auth_utils
from views.components import PRIMARY, badge_html


def _sga_alert(texto: str, tipo: str = "bege"):
    """Exibe caixa de aviso na paleta institucional (bege, vinho/vermelho ou verde)."""
    estilos = {
        "bege": ("#F5F2EB", "#D9D2C5", "#2C241E"),
        "vinho": ("#FFF0F2", "#FFD6D9", "#8B0019"),
        "verde": ("#EAF5EA", "#B8DFB8", "#2B5E2B"),
    }
    bg, border, fg = estilos.get(tipo, estilos["bege"])
    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {border};
            border-left:4px solid {fg};
            color:{fg};
            padding:0.75rem 1rem;
            border-radius:10px;
            font-size:0.9rem;
            line-height:1.45;
            margin:0.5rem 0 0.9rem 0;
        ">{texto}</div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Confirmar alteração de e-mail")
def confirmar_email_modal():
    """Pop-up institucional (vermelho/bege/branco/preto) para validar o código de 6 dígitos."""
    pendente = st.session_state.get("email_change_pending")
    if not pendente:
        st.rerun()
        return

    # Estilização local do modal na paleta do SGA (sem azul)
    st.markdown(
        f"""
        <style>
        div[data-testid="stDialog"] div[role="dialog"] {{
            background-color: #FAF9F6;
            border: 1px solid #D9D2C5;
            border-radius: 16px;
            color: #1F1B18;
        }}
        div[data-testid="stDialog"] div[data-testid="stTextInput"] input {{
            background-color: #FFFFFF !important;
            border: 1.5px solid #D9D2C5 !important;
            color: #1F1B18 !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.35em !important;
            text-align: center !important;
        }}
        div[data-testid="stDialog"] div[data-testid="stTextInput"] input:focus {{
            border-color: {PRIMARY} !important;
            box-shadow: 0 0 0 2px rgba(139, 0, 25, 0.15) !important;
        }}
        div[data-testid="stDialog"] button[kind="primary"] {{
            background-color: {PRIMARY} !important;
            border-color: {PRIMARY} !important;
            color: #FFFFFF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    _sga_alert(
        f"Enviamos um código de verificação de <b>6 dígitos</b> para:<br/>"
        f"<span style='font-weight:700;'>{pendente['novo_email']}</span>",
        tipo="bege",
    )

    codigo_digitado = st.text_input(
        "Código de verificação *",
        max_chars=6,
        placeholder="000000",
        key="modal_codigo_email_input",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", use_container_width=True, key="btn_cancelar_codigo_email"):
            st.session_state.pop("email_change_pending", None)
            st.rerun()

    with c2:
        if st.button("Confirmar código", type="primary", use_container_width=True, key="btn_confirmar_codigo_email"):
            if codigo_digitado.strip() != pendente["codigo"]:
                _sga_alert("Código incorreto. Verifique o e-mail recebido e tente novamente.", tipo="vinho")
            else:
                err = auth_controller.update_current_user_profile(
                    pendente["nome"],
                    pendente["novo_email"],
                )
                if err:
                    _sga_alert(err, tipo="vinho")
                else:
                    st.session_state.pop("email_change_pending", None)
                    st.toast("E-mail confirmado e perfil atualizado!", icon="✅")
                    st.rerun()

    st.write("")
    if st.button("Reenviar código", use_container_width=True, key="btn_reenviar_codigo_email"):
        novo_codigo = auth_utils.gerar_codigo_verificacao()
        enviado, msg_envio = auth_utils.enviar_codigo_confirmacao_email(
            pendente["novo_email"],
            pendente["nome"],
            novo_codigo,
        )
        if enviado:
            st.session_state["email_change_pending"]["codigo"] = novo_codigo
            _sga_alert("Um novo código foi enviado para a sua caixa de entrada.", tipo="verde")
        else:
            _sga_alert(msg_envio, tipo="vinho")


def render():
    user = auth_controller.current_user()
    rc = data.ROLE_COLORS[user["role"]]

    st.markdown('<div class="sga-eyebrow">SISTEMA</div>', unsafe_allow_html=True)
    st.markdown("<div class='sga-title'>Configurações</div>", unsafe_allow_html=True)
    st.caption("Preferências e configurações da sua conta.")

    initials = "".join(w[0] for w in user["nome"].split(" ")[:2]).upper()
    with st.container(border=True):
        c1, c2 = st.columns([1, 5])
        c1.markdown(
            f"<div style='width:56px;height:56px;border-radius:16px;background:{PRIMARY};"
            f"color:white;display:flex;align-items:center;justify-content:center;"
            f"font-weight:800;font-size:1.2rem;'>{initials}</div>",
            unsafe_allow_html=True,
        )
        with c2:
            st.markdown(f"**{user['nome']}**")
            st.caption(user["email"])
            st.markdown(badge_html(user["role"], rc["bg"], rc["text"], rc["dot"]), unsafe_allow_html=True)

    st.write("")
    with st.form("profile_form"):
        st.markdown("###### Informações do Perfil")
        st.caption("Atualize seu nome e e-mail de contato.")
        nome = st.text_input("Nome completo", value=user["nome"])
        email = st.text_input("E-mail institucional", value=user["email"])
        st.text_input("Cargo / Função (somente ADM)", value=user["role"], disabled=True)
        st.caption("O cargo só pode ser alterado por um administrador na lista de membros.")

        if st.form_submit_button("Salvar perfil", type="primary"):
            nome_limpo = nome.strip()
            email_novo = email.strip().lower()
            email_atual = user["email"].strip().lower()

            if len(nome_limpo) < 3:
                _sga_alert("O nome deve ter no mínimo 3 caracteres.", tipo="vinho")
            elif email_novo == email_atual:
                st.session_state.pop("email_change_pending", None)
                err = auth_controller.update_current_user_profile(nome_limpo, email_novo)
                if err:
                    _sga_alert(err, tipo="vinho")
                else:
                    st.toast("Perfil atualizado com sucesso!", icon="✅")
                    st.rerun()
            elif not auth_utils.validar_email(email_novo):
                _sga_alert("Informe um endereço de e-mail válido (ex.: nome@dominio.com).", tipo="vinho")
            elif not auth_utils.dominio_email_existe(email_novo):
                _sga_alert("O domínio deste e-mail não existe ou não recebe mensagens.", tipo="vinho")
            else:
                codigo = auth_utils.gerar_codigo_verificacao()
                enviado, msg_envio = auth_utils.enviar_codigo_confirmacao_email(
                    email_novo,
                    nome_limpo,
                    codigo,
                )
                if enviado:
                    st.session_state["email_change_pending"] = {
                        "nome": nome_limpo,
                        "novo_email": email_novo,
                        "codigo": codigo,
                    }
                    st.rerun()
                else:
                    _sga_alert(msg_envio, tipo="vinho")

    # Abre o pop-up automaticamente enquanto houver troca de e-mail aguardando código
    if st.session_state.get("email_change_pending"):
        confirmar_email_modal()

    st.write("")
    with st.form("password_form"):
        st.markdown("###### Segurança")
        st.caption("Altere sua senha de acesso.")
        st.caption(
            "⚠ Dica: uma senha forte deve conter letras maiúsculas, "
            "letras minúsculas, números e caracteres especiais."
        )
        nova = st.text_input("Nova senha *", type="password", placeholder="Mínimo 6 caracteres")
        confirmar = st.text_input("Confirmar nova senha *", type="password")
        if st.form_submit_button("Alterar senha", type="primary"):
            if not nova:
                _sga_alert("Informe a nova senha.", tipo="vinho")
            elif len(nova) < 6:
                _sga_alert("A nova senha deve ter pelo menos 6 caracteres.", tipo="vinho")
            elif nova != confirmar:
                _sga_alert("A confirmação não coincide com a nova senha.", tipo="vinho")
            else:
                sucesso, mensagem = auth_controller.atualizar_senha(nova)
                if sucesso:
                    _sga_alert(mensagem, tipo="verde")
                else:
                    _sga_alert(mensagem, tipo="vinho")