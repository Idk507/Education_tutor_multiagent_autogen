Educational Tutor System
The Educational Tutor System is an interactive Python application designed to assist high-school students in learning and practicing academic subjects. It leverages the Azure OpenAI API (via gpt-4o) and the AutoGen framework to create an agentic system with a tutor, student, and progress tracker. The system supports concept explanations, practice problem generation, interactive problem-solving, and progress tracking, all tailored for a supportive learning experience.
Table of Contents

Features
Requirements
Installation
Usage
System Architecture
Agents
Workflow
Agent Workflow Diagram


Functions
File Structure
Progress and Conversation Storage
Troubleshooting
Future Enhancements

![image](https://github.com/user-attachments/assets/7b7ab9e3-2477-4160-90cb-a368beabeabd)

Features

Concept Explanation: Provides clear, step-by-step explanations of academic topics with examples and practice questions, tailored to difficulty and learning style (visual, auditory, kinesthetic).
Practice Problems: Generates practice problems with solutions and correct answers, supporting multiple difficulty levels.
Interactive Problem-Solving: Offers options to solve problems immediately, take time, request hints, or skip, with detailed feedback on solutions.
Progress Tracking: Monitors student performance, generating JSON reports with strengths, areas for improvement, and recommendations.
AI-Powered Classification: Uses Azure OpenAI to classify queries into subject, topic, difficulty, and learning style, with a rule-based fallback.
Session Persistence: Saves conversation history and progress to JSON files for continuity across sessions.
Error Handling: Robust retry logic for API calls and JSON parsing to ensure reliability.

Requirements

Python 3.8+
Dependencies:
pyautogen
openai
langchain
tenacity


Azure OpenAI API key (set as environment variable or in code)
No Docker (AutoGen Docker support is disabled)

Installation

Clone or download the repository.
Install dependencies:pip install pyautogen openai langchain tenacity


Set the Azure OpenAI API key:export AZURE_OPENAI_API_KEY="your_api_key"

Alternatively, replace the hardcoded key in the llm_config with your key.
Ensure the data directory is writable for storing conversation and progress files.
Run the script:python educational_tutor.py



Usage

Start the Program:
Run the script to enter the main menu.
A unique session ID is generated for each session.


Main Menu Actions:
1. Explain a Concept: Enter a query (e.g., "Explain quadratic equations, medium difficulty, visual style") to receive a detailed explanation.
2. Request Practice Problems: Request problems (e.g., "Create problems on quadratic equations, medium difficulty") to generate and store a problem.
3. Quick Problem Attempt: Submit a problem and solution (e.g., "For x^2 - 7x + 10 = 0, I got x = 2, x = 5") for immediate evaluation.
4. Solve a Problem: Interactively solve a new or saved problem with options to solve now, take time, request a hint, or skip.
5. Generate Progress Report: View a detailed report of your learning progress.
6. Exit: End the session and view final statistics.


Interactive Problem-Solving:
Choose to solve immediately, take time, request a hint, or skip.
Submit solutions to receive feedback, performance scores, and correct answers if incorrect.


Progress Tracking:
Progress is saved in data/progress_data/<student_id>_progress.json.
Conversation history is saved in data/conversation_history/<session_id>.json.



System Architecture
Agents
The system uses the AutoGen framework to create a multi-agent setup with distinct roles:

Student Agent (Student_Learner):

Role: Acts as the user proxy, forwarding inputs to other agents and reflecting on feedback.
System Message: Engages actively by sharing solutions, reflecting on feedback, and summarizing activities.
Key Functions: Initiates group chats and logs user queries to conversation memory.


Tutor Agent (Educational_Tutor):

Role: Provides explanations, generates practice problems, and evaluates solutions.
System Message: Delivers clear explanations, step-by-step solutions, and constructive feedback, tailored for high-school students.
Key Functions:
explain_concept: Explains topics with examples and practice questions.
create_practice_problems: Generates JSON-structured practice problems.
evaluate_solution: Evaluates student solutions with feedback and scores.




Progress Tracker Agent (Progress_Tracker):

Role: Monitors and reports student progress.
System Message: Generates student-friendly JSON reports with summaries, strengths, areas for improvement, and recommendations.
Key Functions:
generate_progress_report: Creates detailed progress reports based on stored data.




Group Chat Manager (Education_Manager):

Role: Orchestrates communication between agents in a group chat.
Speaker Selection: Uses a custom method to cycle through agents, skipping empty student responses and selecting the next logical agent.



Workflow

Initialization:
A student ID (test_student_001) and unique session ID (UUID) are set.
Agents are created with their system messages and registered functions.
Conversation and progress memory are initialized, loading any existing data.


User Interaction:
The user selects an action from the main menu (1–6).
Queries are processed by extract_subject_and_topic using Azure OpenAI for classification, with a rule-based fallback.


Action Processing:
Explain Concept: The tutor agent generates an explanation, logged to conversation memory.
Practice Problems: The tutor generates a problem, stored in current_problems and logged.
Quick Attempt: The student initiates a group chat, and the tutor evaluates the solution.
Interactive Solving: The user solves a new or saved problem interactively, with feedback from the tutor.
Progress Report: The progress tracker generates a report based on stored data.


Progress Tracking:
ProgressMemory updates skill levels, attempts, and session data after each interaction.
LangChainConversationMemory logs all interactions for context.


Session End:
Final statistics are displayed, summarizing sessions, questions, accuracy, and progress by subject.
Data is saved to JSON files.



Agent Workflow Diagram
Below is a textual representation of the agent workflow. Arrows indicate the flow of messages and actions.
[User Input]
     |
     v
[Student Agent]
     | (Forwards query)
     v
[Group Chat Manager]
     |-------------------|
     |                   |
     v                   v
[Tutor Agent]     [Progress Tracker]
     |                   |
     v                   v
[Explain Concept]  [Generate Report]
[Create Problem]   [Update Progress]
[Evaluate Solution]
     |
     v
[Conversation Memory] <--> [Progress Memory]
     |
     v
[User Output]

Explanation:

The User Input is received via the console and sent to the Student Agent.
The Student Agent forwards the query to the Group Chat Manager, which routes it to the appropriate agent based on the custom speaker selection.
The Tutor Agent handles explanations, problem generation, and evaluations, interacting with the Conversation Memory for context.
The Progress Tracker generates reports and updates progress, storing data in the Progress Memory.
Both memory modules save data to JSON files for persistence.
The final output (explanations, feedback, or reports) is displayed to the user.

Functions

extract_subject_and_topic(query: str) -> tuple:

Purpose: Classifies a user query into subject, topic, difficulty, and learning style.
Process:
Uses Azure OpenAI (gpt-4o) to parse the query into a JSON object.
Falls back to rule-based logic if the API fails, checking keywords for subjects (e.g., "math" -> "Mathematics") and topics (e.g., "quadratic" -> "Quadratic Equations").


Returns: (subject, topic, difficulty, style) tuple.
Example: "Explain quadratic equations, easy, visual" -> ("Mathematics", "Quadratic Equations", "easy", "visual").


explain_concept(subject: str, topic: str, difficulty_level: str, learning_style: str) -> str:

Purpose: Generates a detailed explanation of a topic.
Process:
Uses the tutor agent to create a step-by-step explanation with an example and practice question.
Incorporates conversation history for context.
Logs the response to conversation memory and updates progress.


Retries: 3 attempts with 5-second delays for API failures.
Returns: Explanation string or error message.


create_practice_problems(subject: str, topic: str, count: int, difficulty: str) -> Dict[str, Any]:

Purpose: Generates practice problems in JSON format.
Process:
Prompts the tutor agent to create problems with questions, correct answers, and solutions.
Parses the JSON response, stores the problem in current_problems, and logs it.


Retries: 3 attempts for API/JSON errors.
Returns: Problem data dictionary or error.


evaluate_solution(session_id: str, student_solution: str) -> Dict[str, Any]:

Purpose: Evaluates a student’s solution to a stored problem.
Process:
Compares the solution to the correct answer, generating JSON feedback with correctness, score (0.0–1.0), and tips.
Updates conversation and progress memory.


Retries: 3 attempts for API/JSON errors.
Returns: Evaluation dictionary or error.


generate_progress_report() -> Dict[str, Any]:

Purpose: Creates a progress report based on stored data.
Process:
Analyzes ProgressMemory data to summarize performance.
Returns JSON with summary, strengths (>0.7 skill level), areas for improvement (<0.5), and recommendations.


Retries: 3 attempts for API/JSON errors.
Returns: Report dictionary or error.


solve_problem_interactive(problem_data: Dict[str, Any], session_id: str, conv_memory, progress_memory, evaluate_solution_func) -> Optional[Dict[str, Any]]:

Purpose: Facilitates interactive problem-solving.
Process:
Displays the problem and offers options: solve now, take time, request hint, or skip.
For "solve now," evaluates the solution and shows feedback.
Logs interactions and updates progress.


Returns: Evaluation result or None.


evaluate_and_show_results(problem_data, solution, session_id, conv_memory, progress_memory, evaluate_solution_func) -> Optional[Dict[str, Any]]:

Purpose: Displays evaluation results for a solution.
Process:
Calls evaluate_solution and formats the output with correctness, score, and feedback.
Shows correct answers and solutions if incorrect.
Logs the interaction.


Returns: Evaluation result or None.




Progress and Conversation Storage

Conversation Memory (LangChainConversationMemory):
Stores messages as HumanMessage (student) or AIMessage (tutor) using LangChain.
Saves to data/conversation_history/<session_id>.json with metadata (subjects, topics, timestamps).
Provides context for explanations and evaluations.


Progress Memory (ProgressMemory):
Tracks LearningProgress (subject, topic, skill level, attempts, successes) and LearningSession (session ID, subjects, questions, correct answers).
Saves to data/progress_data/<student_id>_progress.json.
Updates skill levels using a weighted average (70% previous, 30% new performance).



Troubleshooting

API Errors: Ensure the Azure OpenAI API key is valid and the endpoint is accessible. Check logs for details.
JSON Parsing Issues: Verify that API responses contain valid JSON. The system retries 3 times for parsing errors.
No Saved Problems: Request a new problem (Action 2) before solving interactively (Action 4).
File Permission Errors: Ensure the data directory is writable.
Dependencies: Install all required packages with correct versions.

Future Enhancements

Adaptive Difficulty: Adjust problem difficulty based on skill level.
Multi-Problem Support: Allow generating and solving multiple problems per session.
Session Resumption: Enable resuming previous sessions.
Visual Aids: Add ASCII art or image generation for visual learners.
Timed Challenges: Introduce timed problem-solving modes.
PDF Reports: Export progress reports as LaTeX-generated PDFs.
Web Interface: Develop a Flask/FastAPI frontend for browser access.
Additional Agents: Add feedback or planner agents for richer interactions.

Example Interaction
=== Welcome to the Educational Session ===
🔹 [System] Creating new session: 123e4567-e89b-12d3-a456-426614174000

Available Actions:
1. Explain a concept...
2. Request practice problems...
...

> 2
Enter your practice problems request: Create problems on quadratic equations, medium difficulty
🔹 [AI Classifier] Analyzing query for subject and topic
🔹 [AI Classifier] Identified: Subject=Mathematics, Topic=Quadratic Equations, Difficulty=medium, Style=visual
🔹 [Educational_Tutor] Creating 1 practice problem(s) for Quadratic Equations in Mathematics (Difficulty: medium)
🔹 [Educational_Tutor] Generating practice problems...

 Practice Problem:
Question: Solve x^2 - 7x + 10 = 0
(Answer will be revealed after you submit your solution)

> 4
Solve a Problem - Interactive Mode
1. Request a new problem to solve
2. Solve a previously requested problem
3. Return to main menu

Enter choice (1-3): 2

============================================================
 SAVED PROBLEM
============================================================
 Subject: Mathematics
 Topic: Quadratic Equations
 Question: Solve x^2 - 7x + 10 = 0
============================================================

How would you like to solve this problem?
1. Solve now
2. Take time to solve
3. Request a hint
4. Skip this problem

Enter your choice (1-4): 1
Enter your solution: x = 2, x = 5

🔹 [Educational_Tutor] Evaluating your solution...
============================================================
 EVALUATION RESULTS
============================================================
✅ CORRECT! Well done!
 Performance Score: 0.85/1.0
 Feedback: Great job factoring the equation to (x-2)(x-5)=0, leading to x=2 and x=5.
============================================================

> 5
Generating Progress Report...
============================================================
 YOUR LEARNING PROGRESS REPORT
============================================================
 Summary: You solved one quadratic equation correctly.
 Strengths:
   Quadratic Equations
 Areas for Improvement: None
 Recommendations:
   Try more quadratic problems
   Explore linear equations
 Report Generated: 2025-06-13T00:30:00Z
============================================================

