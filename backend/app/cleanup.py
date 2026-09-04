from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from .models import QuizSession, utcnow


def delete_expired_sessions(db: Session, older_than: timedelta = timedelta(hours=1)) -> int:
    cutoff = utcnow() - older_than
    expired = db.query(QuizSession).filter(QuizSession.updated_at < cutoff).all()
    count = len(expired)
    for session in expired:
        db.delete(session)
    db.commit()
    return count
