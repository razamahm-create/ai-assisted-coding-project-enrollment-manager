Initial Refactor Plan:

You are an expert backend engineer. Produce a detailed, actionable refactor plan to move the procedural student-enrollment backend in enrollment_starter.py toward an object‑oriented, layered design. Base the plan on the structural analysis below and on typical best practices for separating persistence (DB) and business/service logic.

Context / Structural analysis (use these as primary inputs)

DB_PATH, SNAPSHOT_PATH, statuses, current student: Mixed — global constants/config used across DB and service.
AVAILABLE_COURSE_KEYS: Database.
connect: Database (reads global DB_PATH).
create_tables: Database.
seed_sample_data: Database (reads global state).
get_available_course_keys: Database.
get_course_by_key: Database.
get_student_enrollments: Database.
get_student_enrollment_history: Database.
enroll_with_key: Mixed (cross-layer: validation + DB upsert).
soft_unenroll_student: Mixed (cross-layer).
get_student_summary: Service (but currently iterates DB rows — mixed responsibilities).
get_all_enrollment_records: Database.
export_database_snapshot / JSON writing: Mixed (DB read + file I/O).
SQLite SELECT / INSERT / UPDATE statements: Database.
main runner / top-level flow: Mixed (orchestration + side effects + DB setup).
Goals and hard constraints

Keep the persistence layer strictly focused on SQLite responsibilities: schema management, parameterized SELECT/INSERT/UPDATE/DELETE, and simple row-to-dict mapping. The DB layer should expose a small, testable API (method signatures only), and should NOT contain business rules (e.g., enrollment-key semantics).
Keep the service layer responsible for business logic: enrollment-key validation/normalization, dashboard semantics (what "enrolled" means for the UI), summary counting and aggregation, validation and normalization of inputs, and transaction boundaries for composite operations.
Remove or isolate global mutable state (e.g., CURRENT_STUDENT, DB_PATH) and replace with explicit dependency injection or a configuration/context object.
Do not include Streamlit/UI concerns in the plan.
The plan should avoid providing refactored code or code snippets; method/class names and signatures are fine, but no implementations.
Requested deliverables (structured output)

High-level architecture overview: layers, responsibilities, and data flow diagram (text/ASCII or Mermaid).
Proposed classes/modules and responsibilities (e.g., Database, EnrollmentRepository, EnrollmentService, SnapshotExporter, AppRunner), with key public method signatures (name, params, return type/shape) — no method bodies.
File/module layout (filenames and short purpose).
A clear mapping table: each existing function → target class/method where it will live after refactor.
An incremental, prioritized refactor roadmap (phases) with concrete, small tasks per phase. Each task should include:
What to change
Why (purpose / risk mitigated)
Acceptance criteria (how to verify behavior preserved)
Suggested unit/integration tests to add or update
Estimated effort (small/medium/large)
Test plan: unit + integration tests, key test cases (e.g., upsert behavior, reactivation on conflict, soft‑unenroll, summary counts), and guidance for isolating DB in tests (in-memory SQLite or temp DB file).
Migration checklist to apply changes with minimal disruption and roll-back guidance.
Risks & mitigations: scalability (SQLite concurrency), global state, transactional consistency, leaking DB schemas to service/UI, and suggestions for handling each.
Recommendations for dependency injection patterns and minimal interfaces to make DB layer mockable.
A final short prioritized checklist for the first three pull requests to implement the refactor incrementally.


Final Plan:
You are an expert backend engineer. Produce a clear, actionable refactor plan to move the procedural student-enrollment backend in enrollment_starter.py toward an object‑oriented, layered design. Use the structural analysis given below as primary input and explicitly address each weakness called out (DB leaks, global state, transaction ownership, test strategy, PII/redaction, observability, and estimate precision).

Context / structural analysis (use these as primary inputs)

DB_PATH, SNAPSHOT_PATH, statuses, CURRENT_STUDENT: Mixed — global config/state used by DB and service.
AVAILABLE_COURSE_KEYS: Database.
connect: Database (reads global DB_PATH).
create_tables: Database.
seed_sample_data: Database (reads global state).
get_available_course_keys: Database.
get_course_by_key: Database.
get_student_enrollments: Database.
get_student_enrollment_history: Database.
enroll_with_key: Mixed (validation/business logic + DB upsert).
soft_unenroll_student: Mixed (business + DB update).
get_student_summary: Service-like but currently iterates DB rows—mixed responsibility.
get_all_enrollment_records: Database.
export_database_snapshot / JSON writing: Mixed (DB read + file I/O).
SQLite SELECT / INSERT / UPDATE statements: Database.
main runner / top-level flow: Mixed (orchestration + side effects).
Critical fixes I want you to enforce in the plan (do not skip)

Reify storage → domain boundaries: repositories must map DB rows to domain DTOs or typed dicts. Document each DTO’s field names and types so service layer never depends on raw SELECT shapes.
Connection & transaction ownership: require a connection-factory / connection-provider to be injected and specify a UnitOfWork or transaction scope pattern for multi-step operations (who opens/closes transactions; how rollback is handled).
Global state removal: replace CURRENT_STUDENT, DB_PATH, and other globals with an injectable Config/context object; document how to pass it into services/repositories.
Test DB strategy: explicitly state test approaches and trade-offs:
For multi-connection integration tests: prefer temp-file SQLite DBs (temporary files), not plain per-connection in-memory DBs (which are isolated per connection).
For isolated unit tests: in-memory DB or mocked repository is acceptable; document how to share an in-memory DB across connections only if needed (shared-cache caveat).
Recommend a default (temp-file for integration, in-memory for unit).
Snapshot exports & PII: require snapshot export to support configurable PII-redaction/anonymization flags; document minimal default (redact emails) and opt-in clear-data mode.
Observability & errors: require error/exception taxonomy (e.g., ValidationError, NotFoundError, RepositoryError), and logging guidance (what to log at INFO/WARN/ERROR). Describe how the service layer should propagate vs. handle exceptions.
Size estimates: define estimates as numeric ranges (small: <=2 hours; medium: 2–8 hours; large: >8 hours).
Diagrams: prefer Mermaid diagrams for architecture, with a one-paragraph textual fallback.
Two-phase output: produce a concise high-level plan first; wait for my approval before expanding into exhaustive, per-task steps (this reduces scope risk).
Goals & hard constraints

Persistence layer responsibilities: only schema management, parameterized SQL, row→DTO mapping, and simple CRUD/query methods. No business rules, input validation, or summary logic in repositories.
Service layer responsibilities: enrollment-key validation/normalization, dashboard semantics (what counts as enrolled), summary aggregation, transaction boundaries for composite operations, and input validation.
Keep using SQLite for this project by default, but include concrete migration thresholds and a migration path to a server RDBMS.
No UI/Streamlit concerns in the plan.
No refactored code in the plan; method/class names and public signatures are allowed.
Requested deliverables (produce these, but follow two‑phase output rule)
Phase A — High-level (first deliverable)

Brief architecture overview: layers, responsibilities, and a Mermaid diagram (plus one-paragraph textual fallback).
Proposed modules/classes and responsibilities (names only), with public method signatures (name, params, return type/shape) — no implementations.
File/module layout (filenames and purpose).
A mapping table: each existing function → target class/method after refactor.
A prioritized, small-step roadmap (phases) listing what to change and why (acceptance criteria briefly), with task size estimates using the ranges above.
Phase B — Detailed (produce only after I approve Phase A)
6. Detailed tasks per phase: exact refactor steps, acceptance tests, suggested unit/integration tests, and estimated effort (small/medium/large).
7. Test plan details: how to isolate DB in tests, recommended fixtures (temp-file vs in-memory), key test cases (upsert/reactivation, soft-unenroll, summary counts), and mocking guidance.
8. Migration checklist and rollback guidance for switching from file-based SQLite to a server DB.
9. Risks & mitigations: include concrete thresholds for migrating from SQLite (e.g., sustained write contention or locking observed, sustained writes > ~10/sec, many concurrent writers, need for multi-host writes), and suggested mitigations (connection pooling, serialized writes, or migration).
10. Dependency injection recommendations: minimal interfaces (e.g., EnrollmentRepository, ConnectionFactory, UnitOfWork) to make DB layer mockable and testable.
11. A short prioritized checklist for the first three PRs to implement the refactor incrementally.

Style constraints

No implementation code or refactoring patches. Method/class signatures allowed.
Repositories must expose typed DTO shapes and document expected fields/types.
Include explicit transaction ownership statements for each multi-step task (who opens/closes transactions).
Provide concrete test DB recommendations and PII/redaction defaults.
Use Mermaid for diagrams; provide textual fallback.
Use estimate ranges (small <=2h; medium 2–8h; large >8h).
Keep the initial Phase A output concise (1–2 pages). Wait for my confirmation before Phase B.
If you need the