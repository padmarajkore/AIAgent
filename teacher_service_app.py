from flask import Flask, jsonify
from agents.teacher_console_agent import TeacherConsoleAgent
from agents.teacher_data_aggregator_agent import TeacherDataAggregatorAgent
from agents.student_interaction_agent import StudentInteractionAgent
import os
import json

app = Flask(__name__)

# --- Global instances for the teacher service ---
# In a real app, managing these instances and their lifecycle would be more sophisticated.
teacher_aggregator = None
teacher_console = None

# --- Student data for the teacher service's aggregator ---
# This will be a separate set of student agent instances from student_service_app.py for now.
# This is a simplification for MVP. A real system would have a shared student data source.
teacher_managed_student_agents = {}

def initialize_teacher_service():
    global teacher_aggregator, teacher_console

    teacher_aggregator = TeacherDataAggregatorAgent()

    # --- Initialize and register some student agents for the teacher to see ---
    # These are distinct from any instances managed by student_service_app.py in this MVP model
    student_ids_for_teacher = ["student001", "student002", "student007_mirrored"]

    syllabus_filename = "sample_syllabus.json" # Ensure this exists
    syllabus_path = os.path.join(os.path.dirname(__file__), 'agents', syllabus_filename)

    if not os.path.exists(syllabus_path):
        print(f"ERROR: Syllabus file {syllabus_path} not found for teacher_service_app! Student agents may lack proper syllabus.")
        # Create a minimal dummy to prevent crashes if it doesn't exist
        # This is mainly for robustness during isolated testing.
        os.makedirs(os.path.join(os.path.dirname(__file__), 'agents'), exist_ok=True)
        with open(syllabus_path, 'w') as f:
            json.dump({"course_name": "Placeholder Course - File Missing", "topics": []}, f)
        print(f"Created placeholder syllabus at {syllabus_path} for teacher_service_app")


    for s_id in student_ids_for_teacher:
        if s_id not in teacher_managed_student_agents:
            student_agent_instance = StudentInteractionAgent(student_id=s_id, syllabus_path=syllabus_path)
            if not student_agent_instance.syllabus: # If syllabus loading failed
                print(f"Warning: Syllabus loading failed for {s_id} in teacher_service. Using placeholder content.")
                student_agent_instance.syllabus = {"course_name": f"Placeholder for {s_id}", "topics": [{"id":"ERR01", "title":"Syllabus Load Error"}]}

            teacher_managed_student_agents[s_id] = student_agent_instance
            teacher_aggregator.register_student_agent(student_agent_instance)

            # Log some mock activity for these students so the teacher sees something
            if s_id == "student001":
                student_agent_instance.log_activity("learning", "Initial reading on Scientific Method", "sci_topic_01")
                student_agent_instance.log_activity("exercise", "Practice quiz on Cells", "sci_topic_02")
            if s_id == "student002":
                student_agent_instance.log_activity("learning", "Studied Earth and Space", "sci_topic_03")

    teacher_console = TeacherConsoleAgent(teacher_aggregator)
    print("Teacher service initialized with aggregator and console agent.")


@app.route('/teachers/<teacher_id>/students', methods=['GET'])
def get_all_students_for_teacher(teacher_id):
    # The teacher_id path parameter isn't strictly used in this MVP console agent,
    # as the console agent has a single aggregator. In a multi-tenant system,
    # teacher_id would be crucial for scoping.
    if not teacher_console:
        return jsonify({"error": "Teacher console not initialized"}), 500

    student_ids = teacher_console.aggregator.get_all_student_ids() # Direct call for MVP
    return jsonify({"teacher_id": teacher_id, "student_ids": student_ids})

@app.route('/teachers/<teacher_id>/students/<student_id>/summary', methods=['GET'])
def get_student_summary_for_teacher(teacher_id, student_id):
    if not teacher_console:
        return jsonify({"error": "Teacher console not initialized"}), 500

    summary = teacher_console.aggregator.get_student_activity_summary(student_id) # Direct call for MVP
    if "error" in summary and student_id not in teacher_managed_student_agents:
         return jsonify({"error": f"Student {student_id} not managed or found by this teacher service."}), 404
    return jsonify({"teacher_id": teacher_id, "student_id": student_id, "summary": summary})

@app.route('/teachers/<teacher_id>/students/<student_id>/strengths_weaknesses', methods=['GET'])
def get_student_strengths_weaknesses_for_teacher(teacher_id, student_id):
    if not teacher_console:
        return jsonify({"error": "Teacher console not initialized"}), 500

    sw_data = teacher_console.aggregator.get_student_strengths_weaknesses(student_id) # Direct call for MVP
    if "error" in sw_data and student_id not in teacher_managed_student_agents:
         return jsonify({"error": f"Student {student_id} not managed or found by this teacher service."}), 404
    return jsonify({"teacher_id": teacher_id, "student_id": student_id, "strengths_weaknesses": sw_data})

if __name__ == '__main__':
    initialize_teacher_service()
    print("Teacher service app starting on port 5000.")
    app.run(debug=True, port=5000)
