"""Gigi Robot"""

import json
import os

from openai import OpenAI


class Gigi:
  """Gigi Robot."""

  def __init__(self, model: str = "doubao-1-5-lite-32k-250115"):
    """Initialize Gigi chatbot.

    Args:
        model: Model name, default is "doubao-1-5-lite-32k-250115".
    """
    self.model = model
    self.api_key = os.getenv("API_KEY")
    self.api_base = os.getenv("API_BASE")
    self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)
    self.history_file = "gigi_memory.json"
    self.role_file = "gigi_role.json"
    self.system_prompt = ""
    self.messages = self._load_history()
    self._load_role()

  def _load_history(self) -> list[dict]:
    """Load conversation history from file.

    Returns:
        List of message dictionaries.
    """
    if os.path.exists(self.history_file):
      try:
        with open(self.history_file, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        return []
    return []

  def _load_role(self) -> None:
    """Load role/persona from file."""
    if os.path.exists(self.role_file):
      try:
        with open(self.role_file, "r", encoding="utf-8") as f:
          self.system_prompt = f.read().strip()
      except Exception:
        pass

  def _save_history(self) -> None:
    """Save conversation history to file."""
    with open(self.history_file, "w", encoding="utf-8") as f:
      json.dump(self.messages, f, ensure_ascii=False, indent=2)

  def talk(self, message: str) -> str:
    """Chat with Gigi.

    Args:
        message: User message content.

    Returns:
        Gigi's response.
    """
    messages = []
    if self.system_prompt:
      messages.append({"role": "system", "content": self.system_prompt})
    messages.extend(self.messages)
    messages.append({"role": "user", "content": message})

    completion = self.client.chat.completions.create(
        model=self.model, messages=messages
    )

    response = completion.choices[0].message.content
    self.messages.append({"role": "user", "content": message})
    self.messages.append({"role": "assistant", "content": response})

    self._save_history()

    return response

  def clear_memory(self) -> None:
    """Clear conversation history."""
    self.messages = []
    if os.path.exists(self.history_file):
      os.remove(self.history_file)
