from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database as db
import os

app = Flask(__name__, static_folder='.')
CORS(app)

db.init_db()

# ─── Serve frontend ───────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ─── Students ─────────────────────────────────────────────────
@app.route('/api/students', methods=['GET'])
def get_students():
    return jsonify(db.get_all_students())

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    required = ['name', 'seat', 'fees', 'shift', 'plan']
    if not all(data.get(k) for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    if db.seat_taken(data['seat']):
        return jsonify({'error': f"Seat {data['seat']} is already occupied"}), 400
    student = db.add_student(
        name=data['name'],
        seat=int(data['seat']),
        fees=float(data['fees']),
        phone=data.get('phone', ''),
        shift=data['shift'],
        plan=data['plan'],
        note=data.get('note', '')
    )
    return jsonify(student), 201

@app.route('/api/students/<int:sid>', methods=['PUT'])
def update_student(sid):
    data = request.json
    if 'seat' in data:
        if db.seat_taken(data['seat'], exclude_id=sid):
            return jsonify({'error': f"Seat {data['seat']} is already occupied"}), 400
    student = db.update_student(sid, data)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

@app.route('/api/students/<int:sid>', methods=['DELETE'])
def delete_student(sid):
    db.delete_student(sid)
    return jsonify({'success': True})

# ─── Attendance ────────────────────────────────────────────────
@app.route('/api/attendance/<date>', methods=['GET'])
def get_attendance(date):
    return jsonify(db.get_attendance(date))

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    rec = db.mark_attendance(data['student_id'], data['date'], data['status'])
    return jsonify(rec)

@app.route('/api/attendance/bulk', methods=['POST'])
def bulk_attendance():
    data = request.json
    db.bulk_mark_attendance(data['student_ids'], data['date'], data['status'])
    return jsonify({'success': True})

# ─── Fees ──────────────────────────────────────────────────────
@app.route('/api/fees', methods=['GET'])
def get_fees():
    month = request.args.get('month')
    return jsonify(db.get_fees(month))

@app.route('/api/fees', methods=['POST'])
def update_fee():
    data = request.json
    rec = db.update_fee(data['student_id'], data['month'], data['status'])
    return jsonify(rec)

# ─── Dashboard stats ───────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    date = request.args.get('date')
    month = request.args.get('month')
    return jsonify(db.get_stats(date, month))

# ─── Production ready ──────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"✅ Wisdom Library running at http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)