function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        const chatContainer = document.querySelector(".chat-container");
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const resultsDiv = document.getElementById("results");
    const title = document.querySelector('.title');
    const container = document.querySelector('.container');
    const inputContainer = document.querySelector('.input-container');
    let pdfData = null;

    fetch('/get_pdf_data')
        .then(response => response.json())
        .then(data => {
            if (data.pdf_data) {
                pdfData = data.pdf_data;
            } else {
                resultsDiv.innerHTML = `<div class="message">Please upload a PDF on the home page.</div>`;
                return;
            }
        })
        .catch(error => {
            console.error("Error fetching PDF data:", error);
            resultsDiv.innerHTML = `<div class="message">An error occurred fetching PDF data.</div>`;
            return;
        });

    document.querySelector(".send-btn").addEventListener("click", function () {
        const message = document.getElementById("messageInput").value;
        if (message && pdfData) {
            resultsDiv.innerHTML += `<div class="message user-message">${message}</div>`;
            scrollToBottom();

            document.getElementById("messageInput").value = "";

            if (resultsDiv.children.length === 1) {
                title.style.display = 'none';
                container.style.justifyContent = 'flex-end';
                inputContainer.classList.add('fixed');
            }

            fetch('/ask_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message, pdf_data: pdfData }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.answer) {
                        let formattedAnswer = data.answer;

                        formattedAnswer = formattedAnswer.replace(/\*(.*?)\*/g, "<strong>$1</strong>");
                        formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
                        formattedAnswer = formattedAnswer.replace(/\* (.*?)\n/g, "<ul><li>$1</li></ul>");
                        formattedAnswer = formattedAnswer.replace(/\d+\. (.*?)\n/g, "<ol><li>$1</li></ol>");

                        resultsDiv.innerHTML += `<div class="message bot-message">${formattedAnswer}</div>`;
                        scrollToBottom(); // Call scrollToBottom() AFTER adding the message

                    } else {
                        resultsDiv.innerHTML += `<div class="message">There was an error getting an answer.</div>`;
                    }
                })
                .catch(error => {
                    console.error("Error asking question:", error);
                    resultsDiv.innerHTML += `<div class="message">An error occurred asking the question.</div>`;
                });
        }
    });

    const messageInput = document.getElementById("messageInput");
    messageInput.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            document.querySelector(".send-btn").click();
        }
    });
});