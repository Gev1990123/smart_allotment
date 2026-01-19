from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.probes import Probe
from extensions import db
from sensors import soil_moisture, light, temperature

probes_bp = Blueprint('probes', __name__, url_prefix='/probes')

@probes_bp.route('/')
def probe_dashboard():
    probes = Probe.query.order_by(Probe.sensor_type, Probe.name).all()
    return render_template('probes.html', probes=probes)

# Copy ALL your add_probe, toggle_probe, delete_probe routes exactly
@probes_bp.route('/add', methods=['POST'])
def add_probe():
    """Add new probe via web form"""
    name = request.form['name']
    sensor_type = request.form['sensor_type']
    channel = request.form['channel']
    
    probe = Probe(
        name=name,
        sensor_type=sensor_type,
        channel=channel,
        description=request.form.get('description', ''),
        active=True
    )
    
    # ALL SENSORS: Thresholds (ALERT bounds)
    min_val = request.form.get('min_value', '').strip()
    max_val = request.form.get('max_value', '').strip()
    if min_val: probe.min_value = float(min_val)  # All sensors
    if max_val: probe.max_value = float(max_val)  # All sensors

    # Soil-specific calibration
    if sensor_type == 'soil':
        dry_voltage = request.form.get('dry_voltage', '').strip()
        wet_voltage = request.form.get('wet_voltage', '').strip()
        if dry_voltage: probe.dry_voltage = float(dry_voltage)
        if wet_voltage: probe.wet_voltage = float(wet_voltage)

    db.session.add(probe)
    db.session.commit()
    flash(f'Probe "{name}" added!')

    if sensor_type == 'soil':
        soil_moisture.refresh_channels()
        flash('Soil sensors refreshed!')
    elif sensor_type == 'light':
        light.refresh_channels()
        flash('Light sensors refreshed!')
    elif sensor_type == 'temperature':
        temperature.refresh_channels()


    return redirect(url_for('probe_dashboard'))

@probes_bp.route('/<name>/toggle', methods=['POST'])
def toggle_probe(name):
    """Toggle probe active/inactive"""
    probe = Probe.query.filter_by(name=name).first_or_404()
    probe.active = not probe.active
    db.session.commit()

    status = 'activated' if probe.active else 'deactivated'
    flash(f'Probe "{name}" {status}!')

    if probe.sensor_type == 'soil':
        soil_moisture.refresh_channels()
    elif probe.sensor_type == 'light':
        light.refresh_channels()
    elif probe.sensor_type == 'temperature':
        temperature.refresh_channels()

    return redirect(url_for('probe_dashboard'))

@probes_bp.route('/<name>/delete', methods=['POST'])
def delete_probe(name):
    """Delete probe"""
    probe = Probe.query.filter_by(name=name).first_or_404()
    db.session.delete(probe)
    db.session.commit()
    flash(f'Probe "{name}" deleted!')
    return redirect(url_for('probe_dashboard'))