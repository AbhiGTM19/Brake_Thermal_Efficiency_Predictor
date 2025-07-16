// script.js
document.addEventListener('DOMContentLoaded', () => {
    const statusDiv = document.getElementById('status');

    // Check backend status on page load - now calling /status endpoint
    fetch('/status') // <--- CHANGED THIS TO /status
        .then(response => {
            if (!response.ok) {
                // If the status endpoint itself returns an error (e.g., 500)
                return response.json().then(err => { throw new Error(err.message || 'Server error'); });
            }
            return response.json();
        })
        .then(data => {
            //            statusDiv.textContent = data.message || '✅ Backend is running.';
            //            statusDiv.style.display = 'block';
            if (data.status === 'warning') {
                statusDiv.style.backgroundColor = '#fff3cd'; // Yellowish for warning
                statusDiv.style.color = '#856404';
            } else if (data.status === 'error') {
                statusDiv.style.backgroundColor = '#f8d7da'; // Reddish for error
                statusDiv.style.color = '#721c24';
            } else {
                statusDiv.style.backgroundColor = '#d4edda'; // Greenish for success
                statusDiv.style.color = '#155724';
            }
        })
        .catch(error => {
            statusDiv.textContent = `❌ Error: Could not connect to the backend or status check failed. ${error.message || ''}`;
            statusDiv.style.display = 'block';
            statusDiv.style.backgroundColor = '#f8d7da';
            statusDiv.style.color = '#721c24';
        });
});

document.getElementById('bte-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = {};
    // Convert form data to a plain object and ensure values are numbers
    for (let [key, value] of formData.entries()) {
        data[key] = Number(value);
    }

    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Predicting...';

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.predicted_BTE !== undefined) {
                resultDiv.className = 'result success';
                resultDiv.innerHTML = `<strong>Predicted BTE:</strong> ${data.predicted_BTE.toFixed(3)}`;
            } else {
                throw new Error(data.error || 'An unknown error occurred with prediction result.');
            }
        })
        .catch(error => {
            console.error('Prediction fetch error:', error);
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${error.message || 'Could not get prediction.'}`;
        });
});