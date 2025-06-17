from autogen import AssistantAgent
from config.agent_config import AgentConfig
from tenacity import retry, stop_after_attempt, wait_fixed
import json
from datetime import datetime

def create_progress_tracker_agent(llm_config, progress_memory):
    progress_tracker = AssistantAgent(
        name="Progress_Tracker",
        system_message=AgentConfig.get_progress_tracker_system_message(),
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def generate_progress_report():
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
        response = progress_tracker.generate_reply([{"content": prompt, "role": "user"}])
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        return json.loads(response[json_start:json_end])

    progress_tracker.register_function(
        function_map={"generate_progress_report": generate_progress_report}
    )
    return progress_tracker, generate_progress_report