function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf";
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    const uploadButton = document.getElementById("upload-button");
    const resultsDiv = document.getElementById("results");
    let pdfData = null;

    uploadButton.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            console.log("PDF uploaded:", file.name);
            const formData = new FormData();
            formData.append('pdf', file);

            fetch('/process_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    resultsDiv.innerHTML = data.message;
                    pdfData = data.pdf_data;
                } else {
                    resultsDiv.innerHTML = "Error processing PDF.";
                }
            })
            .catch(error => {
                console.error('Error:', error);
                resultsDiv.innerHTML = "An error occurred.";
            });
        }
    });

    document.querySelector(".send-btn").addEventListener("click", function(){
        const message = document.getElementById("messageInput").value;
        if(message && pdfData){
            fetch('/ask_question',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({question: message, pdf_data: pdfData}),
            })
            .then(response => response.json())
            .then(data=>{
                if(data.answer){
                    resultsDiv.innerHTML = data.answer;
                } else {
                    resultsDiv.innerHTML = "there was an error getting an answer.";
                }
            })
            .catch(error=>{
                console.error("error:", error);
                resultsDiv.innerHTML = "an error occurred.";
            });
        }
    });
});