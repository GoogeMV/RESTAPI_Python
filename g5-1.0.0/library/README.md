# Modulul Library

Modulul Library gestioneaza cartile si imprumuturile dintr-o biblioteca universitara.
Permite adaugarea cartilor, imprumutarea si returnarea lor, si vizualizarea istoricului.

## Endpoint-uri

| Metoda | URL | Descriere |
|--------|-----|-----------|
| POST | `/library/books` | Adauga o carte noua |
| GET | `/library/books` | Listeaza cartile (paginare + filtrare dupa autor) |
| GET | `/library/books/{book_id}` | Returneaza o carte dupa ID |
| POST | `/library/borrow` | Imprumuta o carte |
| POST | `/library/return` | Returneaza o carte imprumutata |
| GET | `/library/loans` | Listeaza imprumuturile (optional filtrat dupa student) |
| GET | `/library/availability/{book_id}` | Verifica disponibilitatea unei carti |
| GET | `/library/student/{student_id}/history` | Istoricul imprumuturilor unui student |

## Exemple

**Adauga o carte:**
```
POST /library/books
{
"title": "Clean Code",
"author": "Robert Martin",
"isbn": "9780132350884",
"copies": 3
}
```


**Imprumuta o carte:**
```
POST /library/borrow
{
"book_id": 1,
"student_id": 42
}
```


**Istoric student:**
```
GET /library/student/42/history
→ 200 [{"id": 1, "book_id": 1, "student_id": 42, "status": "active"}]
→ 404 daca studentul nu are imprumuturi
→ 422 daca student_id <= 0
```


## Dependente de alte module

Modulul Library este independent — nu apeleaza alte module.
Datele despre `student_id` sunt furnizate de clientul care face cererea,
fara validare cross-modul (nu verifica daca studentul exista in modulul Students).

## Rulare teste
pytest tests/test_router_library.py -v