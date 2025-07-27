from flask import Flask, request, jsonify
from models import db, Event, Attendee

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

@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([
        {'id': e.id, 'name': e.name, 'location': e.location, 'date': e.date}
        for e in events
    ])

@app.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    event = Event.query.get_or_404(id)
    return jsonify({
        'id': event.id,
        'name': event.name,
        'location': event.location,
        'date': event.date
    })

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    new_event = Event(name=data['name'], location=data['location'], date=data['date'])
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event created successfully'}), 201

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

@app.route('/events/<int:event_id>/attendees', methods=['POST'])
def add_attendee(event_id):
    data = request.get_json()
    new_attendee = Attendee(name=data['name'], email=data['email'], event_id=event_id)
    db.session.add(new_attendee)
    db.session.commit()
    return jsonify({'message': 'Attendee registered'}), 201

@app.route('/events/<int:event_id>/attendees', methods=['GET'])
def get_attendees(event_id):
    attendees = Attendee.query.filter_by(event_id=event_id).all()
    return jsonify([
        {'id': a.id, 'name': a.name, 'email': a.email}
        for a in attendees
    ])

@app.route('/attendees/<int:id>', methods=['DELETE'])
def delete_attendee(id):
    attendee = Attendee.query.get_or_404(id)
    db.session.delete(attendee)
    db.session.commit()
    return jsonify({'message': 'Attendee deleted'})
    
if __name__ == '__main__':
    app.run(debug=True)
