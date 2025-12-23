import openai


class AI:
    def __init__(self, client: openai.Client, model: str) -> None:
        self.client = client
        self.model = model

    def request(self, system: str, user: str) -> str:
        print(">>>>> " + system + " " + user)
        completions = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": user,
                },
            ],
            model=self.model,
            temperature=0,
        )
        print(completions.choices[0].message.content)
        return completions.choices[0].message.content
