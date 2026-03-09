"""Flask web server for Gigi chatbot."""

from flask import Flask, jsonify, request

from gigi import Gigi

app = Flask(__name__)
gigi_instance = Gigi()


@app.route("/")
def index() -> str:
  """Serve the HTML chat interface.

  Returns:
        HTML content of the chat interface.
  """
  with open("index.html", encoding="utf-8") as f:
    return f.read()


@app.route("/chat", methods=["POST"])
def chat() -> dict:
  """Handle chat requests.

  Returns:
        JSON response with Gigi's reply.
  """
  data = request.json
  message = data.get("message", "")
  response = gigi_instance.talk(message)
  return jsonify({"response": response})


@app.route("/clear", methods=["POST"])
def clear() -> dict:
  """Clear conversation history.

  Returns:
        JSON response indicating success.
  """
  gigi_instance.clear_memory()
  return jsonify({"status": "cleared"})


if __name__ == "__main__":
  app.run(debug=True, port=5000)
