document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const bteForm = document.getElementById('bte-form');
    const predictButton = document.getElementById('predict-button');
    const btnText = predictButton.querySelector('.btn-text');
    const btnLoader = predictButton.querySelector('.btn-loader');

    const predictionModal = document.getElementById('predictionModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const closeButton = document.querySelector('.close-button');
    const modalOkButton = document.querySelector('.modal-ok-button');

    // --- UI State Functions ---

    /**
     * Shows a loading state on the predict button with an engaging message.
     */
    function showLoading() {
        btnText.textContent = 'Analyzing Parameters...'; // More engaging text
        btnLoader.style.display = 'inline-block';
        predictButton.disabled = true;
    }

    /**
     * Hides the loading state on the predict button.
     */
    function hideLoading() {
        btnText.textContent = 'Predict BTE';
        btnLoader.style.display = 'none';
        predictButton.disabled = false;
    }

    /**
     * Displays the modal with a specified title and message.
     * @param {string} title - The title for the modal.
     * @param {string} message - The message content for the modal.
     * @param {boolean} isSuccess - Determines if the modal shows a success or error state.
     */
    function showModal(title, message, isSuccess = true) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        
        const modalContent = predictionModal.querySelector('.modal-content');
        if (isSuccess) {
            modalContent.classList.remove('error-modal');
        } else {
            modalContent.classList.add('error-modal');
        }
        
        predictionModal.classList.add('show');
    }

    /**
     * Hides the modal and clears the form.
     */
    function hideModal() {
        predictionModal.classList.remove('show');
        bteForm.reset();
    }

    // --- Event Listeners ---

    bteForm.addEventListener('submit', function (event) {
        event.preventDefault();
        showLoading();

        const formData = new FormData(this);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = Number(value);
        }

        // 1. Create the API request promise
        const predictionPromise = fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (!response.ok) {
                // If the response is not OK, parse the error and throw it
                return response.json().then(err => { throw new Error(err.error || 'Server error'); });
            }
            return response.json();
        });

        // 2. Create a promise that resolves after 3 seconds
        const delayPromise = new Promise(resolve => setTimeout(resolve, 3000));

        // 3. Wait for BOTH the API call and the 3-second delay to complete
        Promise.all([predictionPromise, delayPromise])
            .then(([predictionResult]) => {
                // This block runs only after 3 seconds AND after the API has responded
                if (predictionResult.predicted_BTE !== undefined) {
                    showModal('Prediction Result', `Predicted Brake Thermal Efficiency is: ${predictionResult.predicted_BTE}`, true);
                } else {
                    showModal('Prediction Error', predictionResult.error || 'An unknown error occurred.', false);
                }
            })
            .catch(error => {
                // Handle any error from the fetch request
                console.error('Prediction fetch error:', error);
                showModal('Prediction Error', `Error: ${error.message}`, false);
            })
            .finally(() => {
                // This always runs, ensuring the button is reset
                hideLoading();
            });
    });

    // Handle modal closing events
    closeButton.addEventListener('click', hideModal);
    modalOkButton.addEventListener('click', hideModal);
    window.addEventListener('click', (event) => {
        if (event.target === predictionModal) {
            hideModal();
        }
    });
});