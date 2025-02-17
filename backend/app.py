from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import pathlib
import google.generativeai as generativeai
import summary_logic #import your backend logic files.


# Adjust the path to api_key.txt
def get_api_key(file_path: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), file_path), 'r') as file:
        return file.readline().strip()

generativeai.configure(api_key=get_api_key("API_KEY.txt"))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), 'home.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), filename)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    return summary_logic.process_pdf()

@app.route('/ask_question', methods=['POST'])
def ask_question():
    return summary_logic.ask_question()

if __name__ == '__main__':
    app.run(debug=True)