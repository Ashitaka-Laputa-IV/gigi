import os
from openai import OpenAI

class gigi:
    def __init__(self, model="doubao-1-5-lite-32k-250115"):
        """
        初始化gigi类
        :param model_name: 模型名称，默认值为"doubao-1-5-lite-32k-250115"
        """
    
        self.model = model
        self.api_key = os.getenv("API_KEY")
        self.api_base = os.getenv("API_BASE")
        self.client = OpenAI(base_url=self.api_base, api_key=self.api_key,)
        
    def talk(self, message) -> str:
        """
        与gigi进行对话
        :param message: 对话内容
        :return: gigi的回复
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": message},
            ],
        )
        return completion.choices[0].message.content

