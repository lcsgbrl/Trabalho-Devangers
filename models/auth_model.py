# -*- coding: utf-8 -*-
"""
models/auth_model.py

Model para gerenciar autenticação.
Integra Firebase Auth + Firestore com suporte multi-instituição.
"""

import streamlit as st
from firebase_admin import auth
from models import academico_model
from utils import auth_utils
from utils.datetime_utils import agora_br

INSTITUICAO_PADRAO_ID = "inst_001"
CODIGO_INSTITUICAO_PADRAO = "SGA2026"


def _normalizar_role(role_raw: str | None) -> str:
    r = (role_raw or "").strip().lower()
    if r in ("professor",):
        return "professor"
    if r in ("coordenador",):
        return "coordenador"
    if r in ("admin", "administrador"):
        return "admin"
    return "aluno"


def consultar_perfil_primeiro_acesso(nome: str, email: str) -> dict:
    """
    Consulta o pré-cadastro pelo e-mail nas coleções `usuarios` e `membros`
    para identificar o perfil (role) e a instituição antes de concluir o primeiro acesso.
    """
    email_limpo = (email or "").strip().lower()
    nome_limpo = (nome or "").strip()

    if not email_limpo or not auth_utils.validar_email(email_limpo):
        return {
            "encontrado": False,
            "role_normalizado": None,
            "role_raw": None,
            "instituicao_id": INSTITUICAO_PADRAO_ID,
            "nome_cadastrado": "",
            "mensagem": "Informe um e-mail válido para identificar seu perfil.",
        }

    db = st.session_state.get("firestore_db")
    if not db:
        return {
            "encontrado": False,
            "role_normalizado": None,
            "role_raw": None,
            "instituicao_id": INSTITUICAO_PADRAO_ID,
            "nome_cadastrado": "",
            "mensagem": "Conexão com o banco indisponível no momento.",
        }

    try:
        # 1. Busca na coleção `usuarios`
        user_doc = next(
            db.collection("usuarios").where("email", "==", email_limpo).limit(1).stream(),
            None,
        )
        # Fallback caso o e-mail tenha sido salvo com maiúsculas/minúsculas mistas
        if not user_doc and (email or "").strip():
            user_doc = next(
                db.collection("usuarios")
                .where("email", "==", (email or "").strip())
                .limit(1)
                .stream(),
                None,
            )

        # 2. Busca na coleção `membros` (caso exista lá com funcao/instituicao_id)
        membro_doc = next(
            db.collection("membros").where("email", "==", email_limpo).limit(1).stream(),
            None,
        )
        if not membro_doc and (email or "").strip():
            membro_doc = next(
                db.collection("membros")
                .where("email", "==", (email or "").strip())
                .limit(1)
                .stream(),
                None,
            )

        dados_user = user_doc.to_dict() if user_doc else {}
        dados_membro = membro_doc.to_dict() if membro_doc else {}

        if not dados_user and not dados_membro:
            return {
                "encontrado": False,
                "role_normalizado": None,
                "role_raw": None,
                "instituicao_id": INSTITUICAO_PADRAO_ID,
                "nome_cadastrado": "",
                "mensagem": "Pré-cadastro não encontrado para este e-mail. Verifique com o administrador.",
            }

        if dados_user.get("ativo") is False or dados_membro.get("status") == "Inativo":
            return {
                "encontrado": False,
                "role_normalizado": None,
                "role_raw": None,
                "instituicao_id": dados_user.get("instituicao_id")
                or dados_membro.get("instituicao_id")
                or INSTITUICAO_PADRAO_ID,
                "nome_cadastrado": dados_user.get("nome") or dados_membro.get("nome") or "",
                "mensagem": "Esta conta está inativa. Procure o administrador.",
            }

        role_raw = dados_user.get("role") or dados_membro.get("funcao") or "usuario"
        role_norm = _normalizar_role(role_raw)
        inst_id = (
            dados_user.get("instituicao_id")
            or dados_membro.get("instituicao_id")
            or INSTITUICAO_PADRAO_ID
        )
        nome_cadastrado = (dados_user.get("nome") or dados_membro.get("nome") or "").strip()

        alerta_nome = ""
        if nome_limpo and nome_cadastrado and nome_limpo.lower() != nome_cadastrado.lower():
            alerta_nome = f" (cadastrado como: {nome_cadastrado})"

        rotulo_perfil = {
            "professor": "Professor",
            "aluno": "Aluno",
            "coordenador": "Coordenador",
            "admin": "Administrador",
        }.get(role_norm, "Usuário")

        return {
            "encontrado": True,
            "role_normalizado": role_norm,
            "role_raw": role_raw,
            "instituicao_id": inst_id,
            "nome_cadastrado": nome_cadastrado,
            "mensagem": f"Perfil identificado: {rotulo_perfil}{alerta_nome}.",
        }

    except Exception as e:
        return {
            "encontrado": False,
            "role_normalizado": None,
            "role_raw": None,
            "instituicao_id": INSTITUICAO_PADRAO_ID,
            "nome_cadastrado": "",
            "mensagem": f"Erro ao consultar pré-cadastro: {e}",
        }


def carregar_academico_primeiro_acesso(instituicao_id: str | None = None) -> dict:
    """
    Carrega núcleos, cursos, turmas e disciplinas da instituição para popular
    as listas do Primeiro Acesso antes do login.
    """
    inst_id = instituicao_id or INSTITUICAO_PADRAO_ID
    try:
        return academico_model.listar_academico_firestore(inst_id)
    except Exception:
        return {
            "nucleos": [],
            "cursos": [],
            "turmas": [],
            "disciplinas": [],
            "max_id": 0,
        }


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
    if not auth_utils.validar_email(email):
        return False, None, "E-mail inválido."

    if not auth_utils.validar_senha(senha):
        return False, None, "A senha deve ter no mínimo 6 caracteres."

    if len(nome) < 3:
        return False, None, "O nome deve ter no mínimo 3 caracteres."

    inst_valida, instituicao_id, msg_inst = validar_codigo_instituicao(codigo_instituicao)
    if not inst_valida:
        return False, None, msg_inst

    sucesso, uid, mensagem = auth_utils.registrar_usuario(email, senha)
    if not sucesso:
        return False, None, mensagem

    try:
        db = st.session_state.firestore_db

        perfil_usuario = {
            "uid": uid,
            "nome": nome,
            "email": email,
            "role": "usuario",
            "instituicao_id": instituicao_id,
            "criado_em": agora_br(),
            "ativo": True,
            "email_verificado": False,
        }

        db.collection("usuarios").document(uid).set(perfil_usuario)

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
    sucesso, uid, mensagem = auth_utils.autenticar_usuario(email, senha)
    if not sucesso:
        return False, None, mensagem

    try:
        usuario = auth.get_user(uid)

        if not usuario.email_verified:
            return False, None, (
                "E-mail não verificado. "
                "Verifique sua caixa de entrada."
            )

        db = st.session_state.firestore_db
        doc = db.collection("usuarios").document(uid).get()

        if not doc.exists:
            return False, None, "Perfil do usuário não encontrado."

        perfil = doc.to_dict()

        if not perfil.get("ativo"):
            return False, None, "Esta conta está inativa."

        atualizacoes = {}
        if not perfil.get("email_verificado"):
            atualizacoes["email_verificado"] = True

        if not perfil.get("instituicao_id"):
            atualizacoes["instituicao_id"] = INSTITUICAO_PADRAO_ID
            perfil["instituicao_id"] = INSTITUICAO_PADRAO_ID

        if atualizacoes:
            db.collection("usuarios").document(uid).update(atualizacoes)

        st.session_state["instituicao_id"] = perfil["instituicao_id"]
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
        dados_seguros = {k: v for k, v in dados.items() if k != "instituicao_id"}
        dados_seguros["atualizado_em"] = agora_br()

        db.collection("usuarios").document(uid).update(dados_seguros)
        return True, "Perfil atualizado."

    except Exception as e:
        return False, f"Erro: {str(e)}"


def atualizar_dados_conta(uid: str, nome: str, novo_email: str, email_atual: str):
    """
    Valida nome e e-mail, atualiza o Firebase Authentication (se o e-mail mudou)
    e sincroniza os dados nas coleções `usuarios` e `membros`.
    """
    nome_limpo = (nome or "").strip()
    email_limpo = (novo_email or "").strip().lower()
    email_antigo = (email_atual or "").strip().lower()

    if len(nome_limpo) < 3:
        return False, "O nome deve ter no mínimo 3 caracteres."

    if not auth_utils.validar_email(email_limpo):
        return False, "Informe um endereço de e-mail válido (ex.: nome@dominio.com)."

    if not auth_utils.dominio_email_existe(email_limpo):
        return False, "O domínio deste e-mail não existe ou não recebe mensagens."

    if email_limpo != email_antigo:
        sucesso_auth, msg_auth = auth_utils.atualizar_email(uid, email_limpo)
        if not sucesso_auth:
            return False, msg_auth.replace("❌ ", "")

    try:
        db = st.session_state.firestore_db
        db.collection("usuarios").document(uid).update({
            "nome": nome_limpo,
            "email": email_limpo,
            "atualizado_em": agora_br(),
        })

        membros_ref = db.collection("membros")
        docs_por_uid = list(membros_ref.where("uid", "==", uid).limit(1).stream())
        alvo_doc = docs_por_uid[0] if docs_por_uid else next(
            membros_ref.where("email", "==", email_antigo).limit(1).stream(),
            None,
        )
        if alvo_doc:
            membros_ref.document(alvo_doc.id).update({
                "nome": nome_limpo,
                "email": email_limpo,
            })

        return True, "Perfil atualizado com sucesso."

    except Exception as e:
        if email_limpo != email_antigo:
            auth_utils.atualizar_email(uid, email_antigo)
        return False, f"Erro ao salvar perfil no banco de dados: {e}"


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
    cursos_ids: list[int] | None = None,
    turma_id: int | None = None,
    disciplinas_ids: list[int] | None = None,
):
    """
    Valida o pré-cadastro com a senha temporária, atualiza para a nova senha
    no Firebase Auth e grava o vínculo acadêmico conforme o perfil no Firestore.
    """
    nome_limpo = (nome or "").strip()
    email_limpo = (email or "").strip().lower()

    if len(nome_limpo) < 3:
        return False, "Informe seu nome completo."

    if not auth_utils.validar_email(email_limpo):
        return False, "E-mail inválido."

    if not senha_temporaria:
        return False, "Informe a senha temporária recebida."

    if not auth_utils.validar_senha(nova_senha):
        return False, "A nova senha deve ter no mínimo 6 caracteres."

    if senha_temporaria == nova_senha:
        return False, "A nova senha deve ser diferente da senha temporária."

    sucesso, uid, _ = auth_utils.autenticar_usuario(email_limpo, senha_temporaria)
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

        inst_id = perfil.get("instituicao_id") or INSTITUICAO_PADRAO_ID
        role_norm = _normalizar_role(perfil.get("role"))

        cursos_ids = list(cursos_ids or [])
        disciplinas_ids = list(disciplinas_ids or [])

        # Resolve nomes legíveis a partir da estrutura acadêmica da instituição
        acad = academico_model.listar_academico_firestore(inst_id)
        cursos_mapa = {c["id"]: c["nome"] for c in acad.get("cursos", [])}
        turmas_mapa = {t["id"]: t["nome"] for t in acad.get("turmas", [])}
        discs_mapa = {d["id"]: d["nome"] for d in acad.get("disciplinas", [])}

        if role_norm == "professor":
            if not cursos_ids:
                return False, "Selecione pelo menos um curso para o seu perfil de professor."
            vinculo_usuario = {
                "cursosIds": cursos_ids,
                "cursos": [cursos_mapa[cid] for cid in cursos_ids if cid in cursos_mapa],
                "curso": cursos_mapa.get(cursos_ids[0], ""),
                "turmaId": None,
                "turma": "",
                "disciplinasIds": [],
                "materias": [],
            }
            vinculo_membro = {
                "cursosIds": cursos_ids,
                "cursos": vinculo_usuario["cursos"],
                "curso": vinculo_usuario["curso"],
                "turma": "",
                "materia": "",
            }
        elif role_norm == "aluno":
            if not cursos_ids:
                return False, "Selecione o seu curso."
            if turma_id is None:
                return False, "Selecione a sua turma."
            if not disciplinas_ids:
                return False, "Selecione pelo menos uma disciplina/matéria."

            curso_principal_id = cursos_ids[0]
            curso_nome = cursos_mapa.get(curso_principal_id, "")
            turma_nome = turmas_mapa.get(turma_id, "")
            nomes_discs = [discs_mapa[did] for did in disciplinas_ids if did in discs_mapa]

            vinculo_usuario = {
                "cursosIds": [curso_principal_id],
                "cursos": [curso_nome] if curso_nome else [],
                "curso": curso_nome,
                "turmaId": turma_id,
                "turma": turma_nome,
                "disciplinasIds": disciplinas_ids,
                "materias": nomes_discs,
                "materia": ", ".join(nomes_discs),
            }
            vinculo_membro = {
                "cursosIds": [curso_principal_id],
                "curso": curso_nome,
                "turmaId": turma_id,
                "turma": turma_nome,
                "disciplinasIds": disciplinas_ids,
                "materias": nomes_discs,
                "materia": ", ".join(nomes_discs),
            }
        else:
            # Coordenador ou Administrador
            vinculo_usuario = {
                "cursosIds": cursos_ids,
                "turmaId": turma_id,
                "disciplinasIds": disciplinas_ids,
            }
            vinculo_membro = {}

        auth.update_user(uid, password=nova_senha, email_verified=True)

        atualizacoes = {
            "nome": nome_limpo,
            **vinculo_usuario,
            "primeiro_acesso": False,
            "email_verificado": True,
            "atualizado_em": agora_br(),
        }
        doc_ref.update(atualizacoes)

        membro_doc = next(
            db.collection("membros").where("email", "==", email_limpo).limit(1).stream(),
            None,
        )
        if not membro_doc and (email or "").strip():
            membro_doc = next(
                db.collection("membros")
                .where("email", "==", (email or "").strip())
                .limit(1)
                .stream(),
                None,
            )

        if membro_doc:
            db.collection("membros").document(membro_doc.id).update({
                "nome": nome_limpo,
                **vinculo_membro,
                "primeiroAcesso": False,
                "status": "Ativo",
            })

        return True, "Primeiro acesso concluído com sucesso! Faça login com sua nova senha."

    except Exception as e:
        return False, f"Erro ao concluir primeiro acesso: {str(e)}"