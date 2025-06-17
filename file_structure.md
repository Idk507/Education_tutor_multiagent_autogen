educational_tutor_agent/
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── llm_config.py
│   └── agent_config.py
├── agents/
│   ├── __init__.py
│   ├── tutor_agent.py
│   ├── student_agent.py
│   └── progress_tracker.py
├── memory/
│   ├── __init__.py
│   ├── conversation_memory.py
│   └── progress_memory.py
├── llm_providers/
│   ├── __init__.py
│   ├── openai_provider.py
│   ├── azure_openai_provider.py
│   ├── huggingface_provider.py
│   └── gemini_provider.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── validators.py
├── data/
│   ├── conversation_history/
│   ├── progress_data/
│   └── student_conversations/
├── tests/
│   ├── __init__.py
│   └── test_agents.py
└── main.py
