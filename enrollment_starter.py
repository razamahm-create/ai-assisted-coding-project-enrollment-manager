"""
Refactored Enrollment starter using layered design.

This module delegates DB and business logic to smaller modules:
 - config: application configuration
 - db: connection factory and schema/seed helpers
 - repositories: low-level SQL operations and row→DTO mapping
 - services: business logic, validation, and transaction boundaries
 - exporter: snapshot export with PII redaction

Run this module to exercise the refactored flows.
"""

from config import default_config
from db import ConnectionFactory, create_tables, seed_sample_data
from repositories import CourseRepository, EnrollmentRepository
from services import EnrollmentService
from exporter import SnapshotExporter


def main() -> None:
    cfg = default_config()
    conn_factory = ConnectionFactory(cfg.db_path)

    # Ensure schema and example data exist
    create_tables(conn_factory)
    seed_sample_data(conn_factory)

    current_student = {
        "user_id": "u100",
        "name": "Maya Patel",
        "email": "maya.patel@example.edu",
    }

    course_repo = CourseRepository()
    enroll_repo = EnrollmentRepository()
    service = EnrollmentService(conn_factory, course_repo, enroll_repo, cfg)
    exporter = SnapshotExporter(conn_factory, course_repo, enroll_repo)

    print("Current student:")
    print(current_student)

    print("\nAvailable enrollment keys:")
    print(service.get_available_course_keys())

    print("\nInitial enrolled classes:")
    print(service.get_student_enrollments(current_student["user_id"]))

    print("\nStudent enters key DATA210-SPRING:")
    print(service.enroll_with_key(current_student["user_id"], current_student["email"], "DATA210-SPRING"))

    print("\nUpdated enrolled classes:")
    print(service.get_student_enrollments(current_student["user_id"]))

    print("\nStudent summary:")
    print(service.get_student_summary(current_student["user_id"]))

    # Export snapshot — explicit opt-in to include clear emails for demo
    exporter.export(cfg.snapshot_path, redact_emails=False, current_student=current_student)
    print(f"\nDatabase snapshot written to: {cfg.snapshot_path}")


if __name__ == "__main__":
    main()
