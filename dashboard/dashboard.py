from flask import Flask, request, jsonify, render_template_string
import sqlite3
import time
import threading

app = Flask(__name__)
DB = "/opt/dashboard.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        type TEXT,
        status TEXT,
        last_seen REAL
    )""")
    conn.commit()
    conn.close()

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    conn = sqlite3.connect(DB)
    conn.execute("""INSERT INTO devices (device_id, type, status, last_seen)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(device_id) DO UPDATE SET
        type=excluded.type, status=excluded.status, last_seen=excluded.last_seen""",
        (data['device_id'], data['type'], data['status'], time.time()))
    conn.commit()
    conn.close()
    return jsonify({"result": "ok"})

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT device_id, type, status, last_seen FROM devices").fetchall()
    conn.close()
    now = time.time()
    devices = []
    for device_id, dtype, status, last_seen in rows:
        online = (now - last_seen) < 90
        devices.append({
            "id": device_id,
            "type": dtype,
            "online": online,
            "last_seen": time.strftime('%H:%M:%S', time.localtime(last_seen))
        })
    html = """
    <h1>Command Dashboard</h1>
    <table border=1 cellpadding=8>
    <tr><th>Device ID</th><th>Type</th><th>Status</th><th>Last Seen</th></tr>
    {% for d in devices %}
    <tr style="background-color:{{ 'lightgreen' if d.online else 'salmon' }}">
    <td>{{ d.id }}</td><td>{{ d.type }}</td>
    <td>{{ 'ONLINE' if d.online else 'OFFLINE' }}</td>
    <td>{{ d.last_seen }}</td>
    </tr>
    {% endfor %}
    </table>
    """
    return render_template_string(html, devices=devices)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')