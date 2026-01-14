let soilChart, tempChart, lightChart;

// Update sensor charts
async function updateCharts() {
    try {
        const res = await fetch('/api/readings');
        const data = await res.json();

        function initChart(id, label, color, values, labels, maxY) {
            const ctx = document.getElementById(id).getContext('2d');
            return new Chart(ctx, {
                type: 'line',
                data: { labels: labels, datasets: [{ label: label, data: values, borderColor: color, fill: false }] },
                options: { scales: { y: { min: 0, max: maxY } } }
            });
        }

        if (!soilChart) {
            soilChart = initChart('soilChart', 'Soil Moisture', 'green', data.soil_moisture, data.soil_labels, 100);
            tempChart = initChart('tempChart', 'Temperature', 'red', data.temperature, data.temp_labels, 50);
            lightChart = initChart('lightChart', 'Light', 'orange', data.light, data.light_labels, 30000);
        } else {
            function updateChart(chart, values, labels) {
                chart.data.labels = labels;
                chart.data.datasets[0].data = values;
                chart.update();
            }
            updateChart(soilChart, data.soil_moisture, data.soil_labels);
            updateChart(tempChart, data.temperature, data.temp_labels);
            updateChart(lightChart, data.light, data.light_labels);
        }

        // Update sensor status indicators
        updateSensorStatus(data);

    } catch (err) {
        console.error('Error fetching readings:', err);
    }
}

// ----- Alerts live update -----
async function updateAlerts() {
    try {
        const res = await fetch('/alerts');
        const alerts = await res.json();

        const tbody = document.querySelector('#alerts-table tbody');
        tbody.innerHTML = ''; // Clear previous rows

        alerts.slice(-10).forEach(alert => {  // Display only last 10 alerts
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${alert.time}</td>
                <td>${alert.type}</td>
                <td>${alert.sensor}</td>
                <td>${alert.value}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error('Error fetching alerts:', err);
    }
}

// ----- Sensor status update -----
function updateSensorStatus(data) {
    const soilEl = document.getElementById('soil-status');
    const tempEl = document.getElementById('temp-status');
    const lightEl = document.getElementById('light-status');

    soilEl.textContent = data.soil_status;
    tempEl.textContent = data.temp_status;
    lightEl.textContent = data.light_status;

    soilEl.className = data.soil_status.toLowerCase();    // "online" or "offline"
    tempEl.className = data.temp_status.toLowerCase();
    lightEl.className = data.light_status.toLowerCase();

    // Current Level row
    document.getElementById('soil-level').textContent = data.soil_current || 'N/A';
    document.getElementById('temp-level').textContent = data.temp_current || 'N/A';
    document.getElementById('light-level').textContent = data.light_current || 'N/A';

}

// Run updates every 5 seconds
setInterval(() => {
    updateCharts();
    updateAlerts();
}, 5000);

// Initial load
window.onload = () => {
    updateCharts();
    updateAlerts();
};