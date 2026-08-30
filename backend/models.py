"""
Pydantic-Modelle.

Was ist das? Pydantic beschreibt, wie eingehendes/ausgehendes JSON aussehen
MUSS. FastAPI nutzt das automatisch, um Anfragen zu validieren: schickt das
Frontend fehlerhaftes JSON (z.B. fehlt ein Feld), bekommt es automatisch
einen 422-Fehler mit genauer Erklärung zurück - du musst das nicht selbst
prüfen.
"""

from pydantic import BaseModel
from typing import Literal


class ChairIn(BaseModel):
    id: str
    x: float
    y: float


class PersonIn(BaseModel):
    id: str
    name: str
    desired: list[str] = []
    avoid: list[str] = []
    position_mode: Literal["keine", "wunsch", "erforderlich"] = "keine"


class AssignRequest(BaseModel):
    chairs: list[ChairIn]
    people: list[PersonIn]


class AssignResponse(BaseModel):
    # chair_id -> person_id
    assignment: dict[str, str]
