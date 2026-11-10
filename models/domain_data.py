# -*- coding: utf-8 -*-
"""Constantes de domínio, permissões e estilos do SGA."""

PERMISSIONS_MATRIX = {
    "Aluno": {
        "canViewSalas": True, "canCheckAvailability": True, "canViewSalaResources": True,
        "canRequestReserva": True, "canMakeDirectReserva": False,
        "canApproveStudentRequests": False, "canApproveAuthRequests": False,
        "canViewAllReservas": False, "canViewOwnReservas": True,
        "canManageUsers": False, "canManageSalas": False, "canViewMembros": False,
        "canViewDashboard": False, "canViewConfig": True, "canManageAcademic": False,
    },
    "Professor": {
        "canViewSalas": True, "canCheckAvailability": True, "canViewSalaResources": True,
        "canRequestReserva": True, "canMakeDirectReserva": True,
        "canApproveStudentRequests": True, "canApproveAuthRequests": False,
        "canViewAllReservas": False, "canViewOwnReservas": True,
        "canManageUsers": False, "canManageSalas": False, "canViewMembros": False,
        "canViewDashboard": True, "canViewConfig": True, "canManageAcademic": False,
    },
    "Coordenador": {
        "canViewSalas": True, "canCheckAvailability": True, "canViewSalaResources": True,
        "canRequestReserva": False, "canMakeDirectReserva": True,
        "canApproveStudentRequests": False, "canApproveAuthRequests": True,
        "canViewAllReservas": True, "canViewOwnReservas": True,
        "canManageUsers": False, "canManageSalas": False, "canViewMembros": False,
        "canViewDashboard": True, "canViewConfig": True, "canManageAcademic": True,
    },
    "Administrador": {
        "canViewSalas": True, "canCheckAvailability": True, "canViewSalaResources": True,
        "canRequestReserva": False, "canMakeDirectReserva": True,
        "canApproveStudentRequests": False, "canApproveAuthRequests": False,
        "canViewAllReservas": True, "canViewOwnReservas": True,
        "canManageUsers": True, "canManageSalas": True, "canViewMembros": True,
        "canViewDashboard": True, "canViewConfig": True, "canManageAcademic": True,
    },
}

ROLE_COLORS = {
    "Aluno": {"bg": "#E3ECEE", "text": "#1E5E60", "border": "#B0CDD2", "dot": "#1E5E60"},
    "Professor": {"bg": "#E8EFE2", "text": "#3C5E53", "border": "#B0CEB8", "dot": "#3C5E53"},
    "Coordenador": {"bg": "#FFF8E6", "text": "#805B00", "border": "#FFE19A", "dot": "#B08A00"},
    "Administrador": {"bg": "#FFF0F2", "text": "#8B0019", "border": "#FFD6D9", "dot": "#8B0019"},
}

ROLE_DESCRIPTIONS = {
    "Aluno": "Consulta salas e solicita reservas",
    "Professor": "Realiza reservas e aprova solicitações de alunos",
    "Coordenador": "Acompanha reservas e autoriza ambientes especiais",
    "Administrador": "Gerencia usuários, salas e todo o sistema",
}

TIPO_OPTIONS = ["Laboratório", "Reunião", "Auditório", "Aula", "Estudo", "Outro"]
RECURSO_OPTIONS = [
    "Projetor", "Ar-condicionado", "Computadores", "TV", "Quadro branco", "Som",
    "Wi-Fi", "Tomadas", "Capelas", "Bancadas",
]

STATUS_SALA_STYLE = {
    "Disponível": {"bg": "#EAF5EA", "text": "#2B5E2B", "dot": "#4A9A4A"},
    "Manutenção": {"bg": "#FFF8E6", "text": "#805B00", "dot": "#B08A00"},
    "Inativa": {"bg": "#F5F2EB", "text": "#776D5B", "dot": "#A8A09A"},
}

STATUS_SOL_STYLE = {
    "Pendente": {"bg": "#FFF8E6", "text": "#805B00", "dot": "#B08A00"},
    "Em análise": {"bg": "#E3ECEE", "text": "#1E5E60", "dot": "#1E5E60"},
    "Aprovado": {"bg": "#EAF5EA", "text": "#2B5E2B", "dot": "#4A9A4A"},
    "Recusado": {"bg": "#FDF0F2", "text": "#991B1B", "dot": "#C0303F"},
    "Cancelado": {"bg": "#F5F2EB", "text": "#776D5B", "dot": "#A8A09A"},
}

FUNCOES = ["Administrador", "Professor", "Coordenador", "Aluno"]
FUNCAO_BADGE = {
    "Administrador": {"bg": "#FFF0F2", "text": "#8B0019"},
    "Professor": {"bg": "#E8EFE2", "text": "#3C5E53"},
    "Coordenador": {"bg": "#E3ECEE", "text": "#154749"},
    "Aluno": {"bg": "#EAF5EA", "text": "#2B5E2B"},
}

MEMBER_STATUS_BADGE = {
    "Ativo": {"bg": "#EAF5EA", "text": "#2B5E2B", "dot": "#4A9A4A"},
    "Inativo": {"bg": "#F5F2EB", "text": "#776D5B", "dot": "#A8A09A"},
    "Pendente": {"bg": "#FFF8E6", "text": "#805B00", "dot": "#B08A00"},
    "Aguardando Correção": {"bg": "#FDF0F2", "text": "#991B1B", "dot": "#C0303F"},
}

TURNOS = ["Matutino", "Vespertino", "Noturno", "Integral"]
