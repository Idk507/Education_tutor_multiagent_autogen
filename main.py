import os
import uuid
import logging
import sys
from autogen import GroupChat, GroupChatManager
from config.llm_config import get_azure_openai_config
from agents.tutor_agent import create_tutor_agent
from agents.student_agent import create_student_agent
from agents.progress_tracker import create_progress_tracker_agent
from memory.conversation_memory import LangChainConversationMemory
from memory.progress_memory import ProgressMemory
from utils.helpers import extract_subject_and_topic, solve_problem_interactive, evaluate_and_show_results

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

llm_config = get_azure_openai_config()
os.makedirs("data/conversation_history", exist_ok=True)
os.makedirs("data/progress_data", exist_ok=True)
current_problems = {}

def create_educational_agents(student_id: str, session_id: str):
    progress_memory = ProgressMemory(student_id)
    conv_memory = LangChainConversationMemory(session_id)
    progress_memory.start_session(session_id)

    tutor, explain_concept, create_practice_problems, evaluate_solution = create_tutor_agent(llm_config, conv_memory, progress_memory, session_id)
    student = create_student_agent(llm_config)
    progress_tracker, generate_progress_report = create_progress_tracker_agent(llm_config, progress_memory)

    def custom_speaker_selection(last_speaker, groupchat):
        agents = groupchat.agents
        last_message = groupchat.messages[-1]["content"].strip() if groupchat.messages else ""
        if last_speaker == student and not last_message:
            return tutor
        return agents[(agents.index(last_speaker) + 1) % len(agents)]

    groupchat = GroupChat(
        agents=[student, tutor, progress_tracker],
        messages=[],
        max_round=20,
        speaker_selection_method=custom_speaker_selection
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config, name="Education_Manager")
    return {
        "student": student, "tutor": tutor, "progress_tracker": progress_tracker, "manager": manager,
        "progress_memory": progress_memory, "conv_memory": conv_memory,
        "explain_concept": explain_concept, "create_practice_problems": create_practice_problems,
        "evaluate_solution": evaluate_solution, "generate_progress_report": generate_progress_report
    }

def main():
    print("=== Welcome to the Educational Session ===")
    student_id = "test_student_001"
    session_id = str(uuid.uuid4())
    agents = create_educational_agents(student_id, session_id)
    student, manager, tutor, progress_memory, conv_memory = agents["student"], agents["manager"], agents["tutor"], agents["progress_memory"], agents["conv_memory"]
    explain_concept, create_practice_problems, evaluate_solution, generate_progress_report = (
        agents["explain_concept"], agents["create_practice_problems"], agents["evaluate_solution"], agents["generate_progress_report"]
    )

    print("\nAvailable Actions:\n1. Explain a concept\n2. Request practice problems\n3. Quick problem attempt\n4. Solve a problem\n5. Generate progress report\n6. Exit")
    while True:
        action = input("\nWhat would you like to do? (1-6) > ").strip()
        if action == "6":
            print("\n=== Session Ended ===")
            break
        if action not in ["1", "2", "3", "4", "5"]:
            print("Invalid action.")
            continue

        try:
            if action == "1":
                query = input("Enter your concept query > ").strip()
                if not query:
                    print("Query cannot be empty.")
                    continue
                subject, topic, difficulty, style = extract_subject_and_topic(query, llm_config)
                print(f"\n🤖 Explaining {topic} in {subject}...")
                response = explain_concept(subject, topic, difficulty, style)
                print(f"\n📚 Explanation:\n{response}")
                conv_memory.add_message("student", query, {"subject": subject, "topic": topic})

            elif action == "2":
                query = input("Enter your practice problems request > ").strip()
                if not query:
                    print("Query cannot be empty.")
                    continue
                subject, topic, difficulty, _ = extract_subject_and_topic(query, llm_config)
                count = 1
                for word in query.split():
                    if word.isdigit():
                        count = int(word)
                        break
                print(f"\n🤖 Creating {count} practice problem(s) for {topic}...")
                problems = create_practice_problems(subject, topic, count, difficulty)
                if "error" in problems:
                    print(f"Error: {problems['error']}")
                else:
                    print(f"\n Practice Problem:\nQuestion: {problems.get('question', 'N/A')}")
                    current_problems[session_id] = {"subject": subject, "topic": topic, **problems}
                conv_memory.add_message("student", query, {"subject": subject, "topic": topic})

            elif action == "3":
                query = input("Enter your problem attempt > ").strip()
                if not query:
                    print("Query cannot be empty.")
                    continue
                subject, topic, _, _ = extract_subject_and_topic(query, llm_config)
                print(f"\n Tutor is reviewing your attempt...")
                student.initiate_chat(manager, message=query)
                conv_memory.add_message("student", query, {"subject": subject, "topic": topic})
                progress_memory.update_progress(subject, topic, 0.7, True)
                progress_memory.update_session(session_id, subject, topic, question_asked=True, correct_answer=True)

            elif action == "4":
                solve_choice = input("\n1. Request a new problem\n2. Solve a saved problem\n3. Return to main menu\nEnter choice (1-3): ").strip()
                if solve_choice == "1":
                    query = input("Enter the type of problem > ").strip()
                    if not query:
                        print("Query cannot be empty.")
                        continue
                    subject, topic, difficulty, _ = extract_subject_and_topic(query, llm_config)
                    problem_data = create_practice_problems(subject, topic, 1, difficulty)
                    if "error" in problem_data:
                        print(f"Error: {problem_data['error']}")
                        continue
                    current_problems[session_id] = {"subject": subject, "topic": topic, **problem_data}
                    solve_problem_interactive(current_problems[session_id], session_id, conv_memory, progress_memory, evaluate_solution)
                elif solve_choice == "2":
                    if session_id not in current_problems:
                        print("No saved problems available.")
                    else:
                        solve_problem_interactive(current_problems[session_id], session_id, conv_memory, progress_memory, evaluate_solution)
                elif solve_choice == "3":
                    print("Returning to main menu...")
                else:
                    print("Invalid choice.")

            elif action == "5":
                print("\n Generating Progress Report...")
                report = generate_progress_report()
                if "error" in report:
                    print(f"Error: {report['error']}")
                else:
                    print("\n" + "=" * 60)
                    print(" YOUR LEARNING PROGRESS REPORT")
                    print("=" * 60)
                    print(f" Summary: {report.get('summary', 'N/A')}")
                    print(f"\n Strengths: {' '.join(report.get('strengths', [])) or 'None yet'}")
                    print(f"\n Areas for Improvement: {' '.join(report.get('areas_for_improvement', [])) or 'None identified'}")
                    print(f"\n Recommendations: {' '.join(report.get('recommendations', []))}")
                    print(f"\n Report Generated: {report.get('timestamp', 'N/A')}")
                    print("=" * 60)

        except Exception as e:
            logger.error(f"Error in action {action}: {e}")
            print(f"An error occurred: {e}")

    print("\n🎓 Thank you for using the Educational Tutor System!")

if __name__ == "__main__":
    os.environ["AUTOGEN_USE_DOCKER"] = "False"
    main()