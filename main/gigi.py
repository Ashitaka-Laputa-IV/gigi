import os
import json
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
        self.history_file = "gigi_memory.json"
        self.messages = self._load_history()
        
    def _load_history(self):
        """
        从文件加载对话历史
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """
        保存对话历史到文件
        """
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
        
    def talk(self, message) -> str:
        """
        与gigi进行对话
        :param message: 对话内容
        :return: gigi的回复
        """
        self.messages.append({"role": "user", "content": message})
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        
        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        
        self._save_history()
        
        return response
    
    def clear_memory(self):
        """
        清空对话历史
        """
        self.messages = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

