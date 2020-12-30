# coding: utf-8
import json
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def get():
    return "Hello world!"

@app.route('/send', methods=['POST'])
def send():
    print(request.json)
    return request.json['value']

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
