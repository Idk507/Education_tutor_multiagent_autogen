from autogen import AssistantAgent
from config.agent_config import AgentConfig
from tenacity import retry, stop_after_attempt, wait_fixed

def create_tutor_agent(llm_config, conv_memory, progress_memory, session_id):
    tutor = AssistantAgent(
        name="Educational_Tutor",
        system_message=AgentConfig.get_tutor_system_message(),
        llm_config=llm_config,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5
    )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def explain_concept(subject: str, topic: str, difficulty_level: str = "medium", learning_style: str = "visual"):
        context = conv_memory.get_context()
        prompt = f"""Using this conversation history:
{context}

Explain {topic} in {subject} at {difficulty_level} difficulty for a high-school student, using a {learning_style} learning style. Provide:
1. Step-by-step breakdown
2. One example
3. One practice question"""
        response = tutor.generate_reply([{"content": prompt, "role": "user"}])
        conv_memory.add_message("tutor", response, {"subject": subject, "topic": topic})
        progress_memory.update_progress(subject, topic, 0.6, True)
        progress_memory.update_session(session_id, subject, topic, question_asked=True)
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def create_practice_problems(subject: str, topic: str, count: int = 1, difficulty: str = "medium") -> dict:
        context = conv_memory.get_context()
        prompt = f"""Using this conversation history:
{context}

Generate {count} practice problem(s) for {topic} in {subject} at {difficulty} difficulty. For each problem, include:
- Question
- Correct answer
- Solution (step-by-step explanation)

Return ONLY a valid JSON object with this exact structure:
{{
    "question": "the problem statement",
    "correct_answer": "the correct answer",
    "solution": "step-by-step solution explanation"
}}"""
        response = tutor.generate_reply([{"content": prompt, "role": "user"}])
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        problem_data = json.loads(response[json_start:json_end])
        conv_memory.add_message("tutor", json.dumps(problem_data, indent=2), {"subject": subject, "topic": topic})
        progress_memory.update_session(session_id, subject, topic, question_asked=True)
        return problem_data

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def evaluate_solution(session_id_param: str, student_solution: str, current_problems: dict) -> dict:
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
}}"""
        response = tutor.generate_reply([{"content": prompt, "role": "user"}])
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        evaluation = json.loads(response[json_start:json_end])
        conv_memory.add_message("tutor", json.dumps(evaluation, indent=2), 
                              {"subject": problem_data["subject"], "topic": problem_data["topic"]})
        progress_memory.update_progress(
            problem_data["subject"], problem_data["topic"],
            evaluation.get("performance_score", 0.5), evaluation.get("is_correct", False)
        )
        progress_memory.update_session(
            session_id_param, problem_data["subject"], problem_data["topic"],
            question_asked=True, correct_answer=evaluation.get("is_correct", False)
        )
        return evaluation

    tutor.register_function(
        function_map={
            "explain_concept": explain_concept,
            "create_practice_problems": create_practice_problems,
            "evaluate_solution": lambda session_id_param, student_solution: evaluate_solution(session_id_param, student_solution, current_problems)
        }
    )
    return tutor, explain_concept, create_practice_problems, evaluate_solution