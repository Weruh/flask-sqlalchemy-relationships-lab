"""Regression coverage for database safety and relationship edge cases."""
from datetime import datetime
from unittest.mock import patch

import pytest
from flask_migrate import downgrade, upgrade
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from server.app import create_app
from server.models import Bio, Event, Session, Speaker, db, session_speakers
from server.seed import seed_database


def test_apps_use_independent_databases(tmp_path):
    persistent = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path / "app.db"}',
    })
    isolated = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with persistent.app_context():
        db.create_all()
        db.session.add(Event(name='Keep me', location='Nairobi'))
        db.session.commit()
    with isolated.app_context():
        db.create_all()
        assert Event.query.count() == 0
        db.drop_all()
    with persistent.app_context():
        assert Event.query.one().name == 'Keep me'
        db.session.remove()
        db.engine.dispose()


def test_deleting_event_removes_links_but_preserves_speakers(test_client):
    event = Event.query.one()
    speaker = Speaker.query.one()
    db.session.delete(event)
    db.session.commit()
    assert Session.query.count() == 0
    assert db.session.scalar(select(func.count()).select_from(session_speakers)) == 0
    assert Speaker.query.one() is speaker
    assert speaker.bio is not None


def test_deleting_speaker_removes_links_but_preserves_sessions(test_client):
    speaker = Speaker.query.one()
    session = Session.query.one()
    db.session.delete(speaker)
    db.session.commit()
    assert Bio.query.count() == 0
    assert db.session.scalar(select(func.count()).select_from(session_speakers)) == 0
    assert Session.query.one() is session
    assert session.speakers == []


def test_removing_owned_children_deletes_orphans(test_client):
    event = Event.query.one()
    speaker = Speaker.query.one()
    event.sessions.clear()
    speaker.bio = None
    db.session.commit()
    assert Session.query.count() == 0
    assert Bio.query.count() == 0


def test_database_enforces_one_bio_per_speaker(test_client):
    db.session.add(Bio(bio_text='Duplicate', speaker_id=Speaker.query.one().id))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
    assert Bio.query.count() == 1


def test_database_rejects_duplicate_session_speaker_links(test_client):
    session_id = Session.query.one().id
    speaker_id = Speaker.query.one().id
    with pytest.raises(IntegrityError):
        db.session.execute(session_speakers.insert().values(
            session_id=session_id, speaker_id=speaker_id,
        ))
        db.session.commit()
    db.session.rollback()


def test_session_payload_handles_missing_date_and_bio(test_client):
    session = Session.query.one()
    session.start_time = None
    speaker = Speaker(name='No biography')
    session.speakers.append(speaker)
    db.session.commit()
    sessions = test_client.get(f'/events/{session.event_id}/sessions').get_json()
    assert sessions == [{'id': session.id, 'title': session.title, 'start_time': None}]
    speakers = test_client.get(f'/sessions/{session.id}/speakers').get_json()
    assert {'id': speaker.id, 'name': speaker.name, 'bio_text': 'No bio available'} in speakers


def test_empty_collections_return_json_lists(test_client):
    event = Event(name='Empty event', location='Online')
    session = Session(title='No speakers', event=event)
    db.session.add(event)
    db.session.commit()
    assert test_client.get(f'/sessions/{session.id}/speakers').get_json() == []
    event.sessions.clear()
    db.session.commit()
    assert test_client.get(f'/events/{event.id}/sessions').get_json() == []


def test_seed_can_be_repeated(test_client):
    seed_database()
    seed_database()
    assert Event.query.count() == 2
    assert Session.query.count() == 3
    assert Speaker.query.count() == 3
    assert Bio.query.count() == 3
    assert db.session.scalar(select(func.count()).select_from(session_speakers)) == 4
    session = Session.query.filter_by(title='Intro to Machine Learning').one()
    assert {speaker.name for speaker in session.speakers} == {'Riley Chen', 'Jordan Brooks'}
    assert session.start_time == datetime(2023, 9, 15, 14)


def test_failed_seed_preserves_existing_data(test_client):
    event_id = Event.query.one().id
    with patch.object(db.session, 'commit', side_effect=RuntimeError('Simulated failure')):
        with pytest.raises(RuntimeError, match='Simulated failure'):
            seed_database()
    assert Event.query.one().id == event_id
    assert Event.query.one().name == 'Tech Conference'
    assert Session.query.count() == 1
    assert Speaker.query.count() == 1
    assert Bio.query.count() == 1
    assert db.session.scalar(select(func.count()).select_from(session_speakers)) == 1


def test_migrations_and_seed_on_fresh_database(tmp_path):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path / "migrated.db"}',
    })
    with app.app_context():
        upgrade()
        seed_database()
        client = app.test_client()
        assert len(client.get('/events').get_json()) == 2
        event = Event.query.filter_by(name='Tech Future Conference').one()
        assert len(client.get(f'/events/{event.id}/sessions').get_json()) == 2
        db.session.remove()
        downgrade(revision='base')
        upgrade()
        assert Event.query.count() == 0
        db.session.remove()
        db.engine.dispose()
