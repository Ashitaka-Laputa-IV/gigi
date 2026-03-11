"""Command-line interface for Gigi chatbot."""

from gigi import Gigi


def main() -> None:
  """Run the command-line chat interface."""
  my_gigi = Gigi()

  while True:
    message = input("user: ")
    if message == "exit":
      break
    if message == "clear":
      my_gigi.clear_memory()
      print("gigi: 对话历史已清空")
      continue
    if message == "summarize":
      result = my_gigi.summarize_memory()
      print(f"gigi: {result}")
      continue
    response = my_gigi.talk(message)
    print("gigi:", response)


if __name__ == "__main__":
  main()
