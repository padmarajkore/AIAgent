import json

# Attempt to import the necessary agents.
# These imports assume that this script is either in the same directory as the other agent files,
# or that the 'agents' directory is part of PYTHONPATH, or that this is run from a parent script.

try:
    from .teacher_data_aggregator_agent import TeacherDataAggregatorAgent
    from .student_interaction_agent import StudentInteractionAgent # Needed for the test block
except ImportError:
    print("Warning: Could not import TeacherDataAggregatorAgent or StudentInteractionAgent via relative import.")
    print("Using placeholder classes for TeacherConsoleAgent direct execution if imports fail.")

    class TeacherDataAggregatorAgent: # Placeholder
        def __init__(self):
            self.students_data = {} # student_id: data
            print("Placeholder TeacherDataAggregatorAgent created.")

        def register_student_agent(self, student_agent_instance): # Mocking this part
            self.students_data[student_agent_instance.student_id] = {
                "summary": {"course_name": "Placeholder Course", "activity_count": 0},
                "sw": {"strengths": [], "weaknesses": []}
            }
            print(f"Placeholder student {student_agent_instance.student_id} registered in placeholder aggregator.")

        def get_all_student_ids(self):
            return list(self.students_data.keys())

        def get_student_activity_summary(self, student_id):
            return self.students_data.get(student_id, {}).get("summary", {"error": "Student not found in placeholder"})

        def get_student_strengths_weaknesses(self, student_id):
            return self.students_data.get(student_id, {}).get("sw", {"error": "Student not found in placeholder"})

    class StudentInteractionAgent: # Placeholder for the test block
        def __init__(self, student_id, syllabus_path=None):
            self.student_id = student_id
            print(f"Placeholder StudentInteractionAgent for {student_id} created for console test.")
        def log_activity(self, *args, **kwargs): # Mock method
            pass


class TeacherConsoleAgent:
    def __init__(self, aggregator_agent_instance):
        if not isinstance(aggregator_agent_instance, TeacherDataAggregatorAgent):
            raise ValueError("TeacherConsoleAgent requires a valid TeacherDataAggregatorAgent instance.")
        self.aggregator = aggregator_agent_instance
        print("TeacherConsoleAgent initialized.")

    def display_all_students(self):
        """
        Displays (prints) a list of all student IDs known to the aggregator.
        """
        student_ids = self.aggregator.get_all_student_ids()
        if not student_ids:
            print("No students registered in the system yet.")
            return
        print("\n--- Registered Students ---")
        for idx, student_id in enumerate(student_ids):
            print(f"{idx + 1}. {student_id}")
        return student_ids

    def display_student_activity_summary(self, student_id):
        """
        Displays (prints) the activity summary for a given student_id.
        """
        print(f"\n--- Activity Summary for {student_id} ---")
        summary = self.aggregator.get_student_activity_summary(student_id)
        if "error" in summary:
            print(summary["error"])
        else:
            # Basic print; a real UI would format this nicely
            print(json.dumps(summary, indent=2))
        return summary

    def display_student_strengths_weaknesses(self, student_id):
        """
        Displays (prints) the strengths and weaknesses for a given student_id.
        """
        print(f"\n--- Strengths and Weaknesses for {student_id} ---")
        sw_data = self.aggregator.get_student_strengths_weaknesses(student_id)
        if "error" in sw_data:
            print(sw_data["error"])
        else:
            # Basic print
            print(json.dumps(sw_data, indent=2))
        return sw_data

if __name__ == '__main__':
    print("--- Testing TeacherConsoleAgent ---")

    # Create a dummy syllabus file (needed by StudentInteractionAgent if not using placeholder)
    dummy_syllabus_content = {
        "course_name": "Console Test Course",
        "topics": [{"id": "console_topic_01", "title": "Console Topic 1"}]
    }
    syllabus_file_for_console_test = "dummy_syllabus_console_test.json"
    with open(syllabus_file_for_console_test, 'w') as f:
        json.dump(dummy_syllabus_content, f, indent=2)

    # Determine if we are using actual or placeholder agents
    # This relies on the try-except block at the top
    use_actual_agents = 'ActualStudentAgent' in globals() or \
                        (TeacherDataAggregatorAgent.__module__ != __name__ and StudentInteractionAgent.__module__ != __name__)


    if use_actual_agents:
        print("Attempting to use actual imported agents for console test.")
        # These imports would have succeeded if the files are structured correctly
        # and this is run from a context where they are discoverable (e.g. parent dir)
        from .student_interaction_agent import StudentInteractionAgent as ActualStudentAgentForConsole
        from .teacher_data_aggregator_agent import TeacherDataAggregatorAgent as ActualAggregatorForConsole

        student_agent1 = ActualStudentAgentForConsole("student_alpha", syllabus_file_for_console_test)
        student_agent2 = ActualStudentAgentForConsole("student_beta", syllabus_file_for_console_test)

        # Log some activity for student_alpha
        student_agent1.log_activity("learning", "Alpha learning console topic", "console_topic_01")
        student_agent1.log_activity("exercise", "Alpha exercise console topic", "console_topic_01")


        aggregator = ActualAggregatorForConsole()
        aggregator.register_student_agent(student_agent1)
        aggregator.register_student_agent(student_agent2)

    else:
        print("Using placeholder agents for console test due to import issues or direct execution.")
        # Fallback to placeholders defined within this file
        student_agent1 = StudentInteractionAgent("student_alpha_placeholder") # Placeholder
        student_agent2 = StudentInteractionAgent("student_beta_placeholder")  # Placeholder

        aggregator = TeacherDataAggregatorAgent() # Placeholder
        # The placeholder aggregator has a simplified registration
        aggregator.register_student_agent(student_agent1)
        aggregator.register_student_agent(student_agent2)


    # Initialize the TeacherConsoleAgent with the aggregator
    console_agent = TeacherConsoleAgent(aggregator)

    # Test console agent methods
    console_agent.display_all_students()

    console_agent.display_student_activity_summary("student_alpha") # or student_alpha_placeholder
    console_agent.display_student_strengths_weaknesses("student_alpha") # or student_alpha_placeholder

    console_agent.display_student_activity_summary("student_beta") # or student_beta_placeholder
    console_agent.display_student_strengths_weaknesses("student_beta") # or student_beta_placeholder

    console_agent.display_student_activity_summary("student_gamma_nonexistent")

    # Clean up dummy syllabus
    import os
    if os.path.exists(syllabus_file_for_console_test):
        os.remove(syllabus_file_for_console_test)
    # Clean up other dummy syllabi if they exist from previous agent tests in same dir
    if os.path.exists("dummy_syllabus_agg_test.json"):
        os.remove("dummy_syllabus_agg_test.json")
    if os.path.exists("dummy_syllabus.json"):
        os.remove("dummy_syllabus.json")
