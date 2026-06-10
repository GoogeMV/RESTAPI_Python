Modulul professors gestioneaza operatiunile CRUD pentru profesori in cadrul aplicatiei.


Dependente externe

Modulul foloseste pachete externe Python:
- FastAPI, prin componentele APIRouter, HTTPException si Query,
  pentru definirea rutelor, gestionarea erorilor HTTP si declararea
  parametrilor de query cu validare
- Pydantic, prin BaseModel, ConfigDict, Field, EmailStr si field_validator,
  pentru validarea si serializarea datelor
- email-validator, folosit intern de EmailStr 
  pentru validarea formatului adreselor de email


Module interne de care depinde professors

Modulul depinde direct de enrollments si students.

Dependenta de enrollments apare la endpoint-urile GET /{id}/courses
(preia cursurile predate de un profesor) si GET /{id}/students
(determina indirect studentii prin inscrieri).

Dependenta de students apare exclusiv la endpoint-ul GET /{id}/students,
care preia detaliile complete ale studentilor identificati prin
enrollments.

Ambele dependente sunt soft: importurile se fac tarziu, in interiorul
functiilor din service.py, astfel incat modulul professors sa porneasca
corect chiar daca dependentele lipsesc la runtime. Daca un modul lipseste,
endpoint-ul afectat returneaza 503 Service Unavailable (sau, in cazul
/courses, un raspuns dedicat cu lista goala, pentru retrocompatibilitate).


Module care depind de professors

Patru module din proiect au o dependenta de professors.

- main.py inregistreaza router-ul modulului la prefixul /professors
- reports importa  professors.app.data in fisierul reports/app/service.py,
  pentru a numara toti profesorii prin functia get_professor_count().
- schedule si enrollments stocheaza in inregistrarile lor un camp professor_id, dar
  nu importa nimic din modulul professors


Validari aplicate

Schemele Pydantic aplica urmatoarele constrangeri pe datele de intrare:

- name: string intre 2 si 100 de caractere, cu spatiile de la inceput
  si sfarsit eliminate automat inainte de validare
- email: format valid de email, verificat de EmailStr
- department: string intre 2 si 100 de caractere, cu spatiile de la
  inceput si sfarsit eliminate automat inainte de validare
- Campurile necunoscute in payload sunt respinse (ConfigDict extra=forbid)

Pe parametrii de query pentru paginare se aplica constrangeri suplimentare,
prin Query() din FastAPI:

- limit: numar intreg intre 1 si 100, cu valoarea implicita 10
- offset: numar intreg mai mare sau egal cu 0, cu valoarea implicita 0

Valorile in afara acestor intervale (limit=0, limit=200, offset=-1 etc.)
produc raspuns 422 Unprocessable Entity, generat automat de FastAPI
inainte ca handler-ul sa fie apelat.

In plus, la nivelul service-ului se aplica o regula de unicitate:
nu pot exista doi profesori cu acelasi email. Incalcarea acestei
reguli, atat la creare cat si la actualizare, returneaza 409 Conflict.


Paginare si filtrare

Endpoint-urile de listare din modul (GET /professors/,
GET /professors/{id}/courses si GET /professors/{id}/students) accepta
parametrii de paginare limit si offset, cu valorile implicite mentionate
mai sus. Paginarea se aplica intotdeauna ultima, dupa filtrare sau
deduplicare.

Endpoint-ul GET /professors/ accepta in plus trei parametri de filtrare
optionali: name, department si email. Comportamentul lor este:

- Comparatia este de tip substring (se potrivesc inregistrarile care
  contin textul cautat oriunde in valoarea campului)
- Comparatia este case-insensitive (Ion, ion si ION produc aceleasi
  rezultate)
- Filtrele se combina cu AND (toate filtrele specificate trebuie sa
  fie satisfacute simultan)
- Un filtru lipsa sau gol este ignorat (nu restrictioneaza rezultatele)

Un offset mai mare decat numarul total de inregistrari (dupa filtrare)
nu este o eroare; raspunsul este 200 cu o lista goala.

Endpoint-ul GET /professors/{id}/students returneaza studentii inscrisi
la cursurile predate de un profesor. Deoarece relatia profesor-student
este indirecta (prin tabela de inscrieri), un student care urmeaza mai
multe cursuri ale aceluiasi profesor apare o singura data in raspuns
(deduplicare dupa student_id). Ordinea studentilor in raspuns este
deterministica (sortare crescatoare dupa id), astfel incat paginarea
sa fie stabila intre apeluri.


Fluxul unei cereri HTTP

Cand un client HTTP trimite o cerere catre un endpoint din professors,
parcurge urmatorul drum prin straturile modulului.


1) De la URL la router.py

FastAPI primeste cererea si o directioneaza catre handler-ul corespunzator
din router.py, pe baza metodei HTTP (POST, GET, PUT, DELETE) si a
pattern-ului URL. Inainte ca handler-ul sa fie apelat efectiv, FastAPI
realizeaza doua operatii automate. Mai intai, extrage si converteste
parametrii de cale, cum ar fi professor_id, dar si parametrii de query,
cum ar fi limit, offset sau name, in tipurile declarate in semnatura
functiei, validand totodata constrangerile declarate prin Query() pentru
parametrii de query. Apoi, pentru cererile cu corp (POST si PUT),
valideaza payload-ul JSON folosind schema Pydantic declarata ca parametru
al handler-ului.
Daca oricare dintre validari esueaza (tip incorect, email invalid,
lungime in afara limitelor, camp necunoscut, limit sau offset in afara
intervalelor permise), FastAPI returneaza automat un raspuns 422
Unprocessable Entity, fara ca handler-ul sa mai fie apelat.


2) De la router.py la service.py

Handler-ul din router.py primeste obiectul Pydantic deja validat, il
transmite mai departe catre functia corespunzatoare din service.py, si
interpreteaza rezultatul. Daca service-ul returneaza None,
router-ul ridica o exceptie HTTPException cu codul 404. Daca service-ul
ridica direct o HTTPException (de exemplu 409 pentru email duplicat),
aceasta este propagata transparent de FastAPI catre client. Pentru 
cereri reusite, dictionarul intors de service este returnat ca raspuns,
iar FastAPI il serializeaza automat in formatul descris de response_model
(de obicei ProfessorResponse).


3) De la service.py la data.py

In service.py se intampla operatiile concrete:
construirea unei noi inregistrari, alegerea urmatorului ID disponibil prin
citirea variabilei next_id, aplicarea actualizarilor partiale in cazul
cererii PUT (cu verificarea fiecarui camp daca este None inainte de
suprascriere), sau stergerea unei inregistrari existente. Tot aici se
aplica, in cazul listarii, filtrarea dupa name, department si email
(comparatie substring case-insensitive, combinata cu AND), urmata de
paginarea cu limit si offset peste rezultatul filtrat.
La creare si la actualizarea email-ului, service-ul verifica unicitatea
email-ului in professors_db si ridica HTTPException 409 daca exista deja
un alt profesor cu acel email.
Dupa fiecare creare, contorul next_id este incrementat pentru a asigura
ID-uri unice.


4) data.py si stocarea

data.py contine doua variabile de modul. Prima este professors_db, un
dictionar Python in care cheile sunt ID-urile profesorilor iar
valorile sunt dictionarele cu informatiile complete despre fiecare
profesor. A doua este next_id, un contor folosit pentru a genera
ID. Datele sunt volatile si se pierd la fiecare repornire a aplicatiei.


5) Endpoint-uri cu dependente cross-modul

Pentru endpoint-urile GET /{id}/courses si GET /{id}/students, service.py
realizeaza importuri tarzii (in interiorul functiei, nu la nivel de modul)
catre enrollments si, respectiv, students. Aceasta abordare permite
modulului professors sa porneasca chiar daca dependentele nu sunt
incarcate; absenta lor este detectata doar la apelarea endpoint-ului
respectiv. Daca importul esueaza, service-ul returneaza None, iar router-ul
transforma acest semnal in 503 Service Unavailable (sau, pentru /courses,
un raspuns dedicat cu lista goala).

In cazul /students, ordinea operatiilor in service este: identificarea
inscrierilor profesorului in enrollments, extragerea student_id-urilor
unice (deduplicare), preluarea detaliilor complete din students_db cu
omiterea silentioasa a referintelor inconsistente (student_id care nu
mai exista), sortarea dupa id si in final paginarea.