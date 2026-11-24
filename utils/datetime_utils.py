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