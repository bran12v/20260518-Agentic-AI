# Pet Adoption Platform

## Objective

Develop a pet adoption backend that empowers a shelter administrator to manage a catalog of adoptable pets and the applications submitted by potential adopters. Each pet has profile information (name, species, age, intake date, health notes), and each application captures the applicant's contact info, household details, and the specific pet they're requesting. The system should make it easy to add pets to the catalog, track incoming applications, mark pets as adopted, and search the catalog and application queue through a clean RESTful API. Prioritize a clear lifecycle on the pet (available → application pending → adopted) so that the shelter never accidentally double-promises a pet. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Pet Management

- **Add New Pet:**
  - Admins should be able to create a new pet record by specifying the name, species (dog / cat / rabbit / other), age in years, intake date, and any health notes.
- **View Pet Details:**
  - Provide a dashboard endpoint where admins can view all pets, their species, age, intake date, current status (available / pending / adopted), and the number of open applications.
- **Edit Pet Information:**
  - Allow admins to update pet details such as health notes, age (annual updates), or the adoption status.
- **Delete Pet:**
  - Admins should be able to delete a pet record. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting a pet that has historical applications (cascade vs preserve for audit).

### Application Management

- **Add Application:**
  - Admins should be able to log an application from a potential adopter, specifying the applicant's name, contact email, household description, and the pet being requested.
- **Edit Application:**
  - Provide functionality to update existing application details, such as correcting the applicant's contact info or changing the application status (pending / approved / rejected / withdrawn).
- **Delete Application:**
  - Implement a feature for admins to remove an application from the queue. Like pet deletion, this should include a confirmation step.
- **View Applications:**
  - Admins should be able to view a list of all applications, with search and filter capabilities based on applicant name, application status, pet species, or date submitted.
- **Match an Application to a Pet:**
  - Provide an endpoint that approves an application and atomically marks the pet as adopted. All other open applications for the same pet should be automatically transitioned to a documented status (rejected / waitlisted).

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like species, age range, adoption status, application status, and date submitted.

### Edge Case Handling

- **Application for an Already-Adopted Pet:**
  - Decide how to handle a new application submitted for a pet whose status is already "adopted." Should the system reject the application, accept it with a warning, or accept it silently (the user may be checking if there are similar pets available)? Document your choice in the README.
- **Multiple Pending Applications for the Same Pet:**
  - Decide how the system handles many pending applications for one pet at the same time. When one is approved, what happens to the others? Are they auto-rejected, moved to a waitlist for similar pets, or left for the admin to handle manually? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to approve different applications for the same pet at the same time, or delete a pet while an application is being submitted. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Pet Matching:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be matching pets to an applicant's stated preferences (household type, activity level, other pets) and returning a ranked list of pets with a one-sentence reason for each match.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Foster Home entity for tracking which pets are placed in temporary care, or a Veterinary Visit entity for medical history.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many pets in one transaction, with all-or-nothing semantics.

## Technical Requirements

Must be a backend solution consisting of:

- Python 3.11+
- Flask 3.x with the app-factory pattern and blueprints
- Pydantic v2 for HTTP-boundary validation
- SQLite (via the sqlite3 stdlib) for persistence, with parameterized queries
- structlog for structured JSON logging with per-request correlation IDs
- pytest with fixtures and parametrize for the test suite
- Docker multi-stage Dockerfile + docker-compose.yml for local stack
- pyproject.toml with a src/ layout and a [project.optional-dependencies] dev block
- Code should be available in a private GitHub repository, with the instructor added as a collaborator
- Possesses all required CRUD functionality
- Handles edge cases effectively

## Non-Functional Requirements

- Well-documented code (module docstrings + function docstrings on public surfaces)
- Code upholds industry best practices (SOLID / DRY / single-responsibility)
- Type hints on every function signature
- Test coverage on happy + error paths (at least 15 pytest tests)
- Structured logs (no print statements in production code paths)
- Container runnable via a single `docker compose up`
- README with one-line install and one-line run instructions
- Pydantic models have explicit field constraints (Literal types, min/max length, ge/le on numerics)
- No mutable default arguments; use field(default_factory=...) for collections
- Errors raise typed exceptions from a DomainError hierarchy, not generic Exception
