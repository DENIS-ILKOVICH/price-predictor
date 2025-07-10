document.addEventListener("DOMContentLoaded", function () {
    const openButton = document.getElementById("open-modal");
    const closeButton = document.querySelector(".close-modal");
    const modal = document.querySelector(".modal");
    const cardContainer = document.getElementById("card-container");

    function createCards(data) {
        cardContainer.innerHTML = "";

        if (!data || (Array.isArray(data) && data.every(item => item === null))) {
            const card = document.createElement("div");
            card.classList.add("card");
            card.innerHTML = `
                <h3>No Data</h3>
                <p>Unfortunately, there is currently no available information.</p>
            `;
            cardContainer.appendChild(card);
            return;
        }

        let isAuthenticated = false;
        if (Array.isArray(data) && typeof data[data.length - 1] === 'object' && 'user' in data[data.length - 1]) {
            isAuthenticated = data[data.length - 1].user === 'authenticated';
            data = data.slice(0, -1);
        }

        data.forEach(itemArray => {
            if (Array.isArray(itemArray)) {
                itemArray.forEach(item => {
                    if (item !== null) {
                        const card = document.createElement("div");
                        card.classList.add("card");

                        card.innerHTML = `
                            <h3>Prediction #${item.id}</h3>
                            <p><strong>Price:</strong> ${item.price.toFixed(2)} $</p>
                            <p><strong>Type:</strong> ${item.type}</p>
                            <p><strong>District:</strong> ${item.district}</p>
                            <p><strong>Area:</strong> ${item.area} m²</p>
                            <p><strong>Rooms:</strong> ${item.rooms}</p>
                            <p><strong>Floor:</strong> ${item.floor} of ${item.floors}</p>
                            <p><strong>Condition:</strong> ${item.cond}</p>
                            <p><strong>Wall Material:</strong> ${item.walls}</p>
                        `;

                        if (isAuthenticated) {
                            const deleteButton = document.createElement("button");
                            deleteButton.textContent = "⨯";
                            deleteButton.classList.add("delete-button");

                            deleteButton.addEventListener("click", () => {
                                const modal = document.createElement("div");
                                modal.classList.add("close-modal-message");
                                modal.innerHTML = `
                                    <div class="modal-content">
                                        <h2>Are you sure you want to delete this prediction?</h2>
                                        <button class="confirm-delete">Yes</button>
                                        <button class="cancel-delete">No</button>
                                    </div>
                                `;
                                document.body.appendChild(modal);

                                modal.querySelector(".confirm-delete").addEventListener("click", async () => {
                                    try {
                                        const response = await fetch('/del_user_prediction', {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json'
                                            },
                                            body: JSON.stringify({ request_id: item.request_id })
                                        });

                                        if (response.ok) {
                                            card.remove();
                                            console.log(`Prediction #${item.id} deleted.`);
                                        } else {
                                            console.error("Failed to delete prediction.");
                                        }
                                    } catch (err) {
                                        console.error("Error during deletion request:", err);
                                    }
                                    modal.remove();
                                });

                                modal.querySelector(".cancel-delete").addEventListener("click", () => {
                                    modal.remove();
                                });
                            });

                            card.appendChild(deleteButton);
                        }

                        cardContainer.appendChild(card);
                    }
                });
            }
        });
    }

    async function fetchPredictions() {
        try {
            const response = await fetch('/user_predictions');
            if (response.ok) {
                const fetchedData = await response.json();
                if (fetchedData.error === 'No data found') {
                    console.log("No data found.");
                    return null;
                } else {
                    return fetchedData;
                }
            } else if (response.status === 404) {
                console.error("Data not found (404).");
                return null;
            } else {
                console.error("Server response error.");
                return null;
            }
        } catch (error) {
            console.error("Error fetching predictions:", error);
            return null;
        }
    }

    openButton.addEventListener("click", async function () {
        if (modal.classList.contains("active")) {
            modal.classList.remove("active");
            cardContainer.innerHTML = "";
        } else {
            const data = await fetchPredictions();
            createCards(data);
            modal.classList.add("active");
        }
    });

    closeButton.addEventListener("click", function () {
        modal.classList.remove("active");
        cardContainer.innerHTML = "";
    });

    document.addEventListener("click", function (event) {
        if (!modal.contains(event.target) && event.target !== openButton) {
            modal.classList.remove("active");
            cardContainer.innerHTML = "";
        }
    });

    openButton.style.display = 'block';
});
