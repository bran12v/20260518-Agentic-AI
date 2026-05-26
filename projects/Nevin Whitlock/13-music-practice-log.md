# Music Practice Log

## Objective

Develop a music practice tracking backend that helps a musician (or instrumental teacher administrator) record practice goals and the practice sessions logged against each goal. Each goal is a focused objective — "play the C major scale at 120 bpm cleanly" or "memorize the first movement of the sonata" — and each session records the date, the duration, the instrument used, and notes on progress. The system should make it easy to set goals, log sessions as they happen, review progress toward each goal, and search practice history through a clean RESTful API. Prioritize a clean parent-child relationship between goals and sessions so that "how much have I practiced toward goal X this week" is straightforward to compute. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Goal Management

- **Add New Goal:**
  - Admins should be able to create a new goal by specifying its title (the objective in plain English), the target completion date, the priority level (low / medium / high), and an optional description with success criteria.
- **View Goal Details:**
  - Provide a dashboard endpoint where admins can view all goals, their target date, priority, status (active / achieved / abandoned), total minutes practiced toward the goal, and days remaining until target.
- **Edit Goal Information:**
  - Allow admins to update goal details such as title, target date (extending or pulling forward), priority, or status (marking achieved or abandoned).
- **Delete Goal:**
  - Admins should be able to delete a goal. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting a goal with logged practice sessions (cascade vs orphan the sessions).

### Practice Session Management

- **Add Practice Session:**
  - Admins should be able to log a practice session against a goal, specifying the date, the duration in minutes, the instrument used (e.g., "Acoustic Guitar" / "Piano"), and free-text notes on what was worked on.
- **Edit Practice Session:**
  - Provide functionality to update existing session details, such as correcting the duration, adjusting the date, or amending the notes.
- **Delete Practice Session:**
  - Implement a feature for admins to remove a session. Like goal deletion, this should include a confirmation step.
- **View Practice Sessions:**
  - Admins should be able to view a list of all practice sessions, with search and filter capabilities based on instrument, date range, duration range, or note content (partial match).
- **Compute Weekly Practice Summary:**
  - Provide a read endpoint that returns the total minutes practiced this week, broken down per goal, with the day-of-week distribution and a count of distinct instruments used.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like instrument, goal status, priority, date range, and goal title (partial match).

### Edge Case Handling

- **Practice Session With Zero Duration:**
  - Decide how to handle a session logged with zero or negative duration. Should the system reject it as invalid, accept it as a "no-show" marker for accountability, or treat it as a deletion of the day's entry? Document your choice in the README.
- **Logging Practice Against an Achieved or Abandoned Goal:**
  - Decide how to handle a practice session logged against a goal whose status is already "achieved" or "abandoned." Should the system reject the session, accept it but flag it, or accept it silently (musicians keep practicing even after a goal is met)? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to modify the same goal at the same time, or delete a practice session while the weekly summary endpoint is being computed. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Practice Plan:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be generating a daily practice plan (warm-up, technique, repertoire, cool-down — with target minutes per block) from the user's active goals and recent practice history, returning a structured plan ready to be followed.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Repertoire entity that tracks pieces being learned (separate from goals), or an Instrument entity that captures setup notes and maintenance history.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many practice sessions in one transaction, with all-or-nothing semantics.

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
