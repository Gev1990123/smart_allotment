
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from db import get_connection

app = FastAPI(title="Smart Allotment API")

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "details": str(e)})

# -----------------------------
# GET LATEST READING FOR DEVICE
# -----------------------------
@app.get("/latest/{device_id}")
def get_latest(device_id: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT *
            FROM sensor_data
            WHERE device_id = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (device_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return JSONResponse(status_code=404, content={"error": "No data found"})
        return row

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -----------------------------
# GET HISTORICAL DATA
# -----------------------------
@app.get("/history/{device_id}")
def get_history(device_id: str, hours: int = 24):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT *
            FROM sensor_data
            WHERE device_id = %s
              AND timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp ASC;
        """, (device_id, hours))

        rows = cur.fetchall()
        conn.close()
        return rows

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -----------------------------
# LIST ALL DEVICES
# -----------------------------
@app.get("/sensors")
def list_sensors():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT device_id FROM sensor_data;")
        rows = cur.fetchall()
        conn.close()
        return rows

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
