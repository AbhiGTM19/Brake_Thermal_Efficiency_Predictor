 document.addEventListener('DOMContentLoaded', () => {
            const statusDiv = document.getElementById('status');

            // Check backend status on page load
            fetch('/home')
                .then(response => response.json())
                .then(data => {
                    statusDiv.textContent = data.message || '✅ Backend is running.';
                    statusDiv.style.display = 'block';
                })
                .catch(error => {
                    statusDiv.textContent = '❌ Error: Could not connect to the backend.';
                    statusDiv.style.display = 'block';
                    statusDiv.style.backgroundColor = '#f8d7da';
                    statusDiv.style.color = '#721c24';
                });
        });

        document.getElementById('bte-form').addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(this);
            const data = {};
            // Convert form data to a plain object and ensure values are numbers
            for (let [key, value] of formData.entries()) {
                data[key] = Number(value);
            }

            const resultDiv = document.getElementById('result');

            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    // Handle HTTP errors like 400 or 500
                    return response.json().then(err => { throw new Error(err.error) });
                }
                return response.json();
            })
            .then(data => {
                if (data.predicted_BTE !== undefined) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `<strong>Predicted BTE:</strong> ${data.predicted_BTE}`;
                } else {
                    throw new Error(data.error || 'An unknown error occurred.');
                }
            })
            .catch(error => {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            });
        });