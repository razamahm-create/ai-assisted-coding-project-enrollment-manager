import sqlite3
from typing import List, Optional
from db import rows_to_dicts
from models import CourseDTO, EnrollmentRecordDTO


class CourseRepository:
    def insert_courses(self, conn: sqlite3.Connection, courses: List[CourseDTO]) -> None:
        conn.executemany(
            """
            INSERT OR IGNORE INTO courses (
                course_id, course_name, instructor, enrollment_key
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (c["course_id"], c["course_name"], c["instructor"], c["enrollment_key"])
                for c in courses
            ],
        )

    def get_all(self, conn: sqlite3.Connection) -> List[CourseDTO]:
        rows = conn.execute(
            """
            SELECT course_id, course_name, instructor, enrollment_key
            FROM courses
            ORDER BY course_id
            """
        ).fetchall()
        return rows_to_dicts(rows)

    def get_by_enrollment_key(
        self, conn: sqlite3.Connection, enrollment_key: str
    ) -> Optional[CourseDTO]:
        if not enrollment_key:
            return None
        row = conn.execute(
            """
            SELECT course_id, course_name, instructor, enrollment_key
            FROM courses
            WHERE enrollment_key = ?
            """,
            (enrollment_key,),
        ).fetchone()
        return dict(row) if row else None


class EnrollmentRepository:
    def insert_enrollments(self, conn: sqlite3.Connection, enrollments: List[tuple]) -> None:
        conn.executemany(
            """
            INSERT OR IGNORE INTO enrollments (user_id, email, course_id, status)
            VALUES (?, ?, ?, ?)
            """,
            enrollments,
        )

    def get_student_enrollments(self, conn: sqlite3.Connection, user_id: str, status: str) -> List[EnrollmentRecordDTO]:
        if not user_id:
            return []
        rows = conn.execute(
            """
            SELECT
                e.enrollment_id,
                e.user_id,
                e.email,
                e.course_id,
                c.course_name,
                c.instructor,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            WHERE e.user_id = ? AND e.status = ?
            ORDER BY c.course_id
            """,
            (user_id, status),
        ).fetchall()
        return rows_to_dicts(rows)

    def get_student_enrollment_history(self, conn: sqlite3.Connection, user_id: str) -> List[EnrollmentRecordDTO]:
        if not user_id:
            return []
        rows = conn.execute(
            """
            SELECT
                e.enrollment_id,
                e.user_id,
                e.email,
                e.course_id,
                c.course_name,
                c.instructor,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            WHERE e.user_id = ?
            ORDER BY c.course_id
            """,
            (user_id,),
        ).fetchall()
        return rows_to_dicts(rows)

    def get_student_course_record(self, conn: sqlite3.Connection, user_id: str, course_id: str) -> Optional[EnrollmentRecordDTO]:
        if not user_id or not course_id:
            return None
        row = conn.execute(
            """
            SELECT enrollment_id, user_id, email, course_id, status, enrolled_at
            FROM enrollments
            WHERE user_id = ? AND course_id = ?
            """,
            (user_id, course_id),
        ).fetchone()
        return dict(row) if row else None

    def upsert_enrollment(self, conn: sqlite3.Connection, user_id: str, email: str, course_id: str, status: str) -> None:
        conn.execute(
            """
            INSERT INTO enrollments (user_id, email, course_id, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, course_id)
            DO UPDATE SET
                email = excluded.email,
                status = excluded.status,
                enrolled_at = CURRENT_TIMESTAMP
            """,
            (user_id, email, course_id, status),
        )

    def soft_unenroll(self, conn: sqlite3.Connection, user_id: str, course_id: str, new_status: str) -> int:
        if not user_id or not course_id:
            return 0
        cursor = conn.execute(
            """
            UPDATE enrollments
            SET status = ?
            WHERE user_id = ? AND course_id = ?
            """,
            (new_status, user_id, course_id),
        )
        return cursor.rowcount

    def get_all_enrollment_records(self, conn: sqlite3.Connection) -> List[EnrollmentRecordDTO]:
        rows = conn.execute(
            """
            SELECT
                e.enrollment_id,
                e.user_id,
                e.email,
                e.course_id,
                c.course_name,
                c.instructor,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN courses c ON c.course_id = e.course_id
            ORDER BY e.user_id, e.course_id
            """
        ).fetchall()
        return rows_to_dicts(rows)
