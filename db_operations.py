from sqlalchemy.orm import Session
from utils.database import Lecture, Transcript, Summary, Flashcard, Quiz, FlashcardStudySession
from datetime import datetime, timedelta
import json

def create_lecture(db: Session, title: str, filename: str, file_size: int = 0, duration: int = 0):
    """Create a new lecture record"""
    lecture = Lecture(
        title=title,
        filename=filename,
        file_size=file_size,
        duration=duration
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture

def save_transcript(db: Session, lecture_id: int, content: str):
    """Save transcript for a lecture"""
    transcript = Transcript(lecture_id=lecture_id, content=content)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript

def save_summary(db: Session, lecture_id: int, content: str):
    """Save summary for a lecture"""
    summary = Summary(lecture_id=lecture_id, content=content)
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary

def save_flashcards(db: Session, lecture_id: int, flashcards_data: list):
    """Save flashcards for a lecture"""
    flashcards = []
    for card_data in flashcards_data:
        flashcard = Flashcard(
            lecture_id=lecture_id,
            question=card_data.get('question', ''),
            answer=card_data.get('answer', ''),
            category=card_data.get('category', '')
        )
        db.add(flashcard)
        flashcards.append(flashcard)
    db.commit()
    return flashcards

def save_quiz(db: Session, lecture_id: int, quiz_data: dict):
    """Save quiz for a lecture"""
    quiz = Quiz(
        lecture_id=lecture_id,
        multiple_choice=quiz_data.get('multiple_choice', []),
        open_ended=quiz_data.get('open_ended', [])
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def get_all_lectures(db: Session):
    """Get all lectures ordered by most recent first"""
    return db.query(Lecture).order_by(Lecture.created_at.desc()).all()

def get_lecture_by_id(db: Session, lecture_id: int):
    """Get a specific lecture with all its content"""
    return db.query(Lecture).filter(Lecture.id == lecture_id).first()

def delete_lecture(db: Session, lecture_id: int):
    """Delete a lecture and all associated content"""
    lecture = get_lecture_by_id(db, lecture_id)
    if lecture:
        db.delete(lecture)
        db.commit()
        return True
    return False

def record_flashcard_study(db: Session, flashcard_id: int, difficulty_rating: int):
    """
    Record a flashcard study session with spaced repetition algorithm.
    
    difficulty_rating:
    - 1: Hard (review in 1 day)
    - 2: Medium (review in 3 days)
    - 3: Easy (review in 7 days)
    """
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        return None
    
    # Get previous study sessions
    previous_sessions = db.query(FlashcardStudySession).filter(
        FlashcardStudySession.flashcard_id == flashcard_id
    ).order_by(FlashcardStudySession.reviewed_at.desc()).all()
    
    repetition_count = len(previous_sessions) + 1
    
    # Calculate next review date based on difficulty and repetition count
    days_until_review = {
        1: 1,   # Hard
        2: 3,   # Medium
        3: 7    # Easy
    }.get(difficulty_rating, 3)
    
    # Increase interval based on repetition count (spaced repetition)
    if repetition_count > 1:
        days_until_review *= (1.5 ** (repetition_count - 1))
    
    next_review_date = datetime.utcnow() + timedelta(days=days_until_review)
    
    # Create study session record
    study_session = FlashcardStudySession(
        flashcard_id=flashcard_id,
        difficulty_rating=difficulty_rating,
        next_review_date=next_review_date,
        repetition_count=repetition_count
    )
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session

def get_flashcards_for_review(db: Session, lecture_id: int = None):
    """Get flashcards that are due for review"""
    query = db.query(Flashcard)
    
    if lecture_id:
        query = query.filter(Flashcard.lecture_id == lecture_id)
    
    flashcards = query.all()
    
    # Filter flashcards based on study sessions
    due_flashcards = []
    for flashcard in flashcards:
        latest_session = db.query(FlashcardStudySession).filter(
            FlashcardStudySession.flashcard_id == flashcard.id
        ).order_by(FlashcardStudySession.reviewed_at.desc()).first()
        
        if not latest_session or latest_session.next_review_date <= datetime.utcnow():
            due_flashcards.append(flashcard)
    
    return due_flashcards

def get_study_progress(db: Session, lecture_id: int):
    """Get study progress statistics for a lecture"""
    flashcards = db.query(Flashcard).filter(Flashcard.lecture_id == lecture_id).all()
    
    total_flashcards = len(flashcards)
    reviewed_flashcards = 0
    
    for flashcard in flashcards:
        session_count = db.query(FlashcardStudySession).filter(
            FlashcardStudySession.flashcard_id == flashcard.id
        ).count()
        if session_count > 0:
            reviewed_flashcards += 1
    
    return {
        'total': total_flashcards,
        'reviewed': reviewed_flashcards,
        'percentage': (reviewed_flashcards / total_flashcards * 100) if total_flashcards > 0 else 0
    }
