Modulul Înscrieri (Enrollments)

1. Înțelegerea Codului

Dependențe:
1.1 Dependențe directe: Modulul `enrollments` este independent și nu depinde de alte module pentru a funcționa corect.
1.2 Module dependente: Datele gestionate aici sunt esențiale pentru modulele `students`, `professors` și `reports`.

2. Fluxul unei cereri HTTP (Exemplu: Creare Înscriere)

Drumul parcurs de date de la URL până la stocare este următorul:
2.1. Router: Cererea `POST` este recepționată de `enrollments/app/router.py`.
2.2. Validare Schema: Datele de intrare sunt verificate automat față de modelul `EnrollmentCreate` din `schemas.py`.
2.3. Service: Dacă datele sunt valide, rout
erul apelează funcția corespunzătoare din `service.py` pentru logica de business.
2.4. Data: Service-ul salvează obiectul final în dicționarul `enrollments_db` aflat în `data.py`.
2.5. Răspuns: Clientul primește confirmarea sub forma modelului `EnrollmentResponse`.


3. Validări și Controlul Duplicatelor
3.1. Validări Pydantic: Constrângeri de tip `Field` pe `student_id` (>0), `professor_id` (>0) și `course_name` (minim 2 caractere).
3.2. Prevenire duplicate: Logica din `service.py` verifică dacă combinația de `student_id` și `course_name` există deja, aruncând o eroare `HTTP 400 Bad Request` în caz de duplicat.

4. Filtrare și Paginare
Endpoint-ul `GET /enrollments/` a fost extins pentru a suporta query parameters opționali:
4.1. Paginare: `limit` (număr maxim de rezultate, implicit 10) și `offset` (numărul de înregistrări peste care se sare, implicit 0).
4.2. Filtrare dinamică: Se poate filtra lista mare de înscrieri după `student_id`, `professor_id` și/sau `course_name`.

5. Suita de Teste Unitare
Modulul beneficiază de o suită de 5 teste unitare automate implementate în `tests/test_enrollments_router.py` folosind Pytest și TestClient din FastAPI. Acestea validează:
  - Crearea cu succes a unei înscrieri (Răspuns HTTP 201 Created)
  - Blocarea ID-urilor negative de studenți (Validare Pydantic - HTTP 422)
  - Respingerea înscrierilor duplicate la același curs (Logica de business - HTTP 400)
  - Funcționarea corectă a limitării și paginării (Query parameters)
  - Modificarea cu succes a statusului unei înscrieri (HTTP 200 OK)

Pentru a rula aceste teste în mod izolat, activați mediul virtual și executați comanda:
pytest tests/test_enrollments_router.py

6. Actualizare Status Înscriere
Endpoint-ul `PUT /enrollments/{id}/status` permite modificarea stării unei înscrieri existente (ex: în `waitlist`, `enrolled` sau `cancelled`).
6.1. Validare: Noul status trimis în body-ul cererii este validat prin modelul Pydantic `EnrollmentStatusUpdate`.
6.2. Logica de business: În `service.py`, sistemul caută înscrierea după ID. Dacă aceasta nu există, aruncă o eroare `HTTP 404 Not Found`. Dacă există, îi actualizează câmpul `status` în baza de date fictivă.

7. Documentație Interactivă și Schemă Tehnică
7.1. Swagger UI: Rutele modulului pot fi testate interactiv în browser la adresa: `http://localhost:8000/docs`.
7.2. Schemă OpenAPI: Structura completă a API-ului, inclusiv toate modelele de validare și parametrii de query, a fost exportată static în fișierul `enrollments/openapi.json`.
