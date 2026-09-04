from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AnswerKey = Literal["A", "B"]


class CreateSessionRequest(BaseModel):
    previous_session_id: str | None = None


class AnswerRequest(BaseModel):
    question_id: int = Field(ge=1, le=30)
    selected_answer: AnswerKey


class SessionResponse(BaseModel):
    id: str
    current_question: int
    completed: bool
    answered_count: int
    total_questions: int
    question: dict | None
    answers: dict[int, AnswerKey]
