================================================================================
SPECIFICATIE FUNCTIONALITATE NOUA
================================================================================

TITLU:
------
Adaugare documentatie tehnica (README.md) pentru modulul grades




DESCRIERE:
----------
În urma extinderii modulului grades cu funcționalități avansate (validări stricte de 
tip Field, paginare, filtrare după notă minimă, statistici per curs și clasamente 
complexe), este necesară alinierea proiectului la standardele de documentare ale 
echipei. Această propunere vizează crearea fișierului README.md în folderul rădăcină 
al modulului. Fișierul va descrie izolarea arhitecturală a modulului, dependențele 
externe și interne, regulile de business aplicate la validare și modul în care datele 
tranzitează cele patru straturi (router, service, data, schemas). Pentru a asigura o 
lizibilitate ridicată și o parcurgere ușoară la review, documentația va fi structurată 
sub formă de paragrafe cursive.




MODULE AFECTATE:
----------------
Nu există module de cod afectate în mod direct, funcționalitatea API-ului rămânând 
neshimbată. Modificarea vizează exclusiv adăugarea fișierului de documentație:
  Modificari:
    - Creare fișier grades/README.md


ENDPOINT-URI NOI SAU MODIFICATE:
---------------------------------
Nu sunt adăugate sau modificate endpoint-uri din punct de vedere tehnic. Fișierul 
README.md va documenta însă comportamentul complet al tuturor rutelor existente:
- POST /grades/ (Creare notă cu constrângeri de validare)
- GET /grades/ (Listare cu suport pentru paginare și filtru de valoare minimă)
- GET /grades/{grade_id} (Consultare detaliu notă)
- PUT /grades/{grade_id} (Actualizare parțială securizată)
- DELETE /grades/{grade_id} (Ștergere resursă)
- GET /grades/transcript/{student_id} (Situație școlară per student)
- GET /grades/gpa/{student_id} (Calcul și rotunjire medie generală)
- GET /grades/top/{n} (Generare clasament descrescător prin agregare în memorie)
- GET /grades/stats/{course_name} (Statistici descriptive: min, max, medie curs)


CRITERII DE ACCEPTARE:
----------------------
1. Fișierul README.md este creat și plasat corect în folderul grades/.
2. Documentația acoperă toate secțiunile obligatorii: Dependențe externe, Relații cu module interne, Validări de intrare/ieșire, Logica de paginare/agregare și Fluxul cererii HTTP.
3. Secțiunile de text și explicațiile tehnice privind fluxul datelor sunt redactate exclusiv în paragrafe fluide, bine organizate, evitând listele fragmentate sau pereții densi de text.
4. Informațiile documentate reflectă cu precizie de 100% realitatea din cod.