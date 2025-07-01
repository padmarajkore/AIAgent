from flask import Flask, request, jsonify
from agents.student_interaction_agent import StudentInteractionAgent
import os
import json

app = Flask(__name__)

# --- In-memory storage for student agents ---
# In a real application, you'd have a more robust way to manage and persist these.
# For MVP, we'll pre-initialize a couple.
student_agents = {}

# --- Helper function to get or create student agent ---
def get_student_agent(student_id):
    if student_id not in student_agents:
        # For MVP, assume a common syllabus or specific ones if configured
        syllabus_filename = "sample_syllabus.json" # Ensure this exists
        syllabus_path = os.path.join(os.path.dirname(__file__), 'agents', syllabus_filename)

        if not os.path.exists(syllabus_path):
            # Create a minimal dummy if not found, to prevent crash, but log error
            print(f"ERROR: Syllabus file {syllabus_path} not found! Creating a placeholder for student {student_id}.")
            placeholder_syllabus_content = {"course_name": "Placeholder Course - File Missing", "topics": []}
            # Attempt to create it in the expected location for future runs if possible
            try:
                os.makedirs(os.path.join(os.path.dirname(__file__), 'agents'), exist_ok=True)
                with open(syllabus_path, 'w') as f:
                    json.dump(placeholder_syllabus_content, f)
                print(f"Placeholder syllabus created at {syllabus_path}")
            except Exception as e:
                print(f"Could not create placeholder syllabus: {e}")
            # Still initialize agent with a basic structure
            student_agents[student_id] = StudentInteractionAgent(student_id=student_id)
            student_agents[student_id].syllabus = placeholder_syllabus_content # Manually set basic syllabus
        else:
            student_agents[student_id] = StudentInteractionAgent(student_id=student_id, syllabus_path=syllabus_path)
            if not student_agents[student_id].syllabus: # If loading failed for other reasons
                 student_agents[student_id].syllabus = {"course_name": "Placeholder Course - Load Failed", "topics": []}


    return student_agents[student_id]

@app.route('/students/<student_id>/activities', methods=['POST'])
def log_student_activity(student_id):
    agent = get_student_agent(student_id)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    activity_type = data.get('activity_type')
    activity_description = data.get('activity_description')
    related_topic_id = data.get('related_topic_id')

    if not all([activity_type, activity_description]):
        return jsonify({"error": "Missing 'activity_type' or 'activity_description'"}), 400

    activity = agent.log_activity(activity_type, activity_description, related_topic_id)
    return jsonify(activity), 201

@app.route('/students/<student_id>/dashboard_data', methods=['GET'])
def get_student_dashboard_data(student_id):
    agent = get_student_agent(student_id)
    summary = agent.get_activity_summary()
    sw_analysis = agent.get_strengths_weaknesses()

    # Handle cases where syllabus might not have been loaded correctly by the agent
    if "error" in summary and agent.syllabus and not agent.syllabus.get("topics"):
        summary_error_message = summary["error"]
        summary = {"message": f"Activity summary unavailable. Agent reported: {summary_error_message}. Syllabus topics might be missing."}

    if "error" in sw_analysis and agent.syllabus and not agent.syllabus.get("topics"):
         sw_error_message = sw_analysis.get("message", "Analysis error due to syllabus issue.")
         sw_analysis = {"message": f"Strength/Weakness analysis unavailable. Agent reported: {sw_error_message}. Syllabus topics might be missing."}


    dashboard_data = {
        "student_id": student_id,
        "activity_summary": summary,
        "strengths_weaknesses": sw_analysis
    }
    return jsonify(dashboard_data)

@app.route('/students/<student_id>/syllabus', methods=['GET'])
def get_student_syllabus(student_id):
    agent = get_student_agent(student_id)
    if agent.syllabus:
        return jsonify(agent.syllabus)
    else:
        # This case should ideally be handled by get_student_agent creating a placeholder
        return jsonify({"error": "Syllabus not loaded for this student."}), 404

if __name__ == '__main__':
    # Pre-initialize a default student for testing purposes
    print("Initializing default student 'student007' for testing student_service_app...")
    get_student_agent("student007") # Ensure student007 is created with syllabus on startup

    # You can add more pre-initialized students here if needed for testing:
    # get_student_agent("student008")

    print("Student service app starting on port 5001.")
    app.run(debug=True, port=5001)
