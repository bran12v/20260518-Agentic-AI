# Personal Library

## Objective

Develop a personal library backend that helps a reader (or community library administrator) maintain a catalog of books organized into shelves, with the ability to track reading progress per book. Each shelf is its own themed collection — "To Read," "Currently Reading," "All-Time Favorites," "Lent Out" — and each book carries metadata like title, author, ISBN, page count, and genre. The system should make it easy to add, edit, search, and move books between shelves through a clean RESTful API. Prioritize a clean data model where the same book can live on multiple shelves (for example, a book can be "currently reading" AND "borrowed from library") without duplicating its core metadata. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Shelf Management

- **Add New Shelf:**
  - Admins should be able to create a new shelf by specifying its name, owner, color tag, and an optional description.
- **View Shelf Details:**
  - Provide a dashboard endpoint where admins can view all shelves, their owner, current book count, and last-updated timestamp.
- **Edit Shelf Information:**
  - Allow admins to update shelf details like name, color tag, or description.
- **Delete Shelf:**
  - Admins should be able to delete a shelf. Implement a confirmation requirement to prevent accidental deletions. Deleting a shelf should not delete the books themselves, only the placement.

### Book Management

- **Add Book:**
  - Admins should be able to add a book to the catalog, specifying title, author, ISBN, page count, genre, and a personal rating from 1 to 5.
- **Edit Book:**
  - Provide functionality to update existing book details, such as correcting the page count, refining the genre, or adjusting the personal rating after finishing.
- **Delete Book:**
  - Implement a feature for admins to remove a book from the catalog. Like shelf deletion, this should include a confirmation step.
- **View Books:**
  - Admins should be able to view a list of all books, with search and filter capabilities based on title (partial match), author, genre, rating threshold, or page count range.
- **Place Book on Shelf:**
  - Enable adding a book to one or more shelves with an optional position (for ordered shelves) and an optional note (e.g., "borrowed from Sarah, return by July"). A book may appear on multiple shelves but should not be added to the same shelf twice.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like genre, page count range, rating threshold, author, and title (partial match).

### Edge Case Handling

- **Duplicate Book by ISBN:**
  - Decide how to handle adding a book whose ISBN already exists in the catalog. Should the action be rejected as a duplicate, should the existing record be returned instead of creating a new one, or should both coexist? Document your choice in the README.
- **Empty Shelf Deletion:**
  - Decide whether a shelf can be deleted only when empty, or whether it can be deleted at any time (with the books staying in the catalog). The choice has downstream consequences for the user experience; document it.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to modify the same shelf at the same time, or delete a book while another request is placing it on a shelf. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Book Classification:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be classifying a book into genre, sub-genre, and reading-level from its blurb or jacket-copy text, returning a structured classification with a confidence score.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Reading Session entity that records start and end timestamps per book (for tracking time spent reading), or an Author entity with biographical metadata.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload — for example, a Goodreads export) and inserts many books in one transaction, with all-or-nothing semantics.

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
