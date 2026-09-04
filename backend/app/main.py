from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .cleanup import delete_expired_sessions
from .database import Base, engine, get_db
from .models import QuizAnswer, QuizSession
from .questions import QUESTION_BANK, get_question, public_question, validate_question_bank
from .schemas import AnswerRequest, CreateSessionRequest, SessionResponse
from .scoring import build_result

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Renata's Love Language Quiz API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session_or_404(db: Session, session_id: str) -> QuizSession:
    session = db.get(QuizSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    return session


def answers_map(session: QuizSession) -> dict[int, str]:
    return {answer.question_id: answer.selected_answer for answer in session.answers}


def session_payload(session: QuizSession) -> SessionResponse:
    answered = answers_map(session)
    next_question = None if session.completed else public_question(get_question(session.current_question))
    return SessionResponse(
        id=session.id,
        current_question=session.current_question,
        completed=session.completed,
        answered_count=len(answered),
        total_questions=len(QUESTION_BANK),
        question=next_question,
        answers=answered,
    )


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/questions/validation")
def question_validation() -> dict:
    return validate_question_bank()


@app.post("/api/session", response_model=SessionResponse)
def create_session(payload: CreateSessionRequest | None = None, db: Session = Depends(get_db)) -> SessionResponse:
    delete_expired_sessions(db)
    if payload and payload.previous_session_id:
        previous = db.get(QuizSession, payload.previous_session_id)
        if previous:
            db.delete(previous)
    session = QuizSession(id=str(uuid4()), current_question=1, completed=False)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session_payload(session)


@app.get("/api/session/{session_id}", response_model=SessionResponse)
def read_session(session_id: str, db: Session = Depends(get_db)) -> SessionResponse:
    session = get_session_or_404(db, session_id)
    return session_payload(session)


@app.post("/api/session/{session_id}/answer", response_model=SessionResponse)
def answer_question(session_id: str, payload: AnswerRequest, db: Session = Depends(get_db)) -> SessionResponse:
    session = get_session_or_404(db, session_id)
    if payload.question_id != session.current_question:
        raise HTTPException(status_code=409, detail="Answer must match the current question")
    existing = (
        db.query(QuizAnswer)
        .filter(QuizAnswer.session_id == session.id, QuizAnswer.question_id == payload.question_id)
        .one_or_none()
    )
    if existing:
        existing.selected_answer = payload.selected_answer
    else:
        db.add(QuizAnswer(session_id=session.id, question_id=payload.question_id, selected_answer=payload.selected_answer))
    if payload.question_id == len(QUESTION_BANK):
        session.completed = True
        session.current_question = len(QUESTION_BANK)
    else:
        session.current_question = payload.question_id + 1
        session.completed = False
    db.commit()
    db.refresh(session)
    return session_payload(session)


@app.post("/api/session/{session_id}/back", response_model=SessionResponse)
def back(session_id: str, db: Session = Depends(get_db)) -> SessionResponse:
    session = get_session_or_404(db, session_id)
    if session.completed:
        session.completed = False
    session.current_question = max(1, session.current_question - 1)
    db.commit()
    db.refresh(session)
    return session_payload(session)


@app.post("/api/session/{session_id}/reset", response_model=SessionResponse)
def reset(session_id: str, db: Session = Depends(get_db)) -> SessionResponse:
    session = get_session_or_404(db, session_id)
    for answer in list(session.answers):
        db.delete(answer)
    session.current_question = 1
    session.completed = False
    db.commit()
    db.refresh(session)
    return session_payload(session)


@app.get("/api/session/{session_id}/result")
def result(session_id: str, db: Session = Depends(get_db)) -> dict:
    session = get_session_or_404(db, session_id)
    answers = answers_map(session)
    if len(answers) != len(QUESTION_BANK):
        raise HTTPException(status_code=409, detail="Quiz is not complete")
    session.completed = True
    db.commit()
    return build_result(answers)
