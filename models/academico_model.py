# -*- coding: utf-8 -*-
"""
[MODEL] Estrutura acadêmica: Núcleo > Curso > Turma > Disciplina.

Sincroniza as 4 coleções com o Firestore isoladas por instituicao_id,
mantendo compatibilidade total com academico_controller.
"""

import streamlit as st

INSTITUICAO_PADRAO_ID = "inst_001"
COLECAO_NUCLEOS = "academico_nucleos"
COLECAO_CURSOS = "academico_cursos"
COLECAO_TURMAS = "academico_turmas"
COLECAO_DISCIPLINAS = "academico_disciplinas"


def _get_db():
    return st.session_state.get("firestore_db")


def _get_instituicao_id() -> str:
    return st.session_state.get("instituicao_id") or INSTITUICAO_PADRAO_ID


def _doc_id(instituicao_id: str, item_id: int) -> str:
    return f"{instituicao_id}_{item_id}"


def _listar_colecao(db, colecao: str, inst_id: str) -> list:
    docs = db.collection(colecao).where("instituicao_id", "==", inst_id).stream()
    itens = [doc.to_dict() for doc in docs]
    itens.sort(key=lambda x: x.get("id", 0))
    return itens


def listar_academico_firestore(instituicao_id: str | None = None) -> dict:
    """
    Carrega núcleos, cursos, turmas e disciplinas da instituição no Firestore
    e calcula o maior ID utilizado para continuar _next_acad_id sem colisão.
    """
    db = _get_db()
    if not db:
        return {
            "nucleos": [],
            "cursos": [],
            "turmas": [],
            "disciplinas": [],
            "max_id": 0,
        }

    inst_id = instituicao_id or _get_instituicao_id()
    nucleos = _listar_colecao(db, COLECAO_NUCLEOS, inst_id)
    cursos = _listar_colecao(db, COLECAO_CURSOS, inst_id)
    turmas = _listar_colecao(db, COLECAO_TURMAS, inst_id)
    disciplinas = _listar_colecao(db, COLECAO_DISCIPLINAS, inst_id)

    todos_ids = [
        item.get("id", 0)
        for lista in (nucleos, cursos, turmas, disciplinas)
        for item in lista
    ]
    max_id = max(todos_ids, default=0)

    return {
        "nucleos": nucleos,
        "cursos": cursos,
        "turmas": turmas,
        "disciplinas": disciplinas,
        "max_id": max_id,
    }


# ── Lookups ───────────────────────────────────────────────────────────────────

def get_nucleo_by_name(nucleos: list, nome: str):
    return next((n for n in nucleos if n["nome"] == nome), None)


def get_nucleo_by_id(nucleos: list, nid: int):
    return next((n for n in nucleos if n["id"] == nid), None)


def get_curso_by_id(cursos: list, cid: int):
    return next((c for c in cursos if c["id"] == cid), None)


def get_turma_by_id(turmas: list, tid: int):
    return next((t for t in turmas if t["id"] == tid), None)


def cursos_by_nucleo(cursos: list, nucleo_id: int) -> list:
    return [c for c in cursos if c["nucleoId"] == nucleo_id and c["ativo"]]


def turmas_by_curso(turmas: list, curso_id: int) -> list:
    return [t for t in turmas if t["cursoId"] == curso_id and t["ativo"]]


def disciplinas_by_turma(disciplinas: list, turma_id: int) -> list:
    return [d for d in disciplinas if turma_id in d["turmasIds"]]


def disciplinas_by_nucleo(disciplinas: list, nucleo_id: int) -> list:
    return [d for d in disciplinas if d["nucleoId"] == nucleo_id]


# ── Núcleo ────────────────────────────────────────────────────────────────────

def add_nucleo(nucleos: list, new_id: int, nome: str, descricao: str, ativo: bool = True) -> dict:
    inst_id = _get_instituicao_id()
    novo = {
        "id": new_id,
        "instituicao_id": inst_id,
        "nome": nome,
        "descricao": descricao,
        "cursosIds": [],
        "coordenadoresIds": [],
        "ativo": ativo,
    }
    db = _get_db()
    if db:
        db.collection(COLECAO_NUCLEOS).document(_doc_id(inst_id, new_id)).set(novo)

    nucleos.append(novo)
    return novo


def update_nucleo(nucleos: list, nid: int, **kwargs) -> None:
    inst_id = _get_instituicao_id()
    for n in nucleos:
        if n["id"] == nid:
            n.update(kwargs)
            db = _get_db()
            if db:
                db.collection(COLECAO_NUCLEOS).document(_doc_id(inst_id, nid)).update(kwargs)
            return


def delete_nucleo(nucleos: list, nid: int) -> list:
    inst_id = _get_instituicao_id()
    db = _get_db()
    if db:
        db.collection(COLECAO_NUCLEOS).document(_doc_id(inst_id, nid)).delete()
    return [n for n in nucleos if n["id"] != nid]


def nucleo_name_exists(nucleos: list, nome: str) -> bool:
    return any(n["nome"].lower() == nome.strip().lower() for n in nucleos)


# ── Curso ─────────────────────────────────────────────────────────────────────

def add_curso(cursos: list, nucleos: list, new_id: int, nome: str, nucleo_id: int, ativo: bool = True) -> dict:
    inst_id = _get_instituicao_id()
    novo = {
        "id": new_id,
        "instituicao_id": inst_id,
        "nome": nome,
        "nucleoId": nucleo_id,
        "turmasIds": [],
        "ativo": ativo,
    }
    db = _get_db()
    if db:
        db.collection(COLECAO_CURSOS).document(_doc_id(inst_id, new_id)).set(novo)

    cursos.append(novo)
    n = get_nucleo_by_id(nucleos, nucleo_id)
    if n:
        n["cursosIds"].append(new_id)
        if db:
            db.collection(COLECAO_NUCLEOS).document(_doc_id(inst_id, nucleo_id)).update({
                "cursosIds": n["cursosIds"]
            })
    return novo


def update_curso(cursos: list, cid: int, **kwargs) -> None:
    inst_id = _get_instituicao_id()
    for c in cursos:
        if c["id"] == cid:
            c.update(kwargs)
            db = _get_db()
            if db:
                db.collection(COLECAO_CURSOS).document(_doc_id(inst_id, cid)).update(kwargs)
            return


def delete_curso(cursos: list, nucleos: list, cid: int) -> list:
    inst_id = _get_instituicao_id()
    db = _get_db()
    if db:
        db.collection(COLECAO_CURSOS).document(_doc_id(inst_id, cid)).delete()

    novos_cursos = [c for c in cursos if c["id"] != cid]
    for n in nucleos:
        if cid in n["cursosIds"]:
            n["cursosIds"] = [x for x in n["cursosIds"] if x != cid]
            if db:
                db.collection(COLECAO_NUCLEOS).document(_doc_id(inst_id, n["id"])).update({
                    "cursosIds": n["cursosIds"]
                })
    return novos_cursos


# ── Turma ─────────────────────────────────────────────────────────────────────

def add_turma(turmas: list, cursos: list, new_id: int, nome: str, curso_id: int,
              nucleo_id: int, turno: str, ativo: bool = True) -> dict:
    inst_id = _get_instituicao_id()
    novo = {
        "id": new_id,
        "instituicao_id": inst_id,
        "nome": nome,
        "cursoId": curso_id,
        "nucleoId": nucleo_id,
        "turno": turno,
        "alunosIds": [],
        "professoresIds": [],
        "disciplinasIds": [],
        "ativo": ativo,
    }
    db = _get_db()
    if db:
        db.collection(COLECAO_TURMAS).document(_doc_id(inst_id, new_id)).set(novo)

    turmas.append(novo)
    c = get_curso_by_id(cursos, curso_id)
    if c:
        c["turmasIds"].append(new_id)
        if db:
            db.collection(COLECAO_CURSOS).document(_doc_id(inst_id, curso_id)).update({
                "turmasIds": c["turmasIds"]
            })
    return novo


def update_turma(turmas: list, tid: int, **kwargs) -> None:
    inst_id = _get_instituicao_id()
    for t in turmas:
        if t["id"] == tid:
            t.update(kwargs)
            db = _get_db()
            if db:
                db.collection(COLECAO_TURMAS).document(_doc_id(inst_id, tid)).update(kwargs)
            return


def delete_turma(turmas: list, cursos: list, tid: int) -> list:
    inst_id = _get_instituicao_id()
    db = _get_db()
    if db:
        db.collection(COLECAO_TURMAS).document(_doc_id(inst_id, tid)).delete()

    novas_turmas = [t for t in turmas if t["id"] != tid]
    for c in cursos:
        if tid in c["turmasIds"]:
            c["turmasIds"] = [x for x in c["turmasIds"] if x != tid]
            if db:
                db.collection(COLECAO_CURSOS).document(_doc_id(inst_id, c["id"])).update({
                    "turmasIds": c["turmasIds"]
                })
    return novas_turmas


# ── Disciplina ────────────────────────────────────────────────────────────────

def add_disciplina(disciplinas: list, new_id: int, codigo: str, nome: str,
                    nucleo_id: int, carga_horaria: int, turmas_ids: list | None = None) -> dict:
    inst_id = _get_instituicao_id()
    novo = {
        "id": new_id,
        "instituicao_id": inst_id,
        "codigo": codigo,
        "nome": nome,
        "nucleoId": nucleo_id,
        "cargaHoraria": carga_horaria,
        "professoresIds": [],
        "turmasIds": turmas_ids or [],
    }
    db = _get_db()
    if db:
        db.collection(COLECAO_DISCIPLINAS).document(_doc_id(inst_id, new_id)).set(novo)

    disciplinas.append(novo)
    return novo


def update_disciplina(disciplinas: list, did: int, **kwargs) -> None:
    inst_id = _get_instituicao_id()
    for d in disciplinas:
        if d["id"] == did:
            d.update(kwargs)
            db = _get_db()
            if db:
                db.collection(COLECAO_DISCIPLINAS).document(_doc_id(inst_id, did)).update(kwargs)
            return


def delete_disciplina(disciplinas: list, did: int) -> list:
    inst_id = _get_instituicao_id()
    db = _get_db()
    if db:
        db.collection(COLECAO_DISCIPLINAS).document(_doc_id(inst_id, did)).delete()
    return [d for d in disciplinas if d["id"] != did]