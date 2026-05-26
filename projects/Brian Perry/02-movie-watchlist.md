# Movie Watchlist

## Objective

Develop a personal movie watchlist backend that lets a user (or family administrator) maintain multiple themed watchlists and the films placed on them. Each watchlist is its own ordered collection — "Friday Date Night," "Documentaries to Watch," "Top 100 to Catch Up On" — and each movie carries metadata like title, release year, runtime, and genre. The system should make it easy to add, edit, search, and remove watchlists and the movies they contain through a clean RESTful API. Prioritize a strong data model so that the same movie can appear on multiple watchlists without duplication, and so that rich filtering (by genre, runtime, year, rating) feels natural at the API layer. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Watchlist Management

- **Add New Watchlist:**
  - Admins should be able to create a new watchlist by specifying its name, owner, visibility (private / shared / public), and an optional description.
- **View Watchlist Details:**
  - Provide a dashboard endpoint where admins can view all watchlists, their owner, current movie count, and last-updated timestamp.
- **Edit Watchlist Information:**
  - Allow admins to update watchlist details like name, description, or visibility setting after creation.
- **Delete Watchlist:**
  - Admins should be able to delete a watchlist. Implement a confirmation requirement to prevent accidental deletions. Deleting a watchlist should not delete the movies themselves, only the association.

### Movie Management

- **Add Movie:**
  - Admins should be able to add a movie to the catalog, specifying title, release year, runtime in minutes, genre, and a user-supplied rating from 1 to 10.
- **Edit Movie:**
  - Provide functionality to update existing movie details, such as correcting the runtime, adjusting the personal rating, or refining the genre.
- **Delete Movie:**
  - Implement a feature for admins to remove a movie from the catalog. Like watchlist deletion, this should include a confirmation step.
- **View Movies:**
  - Admins should be able to view a list of all movies, with search and filter capabilities based on title (partial match), genre, year range, or rating threshold.
- **Attach Movie to Watchlist:**
  - Enable adding a movie to one or more watchlists with an optional priority (1-5) and a personal note. A movie should not appear twice on the same watchlist.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like genre, release year range, rating threshold, and title (partial match).

### Edge Case Handling

- **Adding the Same Movie Twice:**
  - Decide how to handle attempting to add the same movie to a watchlist twice. Should the second attempt be rejected with a 409 Conflict, silently no-op, or update the priority/note? Document your choice in the README.
- **Deleting a Movie Referenced by Many Watchlists:**
  - Decide what happens when a movie is deleted while it appears on multiple watchlists. Should the deletion be blocked, should the movie be removed from all watchlists automatically, or should the API require the caller to detach it first? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to modify the same watchlist at the same time, or delete a movie while another request is attaching it to a watchlist. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Movie Recommendation:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be recommending the next movie a user should watch given their past ratings and preferred genres, returning a movie title plus a one-sentence rationale.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a User Profile entity with watch history, or a Friend follow relationship so users can share watchlists.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many movies in one transaction, with all-or-nothing semantics.

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
