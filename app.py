from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'emergencies.db'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/emergencies', methods=['GET'])
def get_emergencies():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emergencies")
        emergencies = [{"id": row[0], "lat": row[1], "lon": row[2], "message": row[3]} for row in cursor.fetchall()]
    return jsonify(emergencies)

@app.route('/emergencies', methods=['POST'])
def add_emergency():
    data = request.json
    
    if not data or not all(data.get(k) for k in ["lat", "lon", "message"]):
        abort(400, description="Invalid input: lat, lon, and message are required.")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO emergencies (lat, lon, message) VALUES (?, ?, ?)", (data["lat"], data["lon"], data["message"]))
        conn.commit()
        new_id = cursor.lastrowid
    
    return jsonify({"id": new_id, "lat": data["lat"], "lon": data["lon"], "message": data["message"]}), 201

@app.route('/emergencies/<int:emergency_id>', methods=['DELETE'])
def delete_emergency(emergency_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emergencies WHERE id = ?", (emergency_id,))
        if cursor.rowcount == 0:
            abort(404, description="Emergency not found.")
        conn.commit()
    
    return jsonify({"message": "Emergency deleted"}), 200

@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    return jsonify({"error": error.description}), error.code

if __name__ == '__main__':
    app.run(debug=True)
