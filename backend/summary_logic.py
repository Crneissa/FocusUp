from flask import request, jsonify
import os
import sys
import pathlib
import google.generativeai as generativeai
from app import get_api_key #import the get_api_key function from app.py.

generativeai.configure(api_key=get_api_key("API_KEY.txt"))

def answer_prompt(pdf_path: str, user_prompt: str) -> str:
    filepath = pathlib.Path(pdf_path)
    file = generativeai.upload_file(path=str(filepath))
    model = generativeai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([user_prompt, file])
    return response.text

def process_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if pdf_file:
        # Adjust the path to the uploads directory
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        pdf_path = os.path.join(uploads_dir, pdf_file.filename)
        pdf_file.save(pdf_path)
        message = "Would you like a summary of the document, or do you have any questions about it?"
        pdf_data = pdf_path
        return jsonify({'message': message, 'pdf_data': pdf_data})
    else:
        return jsonify({"error": "there was an error processing the file."})

def ask_question():
    data = request.get_json()
    question = data.get('question')
    pdf_data = data.get('pdf_data')

    if question and pdf_data:
        answer = answer_prompt(pdf_data, question)
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'Invalid request'}), 400