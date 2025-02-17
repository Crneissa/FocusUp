from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
import sys
import pathlib
import google.generativeai as generativeai
import summary_logic, eye_tracker, utils #import your backend logic files.
from dotenv import load_dotenv


load_dotenv() # Load environment variables from .env

# Adjust the path to api_key.txt
def get_api_key(file_path: str) -> str:
    return os.environ.get("API_KEY")


generativeai.configure(api_key=utils.get_api_key()) 

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'))

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

eye_trackers = {}

@app.route('/')
def serve_index():
    return render_template('home.html')

@app.route('/summary')
def serve_summary():
    print("Summary route accessed.")
    print(f"Session: {session}")
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex()
    user_id = session['user_id']
    if user_id not in eye_trackers:
        try:
            eye_trackers[user_id] = eye_tracker.EyeTracker(user_id)
            eye_trackers[user_id].start_tracking()
        except Exception as e:
            print(f"Error starting eye tracker: {e}")
    return render_template('summary.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), filename)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    return summary_logic.process_pdf()

@app.route('/ask_question', methods=['POST'])
def ask_question():
    return summary_logic.ask_question()

@app.route('/strike/<user_id>', methods=['POST'])
def strike(user_id):
    data = request.get_json()
    strikes = data.get('strikes')
    if user_id in eye_trackers:
        print(f"User {user_id} has {strikes} strikes.")
    return jsonify({"status": "success"})

@app.route('/reset_strikes')
def reset_strikes():
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in eye_trackers:
            eye_trackers[user_id].reset_strikes()
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/home')
def serve_home():
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in eye_trackers:
            eye_trackers[user_id].stop_tracking()
            del eye_trackers[user_id]
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)