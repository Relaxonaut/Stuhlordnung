"""
FastAPI-App.

HTTP-SYNTAX KURZ ERKLÄRT (weil du das explizit wolltest):

@app.post("/api/assign")          <- "Wenn eine POST-Anfrage an /api/assign
def assign(payload: AssignRequest): kommt, ruf diese Funktion auf."
    ...                            POST = "ich schicke dir Daten, verarbeite sie"
                                    (im Gegensatz zu GET = "gib mir nur Daten")

payload: AssignRequest             <- FastAPI liest automatisch den JSON-Body
                                    der Anfrage, prüft ihn gegen die
                                    AssignRequest-Struktur aus models.py, und
                                    gibt dir ein fertiges Python-Objekt.
                                    Du musst also NIE selbst json.loads()
                                    aufrufen oder Felder von Hand prüfen.

return {"assignment": ...}         <- Was du zurückgibst, wird automatisch zu
                                    JSON und als HTTP-Response mit
                                    Statuscode 200 (= "alles ok") verschickt.

Starten lokal:  uvicorn backend.main:app --reload --port 8000
Docs (automatisch generiert!): http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .algorithm import Chair, Person, solve
from .models import AssignRequest, AssignResponse

app = FastAPI(title="Sitzordnung API")

# CORS: erlaubt, dass ein Frontend auf einer ANDEREN Domain/Port diese API
# aufrufen darf. Beim lokalen Testen (Frontend auf :5500, Backend auf :8000)
# würde der Browser das sonst blockieren (Same-Origin-Policy). Für den
# Deploy-Fall (Frontend + Backend auf derselben Domain, siehe unten) ist das
# nicht zwingend nötig, aber es schadet nicht und macht lokales Entwickeln
# einfacher.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/assign", response_model=AssignResponse)
def assign(payload: AssignRequest) -> AssignResponse:
    if not payload.chairs:
        raise HTTPException(status_code=400, detail="Keine Stühle übergeben.")
    if len(payload.people) > len(payload.chairs):
        raise HTTPException(
            status_code=400,
            detail=f"{len(payload.people)} Personen, aber nur {len(payload.chairs)} Stühle.",
        )

    chairs = [Chair(id=c.id, x=c.x, y=c.y) for c in payload.chairs]
    people = [
        Person(
            id=p.id,
            name=p.name,
            desired=p.desired,
            avoid=p.avoid,
            position_mode=p.position_mode,
        )
        for p in payload.people
    ]

    result = solve(chairs, people)
    return AssignResponse(assignment=result)


# --- Frontend ausliefern -----------------------------------------------
# Damit Backend UND Frontend als EIN Service deploybar sind (z.B. auf
# Render als einzelner "Web Service"), liefert FastAPI die Frontend-Dateien
# einfach mit aus. Lokal wie remote gleich erreichbar unter "/".
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
