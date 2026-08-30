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

## Deploy auf Render (kostenlose Stufe reicht für den Anfang)

1. Repo auf GitHub pushen.
2. Auf render.com: "New Web Service" -> Repo auswählen.
3. Render erkennt die `render.yaml` automatisch (Build/Start-Command sind
   dort schon definiert) - einfach "Deploy" klicken.
4. Nach ein paar Minuten läuft die Seite unter einer `*.onrender.com`-URL.

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
