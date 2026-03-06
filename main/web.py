from flask import Flask, request, jsonify
from gigi import gigi

app = Flask(__name__)
gigi_instance = gigi()

@app.route('/')
def index():
    return open('index.html', encoding='utf-8').read()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = gigi_instance.talk(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)