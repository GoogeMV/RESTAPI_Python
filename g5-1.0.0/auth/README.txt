================================================================================
MODULUL AUTH - Autentificare si Gestionare Utilizatori
================================================================================

DESCRIERE
---------

Modulul auth gestioneaza serviciile de autentificare si operatiile CRUD cu date
despre utilizatori. Furnizeaza endpoint-uri pentru register, login, verificare
utilizator si actualizare rol. Datele utilizatorilor sunt stocate in memorie
intr-un dictionar Python.

Endpoint-uri disponibile:
  POST   /auth/register    — Inregistrare utilizator nou
  POST   /auth/login       — Logare utilizator
  GET    /auth/me          — Obtinere date utilizator curent
  PUT    /auth/roles       — Actualizare rol utilizator
  GET    /auth/verify      — Verificare autenticitate token

Validari si erori:
  - username trebuie sa aiba intre 3 si 50 de caractere
  - password trebuie sa aiba intre 6 si 128 de caractere
  - role trebuie sa fie una dintre: user, student, professor, admin
  - register respinge duplicatele de username cu HTTP 409 Conflict
  - login returneaza mesajul "Credentiale invalide" daca nu gaseste
    perechea username/parola


DEPENDINTE EXTERNE
-------------------

Modulul auth nu depinde de alte module.


MODULE CARE DEPIND DE AUTH
---------------------------

main.py — Monteaza routerul auth in aplicatia principala la prefixul "/auth".


FLUXUL UNEI CERERI HTTP
-------------------------------------------

De la cererea clientului pana la raspuns, o cerere trece prin urmatoarele faze:

EXEMPLU: POST /auth/register cu params username=ion&password=123456&role=student

FAZA 1: RUTA - router.py

  Fisierul: auth/router.py (linia 7)
  
  FastAPI intercepteaza cererea pe baza URL-ului si metodei HTTP.
  Routerul identifica endpoint-ul corespunzator si functia handler:
  
    @router.post("/register", status_code=201)
    def register(payload: UserCreate = Depends()):
        ...
  
  Parametrii sunt extrasi si validati prin schema Pydantic din schemas.py.


FAZA 2: VALIDARE - schemas.py

  Fisierul: auth/schemas.py (linia 4-7)
  
  FastAPI si Pydantic valideaza parametrii folosind schema UserCreate:
  
    class UserCreate(BaseModel):
        username: str = Field(min_length=3, max_length=50)
        password: str = Field(min_length=6, max_length=128)
        role: Literal["user", "student", "professor", "admin"] = "user"
  
  Daca validarea esueaza (ex: username lipseste, parola este prea scurta
  sau rolul nu este permis), se returneaza eroare 422.
  Daca reuseste, parametrii sunt convertiti in tipurile corecte si transmisi
  functiei handler.


FAZA 3: LOGICA SI STOCARE - data.py + router.py

  Fisierul: auth/router.py (linia 8-11) + auth/data.py
  
  Functia handler primeste parametrii validati si executa logica de business:
  
    for user in db.users_db.values():
        if user["username"] == username:
            raise HTTPException(status_code=409, detail="Utilizatorul exista deja")

    user = {"id": db.next_id, "username": username, "password": password, "role": role}
    db.users_db[db.next_id] = user
    db.next_id += 1
  
  Datele sunt stocate direct in dictionar in memorie (data.py):
  
    users_db: dict[int, dict] = {}
    next_id = 1
  
  Nota: Modulul auth nu are layer de service.py — logica este direct in router.


FAZA 4: RASPUNS - schemas.py + router.py

  Fisierul: auth/router.py (linia 12) + auth/schemas.py (linia 9-12)
  
  Functia returneaza un dict care este automat convertit in JSON conform
  schemei UserResponse:
  
    class UserResponse(BaseModel):
        id: int
        username: str
        role: str
  
  Raspunsul HTTP este contruit automat:
    - Status: 201 Created pentru register
    - Body: {"id": 1, "username": "ion", "role": "student"}
    - Content-Type: application/json


FAZA 5: TRANSMITERE CATRE CLIENT

  Serverul (uvicorn) trimite raspunsul HTTP catre client cu header-urile
  si body-ul corespunzator. Clientul receptioneaza raspunsul si il proceseaza.


EXEMPLU COMPLET: GET /auth/me?user_id=1
-------------------------------------------

1. RUTA (router.py, linia 27-28):
   
   @router.get("/me")
   def get_me(user_id: int):

2. VALIDARE (schemas.py):
   
  user_id este validat automat ca int de FastAPI (din query parameter).
  Daca parametrul lipseste sau nu este int, se returneaza eroare 422.
  Pentru /auth/register si /auth/login, validarea se face prin schemele
  UserCreate si LoginRequest.

3. LOGICA (router.py, linia 29-31, + data.py):
   
   if user_id in db.users_db:  # Cautare in dictionar
       u = db.users_db[user_id]
       return {"id": u["id"], "username": u["username"], "role": u["role"]}

4. RASPUNS:
   
   Status: 200 OK
   Body: {"id": 1, "username": "ion", "role": "student"}
   
   Daca user_id nu exista, functia returneaza None si FastAPI genereaza
  raspuns 200 cu body null.

EXEMPLU: POST /auth/register cu username duplicat
-------------------------------------------------

1. Cerere valida din punct de vedere Pydantic.
2. Routerul verifica daca username-ul exista deja in users_db.
3. Daca da, ridica HTTPException(409, "Utilizatorul exista deja").
4. Clientul primeste raspunsul:
  Status: 409 Conflict
  Body: {"detail": "Utilizatorul exista deja"}


STRUCTURA FISIERELOR
---------------------

  auth/
    __init__.py           — Package marker
    router.py             — Definitii endpoint-uri (faza 1 si 4)
    schemas.py            — Modele Pydantic pentru validare (faza 2)
    data.py               — Stocare in memorie (faza 3)
    README.txt            — Aceasta documentatie


CONCLUZII
---------

Fluxul HTTP in modulul auth urmaza patternul: router → schemas → data

- router.py: Intercepteaza cerere, executa logica, returneaza raspuns
- schemas.py: Valideaza parametrii si tipul raspunsului
- data.py: Stocheaza si gestioneaza starea (users_db, next_id)
- register blocheaza duplicatele de username cu raspuns HTTP 409

Nu exista layer de service.py deoarece logica este relativ simpla si se
afla direct in router pentru modularitate minima.
