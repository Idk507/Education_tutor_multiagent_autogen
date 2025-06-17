def get_azure_openai_config():
    return {
        "config_list": [
            {
                "model": "gpt-4o",
                "api_key": "",  
                "base_url": "https://idkrag.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2024-02-01"
            }
        ],
        "temperature": 0.7,
        "timeout": 120,
        "cache_seed": 42
    }

def get_openai_config():
    return {
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": "your_openai_api_key",  # Replace with actual key
                "api_type": "openai"
            }
        ],
        "temperature": 0.7,
        "timeout": 120,
        "cache_seed": 42
    }

# Placeholder for other providers
def get_huggingface_config():
    return {
        "config_list": [
            {
                "model": "your_hf_model",
                "api_key": "your_hf_api_key"
            }
        ]
    }

def get_gemini_config():
    return {
        "config_list": [
            {
                "model": "your_gemini_model",
                "api_key": "your_gemini_api_key"
            }
        ]
    }