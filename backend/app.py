from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
import sys
import pathlib
import google.generativeai as generativeai
import summary_logic, quiz_logic, eye_tracker, utils #import your backend logic files.
from dotenv import load_dotenv


load_dotenv() # Load environment variables from .env

# Adjust the path to api_key.txt
def get_api_key(file_path: str) -> str:
    return os.environ.get("API_KEY")


generativeai.configure(api_key=utils.get_api_key()) 

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'))

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

eye_trackers = {}

UPLOAD_FOLDER = 'uploads'  # Set the uploads directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/quiz')  # Add this route for quiz.html
def serve_quiz():
    return render_template('quiz.html') 

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'), filename)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' in request.files:
        pdf_file = request.files['pdf']
        if pdf_file.filename.endswith('.pdf'):
            try:
                # Save the PDF to the uploads directory
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
                pdf_file.save(filepath)

                # Process the PDF (e.g., extract text, store in session)
                pdf_data = summary_logic.process_pdf_data(filepath)  # Pass the filepath
                session['pdf_filename'] = pdf_file.filename # Store filename in session
                return jsonify({'message': 'PDF uploaded successfully!'})
            except Exception as e:
                print(f"Error uploading PDF: {e}")
                return jsonify({'error': 'Error uploading PDF'})
        else:
            return jsonify({'error': 'Invalid file type'})
    return jsonify({'error': 'No file uploaded'})

@app.route('/get_pdf_data', methods=['GET'])
def get_pdf_data():
    filename = session.get('pdf_filename')
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            pdf_data = summary_logic.get_pdf_data(filepath) # New function in summary_logic.py
            return jsonify({'pdf_data': pdf_data})
        except Exception as e:
            print(f"Error getting PDF data: {e}")
            return jsonify({'error': 'Error getting PDF data'})
    return jsonify({'error': 'No PDF data found'})

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    return summary_logic.process_pdf()

@app.route('/ask_question', methods=['POST'])
def ask_question():
    return summary_logic.ask_question()

@app.route('/generate_quiz')
def generate_quiz_route():
    print("generate_quiz_route called") # Add this
    num_questions = int(request.args.get('num_questions', 5))
    filename = session.get('pdf_filename')
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_data = summary_logic.get_pdf_data(filepath)  # Call from summary_logic
    else:
        pdf_data = None

    if not pdf_data:
        return jsonify({"error": "No PDF data available"}), 400

    quiz_data, error_message = quiz_logic.generate_quiz(pdf_data, num_questions)  # Call from quiz_logic

    if quiz_data: # Check if quiz_data is not None
        print(f"Data being sent: {quiz_data}") # Add this line
        return jsonify(quiz_data) # Send the dictionary that contains the questions
    else:
        return jsonify({"error": error_message}), 500


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