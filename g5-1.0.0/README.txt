================================================================================
P1 — Sistem de Management Universitar
SOS — Sisteme Orientate pe Servicii — 2025-2026 Sem2
================================================================================

DESCRIERE GENERALA
------------------

Acest proiect este un REST API  pentru gestionarea operatiunilor unei
universitati, construit cu FastAPI si Python. Aplicatia foloseste stocare
in memorie (dictionare si liste Python) — nu exista baza de date. Datele
nu persista intre reporniri.

Aplicatia este compusa din 10 module independente care formeaza impreuna
un sistem functional. Fiecare modul gestioneaza un domeniu specific al
universitatii. Modulele comunica intre ele prin importuri directe ale
structurilor de date.

Aplicatia principala (main.py) auto-descopera modulele disponibile si le
monteaza automat. Daca un modul lipseste, aplicatia continua sa functioneze
cu modulele ramase.


MODULELE APLICATIEI
-------------------

1. Auth (auth/)
   Autentificare si gestionare utilizatori.
   Endpoint-uri: register, login, me, roles, verify.
   Acesta este modulul de baza de care depind toate celelalte.

2. Studenti (students/)
   Gestionarea profilurilor studentilor.
   Endpoint-uri: CRUD complet + listare cursuri la care este inscris studentul.
   Depinde de: enrollments (pentru listarea cursurilor).

3. Profesori (professors/)
   Gestionarea profilurilor profesorilor.
   Endpoint-uri: CRUD complet + listare cursuri predate.
   Depinde de: enrollments (pentru listarea cursurilor).

4. Inscrieri (enrollments/)
   Gestionarea inscrierilor studentilor la cursuri.
   Endpoint-uri: creare, listare, stergere, filtrare dupa student, lista de asteptare.
   Depinde de: nimic (dar este referit de students, professors, reports).

5. Orar (schedule/)
   Gestionarea orarului, salilor si sloturilor de timp.
   Endpoint-uri: CRUD complet + detectie conflicte + filtrare dupa sala.
   Depinde de: nimic.

6. Note (grades/)
   Gestionarea notelor studentilor.
   Endpoint-uri: CRUD complet + situatie scolara + calcul medie (GPA).
   Depinde de: nimic (dar este referit de reports).

7. Materiale de Curs (materials/)
   Gestionarea materialelor didactice.
   Endpoint-uri: CRUD complet + filtrare dupa curs.
   Depinde de: nimic.

8. Anunturi (announcements/)
   Gestionarea anunturilor si comunicarilor.
   Endpoint-uri: CRUD complet + filtrare dupa audienta.
   Depinde de: nimic.

9. Biblioteca (library/)
   Gestionarea cartilor, imprumuturilor si disponibilitatii.
   Endpoint-uri: CRUD carti, imprumut, returnare, verificare disponibilitate.
   Depinde de: nimic (dar este referit de reports).

10. Rapoarte (reports/)
    Agregare date din toate celelalte module.
    Endpoint-uri: statistici inscrieri, distributie note, numar studenti/profesori,
    statistici biblioteca.
    Depinde de: students, professors, enrollments, grades, library.


CUM SE RULEAZA
--------------

1. Instalati dependentele:

   pip install -r requirements.txt

2. Porniti aplicatia:

   uvicorn main:app --reload

3. Accesati documentatia Swagger in browser:

   http://localhost:8000/docs

4. Verificati starea modulelor:

   http://localhost:8000/status


MODUL DE LUCRU
--------------

Intregul grup de studenti lucreaza in acelasi repository Git. Fiecare
student este responsabil de un modul, dar toti fac push in acelasi repo.
Exista un singur pipeline CI/CD partajat care ruleaza testele tuturor
modulelor la fiecare push.

Fiecare student lucreaza pe branch-ul propriu si face merge request
catre branch-ul main. Pipeline-ul ruleaza automat pe fiecare push
si merge request.


STRUCTURA PROIECTULUI
---------------------

  main.py                  — Aplicatia principala (auto-descoperire module)
  requirements.txt         — Dependente Python
  .gitlab-ci.yml           — Pipeline CI/CD partajat
  auth/                    — Modulul de autentificare (furnizat de profesor)
    router.py              — Endpoint-uri auth
    data.py                — Stocare utilizatori in memorie
    schemas.py             — Scheme Pydantic
  <modul>/                 — Fiecare modul student (students, professors, etc.)
    __init__.py
    router.py              — Re-exporta app/router.py pentru auto-descoperire
    app/
      __init__.py
      data.py              — Structuri de date in memorie
      schemas.py           — Modele Pydantic request/response
      service.py           — Logica de business
      router.py            — Endpoint-uri FastAPI
    tests/
      test_router.py       — Teste unitare pentru modul


CERINTE PENTRU STUDENTI
-----------------------

Fiecare student este responsabil de un modul. Urmatoarele cerinte trebuie
indeplinite de fiecare student pe modulul sau:

1. INTELEGEREA CODULUI

   - Rulati aplicatia si testati fiecare endpoint din modulul vostru
     folosind Swagger UI (http://localhost:8000/docs) sau curl.
   - Identificati de ce module depinde modulul vostru si ce module
     depind de el. Documentati aceste dependente in README-ul modulului.
   - Explicati fluxul unei cereri HTTP de la URL pana la raspuns,
     trecand prin router.py -> service.py -> data.py -> schemas.py.

2. ADAUGARE VALIDARI

   - Adaugati constrangeri pe campurile din schemele Pydantic:
     email trebuie sa fie valid, anul studentului intre 1 si 6,
     nota intre 1 si 10, titlul sa aiba minim 3 caractere, etc.
   - Tratati cazurile de duplicate (ex: acelasi student nu poate fi
     inscris de doua ori la acelasi curs).
   - Returnati mesaje de eroare clare cu coduri HTTP corespunzatoare.

3. ADAUGARE FILTRARE SI PAGINARE

   - Adaugati parametri de paginare la endpoint-urile de listare:
     ?limit=10&offset=0
   - Adaugati filtrare/cautare: GET /students/?name=Ion,
     GET /grades/?min_value=5, GET /materials/search?q=algoritmi

4. ADAUGARE ENDPOINT NOU

   - Adaugati cel putin un endpoint nou care necesita intelegerea
     relatiilor intre module. Exemple:
     * Students: GET /students/{id}/gpa (citeste din modulul grades)
     * Professors: GET /professors/{id}/students (citeste din enrollments)
     * Schedule: GET /schedule/professor/{id} (toate sloturile unui profesor)
     * Grades: GET /grades/top/{n} (top N studenti dupa medie)
     * Library: GET /library/student/{id}/history (toate imprumuturile)
     * Announcements: POST /announcements/{id}/archive (schimba status)
     * Materials: GET /materials/search?q=keyword (cautare in titlu/continut)
     * Enrollments: PUT /enrollments/{id}/status (schimba enrolled/waitlist)
     * Reports: GET /reports/export (toate statisticile intr-un singur JSON)

5. SCRIERE TESTE

   - Scrieti minim 5 teste unitare pentru modulul vostru folosind
     pytest si TestClient din FastAPI.
   - Testele trebuie sa acopere: creare, citire, actualizare, stergere
     si cel putin un caz de eroare (ex: resursa inexistenta).
   - Plasati testele in fisierul tests/test_router.py din modulul vostru.

6. EXPORTARE SCHEMA OPENAPI

   - Generati fisierul openapi.json din aplicatia care ruleaza.
   - Verificati ca schema corespunde endpoint-urilor reale.
   - Plasati fisierul in radacina modulului vostru.

7. DOCUMENTATIE

   - Completati README.md al modulului cu:
     * Descrierea modulului si a endpoint-urilor
     * Exemple de cereri si raspunsuri
     * Dependentele de alte module
     * Cum se ruleaza testele

8. PIPELINE CI/CD

   - In radacina repository-ului exista un fisier .gitlab-ci.yml partajat
     de intreaga echipa.
   - Pipeline-ul se declanseaza automat la fiecare push si merge request.
   - Etapele pipeline-ului:
     * lint: verificare cod cu flake8 pe toate modulele
     * test: rulare teste din toate modulele cu pytest si generare raport
   - Pipeline-ul testeaza intreaga aplicatie, nu doar modulul modificat.
     Astfel, daca o modificare intr-un modul strica alt modul, pipeline-ul
     va semnala eroarea.
   - Raportul de teste este publicat ca artefact GitLab si vizibil
     direct in interfata merge request-ului.
   - Nu modificati .gitlab-ci.yml fara acordul echipei.

9. ACTIVITATE GIT

   - Lucrati incremental: minim 2 commit-uri pe saptamana.
   - Distribuiti codul uniform intre commit-uri — nu incarcati
     tot codul intr-un singur commit la final.
   - Folositi mesaje de commit descriptive care explica ce ati facut.

10. INTEGRARE

    - Asigurati-va ca modulul vostru functioneaza corect impreuna cu
      celelalte module ale colegilor.
    - Aplicatia principala trebuie sa porneasca fara erori cu toate
      modulele implementate montate.
    - Endpoint-ul /status trebuie sa raporteze corect modulele active.

FLUXURI DE LUCRU GIT
--------------------

Toti studentii lucreaza in acelasi repository. Folositi urmatoarele fluxuri
pentru a va organiza munca.


FLUX 1: FUNCTIONALITATE NOUA (Feature)

   Cand doriti sa adaugati o functionalitate noua, urmati acesti pasi:

   a) Completati fisierul SPEC.txt cu detaliile functionalitati si
      creati un Merge Request doar cu specificatia, pentru review de echipa.

   b) Dupa aprobare, creati un branch nou si implementati:

      git checkout main
      git pull origin main
      git checkout -b feature/nume-descriptiv

   c) Lucrati pe branch, faceti commit-uri incrementale:

      git add <fisiere_modificate>
      git commit -m "Adaug validare email in modulul students"
      git push origin feature/nume-descriptiv

   d) Cand implementarea este gata, creati un Merge Request in GitLab:
      - Accesati repository-ul in browser
      - Click pe "Create merge request"
      - Selectati branch-ul sursa (feature/nume-descriptiv) si tinta (main)
      - Adaugati descriere si asignati un coleg pentru review
      - Asteptati ca pipeline-ul CI/CD sa treaca (verde)
      - Dupa aprobare, faceti merge

   e) Dupa merge, stergeti branch-ul local:

      git checkout main
      git pull origin main
      git branch -d feature/nume-descriptiv


FLUX 2: MERGE REQUEST (Review Cod)

   Orice modificare in branch-ul main trebuie sa treaca printr-un
   Merge Request. Nu faceti push direct pe main.

   Reguli:
   - Fiecare Merge Request trebuie revizuit de cel putin un coleg
   - Pipeline-ul CI/CD trebuie sa fie verde (testele trec)
   - Descrierea trebuie sa explice ce s-a modificat si de ce
   - Daca Merge Request-ul rezolva un Issue, mentionati: "Closes #NR"

   Comenzi utile:

      git checkout main
      git pull origin main
      git checkout -b fix/descriere-scurta
      ... modificari ...
      git add .
      git commit -m "Descriere modificare"
      git push origin fix/descriere-scurta

   Apoi creati Merge Request din interfata GitLab.


FLUX 3: RAPORTARE PROBLEME (Issues)

   Cand gasiti o problema (bug, eroare, comportament neasteptat),
   creati un Issue in GitLab:

   a) Accesati sectiunea Issues din repository
   b) Click pe "New issue"
   c) Completati:
      - Titlu: descriere scurta a problemei
      - Descriere: pasi de reproducere, comportament asteptat vs actual
      - Labels: bug, modulul afectat (ex: students, grades)
      - Assignee: studentul responsabil de modulul afectat

   d) Cand rezolvati un Issue, creati un branch dedicat:

      git checkout main
      git pull origin main
      git checkout -b fix/issue-NR-descriere

   e) Dupa rezolvare, creati Merge Request cu mentiunea "Closes #NR"
      in descriere. GitLab va inchide automat Issue-ul la merge.


REZUMAT COMENZI GIT FRECVENTE
------------------------------

   git clone <url>                          — clonare repository
   git checkout main                        — comutare pe branch-ul main
   git pull origin main                     — actualizare main cu ultimele modificari
   git checkout -b feature/nume             — creare branch nou
   git add <fisiere>                        — adaugare fisiere in staging
   git add .                                — adaugare toate fisierele modificate
   git commit -m "mesaj"                    — creare commit
   git push origin feature/nume             — trimitere branch pe GitLab
   git branch -d feature/nume               — stergere branch local dupa merge
   git status                               — verificare stare fisiere
   git log --oneline                        — vizualizare istoric commit-uri
   git diff                                 — vizualizare modificari locale
