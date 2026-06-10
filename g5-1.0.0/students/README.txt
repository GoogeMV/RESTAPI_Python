Modulul students gestionează operațiunile CRUD pentru studenți în cadrul aplicației educaționale, precum și integrarea acestora cu alte module (enrollments și grades).

Dependențe externe

Modulul folosește următoarele pachete Python:

-FastAPI, prin componentele APIRouter și HTTPException, pentru definirea rutelor și gestionarea erorilor HTTP
-Pydantic, prin BaseModel, Field și EmailStr, pentru validarea și serializarea datelor
-email-validator, utilizat intern de EmailStr pentru validarea formatului adreselor de email

Module interne de care depinde students

Modulul students depinde direct de următoarele module:

enrollments – utilizat pentru a obține cursurile la care este înscris un student (GET /students/{id}/courses)
grades – utilizat pentru calculul mediei generale (GPA) (GET /students/{id}/gpa)

Dependențele sunt implementate ca soft dependencies, folosind importuri realizate în interiorul funcțiilor din service.py.

Dacă un modul dependent nu este disponibil la runtime:

endpoint-urile afectate returnează fie un răspuns fallback (listă goală),
fie o eroare controlată (ex: 503 Service Unavailable, în funcție de implementare).


Modulul students este utilizat de mai multe componente ale aplicației:

main.py înregistrează router-ul la prefixul /students
enrollments utilizează student_id pentru relații de înscriere
grades utilizează student_id pentru asocierea notelor
reports poate agrega informații despre studenți pentru statistici globale


Validările sunt definite în schemele Pydantic din schemas.py.

   StudentCreate / StudentUpdate:
name: string cu lungime minimă de 3 caractere
email: adresă validă (validată prin EmailStr)
year: număr întreg între 1 și 6 (inclusiv)
   Reguli suplimentare:
câmpurile necunoscute sunt respinse implicit (comportament FastAPI/Pydantic)
update-ul permite câmpuri parțiale (toate câmpurile sunt opționale)
   Reguli de business la nivel service:
email-ul trebuie să fie unic în sistem
nu pot exista doi studenți cu același email

Încălcarea acestei reguli returnează:

400 Bad Request sau 409 Conflict (în funcție de implementare)

Paginare și filtrare

Endpoint-ul de listare:

GET /students/?name=Ion&limit=10&offset=0
   Filtrare:
name → filtrare de tip substring
comparație case-insensitive
filtrul este ignorat dacă lipsește
   Paginare:
limit: număr de rezultate returnate (default: 10)
offset: poziția de start (default: 0)

Paginarea se aplică întotdeauna după filtrare.

Un offset mai mare decât numărul total de rezultate nu este eroare, iar răspunsul este o listă goală.

   Endpoint-uri speciale (cross-module)
   Cursurile studentului
GET /students/{id}/courses

Returnează toate cursurile la care studentul este înscris, prin modulul enrollments.

Dacă modulul enrollments nu este disponibil, endpoint-ul returnează:

listă goală sau mesaj de eroare controlat
   GPA student
GET /students/{id}/gpa

Calculează media notelor studentului pe baza datelor din modulul grades.

Formula utilizată:

media aritmetică a notelor existente
rezultat rotunjit la 2 zecimale

Dacă studentul nu are note:

GPA este 0
   Fluxul unei cereri HTTP
1) De la URL la router.py

FastAPI primește cererea și o direcționează către handler-ul corespunzător din router.py pe baza:

metodei HTTP (GET, POST, PUT, DELETE)
pattern-ului URL

Înainte de apelarea handler-ului:

parametrii sunt validați automat
payload-ul JSON este validat prin Pydantic
query parameters sunt convertiți la tipurile declarate

Dacă validarea eșuează, FastAPI returnează automat:

422 Unprocessable Entity
2) De la router.py la service.py

Router-ul primește date deja validate și le transmite către service.py.

dacă service returnează None → router returnează 404 Not Found
dacă service ridică HTTPException → este propagată automat
răspunsurile valide sunt serializate prin response_model
3) Logica în service.py

În service.py se realizează:

crearea de studenți
actualizarea parțială
ștergerea înregistrărilor
filtrarea datelor
paginarea rezultatelor
verificarea unicitații email-ului

Tot aici sunt implementate:

integrarea cu enrollments
integrarea cu grades
4) Stocarea datelor (data.py)

Modulul utilizează o structură in-memory:

students_db: dicționar cu studenți
next_id: contor pentru generarea ID-urilor

Datele sunt volatile și se pierd la restart.

5) Endpoint-uri cross-module

Pentru endpoint-urile care depind de alte module:

importurile sunt realizate lazy (în interiorul funcțiilor)
evită erori la pornirea aplicației dacă un modul lipsește
erorile sunt gestionate controlat (fallback sau HTTPException)