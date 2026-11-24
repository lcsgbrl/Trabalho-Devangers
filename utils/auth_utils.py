"""
utils/auth_utils.py

Utilitários para autenticação com Firebase Authentication.
"""
import secrets
import smtplib
import string
from email.message import EmailMessage
import dns.resolver
import re
import streamlit as st
import firebase_admin
import requests
from firebase_admin import auth, credentials

def autenticar_usuario(email: str, senha: str):
    """
    Autentica o usuário pelo Firebase Authentication.
    """
    try:
        api_key = st.secrets["firebase"]["api_key"]

        url = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={api_key}"
        )

        dados = {
            "email": email,
            "password": senha,
            "returnSecureToken": True
        }

        resposta = requests.post(url, json=dados, timeout=15)
        resultado = resposta.json()

        if resposta.status_code != 200:
            erro = resultado.get("error", {}).get("message", "")

            mensagens = {
                "EMAIL_NOT_FOUND": "E-mail ou senha incorretos.",
                "INVALID_PASSWORD": "E-mail ou senha incorretos.",
                "INVALID_LOGIN_CREDENTIALS": "E-mail ou senha incorretos.",
                "USER_DISABLED": "Esta conta está desativada.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": (
                    "Muitas tentativas. Aguarde um pouco e tente novamente."
                ),
                "API_KEY_INVALID": "A chave de configuração do Firebase é inválida."
            }

            return False, None, mensagens.get(
                erro, "Não foi possível realizar o login."
            )

        uid = resultado.get("localId")

        if not uid:
            return False, None, "Não foi possível identificar o usuário."

        return True, uid, "Autenticação realizada com sucesso."

    except KeyError:
        return False, None, "Configuração da API Key não encontrada."

    except requests.exceptions.Timeout:
        return False, None, "Tempo de conexão esgotado. Tente novamente."

    except requests.exceptions.RequestException:
        return False, None, "Erro de comunicação com o Firebase."

    except Exception as e:
        print("ERRO REAL NA AUTENTICAÇÃO:", type(e).__name__, str(e))
        return False, None, "Não foi possível autenticar o usuário."


def enviar_verificacao_email(email: str, senha: str):
    """
    Envia um e-mail de confirmação pelo Firebase Authentication.
    """
    try:
        api_key = st.secrets["firebase"]["api_key"]

        # Primeiro, obter um token de autenticação
        url_login = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={api_key}"
        )

        dados_login = {
            "email": email,
            "password": senha,
            "returnSecureToken": True
        }

        resposta_login = requests.post(
            url_login,
            json=dados_login,
            timeout=15
        )

        if resposta_login.status_code != 200:
            return False, "Não foi possível preparar o envio do e-mail."

        id_token = resposta_login.json().get("idToken")

        # Depois, solicitar o envio do e-mail de verificação
        url_verificacao = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:sendOobCode?key={api_key}"
        )

        dados_verificacao = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }

        resposta = requests.post(
            url_verificacao,
            json=dados_verificacao,
            timeout=15
        )

        if resposta.status_code == 200:
            return True, "E-mail de confirmação enviado com sucesso."

        return False, "Não foi possível enviar o e-mail de confirmação."

    except Exception:
        return False, "Erro ao comunicar com o Firebase."


def registrar_usuario(email: str, senha: str):
    """
    Registra um novo usuário no Firebase Auth
    
    Args:
        email: Email do usuário
        senha: Senha (mínimo 6 caracteres)
    
    Returns:
        tuple: (sucesso: bool, uid: str, mensagem: str)
    """
    try:
        user = auth.create_user(email=email, password=senha)
        return True, user.uid, f"✅ Usuário registrado: {email}"
    
    except auth.EmailAlreadyExistsError:
        return False, None, "❌ Este email já está registrado"
    
    except auth.InvalidPasswordError:
        return False, None, "❌ Senha muito fraca (mínimo 6 caracteres)"
    
    except auth.InvalidEmailError:
        return False, None, "❌ Email inválido"
    
    except Exception as e:
        return False, None, f"❌ Erro ao registrar: {str(e)}"


def deletar_usuario_auth(uid: str):
    """Deleta usuário do Firebase Auth"""
    try:
        auth.delete_user(uid)
        return True, "✅ Usuário deletado"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"


def resetar_senha(email: str):
    """Envia email de reset de senha"""
    try:
        auth.send_password_reset_email(email)
        return True, f"✅ Email de reset enviado para {email}"
    except auth.UserNotFoundError:
        return False, "❌ Usuário não encontrado"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"


def atualizar_email(uid: str, novo_email: str):
    """Atualiza email de um usuário"""
    try:
        auth.update_user(uid, email=novo_email)
        return True, f"✅ Email atualizado para {novo_email}"
    except auth.EmailAlreadyExistsError:
        return False, "❌ Este email já está em uso"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"


def atualizar_senha(uid: str, nova_senha: str):
    """Atualiza senha de um usuário"""
    try:
        auth.update_user(uid, password=nova_senha)
        return True, "✅ Senha atualizada"
    except auth.InvalidPasswordError:
        return False, "❌ Senha muito fraca"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"


def obter_usuario_por_email(email: str):
    """Busca usuário por email"""
    try:
        user = auth.get_user_by_email(email)
        return user
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        st.warning(f"Erro ao buscar usuário: {e}")
        return None


def listar_usuarios():
    """Lista todos os usuários (usar com cuidado)"""
    try:
        usuarios = []
        for user in auth.list_users().users:
            usuarios.append({
                'uid': user.uid,
                'email': user.email,
                'email_verificado': user.email_verified,
                'criado_em': user.user_metadata.creation_timestamp,
            })
        return usuarios
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return []


def validar_email(email: str) -> bool:
    """Valida rigorosamente o formato de e-mail."""
    if not email or not isinstance(email, str):
        return False

    email = email.strip()
    if len(email) > 254 or " " in email:
        return False

    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(padrao, email):
        return False

    local, domain = email.rsplit("@", 1)
    if ".." in local or ".." in domain or domain.startswith("-") or domain.endswith("-"):
        return False

    return True


def dominio_email_existe(email: str) -> bool:
    """Verifica via DNS (registros MX/A) se o domínio do e-mail existe e recebe mensagens."""
    if not validar_email(email):
        return False
    dominio = email.strip().rsplit("@", 1)[1].lower()
    try:
        respostas = dns.resolver.resolve(dominio, "MX", lifetime=5.0)
        return len(respostas) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False
    except Exception:
        # Se houver falha momentânea de rede no servidor, não trava o sistema
        return True
    

def validar_senha(senha: str) -> bool:
    """Valida força da senha"""
    return len(senha) >= 6

def gerar_senha_temporaria(tamanho: int = 8) -> str:
    """Gera uma senha temporária aleatória segura."""
    maiusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    digitos = string.digits
    simbolos = "@#$%"

    obrigatorios = [
        secrets.choice(maiusculas),
        secrets.choice(minusculas),
        secrets.choice(digitos),
        secrets.choice(simbolos),
    ]
    todos = maiusculas + minusculas + digitos + simbolos
    restante = [secrets.choice(todos) for _ in range(max(tamanho - 4, 4))]
    caracteres = obrigatorios + restante
    secrets.SystemRandom().shuffle(caracteres)
    return "".join(caracteres)


def enviar_email_primeiro_acesso(destinatario: str, nome: str, senha_temporaria: str) -> tuple[bool, str]:
    """Envia automaticamente por SMTP a senha temporária e instruções de primeiro acesso."""
    try:
        smtp_cfg = st.secrets["smtp"]
        remetente = smtp_cfg["email_remetente"]
        senha_app = smtp_cfg["senha_app"].replace(" ", "")

        msg = EmailMessage()
        msg["Subject"] = "SGA - Dados de Primeiro Acesso"
        msg["From"] = f"Sistema de Gestão de Ambientes <{remetente}>"
        msg["To"] = destinatario

        corpo = (
            f"Olá, {nome}!\n\n"
            "Seu pré-cadastro no Sistema de Gestão de Ambientes (SGA) foi realizado.\n\n"
            "Seus dados de acesso inicial são:\n"
            f"• E-mail: {destinatario}\n"
            f"• Senha temporária: {senha_temporaria}\n\n"
            "Para ativar sua conta:\n"
            "1. Acesse a tela de login do SGA;\n"
            "2. Clique no botão 'Primeiro Acesso';\n"
            "3. Informe seu nome, e-mail, a senha temporária acima, sua nova senha definitiva, curso, turma e matéria.\n\n"
            "Atenciosamente,\n"
            "Equipe SGA"
        )
        msg.set_content(corpo)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(remetente, senha_app)
            server.send_message(msg)

        return True, "E-mail com senha temporária enviado com sucesso."

    except KeyError:
        return False, "Configuração [smtp] não encontrada em secrets.toml."
    except Exception as e:
        return False, f"Falha ao enviar e-mail SMTP: {e}"
    


def gerar_codigo_verificacao() -> str:
    """Gera um código numérico de 6 dígitos."""
    return "".join(secrets.choice(string.digits) for _ in range(6))


def enviar_codigo_confirmacao_email(destinatario: str, nome: str, codigo: str) -> tuple[bool, str]:
    """Envia código de 6 dígitos para confirmar que o novo e-mail existe antes de salvar."""
    try:
        smtp_cfg = st.secrets["smtp"]
        remetente = smtp_cfg["email_remetente"]
        senha_app = smtp_cfg["senha_app"].replace(" ", "")

        msg = EmailMessage()
        msg["Subject"] = "SGA - Código de confirmação de e-mail"
        msg["From"] = f"Sistema de Gestão de Ambientes <{remetente}>"
        msg["To"] = destinatario
        msg.set_content(
            f"Olá, {nome}!\n\n"
            f"Seu código para confirmar a alteração de e-mail no SGA é: {codigo}\n\n"
            "Se você não solicitou esta alteração, ignore esta mensagem."
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(remetente, senha_app)
            server.send_message(msg)

        return True, "Código enviado com sucesso."
    except Exception as e:
        return False, f"Não foi possível enviar o código para este e-mail: {e}"
