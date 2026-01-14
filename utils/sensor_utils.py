def format_light_level(lux):
    """Convert lux value to user-friendly light condition."""
    if lux is None:
        return "N/A"
    elif lux > 50000:
        return "Full Sun"
    elif lux > 10000:
        return "Bright"
    elif lux > 2000:
        return "Good"
    elif lux > 500:
        return "Dim"
    else:
        return "Dark"


def format_moisture(moisture):
    """Format soil moisture percentage."""
    return f"{moisture}%" if moisture is not None else "N/A"


def format_temperature(temp):
    """Format temperature with 1 decimal place."""
    return f"{temp:.1f}°C" if temp is not None else "N/A"


def get_sensor_status(readings):
    """Check if sensor has recent readings (used in app.py)."""
    return "Online" if readings and readings[-1].timestamp else "Offline"