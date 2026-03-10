import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import uuid
import random
from bson import ObjectId

from app.database import connect_db, get_database
from app.utils import seed_questions
from app.adaptive_engine import AdaptiveEngine
from app.ai_service import AIService

if "initialized" not in st.session_state:
    st.set_page_config(page_title="Adaptive Diagnostic Engine", page_icon="🧠", layout="centered")
    connect_db()
    db = get_database()
    seed_questions(db)
    st.session_state.db = db
    st.session_state.ai_service = AIService()
    st.session_state.initialized = True
    st.session_state.view = "home"
    st.session_state.user_id = None

db = st.session_state.db
ai_service = st.session_state.ai_service

st.markdown("""
<style>
    .main-container {
        background: rgba(10, 25, 47, 0.6);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
    }
    .question-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.view == "home":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.title("🌟 Adaptive Diagnostic Engine")
    st.write("An AI-powered assessment that dynamically adjusts to your proficiency level.")
    
    if st.button("Begin Assessment", use_container_width=True, type="primary"):
        user_id = str(uuid.uuid4())
        session = {
            "user_id": user_id,
            "ability_score": 0.5,
            "responses": [],
            "completed": False,
        }
        db.sessions.insert_one(session)
        st.session_state.user_id = user_id
        st.session_state.view = "question"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.view == "question":
    user_id = st.session_state.user_id
    session = db.sessions.find_one({"user_id": user_id})
    
    if session.get("completed") or len(session["responses"]) >= 10:
        db.sessions.update_one({"user_id": user_id}, {"$set": {"completed": True}})
        st.session_state.view = "report"
        st.rerun()
        
    current_ability = session["ability_score"]
    answered_ids = [ObjectId(r["question_id"]) for r in session["responses"]]
    
    query = {"_id": {"$nin": answered_ids}} if answered_ids else {}
    questions = list(db.questions.find(query))
    
    if not questions:
        db.sessions.update_one({"user_id": user_id}, {"$set": {"completed": True}})
        st.session_state.view = "report"
        st.rerun()
        
    questions.sort(key=lambda q: abs(q["difficulty"] - current_ability))
    best = random.choice(questions[:min(3, len(questions))])
    
    q_num = len(session["responses"]) + 1
    
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Question {q_num}/10")
    with col2:
        st.markdown(f"**Topic:** `{best['topic']}`")
    
    st.markdown(f"<div class='question-box'><h4>{best['text']}</h4></div>", unsafe_allow_html=True)
    
    with st.form("question_form"):
        answer = st.radio("Choose your answer:", options=best["options"], index=None)
        submitted = st.form_submit_button("Submit Answer", use_container_width=True)
        
        if submitted and answer:
            is_correct = answer.strip() == best["correct_answer"].strip()
            new_ability = AdaptiveEngine.update_ability(
                session["ability_score"], best["difficulty"], is_correct
            )
            
            response_entry = {
                "question_id": str(best["_id"]),
                "answer": answer,
                "is_correct": is_correct,
                "difficulty": best["difficulty"],
                "topic": best.get("topic", "Unknown"),
            }
            
            db.sessions.update_one(
                {"user_id": user_id},
                {
                    "$push": {"responses": response_entry},
                    "$set": {"ability_score": new_ability},
                },
            )
            st.rerun()
        elif submitted and not answer:
            st.warning("Please select an answer.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.view == "report":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.title("🎯 Assessment Complete")
    st.write("Here is your performance diagnostic based on the Item Response Theory (IRT) model.")
    
    user_id = st.session_state.user_id
    session = db.sessions.find_one({"user_id": user_id})
    responses = session["responses"]
    
    correct_count = sum(1 for r in responses if r["is_correct"])
    total = len(responses)
    struggled = list({r["topic"] for r in responses if not r["is_correct"]})
    topics = list({r["topic"] for r in responses})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Ability Score", f"{session['ability_score']:.2f} / 1.0")
    col2.metric("Accuracy", f"{(correct_count / total) * 100:.1f}%")
    col3.metric("Correct Answers", f"{correct_count}/{total}")
    
    st.divider()
    
    if "study_plan" not in st.session_state:
        with st.spinner("✨ Generating AI Personalized Study Plan..."):
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
            plan = ai_service.generate_study_plan(ai_input)
            st.session_state.study_plan = plan
            
    st.subheader("📚 AI Personalized Study Plan")
    st.write(st.session_state.study_plan)
    
    st.divider()
    if st.button("Restart Assessment", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
