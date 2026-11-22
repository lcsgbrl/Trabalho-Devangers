# -*- coding: utf-8 -*-
"""[VIEW] Dashboard — equivalente a src/pages/Dashboard.tsx.

Toda a preparação de métricas/agregações vive em controllers.dashboard_controller;
aqui só acontece a montagem dos gráficos (Plotly) e a renderização Streamlit.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from controllers import auth_controller, dashboard_controller as dc
from views.components import PRIMARY, TEXT_MUTED, badge_html


def bar_chart(x, y, colors=None, height=260, horizontal=False):
    if horizontal:
        fig = go.Figure(go.Bar(y=x, x=y, orientation="h", marker_color=colors or PRIMARY))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors or PRIMARY))

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=TEXT_MUTED, size=11),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F3EFEA"),
    )
    return fig


# ── Cards personalizados ────────────────────────────────────────────────────
FOOTER_ICONS = {
    "up": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><polyline points="18 15 12 9 6 15"></polyline></svg>',
    "alert": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
}


def render_metric_card(col, icon, label, value, footer=None, footer_icon="up",
                       footer_color="#2F6B3A", value_color="#202938"):
    icon_colors = {
        ":material/event:": "#FDECEC",
        ":material/event_available:": "#E6F2E8",
        ":material/pending_actions:": "#FEF3C7",
        ":material/groups:": "#E3ECEE",
        ":material/meeting_room:": "#E6F2E8",
        ":material/schedule:": "#E6F2E8",
        ":material/home:": "#E6F2E8",
        ":material/block:": "#FDECEC",
    }

    bg = icon_colors.get(icon, "#E5E7EB")
    icon_name = icon.split("/")[-1].replace(":", "")
    icon_key = f"metric_icon_{icon_name}"

    with col:
        st.markdown(
            f"""
            <style>
                div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-{icon_key}) {{
                    background-color: #FFFFFF !important;
                    border: 1px solid #E8E3DA !important;
                    border-radius: 22px !important;
                    padding: 24px 26px !important;
                }}

                div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-{icon_key}) > div,
                div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-{icon_key}) > div > div {{
                    padding: 0 !important;
                }}

                div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-{icon_key}) > div > div[data-testid="stVerticalBlock"] {{
                    gap: 10px !important;
                    justify-content: center !important;
                    align-items: flex-start !important;
                }}

                div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-{icon_key}) [data-testid="stMarkdownContainer"] {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}

                .st-key-{icon_key} {{
                    background-color: {bg} !important;
                    width: 50px !important;
                    height: 50px !important;
                    min-height: 50px !important;
                    border-radius: 14px;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    box-sizing: border-box;
                    overflow: hidden;
                }}

                .st-key-{icon_key} [data-testid="stVerticalBlock"] {{
                    gap: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }}

                .st-key-{icon_key} [data-testid="stElementContainer"] {{
                    width: 100% !important;
                    height: 100% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .st-key-{icon_key} [data-testid="stMarkdownContainer"] {{
                    width: 100% !important;
                    height: 100% !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }}

                .st-key-{icon_key} p {{
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    font-size: 26px !important;
                    line-height: 1 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100%;
                    height: 100%;
                }}

                .st-key-{icon_key} p span {{
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    line-height: 1 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    vertical-align: middle !important;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        value_html = (
            f'<div style="text-align:left;font-size:42px;font-weight:800;color:{value_color};'
            f'line-height:1.0;margin:0 0 6px 0;width:100%;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;">{value}</div>'
        )
        label_html = (
            f'<div style="text-align:left;font-size:15px;color:#2B2B2B;font-weight:500;'
            f'line-height:1.15;margin:0;width:100%;white-space:nowrap;'
            f'overflow:hidden;text-overflow:ellipsis;">{label}</div>'
        )
        footer_html = ""
        if footer:
            footer_html = (
                f'<div style="text-align:left;font-size:14px;color:{footer_color};font-weight:500;'
                f'line-height:1.2;margin:0;padding-top:10px;width:100%;white-space:nowrap;'
                f'overflow:hidden;text-overflow:ellipsis;">'
                f'{FOOTER_ICONS.get(footer_icon, "")}{footer}</div>'
            )

        with st.container(border=True, height=200):
            with st.container(key=icon_key):
                st.markdown(icon)

            st.markdown(value_html + label_html + footer_html, unsafe_allow_html=True)


def _chart_box_css():
    st.markdown(
        """
        <style>
            div[data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-chart_box_"]) {
                background-color: #FFFFFF !important;
                border: 1px solid #E8E3DA !important;
                border-radius: 22px !important;
                padding: 20px 22px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _status_style(value):
    styles = {
        "Aprovado": "background-color:#E6F2E8;color:#2F6B3A;font-weight:600",
        "Pendente": "background-color:#FEF3C7;color:#8A6D00;font-weight:600",
        "Em análise": "background-color:#FEF3C7;color:#8A6D00;font-weight:600",
        "Recusado": "background-color:#FDECEC;color:#8B0019;font-weight:600",
        "Cancelado": "background-color:#EEEEEE;color:#6B6B6B;font-weight:600",
    }
    return styles.get(value, "")

# ── Dashboard do Professor ───────────────────────────────────────────────────
def professor_dashboard(user_name, my_reservas):
    st.markdown('<div class="sga-eyebrow">VISÃO PESSOAL</div>', unsafe_allow_html=True)
    st.markdown("<div class='sga-title'>Meu Dashboard</div>", unsafe_allow_html=True)

    periodo = st.radio(
        "Período",
        list(dc.PROF_PERIOD_DAYS),
        horizontal=True,
        index=1,
        label_visibility="collapsed",
    )

    d = dc.professor_dashboard_data(user_name, my_reservas, periodo)

    st.caption(
        f"Acompanhe suas reservas, utilização dos ambientes e principais indicadores — "
        f"{d['user_first_names']}"
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    render_metric_card(
        c1,
        ":material/event:",
        "Total de reservas",
        d["total_reservas_card"],
        footer=periodo,
        footer_icon="",
        footer_color="#737B89",
        value_color="#1B1B1B",
    )

    sala_reservas = d["sala_top"]["reservas"]
    render_metric_card(
        c2,
        ":material/meeting_room:",
        "Sala mais utilizada",
        d["sala_top"]["sala"],
        footer=f"{sala_reservas} reservas no período" if sala_reservas else "Sem reservas no período",
        footer_icon="",
        footer_color="#737B89",
        value_color="#2F6B3A",
    )

    render_metric_card(
        c3,
        ":material/groups:",
        "Média de participantes",
        f"{d['media_card']} pessoas",
        footer="Por reserva",
        footer_icon="",
        footer_color="#737B89",
        value_color="#1E5E60",
    )

    render_metric_card(
        c4,
        ":material/schedule:",
        "Total de horas utilizadas",
        d["total_horas_card"],
        footer="No período selecionado",
        footer_icon="",
        footer_color="#737B89",
        value_color="#8B0019",
    )

    _chart_box_css()

    col1, col2 = st.columns([1, 2], gap="medium")

    with col1:
        with st.container(border=True, height=330):
            with st.container(key="chart_box_proxima"):
                st.markdown("###### Próxima reserva")
                proxima = d["proxima"]

                if proxima:
                    st.markdown(f"**{proxima['sala']}**")
                    st.caption(proxima["bloco"])
                    st.write(f"📅 {proxima['data']}")
                    st.write(f"🕒 {proxima['inicio']}–{proxima['fim']}")
                    st.write(f"👥 {proxima['pessoas']} participantes")
                    st.markdown(
                        badge_html(d["proxima_tag"], "#FFF0F2", PRIMARY),
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("Você não possui reservas futuras.")

    with col2:
        with st.container(border=True, height=330):
            with st.container(key="chart_box_horarios_prof"):
                st.markdown("###### Horários mais utilizados")

                if d["total_chart_reservas"]:
                    peak = d["peak_periodo"]
                    pct = round(peak["reservas"] / d["total_chart_reservas"] * 100)

                    st.caption(
                        f"Horário preferido: **{peak['label']}** — {pct}% das suas reservas"
                    )

                    for h in d["chart_hours"]:
                        hp = round(h["reservas"] / d["total_chart_reservas"] * 100)
                        st.write(f"{h['periodo']} ({h['label']}) — {h['reservas']} reservas")
                        st.progress(hp / 100)
                else:
                    st.error("Não há reservas neste período.")

    with st.container(border=True):
        with st.container(key="chart_box_utilizacao"):
            st.markdown("###### Utilização por ambiente")

            if d["chart_rooms"]:
                df = pd.DataFrame(d["chart_rooms"])
                max_room = df["reservas"].max()

                colors = [
                    "#8B0019" if max_room and value == max_room else "#D47080"
                    for value in df["reservas"]
                ]

                st.plotly_chart(
                    bar_chart(df["sala"], df["reservas"], colors=colors),
                    use_container_width=True,
                )
            else:
                st.error("Não há dados de utilização para exibir.")

    with st.container(border=True):
        with st.container(key="chart_box_insights"):
            st.markdown("###### Insights")

            for ins in d["insights"]:
                st.markdown(f"- {ins}")

# ── Dashboard do Admin / Coordenador ─────────────────────────────────────────

def admin_coord_dashboard(solicitacoes, salas, pending_for_me, is_admin):
    st.markdown('<div class="sga-eyebrow">VISÃO GERAL</div>', unsafe_allow_html=True)
    st.markdown("<div class='sga-title'>Dashboard</div>", unsafe_allow_html=True)

    st.caption(
        "Visão geral das atividades e reservas do sistema."
    )

    d = dc.admin_coord_dashboard_data(solicitacoes, salas, dc.listar_membros())

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    render_metric_card(
        c1,
        ":material/event:",
        "Reservas hoje",
        d["reservas_hoje"],
        footer=d["reservas_hoje_footer"],
        value_color="#1B1B1B",
    )

    render_metric_card(
        c2,
        ":material/home:",
        "Ambientes disponíveis",
        d["ambientes_disponiveis"],
        footer="Prontos para uso",
        value_color="#2F6B3A",
    )

    render_metric_card(
        c3,
        ":material/block:",
        "Ambientes ocupados",
        d["ambientes_ocupados"],
        footer="Em uso agora",
        footer_icon="alert",
        footer_color="#8A6D00",
        value_color="#8B0019",
    )

    render_metric_card(
        c4,
        ":material/groups:",
        "Total de membros",
        d["total_membros"],
        footer=d["membros_footer"],
        value_color="#1E5E60",
    )

    if not is_admin and pending_for_me:
        st.warning(
            f"Você tem **{len(pending_for_me)}** solicitação(ões) "
            "de autorização aguardando sua decisão."
        )

    _chart_box_css()

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True):
            with st.container(key="chart_box_semana"):
                st.markdown("###### Reservas por dia da semana")
                df = pd.DataFrame(d["week_data"])
                max_day = df["reservas"].max()

                colors = [
                    "#8B0019" if max_day and value == max_day else "#D47080"
                    for value in df["reservas"]
                ]

                st.plotly_chart(
                    bar_chart(df["day"], df["reservas"], colors=colors),
                    use_container_width=True,
                )

    with col2:
        with st.container(border=True):
            with st.container(key="chart_box_horarios"):
                st.markdown("###### Horários de maior utilização")
                df = pd.DataFrame(d["peak_hours"])
                max_val = df["reservas"].max()

                colors = [
                    "#8B0019" if max_val and value == max_val else "#D47080"
                    for value in df["reservas"]
                ]

                st.plotly_chart(
                    bar_chart(df["slot"], df["reservas"], colors=colors),
                    use_container_width=True,
                )

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True):
            with st.container(key="chart_box_ambiente"):
                st.markdown("###### Reservas por ambiente")

                if d["room_stats"]:
                    df = pd.DataFrame(d["room_stats"]).sort_values(
                        "reservas",
                        ascending=True,
                    )

                    st.plotly_chart(
                        bar_chart(df["sala"], df["reservas"], horizontal=True),
                        use_container_width=True,
                    )
                else:
                    st.error("Cadastre ambientes para visualizar este indicador.")

    with col4:
        with st.container(border=True):
            with st.container(key="chart_box_ocupacao"):
                st.markdown("###### Taxa de ocupação dos ambientes")
                st.caption(
                    "Horas reservadas ÷ horas disponíveis (considerando 10h/dia úteis)"
                )

                if d["ocupacao"]:
                    for r in d["ocupacao"]:
                        st.write(f"**{r['sala']}** — {r['taxa']}%")
                        st.progress(r["taxa"] / 100)
                else:
                    st.error("Cadastre ambientes para visualizar a ocupação.")

    st.markdown("###### Reservas Recentes")

    recentes_df = pd.DataFrame(
        d["recentes"],
        columns=["Ambiente", "Solicitante", "Data", "Horário", "Status"],
    )

    if recentes_df.empty:
        table_data = recentes_df
    else:
        styler = recentes_df.style
        apply_style = getattr(styler, "map", None) or styler.applymap
        table_data = apply_style(_status_style, subset=["Status"])

    st.dataframe(
        table_data,
        hide_index=True,
        use_container_width=True,
    )


# ── Renderização ─────────────────────────────────────────────────────────────

def render():
    user = auth_controller.current_user()

    if not dc.can_view_dashboard():
        st.error("Você não tem permissão para acessar esta página.")
        return

    my_reservas = dc.minhas_reservas(user["nome"])

    if user["role"] == "Professor":
        professor_dashboard(user["nome"], my_reservas)
        return

    is_coordenador = user["role"] == "Coordenador"

    pending_for_me = (
        dc.pending_auth_for_coordenador(user.get("nucleo"))
        if is_coordenador
        else []
    )

    from controllers import reservas_controller

    admin_coord_dashboard(
        reservas_controller.list_solicitacoes(),
        reservas_controller.list_salas(),
        pending_for_me,
        auth_controller.is_admin(),
    )