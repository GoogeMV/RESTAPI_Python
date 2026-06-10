================================================================================
SPECIFICATIE FUNCTIONALITATE NOUA
================================================================================

TITLU:
------
Gestiunea cartilor si imprumuturilor in biblioteca universitara


DESCRIERE:
----------
Adauga un modul de biblioteca care permite gestionarea cartilor si a imprumuturilor studentilor. Modulul expune endpoint-uri REST pentru adaugarea cartilor, imprumutarea si returnarea acestora, precum si verificarea disponibilitatii.

Adaugarea unui endpoint care returneaza istoricul complet al imprumuturilor
unui student, identificat prin ID. Functionalitatea permite interogarea tuturor
cartilor imprumutate de un student (atat imprumuturile active cat si cele
returnate). Aceasta functionalitate conecteaza modulul Library cu datele despre
studenti din alte module ale aplicatiei.


MODULE AFECTATE:
----------------
Modul 1: library
  Modificari: Adaugare router, service si scheme pentru gestionarea
              cartilor si imprumuturilor

Modul 2: app principal
  Modificari: Inregistrarea router-ului library in aplicatia FastAPI


ENDPOINT-URI NOI SAU MODIFICATE:
---------------------------------
Endpoint 1:
  Metoda: POST
  URL: /books
  Parametri: title (str), author (str), isbn (str), copies (int)
  Raspuns: BookResponse cu id, title, author, isbn, copies

Endpoint 2:
  Metoda: GET
  URL: /books
  Parametri: niciunul
  Raspuns: lista de BookResponse

Endpoint 3:
  Metoda: GET
  URL: /books/{book_id}
  Parametri: book_id (int, path)
  Raspuns: BookResponse sau 404

Endpoint 4:
  Metoda: POST
  URL: /borrow
  Parametri: book_id (int), student_id (int)
  Raspuns: LoanResponse sau 400 daca nu sunt exemplare disponibile

Endpoint 5:
  Metoda: POST
  URL: /return
  Parametri: loan_id (int)
  Raspuns: LoanResponse actualizat sau 404

Endpoint 6:
  Metoda: GET
  URL: /availability/{book_id}
  Parametri: book_id (int, path)
  Raspuns: { book_id, title, total_copies, available_copies }

Endpoint 7:
  Metoda: GET
  URL: /library/student/{student_id}/history
  Parametri: student_id (path parameter, integer, obligatoriu, gt=0)
  Raspuns: 200 - lista de obiecte LoanResponse (id, book_id, student_id, status)
           404 - {"detail": "No loan history found for this student"}
           422 - daca student_id este 0 sau negativ

CRITERII DE ACCEPTARE:
----------------------
1. POST /books adauga corect o carte si returneaza HTTP 201
2. POST /borrow scade numarul de exemplare disponibile cu 1
3. Imprumutul este refuzat (400) daca nu exista exemplare disponibile
4. POST /return marcheaza imprumutul ca returnat si creste copies cu 1
5. Un imprumut deja returnat nu poate fi returnat din nou (404)
6. GET /availability returneaza corect totalul si exemplarele disponibile

Pentru GET/history
7. Endpoint-ul returneaza 200 si lista completa de imprumuturi
   (active si returnate) pentru un student care are istoric.
8. Endpoint-ul returneaza 404 daca studentul nu are niciun imprumut inregistrat.
9. Endpoint-ul returneaza 422 daca student_id este 0 sau un numar negativ.
10. Lista returnata contine doar imprumuturile studentului specificat,
   nu ale altor studenti.
11. Sunt adaugate teste unitare pentru toate cele 3 cazuri de mai sus.