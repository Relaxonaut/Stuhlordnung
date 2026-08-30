"""
Sitzordnungs-Algorithmus.

KONZEPT (kurz):
Wir haben mehr oder gleich viele Stühle wie Personen. Wir suchen die Zuordnung
Person -> Stuhl, die möglichst viele Wünsche erfüllt. Das ist kein "Sortieren"
im klassischen Sinn, sondern ein Optimierungsproblem: Es gibt extrem viele
mögliche Zuordnungen (bei 28 Personen: 28! = eine Zahl mit 30 Stellen), man
kann also nicht alle durchprobieren.

Lösung: Simulated Annealing ("simuliertes Abkühlen").
1. Starte mit einer zufälligen Zuordnung.
2. Berechne einen "Score" (wie gut ist diese Zuordnung?).
3. Vertausche zufällig zwei Personen (oder eine Person mit einem leeren Stuhl).
4. Wenn der neue Score besser ist -> behalte die Vertauschung.
   Wenn er schlechter ist -> behalte sie TROTZDEM manchmal (mit einer
   Wahrscheinlichkeit, die mit der Zeit sinkt). Das ist der Trick: so
   entkommt der Algorithmus lokalen Sackgassen, statt sich in der erstbesten
   "okay-ish" Lösung festzufahren.
5. Wiederhole das tausende Male, während die "Temperatur" (= Bereitschaft,
   schlechtere Lösungen zu akzeptieren) langsam sinkt. Am Ende bleibt nur die
   beste je gefundene Zuordnung übrig.

Das ist derselbe Grundtrick wie beim Abkühlen von Metall (daher der Name):
heiß = chaotisch/flexibel, kalt = starr/festgelegt.
"""

import math
import random
from dataclasses import dataclass, field
from statistics import median


# ---------------------------------------------------------------------------
# Datenmodelle (reines Python, keine Web-Abhängigkeit -> gut testbar)
# ---------------------------------------------------------------------------

@dataclass
class Chair:
    id: str
    x: float
    y: float  # kleineres y = weiter vorne (Bühne/Front ist bei y=0)


@dataclass
class Person:
    id: str
    name: str
    desired: list[str] = field(default_factory=list)   # IDs gewünschter Nachbarn
    avoid: list[str] = field(default_factory=list)      # IDs zu vermeidender Personen
    position_mode: str = "keine"  # "keine" | "wunsch" | "erforderlich"


# Gewichte: Personenwünsche wiegen stärker als Positionswünsche (dein Wunsch).
# "erforderlich" ist eine harte Regel -> extrem hohe Strafe, damit sie in der
# Praxis nie verletzt wird, außer es ist unmöglich (z.B. mehr "erforderlich"-
# Personen als Plätze in der Front-Zone gibt).
NEIGHBOR_BONUS = 10
AVOID_PENALTY = 15
POSITION_WISH_PENALTY = 4
POSITION_REQUIRED_PENALTY = 5000

FRONT_ZONE_FRACTION = 0.35  # vorderste 35% der Stühle (nach y sortiert) = "vorne"


def _euclidean(a: Chair, b: Chair) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def _build_neighbor_graph(chairs: list[Chair]) -> dict[str, set[str]]:
    """
    Zwei Stühle gelten als 'Nachbarn', wenn sie näher beieinander stehen als
    ein automatisch berechneter Schwellwert. Der Schwellwert passt sich an,
    wie eng/weit die Stühle im UI gesetzt wurden (Median-Abstand * 1.5).
    """
    if len(chairs) < 2:
        return {c.id: set() for c in chairs}

    nearest_distances = []
    for c in chairs:
        dists = sorted(_euclidean(c, other) for other in chairs if other.id != c.id)
        nearest_distances.append(dists[0])

    threshold = median(nearest_distances) * 1.5

    graph: dict[str, set[str]] = {c.id: set() for c in chairs}
    for i, a in enumerate(chairs):
        for b in chairs[i + 1:]:
            if _euclidean(a, b) <= threshold:
                graph[a.id].add(b.id)
                graph[b.id].add(a.id)
    return graph


def _front_zone(chairs: list[Chair]) -> set[str]:
    sorted_chairs = sorted(chairs, key=lambda c: c.y)
    cutoff = max(1, round(len(chairs) * FRONT_ZONE_FRACTION))
    return {c.id for c in sorted_chairs[:cutoff]}


def _score(
    assignment: dict[str, str],   # chair_id -> person_id
    people_by_id: dict[str, Person],
    neighbor_graph: dict[str, set[str]],
    front_zone: set[str],
) -> float:
    chair_of_person = {p_id: c_id for c_id, p_id in assignment.items()}
    score = 0.0

    for chair_id, person_id in assignment.items():
        person = people_by_id[person_id]

        # Positionswunsch
        in_front = chair_id in front_zone
        if person.position_mode == "erforderlich" and not in_front:
            score -= POSITION_REQUIRED_PENALTY
        elif person.position_mode == "wunsch" and not in_front:
            score -= POSITION_WISH_PENALTY

        # Nachbarschaft (nur einmal pro Paar zählen -> id-Vergleich)
        neighbor_chair_ids = neighbor_graph.get(chair_id, set())
        for neighbor_chair_id in neighbor_chair_ids:
            neighbor_person_id = assignment.get(neighbor_chair_id)
            if neighbor_person_id is None or neighbor_person_id >= person_id:
                continue  # jedes Paar nur einmal zählen
            if neighbor_person_id in person.desired:
                score += NEIGHBOR_BONUS
            if neighbor_person_id in person.avoid:
                score -= AVOID_PENALTY
            neighbor_person = people_by_id[neighbor_person_id]
            if person_id in neighbor_person.desired:
                score += NEIGHBOR_BONUS
            if person_id in neighbor_person.avoid:
                score -= AVOID_PENALTY

    return score


def solve(
    chairs: list[Chair],
    people: list[Person],
    iterations: int = 30000,
    seed: int | None = None,
) -> dict[str, str]:
    """
    Gibt ein Mapping chair_id -> person_id zurück (nicht jeder Stuhl muss
    belegt sein, wenn es mehr Stühle als Personen gibt).
    """
    if len(people) > len(chairs):
        raise ValueError("Mehr Personen als Stühle - das kann nicht aufgehen.")

    rng = random.Random(seed)
    people_by_id = {p.id: p for p in people}
    neighbor_graph = _build_neighbor_graph(chairs)
    front_zone = _front_zone(chairs)

    chair_ids = [c.id for c in chairs]
    rng.shuffle(chair_ids)
    assignment = {chair_ids[i]: p.id for i, p in enumerate(people)}
    empty_chairs = chair_ids[len(people):]

    current_score = _score(assignment, people_by_id, neighbor_graph, front_zone)
    best_assignment = dict(assignment)
    best_score = current_score

    start_temp = 50.0
    end_temp = 0.05

    for step in range(iterations):
        progress = step / iterations
        temperature = start_temp * ((end_temp / start_temp) ** progress)

        # Zwei "Plätze" zufällig wählen (können belegt oder leer sein) und tauschen
        all_slots = list(assignment.keys()) + empty_chairs
        slot_a, slot_b = rng.sample(all_slots, 2)

        # Tausch durchführen
        person_a = assignment.get(slot_a)
        person_b = assignment.get(slot_b)

        new_assignment = dict(assignment)
        if person_a is not None:
            new_assignment[slot_b] = person_a
        else:
            new_assignment.pop(slot_b, None)
        if person_b is not None:
            new_assignment[slot_a] = person_b
        else:
            new_assignment.pop(slot_a, None)

        new_score = _score(new_assignment, people_by_id, neighbor_graph, front_zone)
        delta = new_score - current_score

        if delta >= 0 or rng.random() < math.exp(delta / max(temperature, 1e-6)):
            assignment = new_assignment
            current_score = new_score
            empty_chairs = [c for c in chair_ids if c not in assignment]
            if current_score > best_score:
                best_score = current_score
                best_assignment = dict(assignment)

    return best_assignment
