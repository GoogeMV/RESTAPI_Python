# Schedule Module (Orar)

## Descriere

Modulul `schedule` gestionează orarul universitar. Oferă operații CRUD complete
pentru sloturile de orar (curs, profesor, sală, zi, interval orar).

Pe lângă CRUD, modulul include:
- Validări stricte pe toate câmpurile de intrare
- Detectarea duplicatelor (același profesor + sală + zi + oră de început)
- Detectarea conflictelor de sală (suprapuneri de interval în aceeași sală)
- Filtrare după zi, sală sau profesor
- Paginare cu parametrii `limit` și `offset`
- Endpoint dedicat pentru orarul unui profesor

---

## Dependențe între module

### Modulul `schedule` depinde de:
**Niciunul.** Modulul este autonom — gestionează propriile date și nu
consumă API-uri din alte module.

### Module care depind de `schedule`:
| Modul | Motivul dependenței |
|---|---|
| `professors` | Poate afișa orarul unui profesor |
| `reports` | Poate agrega date despre utilizarea sălilor |

---

## Endpoint-uri disponibile

| Metodă | URL | Descriere |
|---|---|---|
| `POST` | `/schedule/` | Creare slot nou |
| `GET` | `/schedule/` | Listare sloturi (cu filtrare și paginare) |
| `GET` | `/schedule/{id}` | Detalii slot |
| `PUT` | `/schedule/{id}` | Actualizare parțială slot |
| `DELETE` | `/schedule/{id}` | Ștergere slot |
| `GET` | `/schedule/conflicts` | Detectare conflicte de sală |
| `GET` | `/schedule/professor/{id}` | Toate sloturile unui profesor |

Documentație interactivă: `http://localhost:8000/docs`

---

## Filtrare și paginare

Endpoint-ul `GET /schedule/` acceptă parametrii:

| Parametru | Tip | Default | Descriere |
|---|---|---|---|
| `day` | string | - | Filtrare după zi (ex: `Luni`) |
| `room` | string | - | Filtrare după sală (ex: `A101`) |
| `professor_id` | int | - | Filtrare după ID profesor |
| `limit` | int | 10 | Număr maxim rezultate (1-100) |
| `offset` | int | 0 | Număr rezultate de sărit |

Exemplu: `GET /schedule/?day=Luni&room=A101&limit=5&offset=0`

---

## Validări

Toate câmpurile sunt validate prin Pydantic:

| Câmp | Regulă |
|---|---|
| `course_name` | Minim 3 caractere |
| `professor_id` | Număr întreg pozitiv |
| `room` | Nu poate fi gol |
| `day` | Obligatoriu din: `Luni`, `Marti`, `Miercuri`, `Joi`, `Vineri` |
| `start_time` | Format `HH:MM`, oră validă (00-23), minute valide (00-59) |
| `end_time` | Format `HH:MM`, strict după `start_time` |

---

## Detectare duplicate

La `POST /schedule/` și `PUT /schedule/{id}`, sistemul verifică dacă există
deja un slot cu același `professor_id` + `room` + `day` + `start_time`.

Răspuns: `409 Conflict`

---

## Detectare conflicte de sală

`GET /schedule/conflicts` returnează toate perechile de sloturi care se
suprapun în timp în aceeași sală.

Exemplu răspuns:
```json
[
  {
    "slot_a": {"id": 1, "room": "A101", "day": "Luni", "start_time": "08:00", "end_time": "10:00", ...},
    "slot_b": {"id": 2, "room": "A101", "day": "Luni", "start_time": "09:00", "end_time": "11:00", ...}
  }
]
```

---

## Exemple cereri și răspunsuri

### POST /schedule/ — creare slot

**Cerere:**
```http
POST /schedule/
Content-Type: application/json

{
  "course_name": "Algoritmi",
  "professor_id": 3,
  "room": "A101",
  "day": "Luni",
  "start_time": "08:00",
  "end_time": "10:00"
}
```

**Răspuns `201 Created`:**
```json
{
  "id": 1,
  "course_name": "Algoritmi",
  "professor_id": 3,
  "room": "A101",
  "day": "Luni",
  "start_time": "08:00",
  "end_time": "10:00"
}
```

---

### GET /schedule/professor/{id} — orarul unui profesor

**Cerere:**
```http
GET /schedule/professor/3
```

**Răspuns `200 OK`:**
```json
[
  {
    "id": 1,
    "course_name": "Algoritmi",
    "professor_id": 3,
    "room": "A101",
    "day": "Luni",
    "start_time": "08:00",
    "end_time": "10:00"
  },
  {
    "id": 4,
    "course_name": "Structuri de Date",
    "professor_id": 3,
    "room": "B202",
    "day": "Miercuri",
    "start_time": "12:00",
    "end_time": "14:00"
  }
]
```

Dacă profesorul nu are sloturi: `200 OK` cu `[]`

---

### PUT /schedule/{id} — actualizare parțială

Poți trimite doar câmpurile pe care vrei să le modifici:

**Cerere:**
```http
PUT /schedule/1
Content-Type: application/json

{
  "room": "B202"
}
```

**Răspuns `200 OK`** — returnează slotul complet actualizat.

---

## Coduri HTTP

| Cod | Situație |
|---|---|
| `200 OK` | GET sau PUT reușit |
| `201 Created` | Slot creat cu succes |
| `404 Not Found` | Slot cu ID-ul dat nu există |
| `409 Conflict` | Duplicat detectat |
| `422 Unprocessable Entity` | Date invalide în request body |

---

## Fluxul unei cereri HTTP

```
Client → router.py → service.py → data.py → Response
              ↕                                  ↕
          schemas.py                         schemas.py
      (validare input)                  (formatare output)
```

`schemas.py` este folosit atât la intrare (validarea datelor primite),
cât și la ieșire (structurarea răspunsului).

---

## Cum se rulează testele

```bash
python -m pytest tests/test_router_schedule.py -v
```

Suita conține 35 de teste care acoperă: CRUD complet, validări, duplicate,
conflicte, filtrare, paginare și endpoint-ul `/professor/{id}`.

---

## Structura modulului

```
schedule/
  __init__.py
  router.py              — Re-exportă router-ul pentru auto-descoperire
  app/
    __init__.py
    data.py              — Stocare în memorie (schedule_db, next_id)
    schemas.py           — Modele Pydantic (ScheduleCreate, ScheduleUpdate, ScheduleResponse)
    service.py           — Logică de business (CRUD, duplicate, filtrare, paginare)
    router.py            — Endpoint-uri FastAPI
  SPEC/
    SPEC_1.txt           — Documentare inițială modul
    SPEC_2.txt           — Validări și detectare duplicate
    SPEC_3.txt           — Filtrare și paginare
    SPEC_4.txt           — Endpoint nou GET /professor/{id}
    SPEC_5.txt           — Teste unitare
  openapi.json           — Schema OpenAPI generată
  README.txt             — Acest fișier
