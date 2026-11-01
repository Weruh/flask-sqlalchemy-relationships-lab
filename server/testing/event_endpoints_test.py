from server.models import Bio, Event, Session, Speaker, db

def test_get_events(test_client):
    response = test_client.get("/events")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for event in data:
        assert "id" in event
        assert "name" in event
        assert "location" in event


def test_get_event_sessions_success(test_client):
    event = db.session.query(Event).first()
    response = test_client.get(f"/events/{event.id}/sessions")
    assert response.status_code == 200
    sessions = response.get_json()
    assert isinstance(sessions, list)
    for session in sessions:
        assert "id" in session
        assert "title" in session
        assert "start_time" in session


def test_get_event_sessions_not_found(test_client):
    response = test_client.get("/events/9999/sessions")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Event not found"}

