# -*- coding: utf-8 -*-
"""
controllers/auth_controller.py

Controller para autenticação.
Gerencia session state + chamadas para o model.
"""

import streamlit as st
from models import auth_model
from models import permissions_model
from controllers import session_controller


def init_auth_state():
    """Inicializa estado de autenticação na sessão"""
    if 'user_uid' not in st.session_state:
        st.session_state.user_uid = None
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'user_nome' not in st.session_state:
        st.session_state.user_nome = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    if 'user_perfil' not in st.session_state:
        st.session_state.user_perfil = None

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if 'instituicao_id' not in st.session_state:
        st.session_state.instituicao_id = 'inst_001'


def is_logged_in():
    """Verifica se usuário está logado"""
    return st.session_state.get('user_uid') is not None


def fazer_login(email: str, senha: str):
    """
    Processa login do usuário
    
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    init_auth_state()
    email = (email or "").strip().lower()
    
    if not email or not senha:
        return False, "E-mail e senha são obrigatórios."

    if not auth_model.auth_utils.validar_email(email):
        return False, "Informe um endereço de e-mail válido."
    
    sucesso, uid, mensagem = auth_model.fazer_login(email, senha)
    
    if sucesso:
        perfil = auth_model.obter_perfil_usuario(uid)
        perfil["role"] = {
            "usuario": "Aluno",
            "professor": "Professor",
            "admin": "Administrador",
        }.get(perfil.get("role"), perfil.get("role"))

        inst_id = perfil.get("instituicao_id") or "inst_001"

        st.session_state.user_uid = uid
        st.session_state.user_email = email
        st.session_state.user_nome = perfil.get('nome')
        st.session_state.user_role = perfil.get('role')
        st.session_state.user_perfil = perfil
        st.session_state.current_user = perfil
        st.session_state.instituicao_id = inst_id
        st.session_state.logged_in = True

        # Carrega dados da instituição do Firestore ao entrar
        session_controller.carregar_dados_instituicao(inst_id)
        session_controller.goto("menu")
    
    return sucesso, mensagem


def fazer_registro(email: str, senha: str, nome: str, codigo_instituicao: str = "SGA2026"):
    init_auth_state()

    sucesso, uid, mensagem = auth_model.criar_nova_conta(
        email, senha, nome, codigo_instituicao=codigo_instituicao
    )

    return sucesso, mensagem


def fazer_logout():
    """Faz logout do usuário"""
    st.session_state.user_uid = None
    st.session_state.user_email = None
    st.session_state.user_nome = None
    st.session_state.user_role = None
    st.session_state.user_perfil = None
    st.session_state.current_user = None
    st.session_state.logged_in = False
    session_controller.limpar_dados_sessao()


def logout():
    """Alias mantido para as views que usam a nomenclatura antiga."""
    fazer_logout()


def atualizar_perfil(dados: dict):
    """Atualiza perfil do usuário logado"""
    if not is_logged_in():
        return False, "Usuário não está logado"
    
    uid = st.session_state.user_uid
    sucesso, mensagem = auth_model.atualizar_perfil(uid, dados)
    
    if sucesso:
        st.session_state.user_perfil = auth_model.obter_perfil_usuario(uid)
    
    return sucesso, mensagem


def atualizar_senha(nova_senha: str):
    """Atualiza a senha da conta autenticada no Firebase Authentication."""
    if not is_logged_in():
        return False, "Usuário não está logado"

    return auth_model.atualizar_senha(st.session_state.user_uid, nova_senha)


def update_current_user_profile(nome: str, email: str):
    """Atualiza nome e e-mail no perfil, no Firebase Auth e na sessão."""
    if not is_logged_in():
        return "Usuário não está logado."

    nome_limpo = (nome or "").strip()
    email_limpo = (email or "").strip().lower()

    if not nome_limpo or not email_limpo:
        return "Nome e e-mail são obrigatórios."

    uid = st.session_state.user_uid
    email_atual = st.session_state.get("user_email") or st.session_state.user_perfil.get("email", "")

    sucesso, mensagem = auth_model.atualizar_dados_conta(
        uid=uid,
        nome=nome_limpo,
        novo_email=email_limpo,
        email_atual=email_atual,
    )

    if sucesso:
        st.session_state.user_nome = nome_limpo
        st.session_state.user_email = email_limpo
        st.session_state.user_perfil.update({"nome": nome_limpo, "email": email_limpo})
        st.session_state.current_user = st.session_state.user_perfil

        for m in st.session_state.get("members", []):
            if m.get("uid") == uid or (m.get("email") or "").lower() == email_atual.lower():
                m["nome"] = nome_limpo
                m["email"] = email_limpo
                break
        return None

    return mensagem


def deletar_conta():
    """Deleta conta do usuário logado"""
    if not is_logged_in():
        return False, "Usuário não está logado"
    
    uid = st.session_state.user_uid
    sucesso, mensagem = auth_model.deletar_conta_completa(uid)
    
    if sucesso:
        fazer_logout()
    
    return sucesso, mensagem


def tem_permissao(permissao: str) -> bool:
    """Verifica se usuário tem determinada permissão"""
    if not is_logged_in():
        return False
    
    role = st.session_state.get('user_role', 'usuario')
    role = {
        'Aluno': 'usuario',
        'Professor': 'professor',
        'Coordenador': 'admin',
        'Administrador': 'admin',
    }.get(role, role)
    
    permissoes = {
        'usuario': ['ver_agenda', 'fazer_reservas'],
        'professor': ['ver_agenda', 'fazer_reservas', 'gerenciar_aulas'],
        'admin': ['ver_agenda', 'fazer_reservas', 'gerenciar_aulas', 'gerenciar_usuarios'],
    }
    
    return permissao in permissoes.get(role, [])


def permissions() -> dict:
    """Retorna as permissões do papel atual para as views do aplicativo."""
    role = st.session_state.get('user_role')
    if role in ('usuario', 'professor', 'admin'):
        role = {
            'usuario': 'Aluno',
            'professor': 'Professor',
            'admin': 'Administrador',
        }[role]
    return permissions_model.get_permissions(role)


def has_perm(permissao: str) -> bool:
    """Verifica uma permissão pelo nome usado na matriz de permissões."""
    role = st.session_state.get('user_role')
    return permissions_model.has_permission(role, permissao)


def is_admin() -> bool:
    """Indica se o usuário atual possui o papel de administrador."""
    return permissions_model.is_admin_role(st.session_state.get('user_role'))


def obter_info_usuario():
    """Retorna informações do usuário logado"""
    return {
        'uid': st.session_state.get('user_uid'),
        'email': st.session_state.get('user_email'),
        'nome': st.session_state.get('user_nome'),
        'role': st.session_state.get('user_role'),
        'instituicao_id': st.session_state.get('instituicao_id', 'inst_001'),
    }


def current_user():
    """Retorna o perfil compatível com as views do aplicativo."""
    perfil = (
        st.session_state.get('current_user')
        or st.session_state.get('user_perfil')
        or {}
    )

    nome = perfil.get('nome') or perfil.get('name') or 'Usuário'
    partes = nome.split()
    iniciais = ''.join(parte[0].upper() for parte in partes[:2])

    perfil['name'] = nome
    perfil['initials'] = iniciais

    return perfil

def consultar_perfil_primeiro_acesso(nome: str, email: str) -> dict:
    """Consulta o perfil pré-cadastrado para adaptar os campos do Primeiro Acesso."""
    init_auth_state()
    return auth_model.consultar_perfil_primeiro_acesso(nome=nome, email=email)


def carregar_academico_primeiro_acesso(instituicao_id: str | None = None) -> dict:
    """Carrega cursos, turmas e disciplinas para as listas do Primeiro Acesso."""
    init_auth_state()
    return auth_model.carregar_academico_primeiro_acesso(instituicao_id=instituicao_id)


def concluir_primeiro_acesso(
    nome: str,
    email: str,
    senha_temporaria: str,
    nova_senha: str,
    cursos_ids: list[int] | None = None,
    turma_id: int | None = None,
    disciplinas_ids: list[int] | None = None,
):
    init_auth_state()
    return auth_model.concluir_primeiro_acesso(
        nome=nome,
        email=email,
        senha_temporaria=senha_temporaria,
        nova_senha=nova_senha,
        cursos_ids=cursos_ids,
        turma_id=turma_id,
        disciplinas_ids=disciplinas_ids,
    )