import sys
import pathlib
import google.generativeai as generativeai
from google.generativeai import types


def get_api_key(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.readline().strip()


# Configure the API with your API key
generativeai.configure(api_key=get_api_key("API_KEY.txt"))


def generate_summary(pdf_path: str) -> str:
    prompt = "I have given you a PDF that outlines an academic concept. I want you to create a detailed summary of the " \
             "content into a text that can be read in 60 seconds. The summary should include critical information and " \
             "specific examples mentioned in the pdf. You do not need to add extra words or formatting, simply give the " \
             "output as described."

    filepath = pathlib.Path(pdf_path)

    # Upload the file
    file = generativeai.upload_file(path=str(filepath))

    # Generate summary using the uploaded file
    model = generativeai.GenerativeModel('gemini-1.5-flash')  # or gemini-1.5-pro if you need vision.
    response = model.generate_content([prompt, file])

    return response.text


def generate_quiz(pdf_path: str) -> str:
    prompt = "I have given you a PDF containing an academic topic. Generate a multiple-choice quiz with 5 questions. " \
             "Each question should have 4 options, with the correct answer marked after the user has picked their choice. Format the output clearly."

    filepath = pathlib.Path(pdf_path)

    # Upload the file
    file = generativeai.upload_file(path=str(filepath))

    # Generate quiz using the uploaded file
    model = generativeai.GenerativeModel('gemini-1.5-flash')  # or gemini-1.5-pro if you need vision.
    response = model.generate_content([prompt, file])

    return response.text


if __name__ == '__main__':
    pdf_path = "uploads/application.pdf"  # Path to your PDF file

    summary_text = generate_summary(pdf_path)
    quiz_text = generate_quiz(pdf_path)

    print("Summary:\n", summary_text)
    print("\nQuiz:\n", quiz_text)
