from fastapi import APIRouter, HTTPException
from database import get_database
from adaptive_engine import AdaptiveEngine
from ai_service import AIService
from utils import seed_questions
from bson import ObjectId
import uuid
import random

router = APIRouter()
ai_service = AIService()

def _db():
    try:
        return get_database()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Make sure MongoDB is running.",
        )

@router.post("/seed")
def seed():
    db = _db()
    return seed_questions(db)

@router.get("/start-session")
def start_session():
    db = _db()
    user_id = str(uuid.uuid4())
    session = {
        "user_id": user_id,
        "ability_score": 0.5,
        "responses": [],
        "completed": False,
    }
    db.sessions.insert_one(session)
    return {
        "user_id": user_id,
        "message": "Session started. Your baseline ability is 0.5.",
        "initial_ability": 0.5,
    }

@router.get("/next-question/{user_id}")
def get_next_question(user_id: str):
    db = _db()

    session = db.sessions.find_one({"user_id": user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("completed") or len(session["responses"]) >= 10:
        db.sessions.update_one(
            {"user_id": user_id}, {"$set": {"completed": True}}
        )
        return {
            "message": "Test completed — 10 questions answered.",
            "completed": True,
            "final_ability": session["ability_score"],
        }

    current_ability = session["ability_score"]
    answered_ids = [ObjectId(r["question_id"]) for r in session["responses"]]

    query = {"_id": {"$nin": answered_ids}} if answered_ids else {}
    questions = list(db.questions.find(query))

    if not questions:
        return {"message": "No more questions available.", "completed": True}

    questions.sort(key=lambda q: abs(q["difficulty"] - current_ability))
    top_n = min(3, len(questions))
    best = random.choice(questions[:top_n])
    best["_id"] = str(best["_id"])

    return {
        "question_number": len(session["responses"]) + 1,
        "question_id": best["_id"],
        "text": best["text"],
        "options": best["options"],
        "difficulty": best["difficulty"],
        "topic": best["topic"],
        "current_ability": current_ability,
    }

@router.post("/submit-answer")
def submit_answer(user_id: str, question_id: str, answer: str):
    db = _db()

    session = db.sessions.find_one({"user_id": user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        question = db.questions.find_one({"_id": ObjectId(question_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid question_id format")

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = answer.strip() == question["correct_answer"].strip()

    new_ability = AdaptiveEngine.update_ability(
        session["ability_score"],
        question["difficulty"],
        is_correct,
    )

    response_entry = {
        "question_id": question_id,
        "answer": answer,
        "is_correct": is_correct,
        "difficulty": question["difficulty"],
        "topic": question.get("topic", "Unknown"),
    }

    db.sessions.update_one(
        {"user_id": user_id},
        {
            "$push": {"responses": response_entry},
            "$set": {"ability_score": new_ability},
        },
    )

    questions_answered = len(session["responses"]) + 1

    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "previous_ability": session["ability_score"],
        "new_ability": round(new_ability, 4),
        "questions_answered": questions_answered,
        "questions_remaining": max(0, 10 - questions_answered),
    }

@router.get("/report/{user_id}")
def get_report(user_id: str):
    db = _db()

    session = db.sessions.find_one({"user_id": user_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    responses = session["responses"]
    if not responses:
        raise HTTPException(
            status_code=400,
            detail="No responses recorded yet. Answer some questions first.",
        )

    topics = list({r["topic"] for r in responses})
    correct_count = sum(1 for r in responses if r["is_correct"])
    total = len(responses)
    struggled = list({r["topic"] for r in responses if not r["is_correct"]})

    summary = (
        f"Answered {correct_count}/{total} correctly. "
        f"Final ability: {session['ability_score']:.2f}. "
        f"Weak areas: {', '.join(struggled) if struggled else 'None'}."
    )

    ai_input = {
        "ability_score": session["ability_score"],
        "topics": topics,
        "performance_summary": summary,
    }
    study_plan = ai_service.generate_study_plan(ai_input)

    return {
        "user_id": user_id,
        "final_ability": round(session["ability_score"], 4),
        "correct_answers": correct_count,
        "total_questions": total,
        "accuracy": f"{(correct_count / total) * 100:.1f}%",
        "topics_covered": topics,
        "weak_topics": struggled,
        "study_plan": study_plan,
    }
