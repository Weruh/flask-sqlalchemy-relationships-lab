import datetime
from models import *

def test_create_event(test_client):
    event = Event(name="Tech Conference", location="New York")
    db.session.add(event)
    db.session.commit()

    assert event.id is not None
    assert event.name == "Tech Conference"
    assert event.location == "New York"

def test_create_session(test_client):
    event = Event(name="Startup Pitch", location="San Francisco")
    db.session.add(event)
    db.session.commit()

    session = Session(title="AI in 2024", start_time=datetime.datetime(2024, 6, 1, 10, 0), event=event)
    db.session.add(session)
    db.session.commit()

    assert session.id is not None
    assert session.event_id == event.id
    assert session.event == event

def test_create_speaker_and_bio(test_client):
    speaker = Speaker(name="Jane Doe")
    bio = Bio(bio_text="An expert in AI and ML.", speaker=speaker)

    db.session.add(speaker)
    db.session.add(bio)
    db.session.commit()

    assert speaker.id is not None
    assert speaker.bio is not None
    assert speaker.bio.bio_text == "An expert in AI and ML."
    assert bio.speaker_id == speaker.id

def test_speaker_session_relationship(test_client):
    event = Event(name="Cloud Summit", location="Austin")
    db.session.add(event)
    db.session.commit()

    session = Session(title="Serverless Architectures", start_time=datetime.datetime(2024, 7, 1, 9, 0), event=event)
    speaker = Speaker(name="John Smith")
    db.session.add_all([session, speaker])
    db.session.commit()

    session.speakers.append(speaker)
    db.session.commit()

    assert speaker.sessions[0].title == "Serverless Architectures"
    assert session.speakers[0].name == "John Smith"


def test_deleting_event_cascades_to_sessions(test_client):
    event = Event(name="Delete Me", location="Nairobi")
    session = Session(title="Temporary Session", event=event)
    db.session.add(event)
    db.session.commit()
    session_id = session.id

    db.session.delete(event)
    db.session.commit()

    assert db.session.get(Session, session_id) is None


def test_deleting_speaker_cascades_to_bio(test_client):
    speaker = Speaker(name="Temporary Speaker")
    bio = Bio(bio_text="Temporary biography", speaker=speaker)
    db.session.add(speaker)
    db.session.commit()
    bio_id = bio.id

    db.session.delete(speaker)
    db.session.commit()

    assert db.session.get(Bio, bio_id) is None
