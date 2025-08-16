# app.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from models import db, Event, Attendee, User
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__) 


app.secret_key = os.environ.get("SECRET_KEY", "default-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///database.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "🎉 Welcome to the Event Manager API!"

# ---------- AUTH ----------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return jsonify({"message": "Login successful", "is_admin": user.is_admin}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@app.route('/whoami', methods=['GET'])
def whoami():
    if 'user_id' in session:
        return jsonify({
            "username": session['username'],
            "is_admin": session['is_admin']
        }), 200
    return jsonify({"error": "Not logged in"}), 401

# ---------- EVENTS ----------
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    result = [{
        "id": e.id,
        "name": e.name,
        "location": e.location,
        "date": e.date.strftime("%Y-%m-%d")
    } for e in events]
    return jsonify(result)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    try:
        new_event = Event(
            name=data['name'],
            location=data['location'],
            date=datetime.strptime(data['date'], "%Y-%m-%d").date()
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({"message": "Event created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'})

# ---------- ATTENDEES ----------
@app.route('/attendees', methods=['GET'])
def get_attendees():
    event_id = request.args.get('event_id')
    attendees = Attendee.query.filter_by(event_id=event_id).all() if event_id else Attendee.query.all()
    result = [{
        "id": a.id,
        "name": a.name,
        "email": a.email,
        "event_id": a.event_id
    } for a in attendees]
    return jsonify(result)

@app.route('/attendees', methods=['POST'])
def create_attendee():
    data = request.get_json()
    try:
        new_attendee = Attendee(
            name=data['name'],
            email=data['email'],
            event_id=data['event_id']
        )
        db.session.add(new_attendee)
        db.session.commit()
        return jsonify({"message": "Attendee added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/attendees/<int:id>', methods=['DELETE'])
def delete_attendee(id):
    attendee = Attendee.query.get_or_404(id)
    db.session.delete(attendee)
    db.session.commit()
    return jsonify({'message': 'Attendee removed'})

if __name__ == '__main__':
    app.run(debug=True)

