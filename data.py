from typing import List, Dict, Any, Tuple

AVAILABLE_COURSE_KEYS: List[Dict[str, Any]] = [
    {
        "course_id": "MISY350",
        "course_name": "Python for Business Analytics",
        "instructor": "Dr. Rivera",
        "enrollment_key": "MISY350-SPRING",
    },
    {
        "course_id": "DATA210",
        "course_name": "Data Storytelling",
        "instructor": "Prof. Morgan",
        "enrollment_key": "DATA210-SPRING",
    },
    {
        "course_id": "WEB220",
        "course_name": "Web Apps With Streamlit",
        "instructor": "Dr. Chen",
        "enrollment_key": "WEB220-SPRING",
    },
]

SAMPLE_ENROLLMENTS: List[Tuple[str, str, str, str]] = [
    ("u100", "maya.patel@example.edu", "MISY350", "enrolled"),
    ("u100", "maya.patel@example.edu", "DATA210", "unenrolled"),
    ("u101", "alex@example.edu", "MISY350", "enrolled"),
    ("u102", "blair@example.edu", "WEB220", "enrolled"),
]
