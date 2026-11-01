from server.models import Bio, Event, Session, Speaker, db

def test_get_speakers(test_client):
    response = test_client.get("/speakers")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for speaker in data:
        assert "id" in speaker
        assert "name" in speaker


def test_get_speaker_with_bio(test_client):
    speaker = db.session.query(Speaker).first()
    response = test_client.get(f"/speakers/{speaker.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert "name" in data
    assert "bio_text" in data


def test_get_speaker_without_bio(test_client):
    new_speaker = Speaker(name="Temporary Speaker")
    db.session.add(new_speaker)
    db.session.commit()

    response = test_client.get(f"/speakers/{new_speaker.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["bio_text"] == "No bio available"

    db.session.delete(new_speaker)
    db.session.commit()


def test_get_speaker_not_found(test_client):
    response = test_client.get("/speakers/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Speaker not found"}

