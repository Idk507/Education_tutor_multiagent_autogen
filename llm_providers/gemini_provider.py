import requests

class GeminiProvider:
    def __init__(self, config):
        self.api_key = config["config_list"][0]["api_key"]
        self.model = config["config_list"][0]["model"]
        self.base_url = "https://gemini.api.endpoint/"  # Replace with actual endpoint

    def generate_reply(self, messages):
        input_text = messages[-1]["content"]
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(f"{self.base_url}{self.model}", headers=headers, json={"prompt": input_text})
        return response.json()["generated_text"]