document.addEventListener('DOMContentLoaded', () => {
    const statusDiv = document.getElementById('status');

    fetch('/status')
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || 'Server error'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'warning') {
                statusDiv.style.backgroundColor = '#fff3cd';
                statusDiv.style.color = '#856404';
            } else if (data.status === 'error') {
                statusDiv.style.backgroundColor = '#f8d7da';
                statusDiv.style.color = '#721c24';
            } else {
                statusDiv.style.backgroundColor = '#d4edda';
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

const predictionModal = document.getElementById('predictionModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const closeButton = document.querySelector('.close-button');
const modalOkButton = document.querySelector('.modal-ok-button');
const bteForm = document.getElementById('bte-form');

function showModal(title, message, isSuccess = true) {
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    predictionModal.classList.add('show');
    if (isSuccess) {
        predictionModal.querySelector('.modal-content').classList.remove('error-modal');
        predictionModal.querySelector('.modal-content').classList.add('success-modal');
    } else {
        predictionModal.querySelector('.modal-content').classList.remove('success-modal');
        predictionModal.querySelector('.modal-content').classList.add('error-modal');
    }
}

function hideModal() {
    predictionModal.classList.remove('show');
}

function clearForm() {
    bteForm.reset();
}

closeButton.addEventListener('click', () => {
    hideModal();
    clearForm(); 
});

modalOkButton.addEventListener('click', () => {
    hideModal();
    clearForm();
});

window.addEventListener('click', (event) => {
    if (event.target === predictionModal) {
        hideModal();
        clearForm();
    }
});

document.getElementById('bte-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = {};
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
                showModal('Prediction Result', `Predicted Brake Thermal Efficiency is: ${data.predicted_BTE.toFixed(3)}`, true);
                resultDiv.innerHTML = '';
            } else {    
                showModal('Prediction Error', data.error || 'An unknown error occurred with prediction result.', false);
            }
            
        })
        .catch(error => {
            console.error('Prediction fetch error:', error);
            showModal('Prediction Error', `Error: ${error.message || 'Could not get prediction.'}`, false);
            resultDiv.innerHTML = ''; 
            
        });
});