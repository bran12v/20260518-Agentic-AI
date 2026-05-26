# Job Application Tracker

## Objective

Develop a job-search tracking backend that empowers a job seeker (or career coach administrator) to manage their active job applications and the interview rounds associated with each. Each application captures the company name, role title, application date, current status (applied → screening → interview → offer → rejected → withdrawn), salary range, and notes; each interview round records the round number, format (phone / video / on-site), scheduled date, interviewer, and outcome. The system should make it easy to log new applications, advance them through their pipeline, log interview rounds as they happen, and search history through a clean RESTful API. Prioritize a clean lifecycle on the application status so the user can answer "what's in flight right now" at any time. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Application Management

- **Add New Application:**
  - Admins should be able to create a new application by specifying the company name, role title, application date, posting URL, salary range (min/max in a chosen currency), location (city or "remote"), and an initial status of "applied."
- **View Application Details:**
  - Provide a dashboard endpoint where admins can view all applications, their company, role, current status, date applied, total interview rounds scheduled, and days since the last status change.
- **Edit Application Information:**
  - Allow admins to update application details such as status (applied / screening / interview / offer / accepted / rejected / withdrawn), salary range (when an offer is extended), location, or notes.
- **Delete Application:**
  - Admins should be able to delete an application. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting an application with logged interview rounds (cascade vs. preserve for history).

### Interview Round Management

- **Add Interview Round:**
  - Admins should be able to add an interview round to an application, specifying the round number, scheduled date, format (phone / video / on-site / take-home), interviewer name, and an optional preparation note.
- **Edit Interview Round:**
  - Provide functionality to update existing round details, such as rescheduling the date, adding the outcome after the interview, or amending notes.
- **Delete Interview Round:**
  - Implement a feature for admins to remove an interview round. Like application deletion, this should include a confirmation step.
- **View Interview Rounds:**
  - Admins should be able to view a list of all interview rounds for an application, with search and filter capabilities based on date range, format, outcome, or interviewer name (partial match).
- **Advance Application to Next Stage:**
  - Provide an endpoint that transitions an application's status to the next logical stage (e.g., screening → interview, interview → offer) and optionally creates a new interview round in the same transaction. Reject the transition if it doesn't follow the documented status lifecycle.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like status, company (partial match), date range, salary range, and location.

### Edge Case Handling

- **Interview Round on a Rejected / Withdrawn Application:**
  - Decide how to handle adding an interview round to an application whose status is already "rejected" or "withdrawn." Should the system reject the operation, accept it with a flag (the rejection might be premature), or accept it silently? Document your choice in the README.
- **Status Lifecycle Violations:**
  - Decide how to handle status transitions that don't follow the documented order — for example moving directly from "applied" to "offer" without going through "interview." Should the system reject the transition, allow it with a warning, or accept it silently? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to modify the same application at the same time, or delete an interview round while another request is advancing the application. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Cover Letter Generation:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be generating a tailored cover letter from a pasted-in job description and a list of user-provided résumé highlights, returning a structured response with the cover letter body, recommended tone, and the top three highlights it leaned on.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Contact entity for tracking recruiters and hiring managers across multiple applications, or a Document entity for storing resumés and cover letters submitted with each application.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many applications in one transaction, with all-or-nothing semantics.

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
