import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


def init_firestore():
    """Inicializa o cliente Firestore lendo st.secrets, variável de ambiente ou secrets/key.json."""
    if not firebase_admin._apps:
        service_account_json = None

        if "FIREBASE_SERVICE_ACCOUNT_JSON" in st.secrets:
            service_account_json = st.secrets["FIREBASE_SERVICE_ACCOUNT_JSON"]
        elif os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON"):
            service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

        if service_account_json:
            cred_info = (
                json.loads(service_account_json)
                if isinstance(service_account_json, str)
                else dict(service_account_json)
            )
            cred = credentials.Certificate(cred_info)
        else:
            key_path = "secrets/key.json"
            if not os.path.exists(key_path):
                raise FileNotFoundError(
                    f"Arquivo 'secrets/key.json' não encontrado em: {os.path.abspath(key_path)}"
                )
            cred = credentials.Certificate(key_path)

        firebase_admin.initialize_app(cred)

    return firestore.client()