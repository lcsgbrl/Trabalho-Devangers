# -*- coding: utf-8 -*-
"""Preparação dos indicadores exibidos no Dashboard a partir dos dados atuais."""

from datetime import date, datetime, timedelta

import streamlit as st

from models import solicitacao_model

PROF_PERIOD_DAYS = {
    "Última semana": 7,
    "Último mês": 30,
    "Últimos 3 meses": 90,
    "Todo o período": None,
}

WEEKDAYS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")
PROF_TIME_PERIODS = (
    {"periodo": "Manhã", "label": "08:00–12:00", "start": 8, "end": 12},
    {"periodo": "Tarde", "label": "12:00–18:00", "start": 12, "end": 18},
    {"periodo": "Noite", "label": "18:00–22:00", "start": 18, "end": 22},
)


def _parse_pt_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%Y").date()


def _parse_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def diff_hours(inicio: str, fim: str) -> float:
    return max(0, (_parse_minutes(fim) - _parse_minutes(inicio)) / 60)


def format_horas(total: float) -> str:
    hours = int(total)
    minutes = round((total - hours) * 60)
    return f"{hours}h {minutes}min" if minutes else f"{hours}h"


def can_view_dashboard() -> bool:
    from controllers import auth_controller
    return auth_controller.has_perm("canViewDashboard")


def minhas_reservas(user_nome: str) -> list:
    return solicitacao_model.minhas_solicitacoes(st.session_state.solicitacoes, user_nome)


def pending_auth_for_coordenador(nucleo: str | None) -> list:
    requests = solicitacao_model.auth_requests_do_nucleo(st.session_state.solicitacoes, nucleo)
    return solicitacao_model.pendentes(requests)


def professor_dashboard_data(user_name: str, my_reservas: list, periodo_label: str) -> dict:
    today = date.today()
    days = PROF_PERIOD_DAYS[periodo_label]
    valid = [r for r in my_reservas if r["status"] not in ("Cancelado", "Recusado")]
    period_reservas = [
        r for r in valid
        if _parse_pt_date(r["data"]) <= today
        and (days is None or _parse_pt_date(r["data"]) >= today - timedelta(days=days - 1))
    ]

    rooms = {}
    for reservation in period_reservas:
        room_name = reservation["sala"]
        room = rooms.setdefault(
            room_name,
            {"sala": room_name, "reservas": 0, "horas": 0.0, "pessoas": 0},
        )
        room["reservas"] += 1
        room["horas"] += diff_hours(reservation["inicio"], reservation["fim"])
        room["pessoas"] += reservation["pessoas"]
    chart_rooms = sorted(rooms.values(), key=lambda room: -room["reservas"])

    chart_hours = []
    for period in PROF_TIME_PERIODS:
        count = sum(
            period["start"] <= int(reservation["inicio"].split(":")[0]) < period["end"]
            for reservation in period_reservas
        )
        chart_hours.append({key: value for key, value in period.items() if key != "start" and key != "end"}
                           | {"reservas": count})

    total_reservas = len(period_reservas)
    total_hours = sum(diff_hours(r["inicio"], r["fim"]) for r in period_reservas)
    total_people = sum(r["pessoas"] for r in period_reservas)
    average_people = round(total_people / total_reservas) if total_reservas else 0
    peak_periodo = max(chart_hours, key=lambda period: period["reservas"]) if total_reservas else None
    sala_top = chart_rooms[0] if chart_rooms else {"sala": "—", "reservas": 0}

    future = sorted(
        [r for r in valid if _parse_pt_date(r["data"]) >= today],
        key=lambda r: (_parse_pt_date(r["data"]), r["inicio"]),
    )
    proxima = future[0] if future else None
    proxima_tag = None
    if proxima:
        days_until = (_parse_pt_date(proxima["data"]) - today).days
        proxima_tag = "Hoje" if days_until == 0 else "Amanhã" if days_until == 1 else f"Faltam {days_until} dias"

    insights = []
    if total_reservas:
        insights = [
            f"Você utiliza mais {sala_top['sala']} — {sala_top['reservas']} reservas no período.",
            f"Seu período de maior utilização é {peak_periodo['periodo'].lower()} "
            f"({peak_periodo['label']}).",
            f"Você realizou {total_reservas} reservas no período selecionado.",
        ]
    else:
        insights.append("Ainda não há reservas realizadas neste período.")

    return {
        "chart_rooms": chart_rooms,
        "chart_hours": chart_hours,
        "total_chart_reservas": total_reservas,
        "peak_periodo": peak_periodo,
        "sala_top": sala_top,
        "total_reservas_card": total_reservas,
        "total_horas_card": format_horas(total_hours),
        "media_card": average_people,
        "proxima": proxima,
        "proxima_tag": proxima_tag,
        "insights": insights,
        "user_first_names": " ".join(user_name.split(" ")[:2]),
    }


def admin_coord_dashboard_data(solicitacoes: list, salas: list) -> dict:
    valid = [s for s in solicitacoes if s["status"] not in ("Cancelado", "Recusado")]
    aprovados = [s for s in solicitacoes if s["status"] == "Aprovado"]
    pendentes = [s for s in solicitacoes if s["status"] in ("Pendente", "Em análise")]

    week_counts = {day: 0 for day in WEEKDAYS}
    for reservation in valid:
        weekday = _parse_pt_date(reservation["data"]).weekday()
        week_counts[WEEKDAYS[weekday]] += 1
    week_data = [{"day": day, "reservas": count} for day, count in week_counts.items()]

    peak_hours = [
        {"slot": f"{start}–{end}h", "reservas": 0}
        for start, end in ((8, 10), (10, 12), (12, 14), (14, 16), (16, 18), (18, 20))
    ]
    for reservation in valid:
        hour = int(reservation["inicio"].split(":")[0])
        slot_index = (hour - 8) // 2
        if 0 <= slot_index < len(peak_hours):
            peak_hours[slot_index]["reservas"] += 1

    room_stats = {
        room["nome"]: {
            "sala": room["nome"],
            "tipo": room["tipo"],
            "bloco": room["bloco"],
            "reservas": 0,
            "horas": 0.0,
            "pessoas": 0,
            "capacidade": room["capacidade"],
        }
        for room in salas
    }
    for reservation in valid:
        room = room_stats.setdefault(
            reservation["sala"],
            {
                "sala": reservation["sala"], "tipo": "", "bloco": reservation.get("bloco", ""),
                "reservas": 0, "horas": 0.0, "pessoas": 0, "capacidade": 0,
            },
        )
        room["reservas"] += 1
        room["horas"] += diff_hours(reservation["inicio"], reservation["fim"])
        room["pessoas"] += reservation["pessoas"]
    all_room_stats = list(room_stats.values())

    occupancy = []
    for room in all_room_stats:
        rate = min(100, round(room["horas"] / (22 * 10) * 100))
        color = "#8B0019" if rate >= 70 else ("#1E5E60" if rate >= 50 else "#A8A09A")
        occupancy.append({"sala": room["sala"], "taxa": rate, "cor": color})

    recentes = [
        {
            "Ambiente": s["sala"], "Solicitante": s["solicitante"], "Data": s["data"],
            "Horário": f"{s['inicio']}–{s['fim']}", "Status": s["status"],
        }
        for s in reversed(solicitacoes[-8:])
    ]

    return {
        "total_reservas": len(valid),
        "aprovadas": len(aprovados),
        "pendentes": len(pendentes),
        "total_pessoas": sum(s["pessoas"] for s in valid),
        "week_data": week_data,
        "peak_hours": peak_hours,
        "room_stats": all_room_stats,
        "ocupacao": occupancy,
        "recentes": recentes,
    }
