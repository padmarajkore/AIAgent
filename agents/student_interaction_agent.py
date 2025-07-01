import json
import datetime

class StudentInteractionAgent:
    def __init__(self, student_id, syllabus_path=None):
        self.student_id = student_id
        self.syllabus = None
        self.activity_log = []
        if syllabus_path:
            self.load_syllabus(syllabus_path)

    def load_syllabus(self, syllabus_path):
        """
        Loads the syllabus from a JSON file.
        """
        try:
            with open(syllabus_path, 'r') as f:
                self.syllabus = json.load(f)
            print(f"Syllabus '{self.syllabus.get('course_name', 'Unknown Course')}' loaded for student {self.student_id}.")
        except FileNotFoundError:
            print(f"Error: Syllabus file not found at {syllabus_path}")
            self.syllabus = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from syllabus file {syllabus_path}")
            self.syllabus = {}

    def log_activity(self, activity_type, activity_description, related_topic_id=None):
        """
        Logs a student activity.
        """
        activity = {
            "student_id": self.student_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "activity_type": activity_type,
            "activity_description": activity_description,
            "related_topic_id": related_topic_id
        }
        self.activity_log.append(activity)
        print(f"Activity logged for student {self.student_id}: {activity_description}")
        return activity

    def get_activities(self, topic_id=None):
        """
        Retrieves logged activities.
        Can be filtered by topic_id.
        """
        if topic_id:
            return [activity for activity in self.activity_log if activity.get("related_topic_id") == topic_id]
        return self.activity_log

    def get_activity_summary(self):
        """
        Provides a basic analysis of logged activities.
        For MVP, this will be a count of activities per topic.
        """
        if not self.syllabus or not self.syllabus.get("topics"):
            return {"error": "Syllabus not loaded or has no topics."}

        summary = {}
        for topic in self.syllabus["topics"]:
            topic_id = topic.get("id")
            topic_title = topic.get("title", "Unknown Topic")
            activities_for_topic = [act for act in self.activity_log if act.get("related_topic_id") == topic_id]
            summary[topic_title] = {
                "topic_id": topic_id,
                "activity_count": len(activities_for_topic),
                "activities": activities_for_topic # Include actual activities for MVP review
            }

        # Count activities not linked to any specific topic
        untagged_activities = [act for act in self.activity_log if not act.get("related_topic_id")]
        if untagged_activities:
            summary["Untagged Activities"] = {
                "topic_id": None,
                "activity_count": len(untagged_activities),
                "activities": untagged_activities
            }
        return summary

    def get_strengths_weaknesses(self):
        """
        Rudimentary analysis of strengths and weaknesses based on activity count.
        More sophisticated analysis will be added later.
        For MVP:
        - A topic with many activities might be a strength (or a struggle if activities are 'attempts').
        - A topic with few activities might be a weakness or simply not yet covered.
        This is highly simplistic for now.
        """
        summary = self.get_activity_summary()
        if "error" in summary:
            return {"strengths": [], "weaknesses": [], "message": summary["error"], "details": {}}

        strengths = []
        weaknesses = []
        details = {} # To provide more context if needed

        if not self.syllabus or not self.syllabus.get("topics"):
            return {"strengths": [], "weaknesses": [], "message": "Syllabus not loaded or has no topics.", "details": {}}

        # Constants for thresholds (can be tuned)
        MIN_ACTIVITIES_FOR_STRENGTH = 3
        MIN_LEARNING_ONLY_FOR_WEAKNESS = 2
        APPLICATION_ACTIVITY_TYPES = ["exercise", "assessment", "quiz", "project"] # Extend as needed

        topics_in_syllabus_details = {
            topic.get("id"): topic.get("title") for topic in self.syllabus.get("topics", [])
        }

        processed_topic_ids = set()

        for topic_title_from_summary, summary_details in summary.items():
            if not isinstance(summary_details, dict): continue # Skip non-dict items like 'Untagged Activities' string header

            topic_id = summary_details.get("topic_id")
            if not topic_id: # Handle untagged or non-topic entries
                continue

            processed_topic_ids.add(topic_id)
            current_topic_title = topics_in_syllabus_details.get(topic_id, "Unknown Topic")
            topic_activities = summary_details.get("activities", [])
            activity_count = len(topic_activities)

            activity_types_present = {act.get("activity_type") for act in topic_activities}
            has_application_activity = any(app_type in activity_types_present for app_type in APPLICATION_ACTIVITY_TYPES)

            # Strength Criteria
            if activity_count >= MIN_ACTIVITIES_FOR_STRENGTH and has_application_activity:
                strengths.append(current_topic_title)
                details[current_topic_title] = "Strength: Good engagement with application activities."
            # Weakness Criteria
            elif activity_count >= MIN_LEARNING_ONLY_FOR_WEAKNESS and not has_application_activity:
                # All activities are non-application (e.g., only 'learning')
                weaknesses.append(f"{current_topic_title} (Primarily review, consider application)")
                details[current_topic_title] = "Weakness: Activities suggest review but limited application practice."
            elif activity_count < MIN_ACTIVITIES_FOR_STRENGTH and not has_application_activity and activity_count > 0 :
                 # Low activity count and no application
                weaknesses.append(f"{current_topic_title} (Low engagement, especially in application)")
                details[current_topic_title] = "Weakness: Low overall engagement and lacks application activities."


        # Identify topics in syllabus with no activity as weaknesses
        for topic_id, topic_title in topics_in_syllabus_details.items():
            if topic_id not in processed_topic_ids:
                weaknesses.append(f"{topic_title} (No activity logged)")
                details[topic_title] = "Weakness: No activities logged for this topic."

        # Remove duplicates that might arise from different phrasing but same core topic
        strengths = sorted(list(set(strengths)))
        weaknesses = sorted(list(set(weaknesses)))

        return {"strengths": strengths, "weaknesses": weaknesses, "message": "Analysis complete.", "details": details}


if __name__ == '__main__':
    # Create a dummy syllabus file for testing
    dummy_syllabus_content = {
        "course_name": "Grade 7 Science",
        "topics": [
            {"id": "topic_01", "title": "Introduction to Cells"},
            {"id": "topic_02", "title": "Photosynthesis"},
            {"id": "topic_03", "title": "Genetics Basics"},
            {"id": "topic_04", "title": "Scientific Method"}
        ]
    }
    syllabus_file = "dummy_syllabus.json"
    with open(syllabus_file, 'w') as f:
        json.dump(dummy_syllabus_content, f, indent=2)

    # Test the agent
    student_agent = StudentInteractionAgent(student_id="student001", syllabus_path=syllabus_file)

    if student_agent.syllabus:
        # Log some activities for various scenarios

        # Scenario 1: Clear Strength (Introduction to Cells)
        student_agent.log_activity("learning", "Read about Cell Structure", related_topic_id="topic_01")
        student_agent.log_activity("exercise", "Completed cell diagram exercise", related_topic_id="topic_01")
        student_agent.log_activity("quiz", "Passed Cell Quiz", related_topic_id="topic_01") # New application type

        # Scenario 2: Weakness - Learning only (Photosynthesis)
        student_agent.log_activity("learning", "Watched video on Photosynthesis", related_topic_id="topic_02")
        student_agent.log_activity("learning", "Read notes on Photosynthesis", related_topic_id="topic_02")

        # Scenario 3: Weakness - Low engagement, no application (Genetics Basics)
        student_agent.log_activity("learning", "Read intro to DNA", related_topic_id="topic_03")

        # Scenario 4: Scientific Method - No activity (will be a weakness)

        # Untagged activity
        student_agent.log_activity("learning", "General science news reading")

        print("\n--- All Activities ---")
        for activity in student_agent.get_activities():
            print(activity)

        print("\\n--- Activities for Topic 'topic_01' (Introduction to Cells) ---")
        for activity in student_agent.get_activities(topic_id="topic_01"):
            print(activity)

        print("\\n--- Activity Summary ---")
        summary = student_agent.get_activity_summary()
        print(json.dumps(summary, indent=2))

        print("\\n--- Strengths and Weaknesses (MVP) ---")
        sw_analysis = student_agent.get_strengths_weaknesses()
        print(json.dumps(sw_analysis, indent=2))
    else:
        print("Agent could not be initialized properly due to syllabus issues.")

    # Clean up dummy syllabus
    import os
    os.remove(syllabus_file)
