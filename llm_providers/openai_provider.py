from openai import OpenAI

class OpenAIProvider:
    def __init__(self, config):
        self.client = OpenAI(api_key=config["config_list"][0]["api_key"])
        self.model = config["config_list"][0]["model"]

    def generate_reply(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content