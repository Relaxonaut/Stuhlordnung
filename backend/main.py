

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .algorithm import Chair, Person, solve
from .models import AssignRequest, AssignResponse

app = FastAPI(title="Sitzordnung API")


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



frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
