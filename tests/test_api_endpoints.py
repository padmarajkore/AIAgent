import unittest
import requests
import json
import time # May be needed if services need a moment to update

# Base URLs for the running services
STUDENT_SERVICE_BASE_URL = "http://localhost:5001"
TEACHER_SERVICE_BASE_URL = "http://localhost:5000"

# Known student IDs from the services' initialization logic
# student_service_app initializes 'student007'
# teacher_service_app initializes 'student001', 'student002', 'student007_mirrored'
DEFAULT_STUDENT_ID_FOR_STUDENT_SVC = "student007" # From student_service_app.py
EXISTING_STUDENT_ID_FOR_TEACHER_SVC = "student001" # From teacher_service_app.py
MIRRORED_STUDENT_ID_IN_TEACHER_SVC = "student007_mirrored"
NON_EXISTENT_STUDENT_ID = "student_nonexistent_999"
DEFAULT_TEACHER_ID = "teacher01" # teacher_id is a path param, but not strictly used for auth/scoping in MVP

class TestStudentServiceAPI(unittest.TestCase):

    def test_01_get_syllabus_existing_student(self):
        student_id = DEFAULT_STUDENT_ID_FOR_STUDENT_SVC
        response = requests.get(f"{STUDENT_SERVICE_BASE_URL}/students/{student_id}/syllabus")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("course_name", data)
        self.assertIn("topics", data)
        self.assertTrue(isinstance(data["topics"], list))

    def test_02_get_syllabus_new_student(self):
        # The student service creates a new student agent on the fly if ID is unknown
        new_student_id = "student_new_test_001"
        response = requests.get(f"{STUDENT_SERVICE_BASE_URL}/students/{new_student_id}/syllabus")
        self.assertEqual(response.status_code, 200) # Expects it to be created with default syllabus
        data = response.json()
        self.assertIn("course_name", data)
        # It should load 'sample_syllabus.json' or a placeholder if that file is missing
        self.assertTrue(data["course_name"] == "Grade 7 General Science" or "Placeholder" in data["course_name"])


    def test_03_log_activity_and_get_dashboard(self):
        student_id = DEFAULT_STUDENT_ID_FOR_STUDENT_SVC
        activity_payload = {
            "activity_type": "unittest_learning",
            "activity_description": "Student service API test - logging activity",
            "related_topic_id": "sci_topic_01" # from sample_syllabus.json
        }
        response = requests.post(
            f"{STUDENT_SERVICE_BASE_URL}/students/{student_id}/activities",
            json=activity_payload
        )
        self.assertEqual(response.status_code, 201)
        logged_activity = response.json()
        self.assertEqual(logged_activity["activity_description"], activity_payload["activity_description"])
        self.assertEqual(logged_activity["student_id"], student_id)

        # Now check the dashboard
        time.sleep(0.1) # Give a tiny moment for any internal updates if truly async (not in current MVP)
        response = requests.get(f"{STUDENT_SERVICE_BASE_URL}/students/{student_id}/dashboard_data")
        self.assertEqual(response.status_code, 200)
        dashboard_data = response.json()
        self.assertIn("activity_summary", dashboard_data)
        self.assertIn("strengths_weaknesses", dashboard_data)

        # Check if the activity summary reflects the new activity (simplistic check)
        found_activity_in_summary = False
        summary = dashboard_data["activity_summary"]
        if summary and isinstance(summary, dict):
            for topic_title, details in summary.items():
                if isinstance(details, dict) and "activities" in details:
                    for act in details["activities"]:
                        if act["activity_description"] == activity_payload["activity_description"]:
                            found_activity_in_summary = True
                            break
                if found_activity_in_summary:
                    break
        self.assertTrue(found_activity_in_summary, "Logged activity not found in dashboard summary.")

    def test_04_log_activity_bad_request(self):
        student_id = DEFAULT_STUDENT_ID_FOR_STUDENT_SVC
        activity_payload_bad = {
            "activity_description": "Missing type"
            # "activity_type" is missing
        }
        response = requests.post(
            f"{STUDENT_SERVICE_BASE_URL}/students/{student_id}/activities",
            json=activity_payload_bad
        )
        self.assertEqual(response.status_code, 400)
        error_data = response.json()
        self.assertIn("error", error_data)


class TestTeacherServiceAPI(unittest.TestCase):

    def test_01_get_all_students_for_teacher(self):
        response = requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("student_ids", data)
        self.assertTrue(isinstance(data["student_ids"], list))
        # Check for students initialized in teacher_service_app.py
        self.assertIn(EXISTING_STUDENT_ID_FOR_TEACHER_SVC, data["student_ids"])
        self.assertIn(MIRRORED_STUDENT_ID_IN_TEACHER_SVC, data["student_ids"])

    def test_02_get_student_summary_existing(self):
        student_id = EXISTING_STUDENT_ID_FOR_TEACHER_SVC
        response = requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students/{student_id}/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertTrue(isinstance(data["summary"], dict))
        # teacher_service_app logs some mock activity for student001
        self.assertTrue(data["summary"]["Introduction to Cells"]["activity_count"] > 0 or \
                        data["summary"]["Living Organisms"]["activity_count"] > 0 or \
                        data["summary"]["The Scientific Method"]["activity_count"] > 0 )


    def test_03_get_student_summary_non_existent(self):
        response = requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students/{NON_EXISTENT_STUDENT_ID}/summary")
        self.assertEqual(response.status_code, 404) # As per teacher_service_app logic

    def test_04_get_student_strengths_weaknesses_existing(self):
        student_id = EXISTING_STUDENT_ID_FOR_TEACHER_SVC
        response = requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students/{student_id}/strengths_weaknesses")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("strengths_weaknesses", data)
        self.assertTrue(isinstance(data["strengths_weaknesses"], dict))
        self.assertIn("strengths", data["strengths_weaknesses"])
        self.assertIn("weaknesses", data["strengths_weaknesses"])

    def test_05_get_student_strengths_weaknesses_non_existent(self):
        response = requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students/{NON_EXISTENT_STUDENT_ID}/strengths_weaknesses")
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    print("IMPORTANT: Ensure student_service_app.py (port 5001) and teacher_service_app.py (port 5000) are running before starting these tests.")
    time.sleep(2) # Give a moment for user to acknowledge the message

    # Check if services are reachable before running tests
    try:
        requests.get(f"{STUDENT_SERVICE_BASE_URL}/students/{DEFAULT_STUDENT_ID_FOR_STUDENT_SVC}/syllabus", timeout=1)
        print("Student service seems reachable.")
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Student service at {STUDENT_SERVICE_BASE_URL} is not reachable. Please start it.")
        exit(1)

    try:
        requests.get(f"{TEACHER_SERVICE_BASE_URL}/teachers/{DEFAULT_TEACHER_ID}/students", timeout=1)
        print("Teacher service seems reachable.")
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Teacher service at {TEACHER_SERVICE_BASE_URL} is not reachable. Please start it.")
        exit(1)

    print("\nStarting API endpoint tests...\n")
    unittest.main()
