from openai import AzureOpenAI

class AzureOpenAIProvider:
    def __init__(self, config):
        self.client = AzureOpenAI(
            api_key=config["config_list"][0]["api_key"],
            azure_endpoint=config["config_list"][0]["base_url"],
            api_version=config["config_list"][0]["api_version"]
        )
        self.model = config["config_list"][0]["model"]

    def generate_reply(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content