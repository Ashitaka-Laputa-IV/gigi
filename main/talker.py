"""Command-line interface for Gigi chatbot."""

from gigi import Gigi


def main() -> None:
  """Run the command-line chat interface."""
  my_gigi = Gigi()

  while True:
    message = input("user: ")
    if message == "exit":
      break
    response = my_gigi.talk(message)
    print("gigi:", response)


if __name__ == "__main__":
  main()
