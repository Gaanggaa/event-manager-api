from flask import Flask, request, jsonify
from models import db, Event, Attendee
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "🎉 Welcome to the Event Manager API!"





# ------------------ EVENTS ------------------



# GET all events
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "name": event.name,
            "location": event.location,
            "date": event.date.strftime("%Y-%m-%d")
        })
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
        return jsonify({"message": "Event created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    event = Event.query.get_or_404(id)
    data = request.get_json()
    event.name = data.get('name', event.name)
    event.location = data.get('location', event.location)
    event.date = data.get('date', event.date)
    db.session.commit()
    return jsonify({'message': 'Event updated successfully'})

@app.route('/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'})

# ------------------ ATTENDEES ------------------

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
        return jsonify({"message": "Attendee created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/attendees', methods=['GET'])
def get_attendees():
    event_id = request.args.get('event_id')
    if event_id:
        attendees = Attendee.query.filter_by(event_id=event_id).all()
    else:
        attendees = Attendee.query.all()
    result = []
    for attendee in attendees:
        result.append({
            "id": attendee.id,
            "name": attendee.name,
            "email": attendee.email,
            "event_id": attendee.event_id
        })
    return jsonify(result)
@app.route('/attendees/<int:id>', methods=['PUT'])
def update_attendee(id):
    data = request.get_json()
    attendee = Attendee.query.get_or_404(id)
    attendee.name = data.get('name', attendee.name)
    attendee.email = data.get('email', attendee.email)
    attendee.event_id = data.get('event_id', attendee.event_id)
    db.session.commit()
    return jsonify({"message": "Attendee updated successfully"})

@app.route('/attendees/<int:id>', methods=['DELETE'])
def delete_attendee(id):
    attendee = Attendee.query.get_or_404(id)
    db.session.delete(attendee)
    db.session.commit()
    return jsonify({"message": "Attendee deleted successfully"})
    
if __name__ == '__main__':
    app.run(debug=True)
