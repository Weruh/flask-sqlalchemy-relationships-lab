import pytest
from server.app import create_app, db
from server.models import Event, Session, Speaker, Bio
import datetime

@pytest.fixture(scope="function")
def test_client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()

        event = Event(name="Tech Conference", location="New York")
        db.session.add(event)
        db.session.commit()

        session = Session(
            title="Future of AI",
            start_time=datetime.datetime(2024, 6, 1, 9, 0),
            event=event
        )
        db.session.add(session)

        speaker = Speaker(name="Jane Doe")
        db.session.add(speaker)

        bio = Bio(bio_text="Expert in AI and ML.", speaker=speaker)
        db.session.add(bio)

        session.speakers.append(speaker)

        db.session.commit()

        try:
            yield app.test_client()
        finally:
            db.session.remove()
            db.drop_all()
