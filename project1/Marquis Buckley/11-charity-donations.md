# Charity Donation Tracker

## Objective

Develop a charity donation tracking backend that helps a nonprofit administrator manage fundraising campaigns and the individual donations contributed to each campaign. Each campaign has a name, fundraising goal, start and end dates, and a current total raised; each donation captures the donor's name, amount, donation method, and an optional message. The system should make it easy to launch campaigns, log donations as they come in, see real-time progress against goals, and reconcile totals through a clean RESTful API. Prioritize careful money handling — donations are denominated in cents to avoid floating-point error — and ensure that the campaign's "amount raised" is always consistent with the sum of its donations. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Campaign Management

- **Add New Campaign:**
  - Admins should be able to create a new campaign by specifying its name, fundraising goal in cents, start date, end date, and an optional description of the cause.
- **View Campaign Details:**
  - Provide a dashboard endpoint where admins can view all campaigns, their fundraising goal, current amount raised, percentage of goal met, donor count, and days remaining.
- **Edit Campaign Information:**
  - Allow admins to update campaign details such as the name, end date (extending the campaign), or description. Editing the goal mid-campaign should be allowed but should be logged for audit purposes.
- **Delete Campaign:**
  - Admins should be able to delete a campaign. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting a campaign with logged donations (cascade vs preserve for audit — this matters for tax records).

### Donation Management

- **Add Donation:**
  - Admins should be able to log a donation against a campaign, specifying the donor's name, donor email (optional), amount in cents, donation method (credit card / check / cash / crypto), and an optional message from the donor.
- **Edit Donation:**
  - Provide functionality to update existing donation details, such as correcting the donor's name or amount. Editing the amount should recompute the campaign's amount raised.
- **Delete Donation:**
  - Implement a feature for admins to remove a donation. Like campaign deletion, this should include a confirmation step. Deleting a donation should reduce the campaign's amount raised accordingly.
- **View Donations:**
  - Admins should be able to view a list of all donations for a campaign, with search and filter capabilities based on donor name (partial match), amount range, donation method, or date range.
- **Generate Receipt for a Donation:**
  - Provide an endpoint that returns a structured donation receipt (donor info, amount, campaign name, date, the nonprofit's tax id) suitable for the donor's records.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like campaign status (active / ended), date range, donation amount range, and campaign name (partial match).

### Edge Case Handling

- **Donation to an Ended Campaign:**
  - Decide how to handle a donation submitted for a campaign whose end date has passed. Should the system reject the donation, accept it with a "late" flag, or accept it silently (donors sometimes contribute after a campaign closes)? Document your choice in the README.
- **Donation That Exceeds the Remaining Goal:**
  - Decide how to handle a donation amount that would push the campaign's amount raised over its goal. Should the system accept the full amount (overshooting the goal), accept only the amount needed to reach the goal (rejecting the excess), or accept it but flag the campaign as "over-funded"? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to log a donation for the same campaign at the same time. Money totals are especially sensitive to race conditions; document how you prevent double-counting or missed donations. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Impact Summary:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be summarizing the impact of a campaign in one short paragraph suitable for a donor thank-you email, returning a structured summary with the headline number, top donor count, and a one-sentence impact statement.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Donor entity that tracks recurring donors across multiple campaigns, or a Beneficiary entity that records where the funds were ultimately spent.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many donations in one transaction, with all-or-nothing semantics.

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
