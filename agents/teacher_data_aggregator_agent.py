# Assuming StudentInteractionAgent might be in the same directory or accessible via PYTHONPATH
# For direct testing, we might need to adjust imports or run from a higher-level script.
# from .student_interaction_agent import StudentInteractionAgent
# For now, we'll define a placeholder if running this file directly and StudentInteractionAgent is not found.

try:
    from .student_interaction_agent import StudentInteractionAgent
except ImportError:
    # This is a placeholder for direct execution or if the module isn't found immediately.
    # In a real scenario, ensure Python's import system can find student_interaction_agent.
    print("Warning: StudentInteractionAgent not found via relative import. Using placeholder for direct execution.")
    class StudentInteractionAgent: # Placeholder
        def __init__(self, student_id, syllabus_path=None):
            self.student_id = student_id
            self.syllabus = {"course_name": "Dummy Course", "topics": []} if syllabus_path else {}
            self.activity_log = []
            print(f"Placeholder StudentInteractionAgent created for {student_id}")

        def get_activity_summary(self):
            return {"student_id": self.student_id, "summary": "Placeholder summary", "activity_count": len(self.activity_log)}

        def get_strengths_weaknesses(self):
            return {"student_id": self.student_id, "strengths": ["Placeholder Strength"], "weaknesses": ["Placeholder Weakness"]}

        def log_activity(self, activity_type, activity_description, related_topic_id=None):
            self.activity_log.append({"type": activity_type, "desc": activity_description, "topic": related_topic_id})


import json # For the main test block

class TeacherDataAggregatorAgent:
    def __init__(self):
        self.student_agents = {} # student_id: StudentInteractionAgent_instance

    def register_student_agent(self, student_agent_instance):
        """
        Registers a StudentInteractionAgent instance.
        """
        if not isinstance(student_agent_instance, StudentInteractionAgent):
            print("Error: Attempted to register an object that is not a StudentInteractionAgent.")
            return

        if student_agent_instance.student_id in self.student_agents:
            print(f"Warning: Student agent for {student_agent_instance.student_id} already registered. Overwriting.")
        self.student_agents[student_agent_instance.student_id] = student_agent_instance
        print(f"StudentInteractionAgent for student '{student_agent_instance.student_id}' registered.")

    def get_student_activity_summary(self, student_id):
        """
        Retrieves the activity summary for a specific student.
        """
        student_agent = self.student_agents.get(student_id)
        if not student_agent:
            return {"error": f"No student agent found for student_id: {student_id}"}
        return student_agent.get_activity_summary()

    def get_student_strengths_weaknesses(self, student_id):
        """
        Retrieves the strengths and weaknesses analysis for a specific student.
        """
        student_agent = self.student_agents.get(student_id)
        if not student_agent:
            return {"error": f"No student agent found for student_id: {student_id}"}
        return student_agent.get_strengths_weaknesses()

    def get_all_student_ids(self):
        """
        Returns a list of all registered student IDs.
        """
        return list(self.student_agents.keys())


if __name__ == '__main__':
    # This block demonstrates the TeacherDataAggregatorAgent.
    # For this to run correctly, StudentInteractionAgent must be properly importable.
    # If StudentInteractionAgent is in agents/student_interaction_agent.py
    # and this script is agents/teacher_data_aggregator_agent.py,
    # you'd typically run tests from a script in the parent directory (e.g., 'run_tests.py')
    # or configure PYTHONPATH.

    # For standalone testing of this file, we rely on the placeholder if direct import fails.
    # To properly test with the real StudentInteractionAgent:
    # 1. Ensure both files are in the 'agents' directory.
    # 2. Create a dummy_syllabus.json in the 'agents' directory or update path.
    # 3. Run a test script from the parent directory of 'agents'.

    print("--- Testing TeacherDataAggregatorAgent ---")

    # Create dummy syllabus file for student agents
    dummy_syllabus_content = {
        "course_name": "Aggregator Test Course",
        "topics": [
            {"id": "agg_topic_01", "title": "Aggregator Topic 1"},
            {"id": "agg_topic_02", "title": "Aggregator Topic 2"}
        ]
    }
    syllabus_file_for_agg_test = "dummy_syllabus_agg_test.json"
    # Ensure the dummy syllabus is in the same directory as this script for this test
    with open(syllabus_file_for_agg_test, 'w') as f:
        json.dump(dummy_syllabus_content, f, indent=2)

    # Create student agent instances
    # If using the real StudentInteractionAgent, ensure it's found
    try:
        # Attempt to use the real one if it was imported
        from .student_interaction_agent import StudentInteractionAgent as ActualStudentAgent
        # Check if the imported one is not the placeholder
        if "Placeholder" in ActualStudentAgent.__name__: # A bit of a hacky check
             print("Using placeholder StudentInteractionAgent for testing.")
             student1_agent = StudentInteractionAgent(student_id="student001", syllabus_path=syllabus_file_for_agg_test)
             student2_agent = StudentInteractionAgent(student_id="student002", syllabus_path=syllabus_file_for_agg_test)
        else:
            print("Using actual StudentInteractionAgent for testing.")
            student1_agent = ActualStudentAgent(student_id="student001", syllabus_path=syllabus_file_for_agg_test)
            student2_agent = ActualStudentAgent(student_id="student002", syllabus_path=syllabus_file_for_agg_test)
    except ImportError: # Fallback to placeholder if the above try fails at import
        print("Actual StudentInteractionAgent import failed. Using placeholder.")
        student1_agent = StudentInteractionAgent(student_id="student001", syllabus_path=syllabus_file_for_agg_test) # Placeholder
        student2_agent = StudentInteractionAgent(student_id="student002", syllabus_path=syllabus_file_for_agg_test) # Placeholder


    # Log some activities for student1
    student1_agent.log_activity("learning", "Student 1 reading Topic 1", related_topic_id="agg_topic_01")
    student1_agent.log_activity("exercise", "Student 1 exercise Topic 1", related_topic_id="agg_topic_01")

    # Log some activities for student2
    student2_agent.log_activity("learning", "Student 2 reading Topic 2", related_topic_id="agg_topic_02")

    # Create and configure aggregator agent
    aggregator_agent = TeacherDataAggregatorAgent()
    aggregator_agent.register_student_agent(student1_agent)
    aggregator_agent.register_student_agent(student2_agent)

    print(f"Registered students: {aggregator_agent.get_all_student_ids()}")

    print("\n--- Summary for student001 ---")
    summary_s1 = aggregator_agent.get_student_activity_summary("student001")
    print(json.dumps(summary_s1, indent=2))

    print("\n--- Strengths/Weaknesses for student001 ---")
    sw_s1 = aggregator_agent.get_student_strengths_weaknesses("student001")
    print(json.dumps(sw_s1, indent=2))

    print("\n--- Summary for student002 ---")
    summary_s2 = aggregator_agent.get_student_activity_summary("student002")
    print(json.dumps(summary_s2, indent=2))

    print("\n--- Strengths/Weaknesses for student002 ---")
    sw_s2 = aggregator_agent.get_student_strengths_weaknesses("student002")
    print(json.dumps(sw_s2, indent=2))

    print("\n--- Summary for non_existent_student ---")
    summary_s3 = aggregator_agent.get_student_activity_summary("student003")
    print(json.dumps(summary_s3, indent=2))

    # Clean up dummy syllabus
    import os
    if os.path.exists(syllabus_file_for_agg_test):
        os.remove(syllabus_file_for_agg_test)

    # Also remove the one created by student_interaction_agent if it's being tested directly before
    # and created dummy_syllabus.json
    if os.path.exists("dummy_syllabus.json"):
        os.remove("dummy_syllabus.json")
