let soilChart, tempChart, lightChart;

async function updateCharts() {
    try {
        const res = await fetch('/api/readings');
        const data = await res.json();
        const now = new Date().toLocaleTimeString();

        function updateChart(chart, value) {
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(value);
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            chart.update();
        }

        if (!soilChart) {
            const ctxSoil = document.getElementById('soilChart').getContext('2d');
            soilChart = new Chart(ctxSoil, {
                type: 'line',
                data: { labels:[now], datasets:[{label:'Soil Moisture', data:[data.soil_moisture], borderColor:'green', fill:false}] },
                options:{scales:{y:{min:0,max:100}}}
            });

            const ctxTemp = document.getElementById('tempChart').getContext('2d');
            tempChart = new Chart(ctxTemp, {
                type: 'line',
                data: { labels:[now], datasets:[{label:'Temperature', data:[data.temperature], borderColor:'red', fill:false}] },
                options:{scales:{y:{min:0,max:50}}}
            });

            const ctxLight = document.getElementById('lightChart').getContext('2d');
            lightChart = new Chart(ctxLight, {
                type: 'line',
                data: { labels:[now], datasets:[{label:'Light', data:[data.light], borderColor:'orange', fill:false}] },
                options:{scales:{y:{min:0,max:100}}}
            });
        } else {
            updateChart(soilChart, data.soil_moisture);
            updateChart(tempChart, data.temperature);
            updateChart(lightChart, data.light);
        }

        // Update sensor status indicators
        document.getElementById('soil-status').textContent = data.soil_status;
        document.getElementById('temp-status').textContent = data.temp_status;
        document.getElementById('light-status').textContent = data.light_status;

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

// Run updates every 5 seconds
setInterval(() => {
    updateCharts();
    updateAlerts();
}, 5000);

window.onload = () => {
    updateCharts();
    updateAlerts();
};