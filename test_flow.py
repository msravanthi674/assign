import urllib.request
import urllib.parse
import json
import time
import random

BASE_URL = "http://localhost:8000/api"

print("--- Testing Adaptive Diagnostic Engine ---")

def make_request(method, url):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# 1. Start Session
session_data = make_request("GET", f"{BASE_URL}/start-session")
if not session_data:
    exit(1)

user_id = session_data["user_id"]
print(f"✅ Session started. User ID: {user_id}")
print(f"📊 Initial Ability: {session_data['initial_ability']}")

# 2. Answer 10 questions
print("\n--- 📝 Answering Questions ---")
for i in range(10):
    # Fetch question
    q_data = make_request("GET", f"{BASE_URL}/next-question/{user_id}")
    
    if q_data.get("completed"):
        print("Finished early!")
        break
        
    print(f"\nQ{q_data['question_number']}: {q_data['text']}")
    print(f"Topic: {q_data['topic']} | Difficulty: {q_data['difficulty']} | Current Ability: {q_data['current_ability']:.4f}")
    
    # Pick an answer randomly
    options = q_data['options']
    answer = random.choice(options)
    print(f"> Picked: {answer}")
    
    # Submit Answer
    encoded_ans = urllib.parse.quote(answer)
    submit_url = f"{BASE_URL}/submit-answer?user_id={user_id}&question_id={q_data['question_id']}&answer={encoded_ans}"
    s_data = make_request("POST", submit_url)
    
    if s_data["is_correct"]:
        print(f"✅ Correct! (Target: {s_data['correct_answer']}) -> New Ability: {s_data['new_ability']:.4f}")
    else:
        print(f"❌ Incorrect. (Target: {s_data['correct_answer']}) -> New Ability: {s_data['new_ability']:.4f}")
    
    time.sleep(0.5)

# 3. Get Final Report
print("\n--- 📈 Fetching Final Report ---")
report_data = make_request("GET", f"{BASE_URL}/report/{user_id}")
if report_data:
    print("\n========== FINAL REPORT ==========")
    print(f"Final Ability: {report_data['final_ability']}")
    print(f"Accuracy: {report_data['accuracy']} ({report_data['correct_answers']}/{report_data['total_questions']})")
    print("\nWeak Topics:")
    for topic in report_data.get('weak_topics', []):
        print(f"- {topic}")
        
    print("\n✨ AI Study Plan:\n")
    print(report_data['study_plan'])
    print("==================================")
