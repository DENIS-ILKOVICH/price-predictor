async function getUserData() {
  try {
    const response = await fetch('/get_user');
    const data = await response.json();
    return data[0];
  } catch (error) {
    console.error('Error fetching user:', error);
    return null;
  }
}

async function getUserPredictions() {
  try {
    const response = await fetch('/user_predictions');
    const data = await response.json();
    const predictions = data.filter(item => Array.isArray(item)).flat();
    const isAuthenticated = data.find(item => typeof item === 'object' && item.user)?.user === "authenticated";
    return { predictions, isAuthenticated };
  } catch (error) {
    console.error('Error fetching predictions:', error);
    return { predictions: [], isAuthenticated: false };
  }
}

async function deletePrediction(requestId) {
  try {
    await fetch('/del_user_prediction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_id: requestId })
    });
    closeModal();
    await loadPage();
  } catch (error) {
    console.error('Error deleting prediction:', error);
  }
}

function closeModal() {
  const modal = document.getElementById('modal');
  modal.style.display = 'none';
  window.removeEventListener('click', outsideClick);
}

function outsideClick(event) {
  const modal = document.getElementById('modal');
  if (event.target === modal) {
    closeModal();
  }
}

function showModal(predDataString, isAuth) {
  const pred = JSON.parse(decodeURIComponent(predDataString));
  const modal = document.getElementById('modal');
  const body = document.getElementById('modal-body');
  body.innerHTML = `
    <h3>Prediction #${pred.id}</h3>
    <table style="width: 100%; border-collapse: collapse;">
      <tr><td><strong>Type:</strong></td><td>${pred.type}</td></tr>
      <tr><td><strong>District:</strong></td><td>${pred.district}</td></tr>
      <tr><td><strong>Area:</strong></td><td>${pred.area} m²</td></tr>
      <tr><td><strong>Rooms:</strong></td><td>${pred.rooms}</td></tr>
      <tr><td><strong>Floor:</strong></td><td>${pred.floor}/${pred.floors}</td></tr>
      <tr><td><strong>Condition:</strong></td><td>${pred.cond}</td></tr>
      <tr><td><strong>Wall material:</strong></td><td>${pred.walls}</td></tr>
      <tr><td><strong>Price:</strong></td><td>${pred.price.toFixed(2)} $</td></tr>
      <tr><td><strong>Request date:</strong></td><td>${pred.request_timestamp.split(' ')[0]} ${pred.request_timestamp.split(' ')[1].split('.')[0]}</td></tr>
    </table>
  `;

  if (isAuth) {
    const delBtn = document.createElement('button');
    delBtn.innerText = 'Delete';
    delBtn.onclick = () => {
      const confirmModal = document.createElement("div");
      confirmModal.classList.add("close-modal-message");
      confirmModal.innerHTML = `
        <div class="modal-content">
            <h2>Are you sure you want to delete this prediction?</h2>
            <button class="confirm-delete">Yes</button>
            <button class="cancel-delete">No</button>
        </div>
      `;
      document.body.appendChild(confirmModal);
      confirmModal.querySelector('.confirm-delete').onclick = () => {
        deletePrediction(pred.request_id);
        confirmModal.remove();
      };
      confirmModal.querySelector('.cancel-delete').onclick = () => {
        confirmModal.remove();
      };
    };
    body.appendChild(delBtn);
  }

  window.addEventListener('click', outsideClick);
  modal.style.display = 'flex';
}

function renderChart(predictions) {
  const chartWrapper = document.getElementById('chart-wrapper');
  const oldChart = document.getElementById('chart');
  if (oldChart) oldChart.remove();
  const newChart = document.createElement('canvas');
  newChart.id = 'chart';
  chartWrapper.appendChild(newChart);

  const ctx = newChart.getContext('2d');

  const reversedPredictions = [...predictions].reverse();
  const labels = reversedPredictions.map((_, index) => `${index + 1}`);
  const prices = reversedPredictions.map(pred => pred.price);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Prediction Price ($)',
        data: prices,
        borderColor: '#7D3C98',
        fill: false,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: 'Price ($)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Requests'
          }
        }
      }
    }
  });
}

function formatDateTimeAndAgo(dateString) {
  const date = new Date(dateString);

  const options = {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };

  const formattedDate = date.toLocaleString('en-US', options);

  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  let agoText = '';
  if (diffYears > 0) {
    agoText = `${diffYears} year(s) ago`;
  } else if (diffMonths > 0) {
    agoText = `${diffMonths} month(s) ago`;
  } else if (diffDays > 0) {
    agoText = `${diffDays} day(s) ago`;
  } else if (diffHours > 0) {
    agoText = `${diffHours} hour(s) ago`;
  } else if (diffMin > 0) {
    agoText = `${diffMin} minute(s) ago`;
  } else {
    agoText = 'just now';
  }

  return `${formattedDate}<br>${agoText}`;
}

async function loadPage() {
  const user = await getUserData();
  const { predictions, isAuthenticated } = await getUserPredictions();

  const userDiv = document.getElementById('user');
  const predDiv = document.getElementById('predictions');

  if (user) {
    userDiv.innerHTML = `
      <div class="user-profile">
        <div class="user-image">
          <img src="${user.image}" alt="Avatar" />
        </div>
        <div class="user-info">
          <div class="user-name">
            <h2>${user.name}</h2>
          </div>
          <div class="user-details">
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>Joined:</strong> ${formatDateTimeAndAgo(user.time)}</p>
          </div>
        </div>
      </div>
    `;
  }

  predDiv.innerHTML = `
    <h3>My Predictions</h3>
    <div class="prediction-table-wrapper">
      <div class="prediction-list">
        <div class="prediction-header">
          <span>#</span><span>ID</span><span>Rooms</span><span>Floor</span><span>Price ($)</span><span></span>
        </div>
      </div>
    </div>
  `;

  const list = predDiv.querySelector('.prediction-list');
  list.innerHTML = list.querySelector('.prediction-header').outerHTML;
  const tableWrapper = predDiv.querySelector('.prediction-table-wrapper');
  tableWrapper.style.maxHeight = '300px';
  tableWrapper.style.overflowY = 'auto';

  predictions.forEach((pred, index) => {
    const row = document.createElement('div');
    row.className = 'prediction-row';
    row.id = `pred-${pred.request_id}`;

    const numberCell = document.createElement('span');
    numberCell.textContent = index + 1;
    const idCell = document.createElement('span');
    idCell.textContent = pred.id;
    const roomsCell = document.createElement('span');
    roomsCell.textContent = pred.rooms;
    const floorCell = document.createElement('span');
    floorCell.textContent = `${pred.floor}/${pred.floors}`;
    const priceCell = document.createElement('span');
    priceCell.textContent = pred.price.toFixed(2);

    const buttonCell = document.createElement('span');
    const button = document.createElement('button');
    button.textContent = 'Details';
    button.classList.add('details-button');
    button.onclick = () => showModal(encodeURIComponent(JSON.stringify(pred)), isAuthenticated);
    buttonCell.appendChild(button);

    row.appendChild(numberCell);
    row.appendChild(idCell);
    row.appendChild(roomsCell);
    row.appendChild(floorCell);
    row.appendChild(priceCell);
    row.appendChild(buttonCell);

    list.appendChild(row);
  });

  const predictionCount = document.createElement('p');
  predictionCount.innerHTML = `<strong>Total predictions:</strong> ${predictions.length}`;
  predictionCount.classList.add('prediction-count');
  predDiv.appendChild(predictionCount);

  if (predictions.length > 0) {
    renderChart(predictions);
  }
}

window.onload = loadPage;
