from typing import TypedDict


class CourseDTO(TypedDict):
    course_id: str
    course_name: str
    instructor: str
    enrollment_key: str


class EnrollmentRecordDTO(TypedDict, total=False):
    enrollment_id: int
    user_id: str
    email: str
    course_id: str
    course_name: str
    instructor: str
    status: str
    enrolled_at: str
