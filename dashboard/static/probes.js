// probes.js - Sensor management form logic
document.addEventListener('DOMContentLoaded', function() {
    const sensorTypeSelect = document.querySelector('[name="sensor_type"]');
    const soilCalibration = document.getElementById('soil-calibration');
    const tempLightRanges = document.getElementById('temp-light-ranges');
    
    if (sensorTypeSelect) {
        sensorTypeSelect.onchange = function() {
            const type = this.value;
            soilCalibration.style.display = type === 'soil' ? 'block' : 'none';
            tempLightRanges.style.display = type !== 'soil' ? 'block' : 'none';
        };
        
        // Trigger initial state
        sensorTypeSelect.onchange();
    }
});
