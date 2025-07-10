document.addEventListener('DOMContentLoaded', () => {
    getStatistics();
});

function getStatistics() {
    fetch('/get_statistics', { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        renderStatistics(data);
        renderTypeDistribution(data);
        renderCharts(data);
        renderRoomsDistribution(data);
        renderRoomsDistributionChart(data);
        renderSummaryStats(data);
        setTimeout(animateStatistics, 1000);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

let chartInstance = null;

async function renderChartData() {
    const chartElement = document.getElementById('priceAreaChart');

    if (chartInstance) {
        chartInstance.destroy();
        chartElement.style.opacity = 0;
        chartInstance = null;
        return;
    }

    try {
        const response = await fetch('/sort_dataframe');
        const data = await response.json();

        const prices = data.map(item => item.price);
        const areas = data.map(item => item.area);

        const ctx = chartElement.getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Apartments',
                    data: areas.map((area, index) => ({
                        x: area,
                        y: prices[index],
                        r: 5
                    })),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Area (m²)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price (USD)'
                        }
                    }
                }
            }
        });

        chartElement.style.opacity = 1;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function renderStatistics(data) {
    const top5ExpensiveContainer = document.getElementById('top5-expensive');
    top5ExpensiveContainer.innerHTML = '';

    if (data.top_expensive?.length > 0) {
        data.top_expensive.forEach((item, index) => {
            const card = document.createElement('div');
            card.classList.add('card', 'p-3', 'shadow-sm');
            card.style.animationDelay = `${index * 0.2}s`;

            card.innerHTML = `
                <div class="number-circle">${index + 1}</div>
                <h3 class="h5">Apartment ${item.id}</h3>
                <p><strong>Price:</strong> ${item.price.toFixed(2)} $</p>
                <p><strong>District:</strong> ${item.district}</p>
                <p><strong>Area:</strong> ${item.area} m²</p>
                <p><strong>Rooms:</strong> ${item.rooms}</p>
                <p><strong>Floor:</strong> ${item.floor}/${item.floors}</p>
            `;
            top5ExpensiveContainer.appendChild(card);
        });
    } else {
        top5ExpensiveContainer.innerHTML = '<p>No data found</p>';
    }

    const top5CheapContainer = document.getElementById('top5-cheap');
    top5CheapContainer.innerHTML = '';

    if (data.top_cheap?.length > 0) {
        data.top_cheap.forEach((item, index) => {
            const card = document.createElement('div');
            card.classList.add('card', 'p-3', 'shadow-sm');
            card.style.animationDelay = `${index * 0.2}s`;

            card.innerHTML = `
                <div class="number-circle">${index + 1}</div>
                <h3 class="h5">Apartment ${item.id}</h3>
                <p><strong>Price:</strong> ${item.price.toFixed(2)} $</p>
                <p><strong>District:</strong> ${item.district}</p>
                <p><strong>Area:</strong> ${item.area} m²</p>
                <p><strong>Rooms:</strong> ${item.rooms}</p>
                <p><strong>Floor:</strong> ${item.floor}/${item.floors}</p>
            `;
            top5CheapContainer.appendChild(card);
        });
    } else {
        top5CheapContainer.innerHTML = '<p>No data found</p>';
    }

    const avgPriceDistrictContainer = document.getElementById('avg-price-district');
    avgPriceDistrictContainer.innerHTML = '';
    avgPriceDistrictContainer.classList.remove('visible');

    if (data.avg_price_district) {
        for (const district in data.avg_price_district) {
            const item = document.createElement('div');
            item.classList.add('numeric-item');
            item.innerHTML = `
                <h4>${district}</h4>
                <p class="price-value">${data.avg_price_district[district].toFixed(2)} $</p>
            `;
            avgPriceDistrictContainer.appendChild(item);
        }
    } else {
        avgPriceDistrictContainer.innerHTML = '<p>No data found</p>';
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                avgPriceDistrictContainer.classList.add('visible');
                document.querySelectorAll('.numeric-item').forEach((el, index) => {
                    setTimeout(() => el.classList.add('visible'), index * 200);
                });
                observer.disconnect();
            }
        });
    }, { threshold: 0.2 });

    observer.observe(avgPriceDistrictContainer);
}

function renderTypeDistribution(data) {
    const container = document.getElementById('type-distribution');
    container.innerHTML = '';

    if (data.type_distribution) {
        for (const type in data.type_distribution) {
            const item = document.createElement('div');
            item.classList.add('numeric-item');
            item.innerHTML = `
                <h4>${type}</h4>
                <p class="type-value">${data.type_distribution[type]}</p>
            `;
            container.appendChild(item);
        }
    } else {
        container.innerHTML = '<p>No data found</p>';
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    observer.observe(container);
}

function animateStatistics() {
    document.querySelectorAll('.price-value').forEach(el => {
        let target = parseFloat(el.textContent.replace('$', '').trim());
        if (isNaN(target)) return;

        let start = 0;
        let step = 10;
        let steps = 100;
        let increment = target / steps;
        let decimals = (target % 1 !== 0) ? 2 : 0;

        const interval = setInterval(() => {
            start += increment;
            if (start >= target) {
                el.textContent = `${target.toFixed(decimals)} $`;
                clearInterval(interval);
            } else {
                el.textContent = `${start.toFixed(decimals)} $`;
            }
        }, step);
    });

    document.querySelectorAll('.type-value').forEach(el => {
        let target = parseInt(el.textContent.trim());
        if (isNaN(target)) return;

        let start = 0;
        let step = 10;
        let increment = target / (1000 / step);

        const interval = setInterval(() => {
            start += increment;
            if (start >= target) {
                el.textContent = target;
                clearInterval(interval);
            } else {
                el.textContent = Math.round(start);
            }
        }, step);
    });
}

function renderRoomsDistribution(data) {
    const container = document.getElementById('rooms-distribution');
    container.innerHTML = '';

    if (data.rooms_distribution) {
        for (const rooms in data.rooms_distribution) {
            const item = document.createElement('div');
            item.classList.add('numeric-item');
            item.innerHTML = `
                <h4>Rooms: ${rooms}</h4>
                <p class="rooms-value">${data.rooms_distribution[rooms]}</p>
            `;
            container.appendChild(item);
        }
    } else {
        container.innerHTML = '<p>No data found</p>';
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    observer.observe(container);
}

function renderRoomsDistributionChart(data) {
    const chartElem = document.getElementById('rooms-distribution-chart');
    if (chartElem && data.rooms_distribution) {
        const ctx = chartElem.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(data.rooms_distribution),
                datasets: [{
                    label: 'Number of apartments by rooms',
                    data: Object.values(data.rooms_distribution),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Rooms'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of apartments'
                        }
                    }
                }
            }
        });
    }
}

function renderSummaryStats(data) {
    const container = document.getElementById('summary-stats');
    container.innerHTML = '';

    if (data.summary_stats) {
        for (const category in data.summary_stats) {
            const stats = data.summary_stats[category];
            const card = document.createElement('div');
            card.classList.add('stat-card');
            card.innerHTML = `
                <h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>
                <p><strong>Min:</strong> ${stats.min}</p>
                <p><strong>Max:</strong> ${stats.max}</p>
                <p><strong>Mean:</strong> ${stats.mean.toFixed(2)}</p>
            `;
            container.appendChild(card);
        }
    } else {
        container.innerHTML = '<p>No data found</p>';
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
    });
}

function renderCharts(data) {
    const avgPriceChart = document.getElementById('avg-price-chart');
    if (avgPriceChart && data.avg_price_district) {
        const ctx = avgPriceChart.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data.avg_price_district),
                datasets: [{
                    label: 'Average Price ($)',
                    data: Object.values(data.avg_price_district),
                    backgroundColor: 'rgba(125, 60, 152, 0.5)',
                    borderColor: '#7D3C98',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    const typeChart = document.getElementById('type-distribution-chart');
    if (typeChart && data.type_distribution) {
        const ctx = typeChart.getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(data.type_distribution),
                datasets: [{
                    data: Object.values(data.type_distribution),
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0', '#9966ff']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}
