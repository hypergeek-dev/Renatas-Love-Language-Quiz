from datetime import timedelta

from app.cleanup import delete_expired_sessions
from app.database import SessionLocal
from app.models import QuizAnswer, QuizSession, utcnow


def create_session(client):
    response = client.post("/api/session", json={})
    assert response.status_code == 200
    return response.json()


def test_session_creation(client):
    session = create_session(client)
    assert session["current_question"] == 1
    assert session["answered_count"] == 0
    assert session["total_questions"] == 30
    assert "dimension" not in str(session["question"])
    assert set(session["question"]["choices"].keys()) == {"A", "B"}


def test_answering_and_editing_existing_answer(client):
    session = create_session(client)
    sid = session["id"]
    first = client.post(f"/api/session/{sid}/answer", json={"question_id": 1, "selected_answer": "A"})
    assert first.status_code == 200
    assert first.json()["current_question"] == 2

    back = client.post(f"/api/session/{sid}/back")
    assert back.status_code == 200
    assert back.json()["current_question"] == 1

    edited = client.post(f"/api/session/{sid}/answer", json={"question_id": 1, "selected_answer": "B"})
    assert edited.status_code == 200
    assert edited.json()["answers"]["1"] == "B"
    assert edited.json()["answered_count"] == 1

    with SessionLocal() as db:
        assert db.query(QuizAnswer).filter(QuizAnswer.session_id == sid, QuizAnswer.question_id == 1).count() == 1


def test_duplicate_answer_prevention(client):
    session = create_session(client)
    sid = session["id"]
    assert client.post(f"/api/session/{sid}/answer", json={"question_id": 1, "selected_answer": "A"}).status_code == 200
    stale = client.post(f"/api/session/{sid}/answer", json={"question_id": 1, "selected_answer": "B"})
    assert stale.status_code == 409


def test_c_answer_is_rejected(client):
    session = create_session(client)
    response = client.post(
        f"/api/session/{session['id']}/answer",
        json={"question_id": 1, "selected_answer": "C"},
    )
    assert response.status_code == 422


def test_session_reset(client):
    session = create_session(client)
    sid = session["id"]
    client.post(f"/api/session/{sid}/answer", json={"question_id": 1, "selected_answer": "A"})
    reset = client.post(f"/api/session/{sid}/reset")
    assert reset.status_code == 200
    assert reset.json()["current_question"] == 1
    assert reset.json()["answered_count"] == 0


def test_refresh_new_session_behavior_deletes_previous(client):
    old = create_session(client)
    new_response = client.post("/api/session", json={"previous_session_id": old["id"]})
    assert new_response.status_code == 200
    assert new_response.json()["id"] != old["id"]
    assert client.get(f"/api/session/{old['id']}").status_code == 404


def test_result_after_complete_quiz(client):
    session = create_session(client)
    sid = session["id"]
    for question_id in range(1, 31):
        assert client.post(
            f"/api/session/{sid}/answer",
            json={"question_id": question_id, "selected_answer": "A"},
        ).status_code == 200
    result = client.get(f"/api/session/{sid}/result")
    assert result.status_code == 200
    assert result.json()["percent_total"] == 100


def test_expired_session_deletion():
    with SessionLocal() as db:
        stale = QuizSession(id="stale", updated_at=utcnow() - timedelta(hours=2))
        fresh = QuizSession(id="fresh", updated_at=utcnow())
        db.add_all([stale, fresh])
        db.commit()
        assert delete_expired_sessions(db) == 1
        assert db.get(QuizSession, "stale") is None
        assert db.get(QuizSession, "fresh") is not None
