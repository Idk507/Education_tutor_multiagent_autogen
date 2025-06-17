import json
from openai import AzureOpenAI

def extract_subject_and_topic(query: str, azure_config):
    client = AzureOpenAI(
        api_key=azure_config["config_list"][0]["api_key"],
        api_version=azure_config["config_list"][0]["api_version"],
        azure_endpoint=azure_config["config_list"][0]["base_url"]
    )
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
        response = client.chat.completions.create(
            model=azure_config["config_list"][0]["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.2,
            max_tokens=200
        )
        content = response.choices[0].message.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        data = json.loads(json_str)
        return (data.get("subject", "General"), data.get("topic", "General"),
                data.get("difficulty", "medium"), data.get("style", "visual"))
    except Exception:
        query_lower = query.lower()
        subject = "General"
        if "math" in query_lower: subject = "Mathematics"
        elif "physics" in query_lower: subject = "Physics"
        elif "chemistry" in query_lower: subject = "Chemistry"
        elif "biology" in query_lower: subject = "Biology"
        topic = "General" if len(query.split()) < 2 else " ".join(query.split()[-2:]).title()
        difficulty = "medium"
        if "easy" in query_lower: difficulty = "easy"
        elif "hard" in query_lower: difficulty = "hard"
        style = "visual"
        if "auditory" in query_lower: style = "auditory"
        elif "kinesthetic" in query_lower: style = "kinesthetic"
        return subject, topic, difficulty, style

def solve_problem_interactive(problem_data: dict, session_id: str, conv_memory, progress_memory, evaluate_solution):
    print("\n" + "=" * 60)
    print(" PROBLEM SOLVING MODE")
    print("=" * 60)
    print(f" Subject: {problem_data.get('subject', 'N/A')}")
    print(f" Topic: {problem_data.get('topic', 'N/A')}")
    print(f" Question: {problem_data.get('problem', 'N/A')}")
    print("\nHow would you like to solve this problem?")
    print("1. Solve now (enter solution immediately)")
    print("2. Take time to solve (I'll enter solution later)")
    print("3. Request a hint")
    print("4. Skip this problem")
    choice = input("Enter your choice (1-4): ").strip()
    if choice == "1":
        print("\nEnter your solution:")
        solution = input("Your solution > ").strip()
        if not solution:
            print("Solution cannot be empty.")
            return None
        return evaluate_and_show_results(problem_data, solution, session_id, conv_memory, progress_memory, evaluate_solution)
    elif choice == "2":
        print("\n Take your time to solve the problem.")
        return None
    elif choice == "3":
        print("\n Hint:")
        hint = problem_data.get('solution', 'No hint available').split('.')[0] + "..."
        print(hint)
        return None
    elif choice == "4":
        print("\nSkipping this problem.")
        return None
    else:
        print("Invalid choice.")
        return None

def evaluate_and_show_results(problem_data, solution, session_id, conv_memory, progress_memory, evaluate_solution_func):
    print(f"\nEvaluating your solution...")
    evaluation = evaluate_solution_func(session_id, solution)
    if "error" in evaluation:
        print(f"Error: {evaluation['error']}")
        return None
    print("\n" + "=" * 60)
    print(" EVALUATION RESULTS")
    print("=" * 60)
    is_correct = evaluation.get("is_correct", False)
    performance_score = evaluation.get("performance_score", 0.0)
    feedback = evaluation.get("feedback", "No feedback available")
    print(" CORRECT!" if is_correct else "Not quite right!")
    print(f" Performance Score: {performance_score:.2f}/1.0")
    print(f"\n Feedback: {feedback}")
    if not is_correct:
        print(f"\n Correct Answer: {problem_data.get('correct_answer', 'N/A')}")
        print(f" Solution Steps: {problem_data.get('solution', 'N/A')}")
    print("=" * 60)
    conv_memory.add_message("student", f"Problem: {problem_data.get('problem', 'N/A')}\nMy solution: {solution}", 
                          {"subject": problem_data["subject"], "topic": problem_data["topic"]})
    return evaluation