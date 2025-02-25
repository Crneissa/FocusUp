import google.generativeai as generativeai
from utils import get_api_key  # Import the get_api_key function from utils.py
import json
import re

generativeai.configure(api_key=get_api_key())

def generate_quiz_prompt(pdf_text: str, num_questions: int) -> str:
    prompt = f"""
    Create a quiz with {num_questions} multiple-choice questions based on the following PDF content:

    ```
    {pdf_text}
    ```

    For each question, provide:
    1. The question text.
    2. Four multiple-choice options (A, B, C, D).
    3. The correct answer.

    **The correct answer MUST be one of the uppercase letters "A", "B", "C", or "D" and NOTHING ELSE. Do not use lowercase letters, do not use the full text of the answer, and do not use any other characters. The correct answer must correspond to the correct option listed in the "options" array.**

    **Return the response as a valid JSON array of objects and ABSOLUTELY NOTHING ELSE. Do not include any explanatory text, comments, or any characters outside of the JSON. The ENTIRE response MUST be valid JSON that can be parsed directly.**

    The JSON should have the following structure:

    ```json
    [
        {{
            "text": "The question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctAnswer": "B" // The correct option (A, B, C, or D)
        }},
        {{
            "text": "Another question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctAnswer": "A" // The correct option (A, B, C, or D)
        }},
        // ... more questions
    ]
    ```
    """
    return prompt


def generate_quiz(pdf_text: str, num_questions: int):
    try:
        model = generativeai.GenerativeModel('gemini-1.5-flash')
        prompt = generate_quiz_prompt(pdf_text, num_questions)
        response = model.generate_content([prompt])
        quiz_json = response.text.strip()
        if not quiz_json:
            return None, "Error: Gemini returned an empty response."
        if quiz_json.startswith('\ufeff'):
            quiz_json = quiz_json[1:]
        print(f"Raw Gemini Response (repr): {repr(quiz_json)}")

        quiz_json = re.sub(r'```json\n|```', '', quiz_json).strip()
        quiz_json = quiz_json.replace('\n', '')

        print(f"Cleaned JSON (repr): {repr(quiz_json)}")

        try:
            quiz_json = quiz_json.encode('utf-8').decode('utf-8')
            quiz_data = json.loads(quiz_json)
            print(f"Parsed JSON Data: {quiz_data}")

            for question in quiz_data:
                if not all(key in question for key in ("text", "options", "correctAnswer")):
                    return None, "Invalid JSON: Each question must have 'text', 'options', and 'correctAnswer' keys."
                if not isinstance(question["options"], list) or len(question["options"]) != 4:
                    return None, "Invalid JSON: 'options' must be a list of 4 options."

            print(f"Data being returned: {{\"questions\": quiz_data}}")
            return {"questions": quiz_data}, None

        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {e}. Raw JSON: {repr(quiz_json)}"
        except KeyError as e:
            return None, f"KeyError in JSON: {e}. Raw JSON: {quiz_json}"

    except Exception as e:
        return None, f"Error generating quiz: {e}"

def get_pdf_data(filepath):  # New function to get the processed data
    try:
        pdf_text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_text += page.extract_text()
        return pdf_text  # Return the extracted text
    except Exception as e:
        print(f"Error in get_pdf_data: {e}")
        return None
