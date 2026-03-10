# AI-Driven Adaptive Diagnostic Engine

This is a prototype for a 1-Dimension Adaptive Testing System. It determines a student's proficiency level by dynamically selecting questions based on their performance, using principles from Item Response Theory (IRT), and generates a personalized study plan using an LLM.

## Tech Stack
* **Language:** Python 3.12
* **Framework:** FastAPI
* **Database:** MongoDB (with an in-memory mock fallback option for local testing)
* **AI Integration:** OpenAI API

## How to Run the Project

### Prerequisites
1. Python 3.12 (or compatible 3.x) installed on your system.
2. (Optional) MongoDB running locally or a MongoDB Atlas URI.

### Setup Instructions
1. **Clone the repository / Navigate to the folder**
2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   A `.env` file is already provided. By default, it uses an in-memory mock database (`USE_MOCK_DB=true`), so no MongoDB installation is required to test!
   If you have an OpenAI API key, update `.env`:
   ```env
   OPENAI_API_KEY=your-actual-api-key
   ```
   *(If you don't provide an API key, the system falls back to a locally generated study plan).*

5. **Start the FastAPI Server:**
   ```bash
   python main.py
   ```
   The server will start at `http://localhost:8000`.

### Testing the Workflow (API Endpoints)
You can use the built-in Swagger UI by navigating to:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Or use `curl`/Postman:
1. **Start a new session:**
   ```bash
   curl http://localhost:8000/api/start-session
   ```
   *Returns a `user_id`.*

2. **Get the next adaptive question:**
   ```bash
   curl http://localhost:8000/api/next-question/{user_id}
   ```
   *Returns the question closest to your current ability score.*

3. **Submit an answer:**
   ```bash
   curl -X POST "http://localhost:8000/api/submit-answer?user_id={user_id}&question_id={question_id}&answer=7"
   ```
   *(Pass the exact option text as the answer).*

4. **Get final report and AI Study Plan:**
   ```bash
   curl http://localhost:8000/api/report/{user_id}
   ```

## Adaptive Algorithm Logic

The adaptive engine is built using a simplified 1-Parameter Logistic (1PL) Item Response Theory (IRT) model.
Here is how it works:
1. **Initialization:** The student starts with an assumed ability score of `0.5` (on a scale of 0.1 to 1.0).
2. **Question Selection:** The system looks at all unanswered questions and selects the one whose `difficulty` score is mathematically closest to the student's current `ability_score`.
3. **Probability Calculation:** Before evaluating the answer, we calculate the probability of the student getting it right using the logistic function:
   `P(correct) = 1 / (1 + e^-(ability - difficulty))`
4. **Scoring Update:** Once the student answers, we update their ability score using a Maximum Likelihood Estimation (MLE) shortcut:
   `New Ability = Old Ability + K * (Actual Outcome - P(correct))`
   *(Where K is a dampening sensitivity factor of 0.5 to prevent extreme jumps).*
5. **Iteration:** If the student answered correctly, `New Ability > Old Ability`, meaning the next question chosen will be harder. If incorrect, the ability drops, and an easier question is chosen.

## The AI Log
**How I used AI Tools (Cursor & LLMs) to build this quickly:**
- **Scaffolding:** I used prompt-driven file creation to lay down the entire generic FastAPI structure (models, routes, main, requirements) within a few seconds.
- **Data Seeding:** Formulating 20 mathematically consistent GRE-style questions with metadata is tedious. I prompted the LLM to generate `app/utils.py` containing a JSON-like array of 20 questions, pre-tagged with topics, tags, and realistic difficulty scores from 0.1 to 1.0.
- **Algorithm Generation:** Writing IRT math from scratch is prone to typos. I utilized an AI assistant to fetch standard functions for the 1PL IRT model and clamp the ability scores, ensuring algorithmic soundness without looking up formulas manually.
- **Error Handling/Fallback:** When local MongoDB was unavailable, I quickly prompted for an architecture pivot to include `mongomock-motor` for in-memory DB support using a `.env` toggle.

**Challenges the AI couldn't solve automatically:**
- **Dependency Conflicts:** The AI generated a dependency tree with conflicting versions of `motor`, `pymongo`, and the newest `fastapi/pydantic`. I had to manually intervene through the command line, observe the pip conflict traces, and explicitly upgrade `motor` and `openai` to mutually compatible modern versions.
- **Windows Console Encoding:** The AI included cute emojis (🧠, ✅) in terminal print statements and API responses. The Windows `cp1252` console crashed on startup attempting to encode them. I manually replaced them with ASCII-safe equivalents.
