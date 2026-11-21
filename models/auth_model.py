# -*- coding: utf-8 -*-
"""
models/auth_model.py

Model para gerenciar autenticação.
Integra Firebase Auth + Firestore com suporte multi-instituição.
"""

import streamlit as st
from datetime import datetime
from firebase_admin import auth
from utils import auth_utils

INSTITUICAO_PADRAO_ID = "inst_001"
CODIGO_INSTITUICAO_PADRAO = "SGA2026"


def validar_codigo_instituicao(codigo: str):
    """
    Busca a instituição pelo código no Firestore e verifica se está ativa.
    Retorna: (sucesso: bool, instituicao_id: str | None, mensagem: str)
    """
    db = st.session_state.firestore_db
    codigo_limpo = (codigo or "").strip().upper()

    if not codigo_limpo:
        return False, None, "Informe o código da instituição."

    docs = (
        db.collection("instituicoes")
        .where("codigo", "==", codigo_limpo)
        .limit(1)
        .stream()
    )

    inst_doc = next(docs, None)

    if not inst_doc:
        # Fallback para o MVP caso a coleção ainda não tenha sido populada manualmente
        if codigo_limpo == CODIGO_INSTITUICAO_PADRAO:
            return True, INSTITUICAO_PADRAO_ID, "Instituição padrão identificada."
        return False, None, "Código de instituição inválido."

    dados_inst = inst_doc.to_dict()
    if not dados_inst.get("ativo", False):
        return False, None, "Esta instituição está inativa no sistema."

    return True, inst_doc.id, f"Instituição identificada: {dados_inst.get('nome', inst_doc.id)}"


def criar_nova_conta(
    email: str,
    senha: str,
    nome: str,
    codigo_instituicao: str = CODIGO_INSTITUICAO_PADRAO,
):
    """
    Cria uma nova conta no Firebase Authentication
    e salva o perfil no Firestore vinculado à instituição.
    """

    # 1. Validar os dados básicos
    if not auth_utils.validar_email(email):
        return False, None, "E-mail inválido."

    if not auth_utils.validar_senha(senha):
        return False, None, "A senha deve ter no mínimo 6 caracteres."

    if len(nome) < 3:
        return False, None, "O nome deve ter no mínimo 3 caracteres."

    # 2. Validar código da instituição antes de criar o usuário no Auth
    inst_valida, instituicao_id, msg_inst = validar_codigo_instituicao(codigo_instituicao)
    if not inst_valida:
        return False, None, msg_inst

    # 3. Criar usuário no Firebase Authentication
    sucesso, uid, mensagem = auth_utils.registrar_usuario(email, senha)

    if not sucesso:
        return False, None, mensagem

    try:
        # 4. Criar perfil no Firestore já com instituicao_id
        db = st.session_state.firestore_db

        perfil_usuario = {
            "uid": uid,
            "nome": nome,
            "email": email,
            "role": "usuario",
            "instituicao_id": instituicao_id,
            "criado_em": datetime.now(),
            "ativo": True,
            "email_verificado": False,
        }

        db.collection("usuarios").document(uid).set(perfil_usuario)

        # 5. Enviar e-mail de confirmação
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
        doc = db.collection("usuarios").document(uid).get()

        if not doc.exists:
            return False, None, "Perfil do usuário não encontrado."

        perfil = doc.to_dict()

        # 4. Verificar se a conta está ativa
        if not perfil.get("ativo"):
            return False, None, "Esta conta está inativa."

        # 5. Garantir retrocompatibilidade para contas antigas sem instituicao_id
        atualizacoes = {}
        if not perfil.get("email_verificado"):
            atualizacoes["email_verificado"] = True

        if not perfil.get("instituicao_id"):
            atualizacoes["instituicao_id"] = INSTITUICAO_PADRAO_ID
            perfil["instituicao_id"] = INSTITUICAO_PADRAO_ID

        if atualizacoes:
            db.collection("usuarios").document(uid).update(atualizacoes)

        # Salvar instituicao_id na sessão do Streamlit para uso global nos models
        st.session_state["instituicao_id"] = perfil["instituicao_id"]

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
        doc = db.collection("usuarios").document(uid).get()

        if doc.exists:
            perfil = doc.to_dict()
            perfil.setdefault("instituicao_id", INSTITUICAO_PADRAO_ID)
            return perfil

        return None

    except Exception as e:
        st.error(f"Erro ao buscar perfil: {e}")
        return None


def atualizar_perfil(uid: str, dados: dict):
    """Atualiza o perfil do usuário no Firestore."""
    try:
        db = st.session_state.firestore_db
        # Impede alteração acidental de instituicao_id pelo perfil comum
        dados_seguros = {k: v for k, v in dados.items() if k != "instituicao_id"}
        dados_seguros["atualizado_em"] = datetime.now()

        db.collection("usuarios").document(uid).update(dados_seguros)
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
        sucesso, mensagem = auth_utils.deletar_usuario_auth(uid)
        if not sucesso:
            return False, mensagem

        db = st.session_state.firestore_db
        db.collection("usuarios").document(uid).delete()

        return True, "Conta deletada completamente."

    except Exception as e:
        return False, f"Erro: {str(e)}"
    
def concluir_primeiro_acesso(
    nome: str,
    email: str,
    senha_temporaria: str,
    nova_senha: str,
    curso: str,
    turma: str,
    materia: str,
):
    """
    Valida o pré-cadastro com a senha temporária, atualiza para a nova senha
    no Firebase Auth e grava o vínculo acadêmico no Firestore.
    """
    if len(nome.strip()) < 3:
        return False, "Informe seu nome completo."

    if not auth_utils.validar_email(email):
        return False, "E-mail inválido."

    if not senha_temporaria:
        return False, "Informe a senha temporária recebida."

    if not auth_utils.validar_senha(nova_senha):
        return False, "A nova senha deve ter no mínimo 6 caracteres."

    if senha_temporaria == nova_senha:
        return False, "A nova senha deve ser diferente da senha temporária."

    # 1. Valida e-mail e senha temporária no Firebase Auth
    sucesso, uid, _ = auth_utils.autenticar_usuario(email.strip(), senha_temporaria)
    if not sucesso:
        return False, "E-mail ou senha temporária inválidos."

    try:
        db = st.session_state.firestore_db
        doc_ref = db.collection("usuarios").document(uid)
        doc = doc_ref.get()

        if not doc.exists:
            return False, "Pré-cadastro não encontrado. Solicite ao administrador."

        perfil = doc.to_dict()
        if not perfil.get("ativo", True):
            return False, "Esta conta está inativa."

        # 2. Atualiza para a senha definitiva e marca e-mail como verificado no Auth
        auth.update_user(uid, password=nova_senha, email_verified=True)

        # 3. Atualiza perfil no Firestore com curso, turma e matéria
        atualizacoes = {
            "nome": nome.strip(),
            "curso": curso.strip(),
            "turma": turma.strip(),
            "materia": materia.strip(),
            "primeiro_acesso": False,
            "email_verificado": True,
            "atualizado_em": datetime.now(),
        }
        doc_ref.update(atualizacoes)

        # 4. Atualiza também o registro na coleção membros (se existir)
        membros_docs = (
            db.collection("membros")
            .where("email", "==", email.strip())
            .limit(1)
            .stream()
        )
        membro_doc = next(membros_docs, None)
        if membro_doc:
            db.collection("membros").document(membro_doc.id).update({
                "nome": nome.strip(),
                "curso": curso.strip(),
                "turma": turma.strip(),
                "materia": materia.strip(),
                "primeiroAcesso": False,
                "status": "Ativo",
            })

        return True, "Primeiro acesso concluído com sucesso! Faça login com sua nova senha."

    except Exception as e:
        return False, f"Erro ao concluir primeiro acesso: {str(e)}"
    