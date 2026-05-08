from typing import Optional, List, Dict
from db import ConnectionFactory, UnitOfWork
from repositories import CourseRepository, EnrollmentRepository
from models import CourseDTO, EnrollmentRecordDTO
from config import Config


class EnrollmentService:
    def __init__(
        self,
        conn_factory: ConnectionFactory,
        course_repo: CourseRepository,
        enroll_repo: EnrollmentRepository,
        config: Config,
    ):
        self.conn_factory = conn_factory
        self.course_repo = course_repo
        self.enroll_repo = enroll_repo
        self.config = config

    def get_available_course_keys(self) -> List[CourseDTO]:
        with self.conn_factory.get_connection() as conn:
            return self.course_repo.get_all(conn)

    def enroll_with_key(self, user_id: str, email: str, enrollment_key: str) -> Optional[EnrollmentRecordDTO]:
        if not user_id or not email or "@" not in email or not enrollment_key:
            return None
        normalized_key = enrollment_key.strip().upper()
        with UnitOfWork(self.conn_factory) as conn:
            course = self.course_repo.get_by_enrollment_key(conn, normalized_key)
            if not course:
                return None
            self.enroll_repo.upsert_enrollment(
                conn, user_id, email, course["course_id"], self.config.status_enrolled
            )
            return self.enroll_repo.get_student_course_record(conn, user_id, course["course_id"])

    def soft_unenroll_student(self, user_id: str, course_id: str) -> bool:
        if not user_id or not course_id:
            return False
        with UnitOfWork(self.conn_factory) as conn:
            updated = self.enroll_repo.soft_unenroll(conn, user_id, course_id, self.config.status_unenrolled)
            return updated > 0

    def get_student_enrollments(self, user_id: str) -> List[EnrollmentRecordDTO]:
        with self.conn_factory.get_connection() as conn:
            return self.enroll_repo.get_student_enrollments(conn, user_id, self.config.status_enrolled)

    def get_student_enrollment_history(self, user_id: str) -> List[EnrollmentRecordDTO]:
        with self.conn_factory.get_connection() as conn:
            return self.enroll_repo.get_student_enrollment_history(conn, user_id)

    def get_student_summary(self, user_id: str) -> Dict[str, int]:
        summary = {"total_records": 0, self.config.status_enrolled: 0, self.config.status_unenrolled: 0}
        history = self.get_student_enrollment_history(user_id)
        for record in history:
            summary["total_records"] += 1
            status = record.get("status")
            if status in summary:
                summary[status] += 1
        return summary

    def get_all_enrollment_records(self) -> List[EnrollmentRecordDTO]:
        with self.conn_factory.get_connection() as conn:
            return self.enroll_repo.get_all_enrollment_records(conn)
