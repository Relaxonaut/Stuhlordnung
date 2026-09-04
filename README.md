# Sitzordnung

## Lokal starten

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Dann im Browser: http://localhost:8000

Die interaktive API-Doku (automatisch von FastAPI generiert, gut zum
Ausprobieren einzelner Requests): http://localhost:8000/docs

## Render Link für Browser

Hier ist der Services erreichbar: https://stuhlordnung.onrender.com/
Der Services braucht ein bisschen zum starten(Wartezeiten von 30-50 Sekunden sind normal).


## Projektstruktur

```
backend/
  algorithm.py   - Zuteilungslogik (Simulated Annealing), unabhängig vom Web
  models.py      - definiert das JSON-Format der API
  main.py        - FastAPI-Server: Endpunkt /api/assign + liefert Frontend aus
frontend/
  index.html     - Grundgerüst
  style.css      - Styling
  app.js         - Canvas-Interaktion, Personenverwaltung, ruft /api/assign auf
```
