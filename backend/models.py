

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
