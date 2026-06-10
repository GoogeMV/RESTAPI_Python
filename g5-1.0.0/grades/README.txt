Modulul grades gestionează operațiunile CRUD pentru notele studenților, precum și calculul de statistici academice și clasamente în cadrul aplicației.
Dependențe externe

În ceea ce privește dependențele externe, modulul utilizează framework-ul FastAPI prin intermediul componentelor APIRouter, HTTPException, Query și Path pentru a defini rutele, a gestiona erorile HTTP și a declara parametrii de cale și query cu validare integrată. De asemenea, pachetul se bazează pe biblioteca Pydantic, folosind clasele BaseModel și Field pentru definirea schemelor de date, constrângerea tipurilor și validarea automată a payload-urilor de intrare și ieșire.
Module interne de care depinde grades

Acest modul funcționează în mod autonom în ceea ce privește stocarea datelor, salvând referințe directe către entități externe sub formă de ID-uri de studenți și șiruri de caractere pentru numele cursurilor în propria sa structură. Modulul nu realizează importuri încrucișate la runtime din alte module de business pentru operațiunile sale standard, ceea ce asigură o decuplare ridicată a componentelor din sistem.
Module care depind de grades

Pe de altă parte, alte componente ale proiectului depind direct de modulul de note. Fișierul principal main.py este cel care înregistrează router-ul modulului la prefixul general /grades, în timp ce suita de teste localizată în grades/tests/test_router.py depinde în mod direct de expunerea corectă a rutelor și de structura internă din data.py pentru simularea stării bazei de date în timpul verificărilor unitare.
Validări aplicate

Schemele de validare implementate prin Pydantic impun constrângeri stricte pe datele primite de la utilizator. Astfel, identificatorul studentului trebuie să fie întotdeauna un număr întreg strict pozitiv, în timp ce numele cursului trebuie să fie un șir de caractere cu o lungime cuprinsă între 3 și 100 de elemente. Nota în sine este definită ca un număr real cuprins obligatoriu în intervalul academic valid de la 1.0 la 10.0.

În mod similar, parametrii de query folosiți la listare și parametrii de cale sunt controlați riguros prin FastAPI, limitând numărul de rezultate pe pagină între 1 și 100 cu o valoare implicită de 10, iar decalajul offset trebuie să fie un număr mai mare sau egal cu 0. Filtrele opționale precum nota minimă trebuie să respecte aceleași limite academice, iar parametrul pentru clasament trebuie să fie strict pozitiv. Orice abatere de la aceste reguli determină respingerea automată a cererii cu un status 422 Unprocessable Entity.
Paginare, filtrare și agregare complexă

Modulul oferă capabilități avansate de manipulare și interpretare a seturilor de date prin rute specifice. Endpoint-ul de listare returnează notele stocate aplicând opțional un filtru de valoare minimă, caz în care paginarea se execută întotdeauna ultima, pe setul de date deja filtrat.

O altă rută importantă este cea dedicată statisticilor unui curs, care realizează o căutare insensibilă la majuscule și curăță spațiile libere accidentale pentru numele cursului solicitat, calculând în timp real media notelor rotunjită la două zecimale, nota maximă, nota minimă și volumul total de note acordate; dacă cursul nu este găsit, se returnează un status 404 Course not found.

În cele din urmă, endpoint-ul pentru topul studenților execută o operație de agregare complexă, grupând toate notele din memorie per student, calculând media generală (GPA), sortând rezultatele în ordine descrescătoare și returnând exact numărul de înregistrări solicitat de utilizator.
Fluxul unei cereri HTTP

1) De la URL la router.py
Atunci când un client trimite o cerere HTTP către modulul de note, aceasta este interceptată de FastAPI și mapată pe handler-ul corect din router.py pe baza metodei HTTP și a URL-ului. Înainte de a rula funcția propriu-zisă, framework-ul extrage parametrii din cale sau query, validează payload-ul JSON pentru cererile de tip POST și PUT folosind regulile din schemas.py și verifică limitele impuse. Dacă regulile sunt încălcate, execuția este blocată instantaneu, iar sistemul întoarce un răspuns standardizat de eroare 422 Unprocessable Entity.

2) De la router.py la service.py
După ce trece de validările inițiale, handler-ul din router.py primește datele curate și le pasează direct către stratul de business din service.py. Router-ul se ocupă de formatarea răspunsurilor prin intermediul modelelor dedicate, cum ar fi GradeResponse, StudentGPA sau CourseStatsResponse. Tot în acest punct sunt gestionate semnalele de eroare venite din service; dacă o funcție întoarce None sau False, router-ul ridică o excepție explicită de tip HTTPException cu codul 404 Not Found, folosind detalii specifice precum "Grade not found" sau "Course not found".

3) De la service.py la data.py
În cadrul stratului service.py se află implementarea efectivă a tuturor algoritmilor și a logicii de business. Pentru crearea unei note, service-ul citește valoarea curentă a contorului de ID-uri, construiește dicționarul notei, îl salvează în structura globală și apoi incrementează contorul pentru a asigura unicitatea următoarei înregistrări. Pentru actualizări parțiale, se verifică prezența fiecărui câmp în payload înainte de a suprascrie resursa existentă, iar pentru listări și clasamente, tot în acest strat se execută filtrările, calculele matematice și sortările descrescătoare.

4) data.py și stocarea în memorie
Ultimul nivel este reprezentat de data.py, care acționează ca un mediu de stocare volatil. Acesta conține dicționarul principal grades_db în care cheile sunt ID-urile unice ale notelor, iar valorile sunt dicționarele cu informațiile complete, alături de contorul next_id folosit pentru auto-incrementare. Deoarece toate aceste date trăiesc exclusiv în memoria RAM, ele sunt volatile și se pierd complet la fiecare repornire a serverului ASGI.