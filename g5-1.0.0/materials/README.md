# Materials Module

Modulul `materials` gestioneaza materialele didactice asociate cursurilor din aplicatia de management universitar.

Acest modul face parte dintr-un REST API construit cu FastAPI si Python. Datele sunt stocate in memorie, folosind structuri Python, deci nu persista dupa repornirea aplicatiei.

## Scopul modulului

Modulul permite gestionarea materialelor de curs, cum ar fi:

- suporturi de curs;
- linkuri catre resurse externe;
- materiale text;
- materiale asociate unui anumit curs.

Functionalitatea implementata include:

- CRUD complet pentru materiale;
- validari Pydantic pentru datele de intrare;
- prevenirea materialelor duplicate;
- mesaje de eroare clare;
- paginare cu `limit` si `offset`;
- filtrare dupa curs;
- cautare in `course_name`, `title` si `content`;
- teste unitare cu `pytest` si `TestClient`;
- export OpenAPI in `materials/openapi.json`.

## Structura modulului

```text
materials/
  __init__.py
  router.py
  app/
    __init__.py
    data.py
    schemas.py
    service.py
    router.py
  specs/
    SPEC-validari.txt
    SPEC-filtrare-paginare.txt
    SPEC-tests-final.txt
  README.md
  openapi.json
```

## Rolul fisierelor

- `materials/router.py` re-exporta router-ul principal al modulului pentru auto-descoperirea facuta de aplicatia principala.
- `materials/app/router.py` defineste endpoint-urile FastAPI.
- `materials/app/service.py` contine logica de business.
- `materials/app/data.py` contine stocarea in memorie.
- `materials/app/schemas.py` contine modelele Pydantic pentru request si response.
- `./tests/test_router_materials.py` contine testele unitare ale modulului.
- `materials/specs/` contine specificatiile functionalitatilor adaugate.
- `materials/openapi.json` contine schema OpenAPI exportata.
- `materials/README.md` documenteaza modulul.

## Fluxul unei cereri HTTP

```text
Client HTTP
  -> main.py
  -> materials/router.py
  -> materials/app/router.py
  -> materials/app/service.py
  -> materials/app/data.py
  -> response JSON
```

1. Clientul trimite o cerere catre un endpoint din `/materials`.
2. Aplicatia principala monteaza router-ul modulului.
3. `materials/app/router.py` primeste request-ul.
4. Datele request-ului sunt validate cu schemele din `schemas.py`.
5. Logica este procesata in `service.py`.
6. Datele sunt citite sau modificate in `data.py`.
7. Raspunsul este returnat clientului in format JSON.

## Dependente

Modulul `materials` nu depinde direct de alte module.

Nu importa date din:

- `students`;
- `professors`;
- `enrollments`;
- `grades`;
- `library`;
- `reports`;
- `announcements`;
- `schedule`;
- `auth`.

In forma actuala, niciun alt modul nu depinde direct de `materials`.

Pe viitor, modulul `reports` ar putea folosi date din `materials` pentru statistici despre resursele didactice.

## Model de date

Un material are urmatoarea structura:

```json
{
  "id": 1,
  "course_name": "Programare Python",
  "title": "Introducere in FastAPI",
  "content": "Material despre construirea unui REST API cu FastAPI.",
  "file_url": "https://example.com/fastapi.pdf"
}
```

## Validari si constrangeri

Validarile sunt implementate folosind sintaxa Pydantic v2.

Reguli pentru creare material:

- `course_name` este obligatoriu;
- `course_name` trebuie sa aiba intre 2 si 100 de caractere;
- `title` este obligatoriu;
- `title` trebuie sa aiba intre 3 si 150 de caractere;
- `content` este obligatoriu;
- `content` trebuie sa aiba intre 5 si 5000 de caractere;
- `file_url` este optional;
- daca `file_url` este completat, trebuie sa inceapa cu `http://` sau `https://`;
- campurile text nu pot fi goale sau formate doar din spatii.

Reguli pentru actualizare material:

- toate campurile sunt optionale;
- daca un camp este trimis, trebuie sa respecte aceleasi reguli ca la creare;
- `file_url` poate fi trimis cu valoarea `null` pentru a elimina URL-ul existent.

## Reguli pentru duplicate

Nu pot exista doua materiale cu aceeasi combinatie:

```text
course_name + title
```

Comparatia este case-insensitive.

Exemplu: daca exista deja un material cu:

```json
{
  "course_name": "Programare Python",
  "title": "Introducere in FastAPI"
}
```

nu se mai poate crea un material cu:

```json
{
  "course_name": "programare python",
  "title": "introducere in fastapi"
}
```

In acest caz, API-ul returneaza:

```http
409 Conflict
```

```json
{
  "detail": "Material already exists for this course"
}
```

## Paginare

Endpoint-urile de listare accepta parametrii `limit` si `offset`.

| Parametru | Tip | Valoare implicita | Reguli |
|---|---|---:|---|
| `limit` | int | `10` | minim `1`, maxim `100` |
| `offset` | int | `0` | minim `0` |

Exemplu:

```http
GET /materials/?limit=10&offset=0
```

## Endpoint-uri

| Metoda | URL | Descriere |
|---|---|---|
| `POST` | `/materials/` | Creeaza un material nou |
| `GET` | `/materials/?limit=10&offset=0` | Listeaza materialele cu paginare |
| `GET` | `/materials/search?q=algoritmi&limit=10&offset=0` | Cauta materiale dupa cuvant-cheie |
| `GET` | `/materials/course/{course_name}?limit=10&offset=0` | Listeaza materialele unui curs |
| `GET` | `/materials/{material_id}` | Returneaza un material dupa ID |
| `PUT` | `/materials/{material_id}` | Actualizeaza un material |
| `DELETE` | `/materials/{material_id}` | Sterge un material |

## Exemple de cereri si raspunsuri

### Creare material

```http
POST /materials/
Content-Type: application/json
```

Request:

```json
{
  "course_name": "Programare Python",
  "title": "Introducere in FastAPI",
  "content": "Material despre construirea unui REST API cu FastAPI.",
  "file_url": "https://example.com/fastapi.pdf"
}
```

Raspuns:

```http
201 Created
```

```json
{
  "id": 1,
  "course_name": "Programare Python",
  "title": "Introducere in FastAPI",
  "content": "Material despre construirea unui REST API cu FastAPI.",
  "file_url": "https://example.com/fastapi.pdf"
}
```

### Listare materiale cu paginare

```http
GET /materials/?limit=10&offset=0
```

Raspuns:

```json
[
  {
    "id": 1,
    "course_name": "Programare Python",
    "title": "Introducere in FastAPI",
    "content": "Material despre construirea unui REST API cu FastAPI.",
    "file_url": "https://example.com/fastapi.pdf"
  }
]
```

### Citire material dupa ID

```http
GET /materials/1
```

Raspuns:

```json
{
  "id": 1,
  "course_name": "Programare Python",
  "title": "Introducere in FastAPI",
  "content": "Material despre construirea unui REST API cu FastAPI.",
  "file_url": "https://example.com/fastapi.pdf"
}
```

### Actualizare material

```http
PUT /materials/1
Content-Type: application/json
```

Request:

```json
{
  "title": "FastAPI actualizat",
  "content": "Continut actualizat pentru materialul despre FastAPI."
}
```

Raspuns:

```json
{
  "id": 1,
  "course_name": "Programare Python",
  "title": "FastAPI actualizat",
  "content": "Continut actualizat pentru materialul despre FastAPI.",
  "file_url": "https://example.com/fastapi.pdf"
}
```

### Stergere material

```http
DELETE /materials/1
```

Raspuns:

```json
{
  "message": "Material deleted successfully"
}
```

### Filtrare dupa curs

```http
GET /materials/course/Programare%20Python?limit=10&offset=0
```

Raspuns:

```json
[
  {
    "id": 1,
    "course_name": "Programare Python",
    "title": "Introducere in FastAPI",
    "content": "Material despre construirea unui REST API cu FastAPI.",
    "file_url": "https://example.com/fastapi.pdf"
  }
]
```

### Cautare materiale

```http
GET /materials/search?q=fastapi&limit=10&offset=0
```

Cautarea se face case-insensitive in campurile:

- `course_name`;
- `title`;
- `content`.

Raspuns:

```json
[
  {
    "id": 1,
    "course_name": "Programare Python",
    "title": "Introducere in FastAPI",
    "content": "Material despre construirea unui REST API cu FastAPI.",
    "file_url": "https://example.com/fastapi.pdf"
  }
]
```

## Erori posibile

### Material inexistent

```http
404 Not Found
```

```json
{
  "detail": "Material not found"
}
```

### Material duplicat

```http
409 Conflict
```

```json
{
  "detail": "Material already exists for this course"
}
```

### Cautare fara rezultate

```http
404 Not Found
```

```json
{
  "detail": "No materials found for this search query"
}
```

### Curs fara materiale

```http
404 Not Found
```

```json
{
  "detail": "No materials found for this course"
}
```

### Date invalide

```http
422 Unprocessable Entity
```

Apare cand datele trimise nu respecta schema Pydantic.

## Rulare aplicatie

Aplicatia se porneste din radacina repository-ului, nu din folderul `materials`.

```bash
uvicorn main:app --reload
```

Documentatia Swagger este disponibila la:

```text
http://localhost:8000/docs
```

Statusul modulelor este disponibil la:

```text
http://localhost:8000/status
```

## Rulare teste

Pentru a rula toate testele proiectului:

```bash
pytest
```

Testele modulului se afla in:

```text
./tests/test_router_materials.py
```

Testele acopera:

- creare material;
- citire material dupa ID;
- listare cu paginare;
- actualizare material;
- stergere material;
- eroare pentru material inexistent;
- eroare pentru material duplicat;
- eroare pentru date invalide;
- cautare materiale;
- filtrare dupa curs.