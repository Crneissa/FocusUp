document.querySelector('.upload-btn').addEventListener('click', function() {
    const featuresSection = document.querySelector('.features');
    featuresSection.scrollIntoView({ behavior: 'smooth' });
});

document.addEventListener('DOMContentLoaded', () => {
    const pdfUpload = document.getElementById('pdfUpload');
    const getStartedButton = document.querySelector('.upload-btn'); // Select the "Get Started" button
    const uploadContainer = document.querySelector('.upload-container'); // Select the upload container

    // Initially hide the upload container
    uploadContainer.style.display = 'none';

    // Event listener for the "Get Started" button
    getStartedButton.addEventListener('click', () => {
        uploadContainer.style.display = 'block'; // Show the upload container
    });


    pdfUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('pdf', file);

            fetch('/upload_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert("Error uploading PDF.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred.");
            });
        } else {
            alert("Please select a PDF file.");
        }
    });
});