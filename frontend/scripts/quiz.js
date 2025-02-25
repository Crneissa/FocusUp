// quiz.js
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

document.addEventListener("DOMContentLoaded", () => {
    const numQuestionsInput = document.getElementById("num-questions");
    const startQuizButton = document.getElementById("start-quiz");
    const quizPrompt = document.getElementById("quiz-prompt");
    const quizContent = document.getElementById("quiz-content");
    const questionText = document.getElementById("question-text");
    const optionsContainer = document.getElementById("options-container");
    const progressBar = document.getElementById("progress-bar");
    const prevButton = document.getElementById("prev-question");
    const nextButton = document.getElementById("next-question");

    let questions = [];
    let currentQuestion = 0;
    let userAnswers = []; // Store user's answers

    startQuizButton.addEventListener("click", () => {
        const numQuestions = parseInt(numQuestionsInput.value, 10);
        if (isNaN(numQuestions) || numQuestions <= 0) {
            alert("Please enter a valid number of questions.");
            return;
        }

        fetch('/generate_quiz?num_questions=' + numQuestions)
            .then(response => response.json())
            .then(data => {
                console.log("Data Received:", data); // Add this line

                if (data.error) {
                    alert(data.error);
                    return;
                } else if (data.questions) {
                    questions = data.questions;
                    currentQuestion = 0;
                    userAnswers = new Array(questions.length).fill(null);
                    showQuestion(currentQuestion);

                    quizPrompt.style.display = "none";
                    quizContent.style.display = "block";
                    progressBar.parentNode.style.display = "block";
                    prevButton.parentNode.style.display = "flex";
                } else {
                    alert("Invalid JSON: 'questions' key missing or not a list");
                }
            })
            .catch(error => {
                console.error("Error fetching quiz questions:", error);
                alert("An error occurred while generating the quiz.");
            });
    });

    function showQuestion(index) {
        if (index < 0 || index >= questions.length) return;

        const question = questions[index];
        questionText.textContent = question.text;
        optionsContainer.innerHTML = "";

        question.options.forEach((option, i) => {
            const optionButton = document.createElement("button");
            optionButton.classList.add("option");
            optionButton.textContent = option;

            // Highlight the selected option (if any)
            if (userAnswers[index] === option) {
                optionButton.classList.add("selected");
            }
            console.log("Question Correct Answer:", question.correctAnswer); // Add this line

            optionButton.addEventListener("click", () => {
                userAnswers[index] = option; // Store the user's answer
                showQuestion(index); // Refresh to highlight selection

                handleAnswerSelection(option, question.correctAnswer, optionButton); // Pass the button
            });
            optionsContainer.appendChild(optionButton);
        });

        updateProgress();
    }

    function handleAnswerSelection(selectedOption, correctAnswer, optionButton) {
        console.log("Selected Option:", selectedOption);
        console.log("Correct Answer:", correctAnswer);
    
        // Find the question object
        const questionIndex = questions.findIndex(q => q.options.includes(selectedOption));
        if (questionIndex === -1) {
            console.error("Question not found for selected option:", selectedOption);
            return;
        }
        const question = questions[questionIndex];
    
        // Get the correct answer text
        const correctAnswerText = question.options[correctAnswer.charCodeAt(0) - 65];
    
        if (selectedOption.trim().toLowerCase() === correctAnswerText.trim().toLowerCase()) {
            optionButton.style.border = "2px solid green";
        } else {
            optionButton.style.border = "2px solid red";
        }
    }

    function updateProgress() {
        const progressPercentage = ((currentQuestion + 1) / questions.length) * 100;
        progressBar.style.width = progressPercentage + "%";
        progressBar.textContent = Math.round(progressPercentage) + "%";
    }

    prevButton.addEventListener("click", () => {
        currentQuestion--;
        if (currentQuestion < 0) currentQuestion = 0;
        showQuestion(currentQuestion);
    });

    nextButton.addEventListener("click", () => {
        currentQuestion++;
        if (currentQuestion >= questions.length) currentQuestion = questions.length - 1;
        showQuestion(currentQuestion);
    });

    const sidebarLinks = document.querySelectorAll(".sidebar nav a");
    sidebarLinks.forEach(link => {
        link.addEventListener("click", () => {
            toggleSidebar();
        });
    });
});