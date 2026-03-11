"""Gigi Robot"""

import json
import os
from datetime import datetime

from openai import OpenAI


class Gigi:
  """Gigi Robot."""

  def __init__(self, model: str = "doubao-1-5-lite-32k-250115", window_size: int = 10, summarize_threshold: int = 20):
    """Initialize Gigi chatbot.

    Args:
        model: Model name, default is "doubao-1-5-lite-32k-250115".
        window_size: Number of recent messages to keep in context, default is 10.
        summarize_threshold: Number of messages before summarizing, default is 20.
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
    self.summarize_threshold = summarize_threshold
    self.messages = self._load_history()
    self._load_role()
    self.tools = self._load_tools()
    self._summarize_memory_if_needed()

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

  def _summarize_memory_if_needed(self) -> None:
    """Summarize conversation history if it exceeds threshold."""
    if len(self.messages) <= self.summarize_threshold:
      return
    
    summary_messages = []
    if self.system_prompt:
      summary_messages.append({"role": "system", "content": self.system_prompt})
    
    messages_to_summarize = self.messages[:-self.window_size]
    summary_messages.extend(messages_to_summarize)
    
    summary_prompt = {
      "role": "system",
      "content": "请用简洁的语言总结以上对话历史，保留关键信息：用户的基本信息、重要的对话内容、双方的关系状态等。"
    }
    summary_messages.append(summary_prompt)
    
    try:
      completion = self.client.chat.completions.create(
          model=self.model, messages=summary_messages
      )
      summary = completion.choices[0].message.content or "对话历史总结"
      
      recent_messages = self.messages[-self.window_size:]
      self.messages = [
        {"role": "system", "content": f"对话历史总结：{summary}"},
      ]
      self.messages.extend(recent_messages)
      
      self._save_history()
    except Exception:
      pass

  def _get_current_time(self, arguments: dict) -> str:
    """Get current time.

    Args:
        arguments: Tool arguments containing optional format string.

    Returns:
        Current time formatted string.
    """
    fmt = arguments.get("format", "%Y-%m-%d %H:%M:%S")
    return datetime.now().strftime(fmt)

  def _read_file(self, arguments: dict) -> str:
    """Read file content.

    Args:
        arguments: Tool arguments containing file_path.

    Returns:
        File content or error message.
    """
    file_path = arguments.get("file_path", "")
    if not file_path:
      return "错误：未指定文件路径"
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    except FileNotFoundError:
      return f"错误：文件 '{file_path}' 不存在"
    except Exception as e:
      return f"错误：读取文件失败 - {str(e)}"

  def _call_tool(self, name: str, arguments: dict) -> str:
    """Execute a tool function.

    Args:
        name: Tool function name.
        arguments: Tool function arguments.

    Returns:
        Tool execution result.
    """
    tool_handlers = {
      "get_current_time": self._get_current_time,
      "read_file": self._read_file,
    }
    handler = tool_handlers.get(name)
    if handler:
      return handler(arguments)
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

  def summarize_memory(self) -> str:
    """Summarize all conversation history.

    Returns:
        Summary text.
    """
    if len(self.messages) == 0:
      return "对话历史为空"
    
    summary_messages = []
    if self.system_prompt:
      summary_messages.append({"role": "system", "content": self.system_prompt})
    
    summary_messages.extend(self.messages)
    
    summary_prompt = {
      "role": "system",
      "content": "请用简洁的语言总结以上所有对话历史，保留关键信息：用户的基本信息、重要的对话内容、双方的关系状态等。"
    }
    summary_messages.append(summary_prompt)
    
    try:
      completion = self.client.chat.completions.create(
          model=self.model, messages=summary_messages
      )
      summary = completion.choices[0].message.content or "对话历史总结"
      
      self.messages = [
        {"role": "system", "content": f"对话历史总结：{summary}"},
      ]
      
      self._save_history()
      return f"对话历史已总结：{summary}"
    except Exception as e:
      return f"总结失败：{str(e)}"
