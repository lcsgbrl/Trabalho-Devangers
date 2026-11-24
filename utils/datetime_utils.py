# -*- coding: utf-8 -*-
"""Utilitários de data e hora com fuso horário do Brasil."""
from datetime import datetime, date
from zoneinfo import ZoneInfo

# Use "America/Sao_Paulo" (UTC-3, Brasília) ou "America/Porto_Velho" (UTC-4, Rondônia)
FUSO_BR = ZoneInfo("America/Porto_Velho")


def agora_br() -> datetime:
    """Retorna o datetime atual no fuso horário configurado."""
    return datetime.now(FUSO_BR)


def hoje_br() -> date:
    """Retorna a data (date) atual no fuso horário configurado."""
    return agora_br().date()


def agora_str(formato: str = "%d/%m/%Y %H:%M") -> str:
    """Retorna data e hora formatadas no fuso horário configurado."""
    return agora_br().strftime(formato)

def formatar_data_br(valor) -> str:
    """Converte datas (date, datetime ou string YYYY-MM-DD) para DD/MM/YYYY."""
    if not valor:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    texto = str(valor).strip()
    # Se vier no formato ISO "YYYY-MM-DD" (ou "YYYY-MM-DD HH:MM:SS"), converte para DD/MM/YYYY
    parte_data = texto.split(" ")[0].split("T")[0]
    partes = parte_data.split("-")
    if len(partes) == 3 and len(partes[0]) == 4:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return texto