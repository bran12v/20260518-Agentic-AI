# Conference Talk Tracker

## Objective

Develop a conference talk tracking backend that empowers a conference administrator to manage talks submitted by speakers across multiple tracks and days. Each talk has a title, abstract, duration, difficulty level, and an assigned track; each speaker has profile information and may have submitted multiple talks. The system should make it easy to add speakers, log talk submissions, schedule accepted talks into time slots, and search across the schedule through a clean RESTful API. Prioritize a clean parent-child relationship between speakers and talks so that filtering ("show me all keynotes from speaker X across all years") is straightforward, and ensure that scheduling logic prevents the same speaker from being double-booked. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Talk Management

- **Add New Talk:**
  - Admins should be able to create a new talk by specifying its title, abstract, duration in minutes (typically 25, 45, or 60), difficulty level (beginner / intermediate / advanced), and the proposed track (e.g., "AI" / "Frontend" / "Infrastructure").
- **View Talk Details:**
  - Provide a dashboard endpoint where admins can view all talks, their status (submitted / accepted / rejected / scheduled), assigned speaker, scheduled time slot (if any), and acceptance/rejection date.
- **Edit Talk Information:**
  - Allow admins to update talk details such as the abstract (after speaker revisions), duration, difficulty, track, or status.
- **Delete Talk:**
  - Admins should be able to delete a talk. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting an accepted talk that was already scheduled (release the time slot or block the deletion?).

### Speaker Management

- **Add Speaker:**
  - Admins should be able to add a speaker by specifying their full name, email address, biography, optional company affiliation, and optional social handle.
- **Edit Speaker:**
  - Provide functionality to update existing speaker details, such as correcting the bio, updating affiliation after a job change, or fixing a typo in the email.
- **Delete Speaker:**
  - Implement a feature for admins to remove a speaker. Like talk deletion, this should include a confirmation step. Document the policy on deleting a speaker who has accepted talks.
- **View Speakers:**
  - Admins should be able to view a list of all speakers, with search and filter capabilities based on name (partial match), company, track of their talks, or talk count.
- **Schedule a Talk to a Time Slot:**
  - Provide an endpoint that assigns an accepted talk to a specific date and time slot. Reject the assignment if the same speaker is already scheduled in an overlapping time slot.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like track, difficulty, talk status, speaker name (partial match), and scheduled date.

### Edge Case Handling

- **Double-Booking a Speaker:**
  - Decide how to handle scheduling an accepted talk when the same speaker is already scheduled in an overlapping time slot. The natural answer is "reject with a clear conflict error" — document the exact error shape and which conflicting talk is identified in the response.
- **Accepting a Withdrawn Talk:**
  - Decide how to handle a talk whose status was previously set to "rejected" or "withdrawn" but is now being accepted (because of a last-minute opening). Should the status flip be allowed freely, require a separate "reinstate" action, or be blocked entirely? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to schedule different talks into the same time slot at the same time, or delete a speaker while a talk is being scheduled. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Abstract Generation:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be generating a structured talk abstract (headline, three key takeaways, target audience) from a speaker's free-form notes, returning a Pydantic-validated abstract ready to be reviewed.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Track entity for managing track owners and capacity, or an Attendee entity for tracking who is registered for which talk.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many talks in one transaction, with all-or-nothing semantics.

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
