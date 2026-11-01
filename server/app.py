#!/usr/bin/env python3

from pathlib import Path

from flask import Blueprint, Flask, jsonify
from flask_migrate import Migrate

if __package__:
    from .models import db, Event, Session, Speaker
else:
    from models import db, Event, Session, Speaker

api = Blueprint('api', __name__)


@api.route('/events')
def get_events():
    return jsonify([
        {'id': event.id, 'name': event.name, 'location': event.location}
        for event in Event.query.all()
    ]), 200


@api.route('/events/<int:id>/sessions')
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


@api.route('/speakers')
def get_speakers():
    return jsonify([
        {'id': speaker.id, 'name': speaker.name}
        for speaker in Speaker.query.all()
    ]), 200


@api.route('/speakers/<int:id>')
def get_speaker(id):
    speaker = db.session.get(Speaker, id)
    if speaker is None:
        return jsonify({'error': 'Speaker not found'}), 404
    return jsonify({
        'id': speaker.id,
        'name': speaker.name,
        'bio_text': speaker.bio.bio_text if speaker.bio else 'No bio available',
    }), 200


@api.route('/sessions/<int:id>/speakers')
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


def create_app(config=None):
    """Configure each app before binding SQLAlchemy, including isolated test apps."""
    server_dir = Path(__file__).resolve().parent
    app = Flask(__name__, instance_path=str(server_dir / 'instance'))
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config is not None:
        app.config.update(config)
    app.json.compact = False

    db.init_app(app)
    Migrate(app, db, directory=str(server_dir / 'migrations'))
    app.register_blueprint(api)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(port=5555, debug=True)
