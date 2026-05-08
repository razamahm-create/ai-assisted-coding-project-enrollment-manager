# Streamlit Student Enrollment UI Plan

## Draft 1: Requesting the UI Plan

I want you to draft a Streamlit UI plan and record it in `streamlit_ui_plan.md` before any code is changed.

App goal and user assumptions: build a student-facing enrollment app for a user who is already logged in as a student. Use the seeded/current student Maya Patel with `user_id` `u100` and email `maya.patel@example.edu`.

Assumptions: do use the existing seeded student, check that the current role is `student`, and store the role, current page, selected class, and feedback messages in `st.session_state`.

Assumptions: do not build login, registration, password handling, account creation, or a new authentication system.

Existing backend structure: follow the Session 1 layered design. The UI should call `EnrollmentService` in `services.py`, which uses `ConnectionFactory` and `UnitOfWork` from `db.py`, `CourseRepository` and `EnrollmentRepository` from `repositories.py`, DTOs from `models.py`, seed data from `data.py`, and `default_config()` from `config.py`. The UI should make minimal or no changes to backend layers.

Routing and session state: use `st.session_state` for `role`, `page`, `selected_class_id`, and a short feedback message. The dashboard should be the default page. The selected class page should appear after the student enrolls in a class or clicks Go to Class.

Page 1: Student Dashboard: use `st.title`, `st.caption`, `st.metric`, `st.container`, `st.columns`, `st.divider`, `st.form`, `st.text_input`, `st.form_submit_button`, `st.button`, `st.dataframe`, `st.success`, `st.warning`, and `st.error`. Show Maya's enrolled courses, provide a textbox for an enrollment key, let the student go to a selected class, and allow soft-unenrollment.

Page 2: Selected Class Page: use `st.title`, `st.caption`, `st.container`, `st.columns`, `st.metric`, `st.divider`, and `st.button` to show the selected course's course ID, course name, instructor, status, and enrolled timestamp, plus a return-to-dashboard action.

Actions and feedback: valid keys should call `EnrollmentService.enroll_with_key()` and move the student to the selected class page. Invalid keys should show a clear error message. Clicking Unenroll should call `EnrollmentService.soft_unenroll_student()`, keep the row in the database with status `unenrolled`, store a short message in `st.session_state`, and refresh or return to the dashboard.

Plan output: provide a clear Markdown implementation plan that can be reviewed before code changes begin.

## AI-Provided UI Plan

### Backend Entry Points

- Create a small Streamlit app file, `app.py`, in the project directory.
- Initialize the database on app startup by calling `create_tables()` and `seed_sample_data()`.
- Build an `EnrollmentService` using `default_config()`, `ConnectionFactory`, `CourseRepository`, and `EnrollmentRepository`.
- Keep UI behavior in the Streamlit layer and use service methods for enrollment, enrolled-course lookup, enrollment history, summaries, and soft-unenrollment.

### Session State

- Initialize `st.session_state.role` to `student`.
- Initialize `st.session_state.page` to `dashboard`.
- Initialize `st.session_state.selected_class_id` to `None`.
- Initialize `st.session_state.feedback` to `None`.
- Only render student pages when the role is `student`; otherwise show `st.error`.

### Page 1: Student Dashboard

- Show the app title and the simulated current student.
- Show summary metrics from `EnrollmentService.get_student_summary()`.
- Show enrolled courses from `EnrollmentService.get_student_enrollments()`.
- Use a form with `st.text_input` for the enrollment key and `st.form_submit_button` for submission.
- On successful enrollment or re-enrollment, save a success message, set `selected_class_id`, and navigate to the class page.
- On invalid enrollment key, save an error message and remain on the dashboard.
- For each enrolled course, show course name, instructor, status, and enrolled date.
- Provide a Go to Class button that sets `selected_class_id` and routes to the class page.
- Provide an Unenroll button that calls `soft_unenroll_student()`, stores a success or warning message, clears the selected class, and refreshes the dashboard.

### Page 2: Selected Class Page

- Look up the selected class from the student's active enrollments.
- Show course ID, course name, instructor, enrollment status, and enrolled timestamp.
- Include a Back to Dashboard button.
- If the selected class is missing because it was unenrolled or no longer active, show a warning and provide a return action.

### Feedback

- Render `st.success`, `st.warning`, or `st.error` from `st.session_state.feedback`.
- Clear the feedback after it is displayed to keep messages short-lived.

## Plan Review Notes

The plan matches the intended two-page app and follows the Session 1 multi-layer backend. It correctly uses Maya Patel as the simulated student, checks `st.session_state.role`, avoids login/authentication work, and keeps navigation in `st.session_state.page` and `st.session_state.selected_class_id`.

No refinement prompt is needed. The plan is specific enough to implement and does not require backend refactoring.

## Draft 3: Request Implementation

Implement the approved Streamlit UI plan in `app.py`. Use the existing Session 1 backend structure and call `EnrollmentService` for all enrollment behavior. Do not build login, registration, password handling, account creation, or a new authentication system. Use Maya Patel (`u100`, `maya.patel@example.edu`) as the already logged-in student. Keep routing in `st.session_state`, support the dashboard and selected class page, provide clear success/warning/error feedback, and preserve the soft-unenroll behavior by calling `soft_unenroll_student()` rather than deleting rows.

## Implementation Impact Notes

Actual UI-layer change:

- `app.py`: new Streamlit application file for the student dashboard and selected class page.

Actual documentation/planning change:

- `streamlit_ui_plan.md`: records the planning prompt, reviewed UI plan, implementation prompt, and impact check.

Backend impact:

- No backend files were changed. The app calls `EnrollmentService` and preserves the existing repository, database, DTO, seed-data, and configuration layers.

Verification:

- Existing integration tests passed with `python -m pytest`.
- The new app passed a syntax check with `python -m py_compile app.py`.
- The Streamlit server launched successfully and returned HTTP 200 at `http://localhost:8501`.
