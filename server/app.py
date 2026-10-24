#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/events')
def get_events():
    return jsonify([
        {'id': event.id, 'name': event.name, 'location': event.location}
        for event in Event.query.all()
    ]), 200


@app.route('/events/<int:id>/sessions')
def get_event_sessions(id):
    event = db.session.get(Event, id)
    if event is None:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify([
        {
            'id': session.id,
            'title': session.title,
            'start_time': session.start_time.isoformat() if session.start_time else None,
        }
        for session in event.sessions
    ]), 200


@app.route('/speakers')
def get_speakers():
    return jsonify([
        {'id': speaker.id, 'name': speaker.name}
        for speaker in Speaker.query.all()
    ]), 200


@app.route('/speakers/<int:id>')
def get_speaker(id):
    speaker = db.session.get(Speaker, id)
    if speaker is None:
        return jsonify({'error': 'Speaker not found'}), 404
    return jsonify({
        'id': speaker.id,
        'name': speaker.name,
        'bio_text': speaker.bio.bio_text if speaker.bio else 'No bio available',
    }), 200


@app.route('/sessions/<int:id>/speakers')
def get_session_speakers(id):
    session = db.session.get(Session, id)
    if session is None:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify([
        {
            'id': speaker.id,
            'name': speaker.name,
            'bio_text': speaker.bio.bio_text if speaker.bio else 'No bio available',
        }
        for speaker in session.speakers
    ]), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
