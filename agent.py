import os
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import uuid
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_fixed


# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Azure OpenAI Configuration
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o",
            "api_key": "",
            "base_url": "",
            "api_type": "azure",
            "api_version": "2024-02-01"
        }
    ],
    "temperature": 0.7,
    "timeout": 120,
    "cache_seed": 42
}



# Create directories
os.makedirs("data/conversation_history", exist_ok=True)
os.makedirs("data/progress_data", exist_ok=True)


# Agent Configuration
class AgentConfig:
    @staticmethod
    def get_tutor_system_message() -> str:
        return """You are an expert Educational Tutor Agent. Explain concepts clearly for high-school students, provide step-by-step breakdowns, examples, and practice questions. Evaluate student solutions with detailed feedback, identifying correctness, errors, and improvement tips. Use visual aids for visual learners when specified. Maintain a supportive tone. When evaluating solutions, provide constructive feedback that helps students learn from their mistakes."""

    @staticmethod
    def get_student_system_message() -> str:
        return """You are a high-school Student Agent. Forward user inputs to the appropriate agent (tutor or progress tracker) and engage actively by:
- Sharing user-provided problem-solving steps, questions, or solutions.
- Reflecting on feedback (e.g., 'I understand my mistake in factoring now!').
- Summarizing recent activities if asked for progress (e.g., 'I worked on quadratic equations')."""

    @staticmethod
    def get_progress_tracker_system_message() -> str:
        return """You are a Progress Tracker Agent. Generate student-friendly JSON progress reports using ProgressMemory data. Include a summary, strengths (skill_level > 0.7), areas for improvement (skill_level < 0.6), and recommendations. Handle minimal data gracefully."""



# Conversation Memory (LangChain)
class LangChainConversationMemory:
    def __init__(self, session_id: str, storage_path: str = "data/conversation_history"):
        self.session_id = session_id
        self.storage_path = storage_path
        self.memory = ConversationBufferMemory(return_messages=True)
        self.metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "subjects": [],
            "topics": []
        }
        os.makedirs(self.storage_path, exist_ok=True)
        self._load()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, str]] = None):
        if role == "student":
            self.memory.chat_memory.add_message(HumanMessage(content=content))
        else:
            self.memory.chat_memory.add_message(AIMessage(content=content))
        if metadata:
            if "subject" in metadata and metadata["subject"] not in self.metadata["subjects"]:
                self.metadata["subjects"].append(metadata["subject"])
            if "topic" in metadata and metadata["topic"] not in self.metadata["topics"]:
                self.metadata["topics"].append(metadata["topic"])
        self._save()

    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {"role": "human" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
            for msg in self.memory.chat_memory.messages
        ]

    def get_context(self) -> str:
        return self.memory.buffer

    def _save(self):
        filepath = os.path.join(self.storage_path, f"{self.session_id}.json")
        try:
            data = {
                "metadata": self.metadata,
                "messages": [
                    {"role": "human" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                    for msg in self.memory.chat_memory.messages
                ]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

    def _load(self):
        filepath = os.path.join(self.storage_path, f"{self.session_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.metadata = data.get("metadata", self.metadata)
                for msg in data.get("messages", []):
                    if msg["role"] == "human":
                        self.memory.chat_memory.add_message(HumanMessage(content=msg["content"]))
                    else:
                        self.memory.chat_memory.add_message(AIMessage(content=msg["content"]))
            except Exception as e:
                logger.error(f"Failed to load conversation: {e}")

# Progress Memory
@dataclass
class LearningProgress:
    subject: str
    topic: str
    skill_level: float
    attempts: int
    successful_attempts: int

@dataclass
class LearningSession:
    session_id: str
    start_time: str
    subjects_covered: List[str]
    questions_asked: int
    questions_answered_correctly: int



class ProgressMemory:
    def __init__(self, student_id: str, storage_path: str = "data/progress_data"):
        self.student_id = student_id
        self.storage_path = storage_path
        self.progress_data: Dict[str, Dict[str, LearningProgress]] = defaultdict(dict)
        self.learning_sessions: List[LearningSession] = []
        os.makedirs(self.storage_path, exist_ok=True)
        self._load()

    def start_session(self, session_id: str) -> LearningSession:
        print(f"🔹 [ProgressTracker] Starting new learning session: {session_id}")
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            subjects_covered=[],
            questions_asked=0,
            questions_answered_correctly=0
        )
        self.learning_sessions.append(session)
        self._save()
        return session

    def update_progress(self, subject: str, topic: str, performance_score: float, was_successful: bool):
        print(f"🔹 [ProgressTracker] Updating progress for {subject}/{topic} - "
              f"Score: {performance_score:.2f}, Successful: {was_successful}")
        if subject not in self.progress_data:
            self.progress_data[subject] = {}
        if topic not in self.progress_data[subject]:
            self.progress_data[subject][topic] = LearningProgress(subject, topic, 0.0, 0, 0)
        progress = self.progress_data[subject][topic]
        progress.attempts += 1
        if was_successful:
            progress.successful_attempts += 1
        progress.skill_level = (progress.skill_level * 0.7) + (performance_score * 0.3)
        logger.info(f"Updated progress: {subject}/{topic}, skill={progress.skill_level:.2f}")
        self._save()

    def update_session(self, session_id: str, subject: str, topic: str, question_asked: bool = False, correct_answer: bool = False):
        print(f"🔹 [ProgressTracker] Updating session {session_id} - "
              f"Subject: {subject}, Question: {question_asked}, Correct: {correct_answer}")
        for session in self.learning_sessions:
            if session.session_id == session_id:
                if subject not in session.subjects_covered:
                    session.subjects_covered.append(subject)
                if question_asked:
                    session.questions_asked += 1
                if correct_answer:
                    session.questions_answered_correctly += 1
                logger.info(f"Updated session {session_id}: subject={subject}, questions_asked={session.questions_asked}")
                self._save()
                break

    def get_progress_report(self) -> Dict[str, Any]:
        print("🔹 [ProgressTracker] Generating progress report")
        return {
            "student_id": self.student_id,
            "subjects": {s: {t: asdict(p) for t, p in topics.items()} for s, topics in self.progress_data.items()},
            "sessions": [asdict(s) for s in self.learning_sessions],
            "timestamp": datetime.now().isoformat()
        }

    def _save(self):
        filepath = os.path.join(self.storage_path, f"{self.student_id}_progress.json")
        try:
            data = {
                "student_id": self.student_id,
                "progress_data": {
                    s: {t: asdict(p) for t, p in topics.items()}
                    for s, topics in self.progress_data.items()
                },
                "learning_sessions": [asdict(s) for s in self.learning_sessions]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def _load(self):
        filepath = os.path.join(self.storage_path, f"{self.student_id}_progress.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for subject, topics in data.get("progress_data", {}).items():
                    self.progress_data[subject] = {
                        topic: LearningProgress(**progress)
                        for topic, progress in topics.items()
                    }
                self.learning_sessions = [
                    LearningSession(**session)
                    for session in data.get("learning_sessions", [])
                ]
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")


# Current Problem Storage
current_problems: Dict[str, Dict[str, Any]] = {}


def extract_subject_and_topic(query: str) -> tuple:
    """Extract subject and topic from user query using Azure OpenAI"""
    print("🔹 [AI Classifier] Analyzing query for subject and topic")
    from openai import AzureOpenAI
    
    # Create Azure OpenAI client
    client = AzureOpenAI(
        api_key= "",
        api_version="2024-02-01",
        azure_endpoint="https://idkrag.openai.azure.com/"
    )
    
    # System message to guide the model
    system_prompt = """You are an expert educational classifier. Analyze the student's query and extract:
1. Subject (Mathematics, Physics, Chemistry, Biology, or General)
2. Main topic/concept
3. Difficulty level (easy, medium, hard, or unknown)
4. Learning style (visual, auditory, kinesthetic, or general)

Return ONLY a JSON object with this structure:
{
    "subject": "subject name",
    "topic": "specific topic",
    "difficulty": "difficulty level",
    "style": "learning style"
}"""

    try:
        # Get response from Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        
        # Parse JSON
        data = json.loads(json_str)
        
        # Extract values with defaults
        subject = data.get("subject", "General")
        topic = data.get("topic", "General")
        difficulty = data.get("difficulty", "medium")
        style = data.get("style", "visual")
        
        print(f"🔹 [AI Classifier] Identified: Subject={subject}, Topic={topic}, "
              f"Difficulty={difficulty}, Style={style}")
        return subject, topic, difficulty, style
        
    except Exception as e:
        logger.error(f"AI classification failed: {e}")
        # Fallback to rule-based method
        query_lower = query.lower()
        
        # Subject detection
        if any(word in query_lower for word in ['math', 'algebra', 'geometry', 'calculus', 'equation']):
            subject = "Mathematics"
        elif any(word in query_lower for word in ['physics', 'force', 'motion', 'energy']):
            subject = "Physics"
        elif any(word in query_lower for word in ['chemistry', 'chemical', 'reaction', 'element']):
            subject = "Chemistry"
        elif any(word in query_lower for word in ['biology', 'cell', 'organism', 'gene']):
            subject = "Biology"
        else:
            subject = "General"
        
        # Topic detection
        topic = "General"
        if "quadratic" in query_lower:
            topic = "Quadratic Equations"
        elif "linear" in query_lower:
            topic = "Linear Equations"
        elif "factor" in query_lower:
            topic = "Factoring"
        elif "derivative" in query_lower:
            topic = "Derivatives"
        elif "integral" in query_lower:
            topic = "Integration"
        elif len(query.split()) >= 2:
            topic = " ".join(query.split()[-2:]).title()
        
        # Difficulty detection
        difficulty = "medium"
        if "easy" in query_lower or "beginner" in query_lower:
            difficulty = "easy"
        elif "hard" in query_lower or "advanced" in query_lower:
            difficulty = "hard"
            
        # Learning style detection
        style = "visual"
        if "auditory" in query_lower or "listen" in query_lower:
            style = "auditory"
        elif "kinesthetic" in query_lower or "hands-on" in query_lower:
            style = "kinesthetic"
        
        print(f"🔹 [AI Classifier] Fallback identified: Subject={subject}, Topic={topic}, "
              f"Difficulty={difficulty}, Style={style}")
        return subject, topic, difficulty, style

def solve_problem_interactive(problem_data: Dict[str, Any], session_id: str, conv_memory, progress_memory, evaluate_solution_func):
    """Interactive problem solving workflow"""
    print("\n" + "=" * 60)
    print(" PROBLEM SOLVING MODE")
    print("=" * 60)
    
    # Ensure we have all necessary problem data
    if not problem_data or "problem" not in problem_data:
        print("⚠️ Error: Problem data is incomplete or missing")
        print("Please try requesting a new problem")
        return None
        
    print(f" Subject: {problem_data.get('subject', 'N/A')}")
    print(f" Topic: {problem_data.get('topic', 'N/A')}")
    print(f" Question: {problem_data.get('problem', 'N/A')}")
    
    # Show solving options
    print("\nHow would you like to solve this problem?")
    print("1. Solve now (enter solution immediately)")
    print("2. Take time to solve (I'll enter solution later)")
    print("3. Request a hint")
    print("4. Skip this problem")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\nEnter your solution:")
        print("You can enter:")
        print("- Just the answer (e.g., 'x = 2, x = 5')")
        print("- Your working steps (e.g., 'First I factored: (x-2)(x-5) = 0, so x = 2 or x = 5')")
        print("- Both your steps and final answer")
        
        solution = input("\nYour solution > ").strip()
        
        if not solution:
            print("Solution cannot be empty. Try again next time.")
            return None
        
        return evaluate_and_show_results(
            problem_data, 
            solution, 
            session_id, 
            conv_memory, 
            progress_memory,
            evaluate_solution_func
        )
    
    elif choice == "2":
        print("\n⏰ Take your time to solve the problem.")
        print("When you're ready to submit your solution, select option 4 from the main menu.")
        print("The problem has been saved for later solving.")
        return None
    
    elif choice == "3":
        print("\n💡 Hint:")
        # Show just the first part of the solution as a hint
        hint = problem_data.get('solution', 'No hint available').split('.')[0] + "..."
        print(hint)
        print("\nTry to solve with this hint. When ready, select option 1 to enter your solution.")
        return None
    
    elif choice == "4":
        print("\nSkipping this problem.")
        return None
    
    else:
        print("Invalid choice. Please try solving the problem.")
        return None


def evaluate_and_show_results(problem_data, solution, session_id, conv_memory, progress_memory, evaluate_solution_func):
    """Evaluate solution and show results"""
    print(f"\n🔹 [Educational_Tutor] Evaluating your solution...")
    
    # Wait a moment for dramatic effect
    time.sleep(1)
    
    # Evaluate the solution
    evaluation = evaluate_solution_func(session_id, solution)
    
    if "error" in evaluation:
        print(f"Error during evaluation: {evaluation['error']}")
        return None
    
    # Display evaluation results
    print("\n" + "=" * 60)
    print(" EVALUATION RESULTS")
    print("=" * 60)
    
    is_correct = evaluation.get("is_correct", False)
    performance_score = evaluation.get("performance_score", 0.0)
    feedback = evaluation.get("feedback", "No feedback available")
    
    if is_correct:
        print("✅ CORRECT! Well done!")
    else:
        print("❌ Not quite right, but good effort!")
    
    print(f" Performance Score: {performance_score:.2f}/1.0")
    print(f"\n Feedback: {feedback}")
    
    # Show correct answer if they got it wrong
    if not is_correct:
        correct_answer = problem_data.get('correct_answer', 'N/A')
        solution_steps = problem_data.get('solution', 'N/A')
        print(f"\n Correct Answer: {correct_answer}")
        print(f" Solution Steps: {solution_steps}")
    
    print("=" * 60)
    
    # Log the interaction
    conv_memory.add_message("student", 
                          f"Problem: {problem_data.get('problem', 'N/A')}\nMy solution: {solution}", 
                          {"subject": problem_data["subject"], "topic": problem_data["topic"]})
    
    # Return the evaluation for further use if needed
    return evaluation


# Create Agents
def create_educational_agents(student_id: str, session_id: str):
    print(f"🔹 [System] Creating agents for session: {session_id}")
    progress_memory = ProgressMemory(student_id)
    conv_memory = LangChainConversationMemory(session_id)
    progress_memory.start_session(session_id)

    print("🔹 [System] Initializing Educational Tutor")
    tutor = AssistantAgent(
        name="Educational_Tutor",
        system_message=AgentConfig.get_tutor_system_message(),
        llm_config=llm_config,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5
    )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def explain_concept(subject: str, topic: str, difficulty_level: str = "medium", learning_style: str = "visual"):
        print(f"🔹 [Educational_Tutor] Explaining {topic} in {subject} (Difficulty: {difficulty_level}, Style: {learning_style})")
        context = conv_memory.get_context()
        prompt = f"""Using this conversation history:
{context}

Explain {topic} in {subject} at {difficulty_level} difficulty for a high-school student, using a {learning_style} learning style. Provide:
1. Step-by-step breakdown
2. One example
3. One practice question"""
        
        try:
            print(f"🔹 [Educational_Tutor] Generating explanation...")
            response = tutor.generate_reply([{"content": prompt, "role": "user"}])
            conv_memory.add_message("tutor", response, {"subject": subject, "topic": topic})
            progress_memory.update_progress(subject, topic, 0.6, True)
            progress_memory.update_session(session_id, subject, topic, question_asked=True)
            return response
        except Exception as e:
            logger.error(f"Error in explain_concept: {e}")
            return f"Sorry, I encountered an error while explaining {topic}. Please try again."

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def create_practice_problems(subject: str, topic: str, count: int = 1, difficulty: str = "medium") -> Dict[str, Any]:
        print(f"🔹 [Educational_Tutor] Creating {count} practice problem(s) for {topic} in {subject} (Difficulty: {difficulty})")
        context = conv_memory.get_context()
        prompt = f"""Using this conversation history:
{context}

Generate {count} practice problem(s) for {topic} in {subject} at {difficulty} difficulty. For each problem, include:
- Question (e.g., 'Solve x^2 - 7x + 10 = 0')
- Correct answer (e.g., 'x = 2, x = 5')
- Solution (step-by-step explanation)

Return ONLY a valid JSON object with this exact structure:
{{
    "question": "the problem statement",
    "correct_answer": "the correct answer",
    "solution": "step-by-step solution explanation"
}}"""
        
        try:
            print(f"🔹 [Educational_Tutor] Generating practice problems...")
            response = tutor.generate_reply([{"content": prompt, "role": "user"}])
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    problem_data = json.loads(response[json_start:json_end])
                    
                    # Ensure it's a single problem format
                    if isinstance(problem_data, list) and len(problem_data) > 0:
                        problem_data = problem_data[0]
                    
                    # Create full problem data with subject and topic
                    full_problem_data = {
                        "subject": subject,
                        "topic": topic,
                        "problem": problem_data.get("question", ""),
                        "correct_answer": problem_data.get("correct_answer", ""),
                        "solution": problem_data.get("solution", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Store the problem for evaluation
                    current_problems[session_id] = full_problem_data
                    
                    # Add to conversation memory
                    conv_memory.add_message("tutor", json.dumps(problem_data, indent=2), {"subject": subject, "topic": topic})
                    progress_memory.update_session(session_id, subject, topic, question_asked=True)
                    
                    return full_problem_data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return {"error": f"Invalid JSON response: {response}"}
            else:
                logger.error(f"No JSON found in response: {response}")
                return {"error": f"No valid JSON in response: {response}"}
                
        except Exception as e:
            logger.error(f"Error in create_practice_problems: {e}")
            return {"error": f"Failed to create practice problems: {str(e)}"}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def evaluate_solution(session_id_param: str, student_solution: str) -> Dict[str, Any]:
        print(f"🔹 [Educational_Tutor] Evaluating solution for session: {session_id_param}")
        if session_id_param not in current_problems:
            return {"error": "No problem assigned. Request a practice problem first."}
        
        problem_data = current_problems[session_id_param]
        context = conv_memory.get_context()
        
        prompt = f"""Using this conversation history:
{context}

Evaluate the student's solution to the following problem:

Question: {problem_data['problem']}
Correct Answer: {problem_data['correct_answer']}
Student's Solution: {student_solution}

Provide feedback in JSON format with this exact structure:
{{
    "is_correct": true/false,
    "feedback": "detailed explanation of correctness, errors, and improvement tips",
    "performance_score": 0.85
}}

The performance_score should be a float between 0.0 and 1.0."""
        
        try:
            print(f"🔹 [Educational_Tutor] Analyzing solution...")
            response = tutor.generate_reply([{"content": prompt, "role": "user"}])
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                try:
                    evaluation = json.loads(response[json_start:json_end])
                    
                    # Validate required fields
                    if "is_correct" not in evaluation:
                        evaluation["is_correct"] = False
                    if "performance_score" not in evaluation:
                        evaluation["performance_score"] = 0.5
                    if "feedback" not in evaluation:
                        evaluation["feedback"] = "Unable to evaluate properly."
                    
                    # Log the evaluation
                    conv_memory.add_message("tutor", json.dumps(evaluation, indent=2), 
                                          {"subject": problem_data["subject"], "topic": problem_data["topic"]})
                    
                    # Update progress
                    progress_memory.update_progress(
                        problem_data["subject"],
                        problem_data["topic"],
                        evaluation.get("performance_score", 0.5),
                        evaluation.get("is_correct", False)
                    )
                    
                    progress_memory.update_session(
                        session_id_param,
                        problem_data["subject"],
                        problem_data["topic"],
                        question_asked=True,
                        correct_answer=evaluation.get("is_correct", False)
                    )
                    
                    return evaluation
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in evaluation: {e}")
                    return {"error": f"Invalid evaluation response: {response}"}
            else:
                logger.error(f"No JSON found in evaluation response: {response}")
                return {"error": f"No valid JSON in evaluation response: {response}"}
                
        except Exception as e:
            logger.error(f"Error in evaluate_solution: {e}")
            return {"error": f"Failed to evaluate solution: {str(e)}"}

    # Register functions with the tutor
    tutor.register_function(
        function_map={
            "explain_concept": explain_concept,
            "create_practice_problems": create_practice_problems,
            "evaluate_solution": evaluate_solution
        }
    )

    print("🔹 [System] Initializing Student Agent")
    student = UserProxyAgent(
        name="Student_Learner",
        system_message=AgentConfig.get_student_system_message(),
        max_consecutive_auto_reply=3,
        code_execution_config=False
    )

    print("🔹 [System] Initializing Progress Tracker")
    progress_tracker = AssistantAgent(
        name="Progress_Tracker",
        system_message=AgentConfig.get_progress_tracker_system_message(),
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def generate_progress_report():
        print(f"🔹 [Progress_Tracker] Generating progress report")
        report = progress_memory.get_progress_report()
        
        if not report["subjects"] and not report["sessions"]:
            return {
                "summary": "No progress data available yet. Try solving problems!",
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": ["Solve practice problems", "Ask clarifying questions"],
                "timestamp": datetime.now().isoformat()
            }
        
        prompt = f"""Generate a student-friendly JSON progress report based on:
{json.dumps(report, indent=2)}

Return a JSON object with this exact structure:
{{
    "summary": "Brief summary of overall progress",
    "strengths": ["list of subjects/topics where skill_level > 0.7"],
    "areas_for_improvement": ["list of subjects/topics where skill_level < 0.5"],
    "recommendations": ["list of specific recommendations"],
    "timestamp": "{datetime.now().isoformat()}"
}}"""
        
        try:
            print(f"🔹 [Progress_Tracker] Analyzing progress data...")
            response = progress_tracker.generate_reply([{"content": prompt, "role": "user"}])
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {"error": "Invalid report format"}
                
        except Exception as e:
            logger.error(f"Error generating progress report: {e}")
            return {"error": f"Failed to generate report: {str(e)}"}

    progress_tracker.register_function(
        function_map={"generate_progress_report": generate_progress_report}
    )

    def custom_speaker_selection(last_speaker, groupchat):
        agents = groupchat.agents
        last_message = groupchat.messages[-1]["content"].strip() if groupchat.messages else ""
        if last_speaker == student and not last_message:
            return tutor  # Skip empty student responses
        next_agent = agents[(agents.index(last_speaker) + 1) % len(agents)]
        print(f"🔹 [GroupChatManager] Next speaker: {next_agent.name}")
        return next_agent

    groupchat = GroupChat(
        agents=[student, tutor, progress_tracker],
        messages=[],
        max_round=20,
        speaker_selection_method=custom_speaker_selection
    )

    print("🔹 [System] Initializing Group Chat Manager")
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        name="Education_Manager"
    )

    return {
        "student": student,
        "tutor": tutor,
        "progress_tracker": progress_tracker,
        "manager": manager,
        "progress_memory": progress_memory,
        "conv_memory": conv_memory,
        "explain_concept": explain_concept,
        "create_practice_problems": create_practice_problems,
        "evaluate_solution": evaluate_solution,
        "generate_progress_report": generate_progress_report
    }


# Main Execution
def main():
    print("=== Welcome to the Educational Session ===")
    student_id = "test_student_001"
    session_id = str(uuid.uuid4())
    print(f"🔹 [System] Creating new session: {session_id}")

    try:
        agents = create_educational_agents(student_id, session_id)
        student = agents["student"]
        manager = agents["manager"]
        tutor = agents["tutor"]
        progress_tracker = agents["progress_tracker"]
        progress_memory = agents["progress_memory"]
        conv_memory = agents["conv_memory"]
        
        # Direct function access
        explain_concept = agents["explain_concept"]
        create_practice_problems = agents["create_practice_problems"]
        evaluate_solution = agents["evaluate_solution"]
        generate_progress_report = agents["generate_progress_report"]

        print("\nAvailable Actions:")
        print("1. Explain a concept (e.g., 'Explain quadratic equations, medium difficulty, visual style')")
        print("2. Request practice problems (e.g., 'Create problems on quadratic equations, medium difficulty')")
        print("3. Quick problem attempt (e.g., 'For x^2 - 7x + 10 = 0, I got x = 2, x = 5')")
        print("4. Solve a problem (work on a problem at your own pace)")
        print("5. Generate progress report")
        print("6. Exit")

        while True:
            print("\nWhat would you like to do? (Enter number 1-6)")
            action = input("> ").strip()

            if action == "6":
                print("\n=== Session Ended ===")
                break

            if action not in ["1", "2", "3", "4", "5", "6"]:
                print("Invalid action. Please choose 1-6.")
                continue

            try:
                if action == "1":
                    print("Enter your concept query:")
                    print("Examples:")
                    print("- 'Explain quadratic equations, medium difficulty, visual style'")
                    print("- 'Explain derivatives in calculus, easy difficulty'")
                    query = input("> ").strip()
                    
                    if not query:
                        print("Query cannot be empty.")
                        continue
                    
                    subject, topic, difficulty, style = extract_subject_and_topic(query)
                    
                    print(f"\n🤖 Tutor is explaining {topic} in {subject}...")
                    response = explain_concept(subject, topic, difficulty, style)
                    print(f"\n📚 Explanation:\n{response}")
                    
                    conv_memory.add_message("student", query, {"subject": subject, "topic": topic})

                elif action == "2":
                    print("Enter your practice problems request:")
                    print("Examples:")
                    print("- 'Create problems on quadratic equations, medium difficulty'")
                    print("- 'Generate 2 linear equation problems, easy difficulty'")
                    query = input("> ").strip()
                    
                    if not query:
                        print("Query cannot be empty.")
                        continue
                    
                    subject, topic, difficulty, style = extract_subject_and_topic(query)
                    
                    # Parse count from query
                    count = 1
                    words = query.split()
                    for i, word in enumerate(words):
                        if word.isdigit():
                            count = int(word)
                            break
                    
                    print(f"\n🤖 Tutor is creating {count} practice problem(s) for {topic}...")
                    problems = create_practice_problems(subject, topic, count, difficulty)
                    
                    if "error" in problems:
                        print(f"Error: {problems['error']}")
                    else:
                        print(f"\n Practice Problem:")
                        print(f"Question: {problems.get('problem', 'N/A')}")
                        print(f"(Answer will be revealed after you submit your solution)")
                    
                    conv_memory.add_message("student", query, {"subject": subject, "topic": topic})

                elif action == "3":
                    print("Enter your problem attempt:")
                    print("Examples:")
                    print("- 'For x^2 - 7x + 10 = 0, I got x = 2, x = 5'")
                    print("- 'My solution to the quadratic equation is x = 2 and x = 5'")
                    query = input("> ").strip()
                    
                    if not query:
                        print("Query cannot be empty.")
                        continue
                    
                    subject, topic, difficulty, style = extract_subject_and_topic(query)
                    
                    print(f"\n Starting group chat with tutor and progress tracker...")
                    student.initiate_chat(manager, message=query)
                    
                    conv_memory.add_message("student", query, {"subject": subject, "topic": topic})
                    progress_memory.update_progress(subject, topic, 0.7, True)
                    progress_memory.update_session(session_id, subject, topic, question_asked=True, correct_answer=True)

                elif action == "4":
                    print("\n Solve a Problem - Interactive Mode")
                    print("Choose an option:")
                    print("1. Request a new problem to solve")
                    print("2. Solve a previously requested problem")
                    print("3. Return to main menu")
                    
                    solve_choice = input("Enter choice (1-3): ").strip()
                    
                    if solve_choice == "1":
                        print("\nEnter the type of problem you want to solve:")
                        print("Examples:")
                        print("- 'Quadratic equations, medium difficulty'")
                        print("- 'Linear equations, easy difficulty'")
                        print("- 'Derivatives, hard difficulty'")
                        
                        query = input("> ").strip()
                        
                        if not query:
                            print("Query cannot be empty.")
                            continue
                        
                        subject, topic, difficulty, style = extract_subject_and_topic(query)
                        
                        print(f"\n Generating a {difficulty} problem for {topic}...")
                        
                        # Generate a single problem
                        problem_data = create_practice_problems(subject, topic, 1, difficulty)
                        
                        if "error" in problem_data:
                            print(f"Error generating problem: {problem_data['error']}")
                            continue
                        
                        # Display the problem immediately
                        print("\n" + "=" * 60)
                        print(" NEW PROBLEM GENERATED")
                        print("=" * 60)
                        print(f" Subject: {problem_data.get('subject', 'N/A')}")
                        print(f" Topic: {problem_data.get('topic', 'N/A')}")
                        print(f" Question: {problem_data.get('problem', 'N/A')}")
                        print("=" * 60)
                        
                        # Start interactive solving
                        solve_problem_interactive(
                            problem_data, 
                            session_id, 
                            conv_memory, 
                            progress_memory,
                            evaluate_solution
                        )
                    
                    elif solve_choice == "2":
                        if session_id not in current_problems:
                            print("No saved problems available. Request a new problem first.")
                        else:
                            problem_data = current_problems[session_id]
                            print("\n Continuing with your saved problem:")
                            # Display the problem
                            print("\n" + "=" * 60)
                            print(" SAVED PROBLEM")
                            print("=" * 60)
                            print(f" Subject: {problem_data.get('subject', 'N/A')}")
                            print(f" Topic: {problem_data.get('topic', 'N/A')}")
                            print(f" Question: {problem_data.get('problem', 'N/A')}")
                            print("=" * 60)
                            
                            solve_problem_interactive(
                                problem_data, 
                                session_id, 
                                conv_memory, 
                                progress_memory,
                                evaluate_solution
                            )
                    
                    elif solve_choice == "3":
                        print("Returning to main menu...")
                    
                    else:
                        print("Invalid choice. Please choose 1, 2, or 3.")

                elif action == "5":
                    print("\n Generating Progress Report...")
                    
                    report = generate_progress_report()
                    
                    if "error" in report:
                        print(f" Error generating report: {report['error']}")
                        continue
                    
                    print("\n" + "=" * 60)
                    print(" YOUR LEARNING PROGRESS REPORT")
                    print("=" * 60)
                    
                    print(f" Summary: {report.get('summary', 'No summary available')}")
                    
                    strengths = report.get('strengths', [])
                    if strengths:
                        print(f"\n Strengths:")
                        for strength in strengths:
                            print(f"   {strength}")
                    else:
                        print(f"\n Strengths: Keep practicing to build your strengths!")
                    
                    areas = report.get('areas_for_improvement', [])
                    if areas:
                        print(f"\n Areas for Improvement:")
                        for area in areas:
                            print(f"   {area}")
                    else:
                        print(f"\n Areas for Improvement: Great job! No major areas identified yet.")
                    
                    recommendations = report.get('recommendations', [])
                    if recommendations:
                        print(f"\n Recommendations:")
                        for rec in recommendations:
                            print(f"   {rec}")
                    
                    print(f"\n Report Generated: {report.get('timestamp', 'N/A')}")
                    print("=" * 60)

            except KeyboardInterrupt:
                print("\n\n Operation interrupted by user.")
                continue
            except Exception as e:
                logger.error(f"Error in action {action}: {e}")
                print(f" An error occurred: {e}")
                print("Please try again or choose a different action.")

        # Final session statistics
        print("\n" + "=" * 60)
        print(" SESSION STATISTICS")
        print("=" * 60)
        
        try:
            final_report = progress_memory.get_progress_report()
            total_sessions = len(final_report.get('sessions', []))
            total_questions = sum(s.get('questions_asked', 0) for s in final_report.get('sessions', []))
            correct_answers = sum(s.get('questions_answered_correctly', 0) for s in final_report.get('sessions', []))
            subjects_covered = list(final_report.get('subjects', {}).keys())
            
            print(f" Total Sessions: {total_sessions}")
            print(f" Total Questions: {total_questions}")
            print(f" Correct Answers: {correct_answers}")
            if total_questions > 0:
                accuracy = (correct_answers / total_questions) * 100
                print(f" Accuracy Rate: {accuracy:.1f}%")
            print(f"Subjects Covered: {', '.join(subjects_covered) if subjects_covered else 'None'}")
            
            # Show detailed progress by subject
            if final_report.get('subjects'):
                print(f"\n Detailed Progress by Subject:")
                for subject, topics in final_report['subjects'].items():
                    print(f"   {subject}:")
                    for topic, progress in topics.items():
                        skill_level = progress.get('skill_level', 0.0)
                        attempts = progress.get('attempts', 0)
                        success_rate = (progress.get('successful_attempts', 0) / attempts * 100) if attempts > 0 else 0
                        print(f"    • {topic}: Skill Level {skill_level:.2f}, Success Rate {success_rate:.1f}% ({attempts} attempts)")
            
        except Exception as e:
            logger.error(f"Error generating final statistics: {e}")
            print(f" Could not generate final statistics: {e}")
        
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n Session interrupted by user.")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f" Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🎓 Thank you for using the Educational Tutor System!")
        print(" Keep learning and practicing!")

    print("\n=== Educational Session Completed ===")



if __name__ == "__main__":
    # Ensure Docker is disabled for AutoGen
    os.environ["AUTOGEN_USE_DOCKER"] = "False"
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Goodbye! Session terminated by user.")
    except Exception as e:
        print(f"\n Fatal error: {e}")
        logging.error(f"Fatal error in main execution: {e}")
        import traceback
        traceback.print_exc()