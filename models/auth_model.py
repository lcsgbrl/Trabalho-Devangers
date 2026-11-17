# -*- coding: utf-8 -*-
"""
models/auth_model.py

Model para gerenciar autenticação.
Integra Firebase Auth + Firestore.
"""

import streamlit as st
from datetime import datetime
from firebase_admin import auth
from utils import auth_utils


def criar_nova_conta(email: str, senha: str, nome: str):
    """
    Cria uma nova conta no Firebase Authentication
    e salva o perfil no Firestore.
    """

    # 1. Validar os dados
    if not auth_utils.validar_email(email):
        return False, None, "E-mail inválido."

    if not auth_utils.validar_senha(senha):
        return False, None, "A senha deve ter no mínimo 6 caracteres."

    if len(nome) < 3:
        return False, None, "O nome deve ter no mínimo 3 caracteres."

    # 2. Criar usuário no Firebase Authentication
    sucesso, uid, mensagem = auth_utils.registrar_usuario(email, senha)

    if not sucesso:
        return False, None, mensagem

    try:
        # 3. Criar perfil no Firestore
        db = st.session_state.firestore_db

        perfil_usuario = {
            'uid': uid,
            'nome': nome,
            'email': email,
            'role': 'usuario',
            'criado_em': datetime.now(),
            'ativo': True,
            'email_verificado': False,
        }

        db.collection('usuarios').document(uid).set(perfil_usuario)

        # 4. Enviar e-mail de confirmação
        email_enviado, mensagem_email = auth_utils.enviar_verificacao_email(
            email, senha
        )

        if email_enviado:
            return True, uid, (
                "Conta criada com sucesso! "
                "Enviamos um e-mail para confirmar seu endereço. "
                "Verifique também a caixa de spam."
            )

        return True, uid, (
            "Conta criada, mas não foi possível enviar o e-mail de confirmação. "
            "Será necessário solicitar um novo envio. "
            + mensagem_email
        )

    except Exception as e:
        # Remover a conta caso ocorra erro ao criar o perfil
        auth_utils.deletar_usuario_auth(uid)
        return False, None, f"Erro ao criar perfil: {str(e)}"


def fazer_login(email: str, senha: str):
    """
    Autentica o usuário e verifica seu perfil no Firestore.
    """

    # 1. Autenticar e-mail e senha
    sucesso, uid, mensagem = auth_utils.autenticar_usuario(email, senha)

    if not sucesso:
        return False, None, mensagem

    try:
        # 2. Verificar se o e-mail foi confirmado
        usuario = auth.get_user(uid)

        if not usuario.email_verified:
            return False, None, (
                "E-mail não verificado. "
                "Verifique sua caixa de entrada."
            )

        # 3. Buscar perfil no Firestore
        db = st.session_state.firestore_db
        doc = db.collection('usuarios').document(uid).get()

        if not doc.exists:
            return False, None, "Perfil do usuário não encontrado."

        perfil = doc.to_dict()

        # 4. Verificar se a conta está ativa
        if not perfil.get('ativo'):
            return False, None, "Esta conta está inativa."

        # 5. Atualizar confirmação do e-mail no Firestore
        if not perfil.get('email_verificado'):
            db.collection('usuarios').document(uid).update({
                'email_verificado': True
        })

        # 6. Login concluído
        return True, uid, f"Bem-vindo, {perfil.get('nome')}!"

    except Exception:
        return False, None, (
            "Erro ao consultar os dados do usuário no Firebase."
        )


def obter_perfil_usuario(uid: str):
    """Busca o perfil completo no Firestore."""

    try:
        db = st.session_state.firestore_db
        doc = db.collection('usuarios').document(uid).get()

        if doc.exists:
            return doc.to_dict()

        return None

    except Exception as e:
        st.error(f"Erro ao buscar perfil: {e}")
        return None


def atualizar_perfil(uid: str, dados: dict):
    """Atualiza o perfil do usuário no Firestore."""

    try:
        db = st.session_state.firestore_db

        dados['atualizado_em'] = datetime.now()

        db.collection('usuarios').document(uid).update(dados)

        return True, "Perfil atualizado."

    except Exception as e:
        return False, f"Erro: {str(e)}"


def atualizar_senha(uid: str, nova_senha: str):
    """Atualiza a senha no Firebase Authentication."""

    if not auth_utils.validar_senha(nova_senha):
        return False, "A senha deve ter no mínimo 6 caracteres."

    return auth_utils.atualizar_senha(uid, nova_senha)


def deletar_conta_completa(uid: str):
    """Deleta a conta do Firebase Authentication e do Firestore."""

    try:
        # 1. Deletar do Firebase Authentication
        sucesso, mensagem = auth_utils.deletar_usuario_auth(uid)

        if not sucesso:
            return False, mensagem

        # 2. Deletar do Firestore
        db = st.session_state.firestore_db
        db.collection('usuarios').document(uid).delete()

        return True, "Conta deletada completamente."

    except Exception as e:
        return False, f"Erro: {str(e)}"
