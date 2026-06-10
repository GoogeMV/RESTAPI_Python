# Reports

Modulul reports gestioneaza agregarea si analiza datelor din celelalte module ale aplicatiei.
Nu detine o baza de date proprie — citeste din modulele existente si returneaza statistici calculate la cerere.


## Dependente externe

Modulul foloseste pachete externe Python:
- FastAPI, prin componentele APIRouter si Query,
  pentru definirea rutelor si declararea parametrilor de query cu validare
- Pydantic, prin BaseModel, ConfigDict si Field,
  pentru validarea si serializarea datelor


## Module interne de care depinde reports

Modulul depinde de patru module interne.

Dependenta de enrollments apare la endpoint-ul GET /reports/enrollment-stats,
care citeste enrollments_db pentru a numara studentii inscrisi per curs.

Dependenta de grades apare la endpoint-ul GET /reports/grade-distribution,
care citeste grades_db pentru a calcula media notelor per curs.

Dependenta de students apare la endpoint-ul GET /reports/student-count,
care citeste students_db pentru a returna numarul total de studenti.

Dependenta de professors apare la endpoint-ul GET /reports/professor-count,
care citeste professors_db pentru a returna numarul total de profesori.

Dependenta de library apare la endpoint-ul GET /reports/library-stats,
care citeste books_db si loans_db pentru a returna numarul de carti
si imprumuturi active.

Toate dependentele sunt soft: importurile se fac tarziu, in interiorul
functiilor din service.py, astfel incat modulul reports sa porneasca
corect chiar daca un modul lipsa la runtime. Daca un modul lipseste,
functia afectata returneaza o valoare implicita (0 sau dictionar gol).


## Module care depind de reports

- main.py inregistreaza router-ul modulului la prefixul /reports


## Endpoint-uri

| Metoda | URL                          | Descriere                                      |
|--------|------------------------------|------------------------------------------------|
| GET    | /reports/enrollment-stats    | Numarul de studenti inscrisi per curs          |
| GET    | /reports/grade-distribution  | Media notelor per curs                         |
| GET    | /reports/student-count       | Numarul total de studenti                      |
| GET    | /reports/professor-count     | Numarul total de profesori                     |
| GET    | /reports/library-stats       | Total carti si imprumuturi active              |
| GET    | /reports/export              | Toate statisticile intr-un singur JSON         |


### Exemple de cereri si raspunsuri

**GET /reports/enrollment-stats**
```json
{
  "Matematica": 3,
  "Informatica": 5
}
```

**GET /reports/grade-distribution**
```
GET /reports/grade-distribution?min_avg=7.0
```
```json
{
  "Matematica": 8.5,
  "Informatica": 9.0
}
```
Parametrul optional `min_avg` (implicit 0.0) filtreaza cursurile cu media sub valoarea specificata.

**GET /reports/student-count**
```json
{
  "student_count": 42
}
```

**GET /reports/professor-count**
```json
{
  "professor_count": 8
}
```

**GET /reports/library-stats**
```json
{
  "total_books": 120,
  "active_loans": 15
}
```

**GET /reports/export**
```json
{
  "enrollment_stats": { "Matematica": 3, "Informatica": 5 },
  "grade_distribution": { "Matematica": 8.5, "Informatica": 9.0 },
  "student_count": 42,
  "professor_count": 8,
  "library_stats": {
    "total_books": 120,
    "active_loans": 15
  }
}
```


## Validari aplicate

Parametrul de query `min_avg` de la GET /reports/grade-distribution
este validat prin Query() din FastAPI:

- min_avg: numar real mai mare sau egal cu 0.0, cu valoarea implicita 0.0

O valoare in afara acestui interval produce raspuns 422 Unprocessable Entity,
generat automat de FastAPI inainte ca handler-ul sa fie apelat.


## Fluxul unei cereri HTTP

Cand un client HTTP trimite o cerere catre un endpoint din reports,
parcurge urmatorul drum prin straturile modulului.


**1) De la URL la router.py**

FastAPI primeste cererea si o directioneaza catre handler-ul corespunzator
din router.py, pe baza metodei HTTP (GET) si a pattern-ului URL.
Pentru GET /reports/grade-distribution, FastAPI extrage si valideaza
parametrul de query min_avg prin constrangerea declarata cu Query().
Daca validarea esueaza, FastAPI returneaza automat 422 Unprocessable Entity.


**2) De la router.py la service.py**

Handler-ul din router.py apeleaza functia corespunzatoare din service.py
si returneaza direct rezultatul. Nu exista operatii de scriere, deci
nu apar exceptii 409 sau 404 in acest modul.


**3) De la service.py la modulele dependente**

In service.py se fac importuri tarzii catre modulele dependente
(enrollments, grades, students, professors, library). Pentru fiecare
functie, service-ul citeste baza de date a modulului respectiv,
calculeaza statistica ceruta si returneaza rezultatul.
Daca importul esueaza (modul lipsa), functia returneaza valoarea
implicita corespunzatoare (0 sau dictionar gol), fara a ridica exceptii.


**4) data.py si stocarea**

data.py contine doua variabile de modul: reports_db (dictionar gol,
neutilizat) si next_id (contor neutilizat). Modulul reports nu stocheaza
date proprii — toate datele sunt citite la cerere din modulele dependente.


