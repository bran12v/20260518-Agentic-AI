# Coffee Shop Loyalty

## Objective

Develop a coffee shop loyalty backend that empowers a cafe owner (or loyalty program administrator) to manage a customer base and the orders each customer places, with automatic reward-point accrual. Each customer has a profile (name, email, signup date, tier) and an order history; each order captures drinks purchased, total amount, and points earned. The system should make it easy to add customers, log orders, look up a customer's current point balance, and redeem points for free drinks through a clean RESTful API. Prioritize correct point arithmetic — customers will notice if their balance is wrong — and ensure that redemption cannot result in a negative balance. The deliverable is a containerized service that runs locally via `docker compose up` and exposes a documented REST API.

## Functional Requirements

### Customer Management

- **Add New Customer:**
  - Admins should be able to create a new customer by specifying their name, email address, optional phone number, and signup date (defaulting to today).
- **View Customer Details:**
  - Provide a dashboard endpoint where admins can view all customers, their current point balance, tier (bronze / silver / gold), lifetime spend, and last order date.
- **Edit Customer Information:**
  - Allow admins to update customer details such as name, email, phone number, or tier (in case of a manual upgrade).
- **Delete Customer:**
  - Admins should be able to delete a customer record. Implement a confirmation requirement to prevent accidental deletions. Document the policy on deleting a customer with order history (cascade vs preserve for audit).

### Order Management

- **Add Order:**
  - Admins should be able to log an order against a customer, specifying the drinks purchased (a list of drink name + size + quantity), the total amount in cents, and the timestamp (defaulting to now). Points should be awarded automatically based on the total amount.
- **Edit Order:**
  - Provide functionality to update existing order details, such as correcting the total amount or the drinks list. Editing an order should recalculate the points awarded.
- **Delete Order:**
  - Implement a feature for admins to remove an order. Like customer deletion, this should include a confirmation step. Deleting an order should subtract the points it awarded from the customer's balance.
- **View Orders:**
  - Admins should be able to view a list of all orders, with search and filter capabilities based on customer name, date range, order total, or drink name (partial match).
- **Redeem Points for a Reward:**
  - Provide an endpoint that accepts a customer id and a reward (a free drink of a given size), deducts the appropriate number of points from the customer's balance, and records the redemption. Reject the redemption with a clear error if the balance is insufficient.

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict) should return a consistent JSON shape with an error code, human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose /live and /ready endpoints. /live confirms the process is up; /ready confirms downstream dependencies (the database) are reachable.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method, path, status code, duration, and correlation id. Logs should be machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across common fields like customer tier, date range, order total, and drink name (partial match).

### Edge Case Handling

- **Redemption With Insufficient Points:**
  - Decide how to handle a redemption request when the customer's balance is below the reward cost. The natural answer is "reject with a clear error" — but document the exact error shape and status code so trainees implement it consistently.
- **Refunding an Order:**
  - Decide how to handle a request to delete or refund an order whose earned points have already been redeemed. Should the redemption be reversed, should the customer be left with a negative balance temporarily, or should the deletion be blocked? Document your choice in the README.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and return a 422 with a clear field-by-field error envelope on malformed input.
- **Concurrent Mutations:**
  - Describe what happens if two clients try to log an order or redeem points for the same customer at the same time. Point arithmetic is especially sensitive to race conditions; document how you prevent double-spending or double-awarding. The expected behavior should be documented in your README.

## Stretch Goals

Stretch goals are features you want to add to an application, but they aren't required. For this project, Stretch Goals are a way to go above and beyond the minimum requirements and I look forward to seeing what unique features you will add to your project. Here are some examples you might consider:

- **AI-Assisted Drink Recommendation:**
  - Add an endpoint that calls an LLM (e.g., OpenAI) and returns a Pydantic-validated structured response. For this theme, that could be recommending a drink for a given customer based on their past order history, returning a structured recommendation with the drink name, size, and a one-sentence rationale.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle requests per client IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support an additional related entity — for example a Menu Item entity for normalizing drink names and prices, or a Promotion entity for time-limited point multipliers.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and demonstrates the primary CRUD flow.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table with timestamp, action, entity, and user.
- **Bulk Import:**
  - Add an endpoint that accepts a JSON array (or CSV upload) and inserts many orders in one transaction, with all-or-nothing semantics.

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
