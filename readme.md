# Educational Tutor Agent

![AI Education](https://img.freepik.com/free-vector/online-tutorials-concept_52683-37481.jpg)

The Educational Tutor Agent is an AI-powered tutoring system that provides personalized learning experiences for students. It uses a multi-agent architecture to simulate student-tutor interactions, track progress, and adapt teaching strategies to individual learning needs.

## Key Features

- **Personalized Learning**: Adapts explanations to student's grade level and learning style
- **Multi-Agent System**: Simulates interactions between student, tutor, and progress tracker
- **Progress Tracking**: Monitors student performance and identifies areas for improvement
- **Multi-LLM Support**: Works with Azure OpenAI, OpenAI, Hugging Face, and Gemini
- **Conversation Memory**: Maintains context across sessions
- **Detailed Reporting**: Generates comprehensive progress reports

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/educational-tutor-agent.git
cd educational-tutor-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# For Azure OpenAI
export AZURE_OPENAI_API_KEY="your_azure_api_key"
export AZURE_OPENAI_ENDPOINT="your_azure_endpoint"

# For OpenAI
export OPENAI_API_KEY="your_openai_api_key"

# For Hugging Face
export HUGGINGFACEHUB_API_TOKEN="your_hf_api_token"

# For Gemini
export GEMINI_API_KEY="your_gemini_api_key"
```

## Configuration

Modify the configuration in `config/llm_config.py`:

```python
# Example for Azure OpenAI configuration
"azure_openai": {
    "config_list": [
        {
            "model": "gpt-4o",
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_type": "azure",
            "api_version": "2025-01-01-preview"
        }
    ],
    "temperature": 0.7,
    "timeout": 120,
    "cache_seed": 42
}
```

## Usage

Run the main application:
```bash
python main.py
```

### Example Session Flow:
1. Tutor explains quadratic equations
2. Student asks for real-world examples
3. Tutor provides examples and practice problems
4. Progress tracker monitors performance
5. System generates detailed progress report

### Customizing the Session:
Modify `main.py` to customize:
- Student grade level
- Learning subjects
- LLM provider
- Session length

```python
# In main.py
agents = create_educational_agents(
    student_id="student_123",
    session_id=generate_session_id(),
    grade_level="high_school",  # Change to elementary, middle_school, etc.
    llm_provider="gemini"  # Change to azure_openai, openai, huggingface
)
```

## Project Structure

```
educational_tutor_agent/
├── requirements.txt
├── config/
│   ├── llm_config.py          # LLM provider configurations
│   └── agent_config.py        # Agent system messages
├── agents/
│   ├── tutor_agent.py         # Educational tutor agent
│   ├── student_agent.py       # Student proxy agent
│   └── progress_tracker.py    # Progress tracking agent
├── memory/
│   ├── conversation_memory.py # Conversation history management
│   └── progress_memory.py     # Learning progress tracking
├── llm_providers/
│   ├── azure_openai_provider.py
│   ├── openai_provider.py
│   ├── huggingface_provider.py
│   └── gemini_provider.py
├── utils/
│   └── helpers.py             # Utility functions
├── data/                      # Storage directory
├── tests/                     # Unit tests
└── main.py                    # Main application
```

## Supported LLM Providers

| Provider | File | Status |
|----------|------|--------|
| Azure OpenAI | `llm_providers/azure_openai_provider.py` | ✅ Fully Supported |
| OpenAI | `llm_providers/openai_provider.py` | ✅ Fully Supported |
| Hugging Face | `llm_providers/huggingface_provider.py` | ✅ Fully Supported |
| Gemini | `llm_providers/gemini_provider.py` | ✅ Fully Supported |

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Microsoft AutoGen](https://microsoft.github.io/autogen/) for the multi-agent framework
- [LangChain](https://www.langchain.com/) for memory management components
- OpenAI, Azure, Hugging Face, and Google for their AI models and APIs

---

