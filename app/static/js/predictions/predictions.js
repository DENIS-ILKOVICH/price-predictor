let currentPage = 1;
const recordsPerPage = 20;
let isAdmin = false;
let allPredictions = [];

function filterPredictions() {
    const price = document.getElementById('searchPrice').value.trim();
    const requestId = document.getElementById('searchRequestId').value.trim();

    const formData = new FormData();
    formData.append('datatype', 'search');
    formData.append('search_value', JSON.stringify({ price, request_id: requestId }));

    fetch('/sort_predictions', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            toastr.options = {
                closeButton: true,
                preventDuplicates: true,
                hideEasing: "linear"
            };
            toastr.error('No matching data found.', 'Error!');
        } else {
            allPredictions = data;
            currentPage = 1;
            renderPredictions();
            toggleLoadMoreButton();
            clearForm();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        toastr.options = {
            closeButton: true,
            preventDuplicates: true,
            hideEasing: "linear"
        };
        toastr.error('An error occurred while processing the request. Please try again.', 'Error!');
    });
}

function loadAllPredictions() {
    fetch('/sort_predictions', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        allPredictions = data;
        renderPredictions();
        toggleLoadMoreButton();
    })
    .catch(error => console.error('Error:', error));
}

function renderPredictions(append = false) {
    const container = document.getElementById('predictionsContainer');
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const currentRecords = allPredictions.slice(startIndex, endIndex);

    if (!append) {
        container.innerHTML = '';
    }

    if (currentRecords.length > 0) {
        currentRecords.forEach(prediction => {
            const card = document.createElement('div');
            card.classList.add('prediction-card');

            let cardHTML = `
                <h3>Prediction #${prediction.id}</h3>
                <p><strong>Request:</strong></p>
                <p>Type: ${prediction.type}</p>
                <p>District: ${prediction.district}</p>
                <p>Rooms: ${prediction.rooms}</p>
                <p>Floor: ${prediction.floor}/${prediction.floors}</p>
                <p>Area: ${prediction.area} m²</p>
                <p>Condition: ${prediction.cond}</p>
                <p>Wall Material: ${prediction.walls}</p>
                <p class="request-timestamp">Submitted on: ${prediction.request_timestamp.split(".")[0]}</p>
                <div class="result">
                    <p><strong>Price:</strong> ${prediction.price.toFixed(2)} $</p>
                </div>
            `;

            if (isAdmin) {
                cardHTML += `<button class="delete-btn" data-id="${prediction.id}">╳</button>`;
            }

            card.innerHTML = cardHTML;

            if (isAdmin) {
                const deleteBtn = card.querySelector('.delete-btn');
                deleteBtn.addEventListener('click', () => {
                    const formData = new FormData();
                    formData.append('delete_mode', 'remove_id');
                    formData.append('value', prediction.id);

                    fetch('/del_predictions', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message === 'Deletion was successful!') {
                            alert(`Prediction #${prediction.id} has been successfully deleted.`);
                            loadAllPredictions();
                        } else {
                            alert('Failed to delete prediction.');
                        }
                    })
                    .catch(error => {
                        console.error('Deletion error:', error);
                        alert('An error occurred while deleting the prediction.');
                    });
                });
            }

            container.appendChild(card);
        });
    } else if (!append) {
        container.innerHTML = '<p>No predictions found.</p>';
    }
}

function clearForm() {
    document.getElementById('searchPrice').value = '';
    document.getElementById('searchRequestId').value = '';
}

function cleanFilterPredictions() {
    clearForm();
    loadAllPredictions();
}

function toggleLoadMoreButton() {
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    if (allPredictions.length > currentPage * recordsPerPage) {
        loadMoreContainer.style.display = 'block';
    } else {
        loadMoreContainer.style.display = 'none';
    }
}

function loadMorePredictions() {
    currentPage++;
    renderPredictions(true);
    toggleLoadMoreButton();
}

function checkAdminAccess() {
    fetch('/get_user')
        .then(response => response.json())
        .then(data => {
            const openBtn = document.getElementById('openDeleteFormBtn');
            const deleteForm = document.getElementById('deletePredictionsForm');

            if (data && data.length > 0 && data[0].type === 'admin') {
                isAdmin = true;
                openBtn.style.display = 'inline-block';

                if (!openBtn.dataset.bound) {
                    openBtn.addEventListener('click', () => {
                        deleteForm.style.display = 'block';
                    });
                    openBtn.dataset.bound = 'true';
                }
            } else {
                isAdmin = false;
                openBtn.style.display = 'none';
                deleteForm.style.display = 'none';
            }

            renderPredictions();
        })
        .catch(error => {
            console.error('Error checking admin access:', error);
        });
}

function deletePrediction(event) {
    event.preventDefault();

    const deleteMode = document.getElementById('deleteMode').value;
    const value = document.getElementById('valueInput').value;

    const formData = new FormData();
    formData.append('delete_mode', deleteMode);
    formData.append('value', value);

    fetch('/del_predictions', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Deletion was successful!') {
            alert('Prediction successfully deleted!');
            loadAllPredictions();
        } else {
            alert('Prediction not found!');
        }
    })
    .catch(error => {
        console.error('Error deleting prediction:', error);
        alert('An error occurred while deleting the prediction.');
    });
}

document.getElementById('delForm').addEventListener('submit', deletePrediction);

function setupSearchKeyListeners() {
    const searchPriceInput = document.getElementById('searchPrice');
    const searchRequestIdInput = document.getElementById('searchRequestId');

    [searchPriceInput, searchRequestIdInput].forEach(input => {
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                filterPredictions();
            } else if (event.key === 'Escape') {
                event.preventDefault();
                cleanFilterPredictions();
            }
        });
    });
}

window.onload = () => {
    checkAdminAccess();
    loadAllPredictions();
    setupSearchKeyListeners();
};
