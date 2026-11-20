# -*- coding: utf-8 -*-
"""
[MODEL] Entidade Sala (ambiente).

Todas as funções são puras: recebem a lista de salas (e demais argumentos)
e devolvem o resultado da operação, sem nunca acessar st.session_state.
Quem guarda o estado é o Controller (reservas_controller).
"""


STATUS_SALA = ("Disponível", "Manutenção", "Inativa")


def _validar_sala(sala: dict) -> None:
    """Valida os campos essenciais e o status de uma sala."""
    for campo in ("nome", "bloco", "numero"):
        if not str(sala.get(campo, "")).strip():
            raise ValueError("Preencha nome, bloco e localização da sala.")

    try:
        capacidade = int(sala.get("capacidade", 0))
    except (TypeError, ValueError):
        raise ValueError("Informe uma capacidade válida para a sala.")

    if capacidade < 1:
        raise ValueError("A capacidade da sala deve ser maior que zero.")

    if sala.get("status") not in STATUS_SALA:
        raise ValueError("Status de sala inválido.")


def add_sala(salas: list, sala: dict) -> dict:
    """Valida e cria uma nova sala com id autoincremental."""
    _validar_sala(sala)
    new_id = (max((s["id"] for s in salas), default=0)) + 1
    novo = dict(sala)
    novo["id"] = new_id
    salas.append(novo)
    return novo


def update_sala(salas: list, sala_id: int, data_new: dict) -> None:
    _validar_sala(data_new)
    for i, s in enumerate(salas):
        if s["id"] == sala_id:
            salas[i] = {**data_new, "id": sala_id}
            return


def toggle_manutencao(salas: list, sala_id: int) -> None:
    """Alterna Disponível/Manutenção; uma sala Inativa volta a Disponível."""
    for s in salas:
        if s["id"] == sala_id:
            if s["status"] == "Disponível":
                s["status"] = "Manutenção"
            else:
                s["status"] = "Disponível"
            return


def get_sala_by_id(salas: list, sala_id: int) -> dict | None:
    return next((s for s in salas if s["id"] == sala_id), None)


def salas_disponiveis(salas: list) -> list:
    return [s for s in salas if s["status"] == "Disponível"]

