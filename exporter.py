import json
from pathlib import Path
from typing import Optional
from db import ConnectionFactory


class SnapshotExporter:
    def __init__(self, conn_factory: ConnectionFactory, course_repo, enroll_repo):
        self.conn_factory = conn_factory
        self.course_repo = course_repo
        self.enroll_repo = enroll_repo

    def export(self, path: Path, redact_emails: bool = True, current_student: Optional[dict] = None) -> None:
        with self.conn_factory.get_connection() as conn:
            available_course_keys = self.course_repo.get_all(conn)
            enrollment_table = self.enroll_repo.get_all_enrollment_records(conn)

        if redact_emails:
            for rec in enrollment_table:
                if "email" in rec:
                    rec["email"] = "<redacted>"

        snapshot = {
            "current_student": current_student,
            "available_course_keys": available_course_keys,
            "enrollment_table": enrollment_table,
        }
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
