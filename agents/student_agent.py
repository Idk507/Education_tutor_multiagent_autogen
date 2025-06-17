from autogen import UserProxyAgent
from config.agent_config import AgentConfig

def create_student_agent(llm_config):
    return UserProxyAgent(
        name="Student_Learner",
        system_message=AgentConfig.get_student_system_message(),
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
        code_execution_config=False
    )