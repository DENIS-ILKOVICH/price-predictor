let loadedRecords = 0;
let totalRecords = 0;
const recordsPerPage = 100;

function showLoading() {
    document.body.classList.add("loading");
    document.getElementById('loadingAnimation').style.display = 'flex';
}

function hideLoading() {
    document.body.classList.remove("loading");
    document.getElementById('loadingAnimation').style.display = 'none';
}

function searchData() {
    const searchValue = document.getElementById('searchInput').value.trim();

    if (!searchValue) {
        toastr.options = {
            "closeButton": true,
            "preventDuplicates": true,
            "hideEasing": "linear"
        };
        toastr.error('Please check the entered values and try again.', 'Error!');
        return;
    }

    showLoading();

    fetch('/sort_dataframe', {
        method: 'POST',
        body: new URLSearchParams({
            datatype: 'search',
            search_value: searchValue
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.error) {
            toastr.error('Information not found', 'Error!');
            return;
        }

        renderTable(data);
        loadedRecords = data.length;
        document.getElementById('totalRecordsLabel').textContent = `Total records: ${data.length}`;
        document.getElementById('loadMoreButton').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
    });
}

function filterData(filterType) {
    showLoading();

    fetch('/sort_dataframe', {
        method: 'POST',
        body: new URLSearchParams({
            datatype: 'filter',
            filter_value: filterType
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.error) {
            alert(data.error);
            return;
        }

        renderTable(data);
        loadedRecords = data.length;
        document.getElementById('totalRecordsLabel').textContent = `Total records: ${data.length}`;
        document.getElementById('loadMoreButton').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
    });
}

function getData(allData = false) {
    showLoading();

    fetch('/sort_dataframe', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        totalRecords = data.totalRecords || data.length;
        if (allData) {
            renderTable(data);
            loadedRecords = totalRecords;
            document.getElementById('totalRecordsLabel').textContent = `Total records: ${totalRecords}`;
            document.getElementById('loadMoreButton').style.display = 'none';
        } else {
            renderTable(data.slice(0, recordsPerPage));
            loadedRecords = recordsPerPage;
            document.getElementById('totalRecordsLabel').textContent = `Total records: ${totalRecords}`;

            if (totalRecords > recordsPerPage) {
                document.getElementById('loadMoreButton').style.display = 'inline-block';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
    });
}

function loadMoreData() {
    showLoading();

    fetch('/sort_dataframe', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const nextRecords = data.slice(loadedRecords, loadedRecords + recordsPerPage);
        renderTable(nextRecords, true);
        loadedRecords += nextRecords.length;

        document.getElementById('totalRecordsLabel').textContent = `Total records: ${totalRecords}`;

        if (loadedRecords >= totalRecords) {
            document.getElementById('loadMoreButton').style.display = 'none';
        }

        hideLoading();
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
    });
}

function confirmGetAllData() {
    const userConfirmed = confirm("Are you sure you want to load all data? This may take some time and could affect your device's performance.");
    if (userConfirmed) {
        getData(true);
    }
}

function renderTable(data, append = false) {
    const tableBody = document.getElementById('tableBody');
    if (!append) {
        tableBody.innerHTML = '';
    }

    if (Array.isArray(data) && data.length > 0) {
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-id', row.id);

            const id = document.createElement('td');
            id.textContent = row.id || '—';
            tr.appendChild(id);

            const price = document.createElement('td');
            price.textContent = row.price || '—';
            tr.appendChild(price);

            const district = document.createElement('td');
            district.textContent = row.district || '—';
            tr.appendChild(district);

            const rooms = document.createElement('td');
            rooms.textContent = row.rooms || '—';
            tr.appendChild(rooms);

            const floor = document.createElement('td');
            floor.textContent = row.floor || '—';
            tr.appendChild(floor);

            const floors = document.createElement('td');
            floors.textContent = row.floors || '—';
            tr.appendChild(floors);

            const area = document.createElement('td');
            area.textContent = row.area || '—';
            tr.appendChild(area);

            const type = document.createElement('td');
            type.textContent = row.type || '—';
            tr.appendChild(type);

            const cond = document.createElement('td');
            cond.textContent = row.cond || '—';
            tr.appendChild(cond);

            const walls = document.createElement('td');
            walls.textContent = row.walls || '—';
            tr.appendChild(walls);

            const desc = document.createElement('td');
            desc.textContent = row.desc || '—';
            tr.appendChild(desc);

            tableBody.appendChild(tr);
        });

        document.getElementById('totalRecordsLabel').textContent = `Total records: ${totalRecords}`;
    } else {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 11;
        td.textContent = 'No data found';
        tr.appendChild(td);
        tableBody.appendChild(tr);

        document.getElementById('totalRecordsLabel').textContent = `Total records: 0`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    getData();

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                searchData();
            } else if (event.key === 'Escape') {
                event.preventDefault();
                searchInput.value = '';
                getData();
            }
        });
    }
});
