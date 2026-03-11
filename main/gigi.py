"""Gigi Robot"""

import json
import os
from datetime import datetime

from openai import OpenAI


class Gigi:
  """Gigi Robot."""

  def __init__(self, model: str = "doubao-1-5-lite-32k-250115", window_size: int = 10):
    """Initialize Gigi chatbot.

    Args:
        model: Model name, default is "doubao-1-5-lite-32k-250115".
        window_size: Number of recent messages to keep in context, default is 10.
    """
    self.model = model
    self.api_key = os.getenv("API_KEY")
    self.api_base = os.getenv("API_BASE")
    self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)
    self.history_file = "gigi_memory.json"
    self.role_file = "gigi_role.json"
    self.tools_file = "gigi_tools.json"
    self.system_prompt = ""
    self.window_size = window_size
    self.messages = self._load_history()
    self._load_role()
    self.tools = self._load_tools()

  def _load_tools(self) -> list[dict]:
    """Load tools definition from file.

    Returns:
        List of tool definitions.
    """
    if os.path.exists(self.tools_file):
      try:
        with open(self.tools_file, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        return []
    return []

  def _call_tool(self, name: str, arguments: dict) -> str:
    """Execute a tool function.

    Args:
        name: Tool function name.
        arguments: Tool function arguments.

    Returns:
        Tool execution result.
    """
    if name == "get_current_time":
      fmt = arguments.get("format", "%Y-%m-%d %H:%M:%S")
      return datetime.now().strftime(fmt)
    return f"Unknown tool: {name}"

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

  def _apply_sliding_window(self) -> list[dict]:
    """Apply sliding window to limit context length.

    Returns:
        Recent messages within window size.
    """
    if len(self.messages) <= self.window_size:
      return self.messages
    return self.messages[-self.window_size:]

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
    
    recent_messages = self._apply_sliding_window()
    messages.extend(recent_messages)
    messages.append({"role": "user", "content": message})

    completion = self.client.chat.completions.create(
        model=self.model, messages=messages, tools=self.tools
    )

    response_message = completion.choices[0].message

    if response_message.tool_calls:
      messages.append(response_message)
      for tool_call in response_message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        func_result = self._call_tool(func_name, func_args)
        messages.append({
          "tool_call_id": tool_call.id,
          "role": "tool",
          "name": func_name,
          "content": func_result
        })
      completion = self.client.chat.completions.create(
          model=self.model, messages=messages, tools=self.tools
      )
      response_message = completion.choices[0].message

    response = response_message.content or ""
    self.messages.append({"role": "user", "content": message})
    self.messages.append({"role": "assistant", "content": response})

    self._save_history()

    return response

  def clear_memory(self) -> None:
    """Clear conversation history."""
    self.messages = []
    if os.path.exists(self.history_file):
      os.remove(self.history_file)
