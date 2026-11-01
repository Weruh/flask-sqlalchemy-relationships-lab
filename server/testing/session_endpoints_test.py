from server.models import Bio, Event, Session, Speaker, db

def test_get_session_speakers_success(test_client):
    session = db.session.query(Session).first()
    response = test_client.get(f"/sessions/{session.id}/speakers")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for speaker in data:
        assert "id" in speaker
        assert "name" in speaker
        assert "bio_text" in speaker


def test_get_session_speakers_not_found(test_client):
    response = test_client.get("/sessions/9999/speakers")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Session not found"}

