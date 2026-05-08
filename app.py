import streamlit as st

from config import default_config
from db import ConnectionFactory, create_tables, seed_sample_data
from repositories import CourseRepository, EnrollmentRepository
from services import EnrollmentService


CURRENT_STUDENT = {
    "user_id": "u100",
    "name": "Maya Patel",
    "email": "maya.patel@example.edu",
}


@st.cache_resource
def get_enrollment_service() -> EnrollmentService:
    cfg = default_config()
    conn_factory = ConnectionFactory(cfg.db_path)
    create_tables(conn_factory)
    seed_sample_data(conn_factory)
    return EnrollmentService(
        conn_factory=conn_factory,
        course_repo=CourseRepository(),
        enroll_repo=EnrollmentRepository(),
        config=cfg,
    )


def initialize_session_state() -> None:
    defaults = {
        "role": "student",
        "page": "dashboard",
        "selected_class_id": None,
        "feedback": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_feedback(level: str, message: str) -> None:
    st.session_state.feedback = {"level": level, "message": message}


def render_feedback() -> None:
    feedback = st.session_state.get("feedback")
    if not feedback:
        return

    level = feedback.get("level", "info")
    message = feedback.get("message", "")
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    else:
        st.error(message)

    st.session_state.feedback = None


def rerun_app() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def get_selected_enrollment(enrollments: list[dict]) -> dict | None:
    selected_class_id = st.session_state.get("selected_class_id")
    if not selected_class_id:
        return None
    return next(
        (record for record in enrollments if record.get("course_id") == selected_class_id),
        None,
    )


def navigate_to_dashboard() -> None:
    st.session_state.page = "dashboard"
    st.session_state.selected_class_id = None


def navigate_to_class(course_id: str) -> None:
    st.session_state.selected_class_id = course_id
    st.session_state.page = "class"


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Enrollment")
        st.caption(f"Signed in as {CURRENT_STUDENT['name']}")
        st.caption(f"Role: {st.session_state.role}")

        page_options = ["Dashboard"]
        if st.session_state.get("selected_class_id"):
            page_options.append("Selected Class")

        current_index = 1 if st.session_state.page == "class" and len(page_options) > 1 else 0
        selected_page = st.radio("View", page_options, index=current_index)
        st.session_state.page = "class" if selected_page == "Selected Class" else "dashboard"


def render_enrollment_form(service: EnrollmentService) -> None:
    st.subheader("Join a Class")
    with st.form("enrollment_key_form", clear_on_submit=True):
        enrollment_key = st.text_input(
            "Enrollment key",
            placeholder="Example: DATA210-SPRING",
        )
        submitted = st.form_submit_button("Enroll or Re-enroll")

    if not submitted:
        return

    enrollment = service.enroll_with_key(
        CURRENT_STUDENT["user_id"],
        CURRENT_STUDENT["email"],
        enrollment_key,
    )
    if enrollment:
        course_id = enrollment["course_id"]
        set_feedback("success", f"You are enrolled in {course_id}.")
        navigate_to_class(course_id)
        rerun_app()

    set_feedback("error", "That enrollment key is not valid. Check the key and try again.")
    rerun_app()


def render_enrollment_card(service: EnrollmentService, enrollment: dict) -> None:
    course_id = enrollment["course_id"]
    with st.container():
        top_cols = st.columns([3, 1])
        with top_cols[0]:
            st.subheader(enrollment["course_name"])
            st.caption(f"{course_id} with {enrollment['instructor']}")
        with top_cols[1]:
            st.metric("Status", enrollment["status"].title())

        st.caption(f"Enrolled at: {enrollment['enrolled_at']}")
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("Go to Class", key=f"go_{course_id}"):
                navigate_to_class(course_id)
                rerun_app()
        with action_cols[1]:
            if st.button("Unenroll", key=f"unenroll_{course_id}"):
                if service.soft_unenroll_student(CURRENT_STUDENT["user_id"], course_id):
                    set_feedback(
                        "success",
                        f"{enrollment['course_name']} was marked as unenrolled.",
                    )
                else:
                    set_feedback(
                        "warning",
                        f"{enrollment['course_name']} could not be unenrolled.",
                    )
                navigate_to_dashboard()
                rerun_app()


def render_dashboard(service: EnrollmentService) -> None:
    st.title("Student Class Dashboard")
    st.caption(
        f"Already logged in as {CURRENT_STUDENT['name']} "
        f"({CURRENT_STUDENT['email']})."
    )
    render_feedback()

    summary = service.get_student_summary(CURRENT_STUDENT["user_id"])
    enrolled_courses = service.get_student_enrollments(CURRENT_STUDENT["user_id"])

    metric_cols = st.columns(3)
    metric_cols[0].metric("Active Classes", summary.get("enrolled", 0))
    metric_cols[1].metric("Unenrolled Records", summary.get("unenrolled", 0))
    metric_cols[2].metric("Total Records", summary.get("total_records", 0))

    st.divider()
    render_enrollment_form(service)

    st.divider()
    st.subheader("Current Classes")
    if enrolled_courses:
        st.dataframe(
            enrolled_courses,
            use_container_width=True,
            hide_index=True,
            column_order=[
                "course_id",
                "course_name",
                "instructor",
                "status",
                "enrolled_at",
            ],
        )
        for enrollment in enrolled_courses:
            render_enrollment_card(service, enrollment)
    else:
        st.warning("You are not currently enrolled in any classes.")


def render_class_page(service: EnrollmentService) -> None:
    enrolled_courses = service.get_student_enrollments(CURRENT_STUDENT["user_id"])
    selected = get_selected_enrollment(enrolled_courses)

    if not selected:
        st.title("Selected Class")
        render_feedback()
        st.warning("No active selected class was found.")
        if st.button("Back to Dashboard"):
            navigate_to_dashboard()
            rerun_app()
        return

    st.title(selected["course_name"])
    st.caption(f"{selected['course_id']} with {selected['instructor']}")
    render_feedback()

    info_cols = st.columns(3)
    info_cols[0].metric("Course ID", selected["course_id"])
    info_cols[1].metric("Status", selected["status"].title())
    info_cols[2].metric("Instructor", selected["instructor"])

    st.divider()
    with st.container():
        st.subheader("Class Information")
        st.write(f"Enrollment record: {selected['enrollment_id']}")
        st.write(f"Student email: {selected['email']}")
        st.write(f"Enrolled at: {selected['enrolled_at']}")

    st.divider()
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Back to Dashboard"):
            navigate_to_dashboard()
            rerun_app()
    with action_cols[1]:
        if st.button("Unenroll from This Class"):
            if service.soft_unenroll_student(CURRENT_STUDENT["user_id"], selected["course_id"]):
                set_feedback(
                    "success",
                    f"{selected['course_name']} was marked as unenrolled.",
                )
            else:
                set_feedback("warning", "This class could not be unenrolled.")
            navigate_to_dashboard()
            rerun_app()


def main() -> None:
    st.set_page_config(page_title="Student Enrollment", layout="wide")
    initialize_session_state()
    render_sidebar()

    if st.session_state.role != "student":
        st.error("This app is only available to student users.")
        return

    service = get_enrollment_service()
    if st.session_state.page == "class":
        render_class_page(service)
    else:
        render_dashboard(service)


if __name__ == "__main__":
    main()
