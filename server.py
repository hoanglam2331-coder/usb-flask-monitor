from flask import Flask, request, render_template, redirect
import sqlite3
import pandas as pd
from lan_scan import scan_lan

app = Flask(__name__)

# kết nối database
conn = sqlite3.connect("monitor.db", check_same_thread=False)
cur = conn.cursor()

# tạo bảng nếu chưa có
cur.execute("""
CREATE TABLE IF NOT EXISTS usb_events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    computer TEXT,
    ip TEXT,
    mac TEXT,
    device TEXT,
    manufacturer TEXT,
    size REAL,
    event TEXT
)
""")

conn.commit()


# trang chủ
@app.route("/")
def home():
    return redirect("/dashboard")


# API nhận dữ liệu từ agent
@app.route("/log", methods=["POST"])
def log():

    data = request.json

    print("Nhan du lieu:", data)

    cur.execute("""
    INSERT INTO usb_events
    (time, computer, ip, mac, device, manufacturer, size, event)
    VALUES (?,?,?,?,?,?,?,?)
    """, (
        data["time"],
        data["computer"],
        data["ip"],
        data["mac"],
        data["device"],
        data["manufacturer"],
        data["size"],
        data["event"]
    ))

    conn.commit()

    return "OK"


# dashboard
@app.route("/dashboard")
def dashboard():

    cur.execute("SELECT COUNT(*) FROM usb_events")
    events = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT computer) FROM usb_events")
    machines = cur.fetchone()[0]

    return render_template(
        "dashboard.html",
        events=events,
        machines=machines
    )


# trang sự kiện USB
@app.route("/events")
def events():

    cur.execute("""
    SELECT time, computer, ip, device, event
    FROM usb_events
    ORDER BY id DESC
    LIMIT 100
    """)

    rows = cur.fetchall()

    return render_template("events.html", rows=rows)


# bản đồ LAN
@app.route("/lanmap")
def lanmap():

    devices = scan_lan()

    return render_template("lanmap.html", devices=devices)


# xuất excel
@app.route("/export")
def export():

    df = pd.read_sql_query("SELECT * FROM usb_events", conn)

    df.to_excel("usb_report.xlsx", index=False)

    return "Da xuat file usb_report.xlsx"


# chạy server
if __name__ == "__main__":

    print("Server dang chay...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )