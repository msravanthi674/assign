from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv(override=True)

class AIService:
    def __init__(self):
        self._client = None
        self.api_key: str | None = None

    @property
    def client(self) -> OpenAI:
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self._client is None or self._client.api_key != self.api_key:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_study_plan(self, session_data: Dict) -> str:
        """
        Generates a 3-step study plan based on student performance.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            # Fallback when no API key is configured
            return (
                "📚 Personalized Study Plan (Generated Locally — No API Key Set)\n\n"
                f"Based on your performance ({session_data['ability_score']:.2f} ability score):\n\n"
                "Step 1: Review foundational concepts in the topics you missed. "
                "Focus on building a strong base before tackling harder problems.\n\n"
                "Step 2: Practice targeted problem sets. Work through 10-15 problems "
                "in each weak area, gradually increasing difficulty.\n\n"
                "Step 3: Take a timed mini-test covering your weak areas to "
                "simulate real exam pressure and track improvement.\n\n"
                "💡 Tip: Set your OPENAI_API_KEY in .env for AI-personalized plans."
            )

        prompt = f"""
You are an expert GRE tutor. Analyze this diagnostic test performance and provide
a concise, actionable 3-step study plan.

Performance Data:
- Final Ability Score: {session_data['ability_score']:.2f} (scale 0.1 to 1.0)
- Topics Covered: {', '.join(session_data['topics'])}
- Summary: {session_data['performance_summary']}

Requirements:
1. Each step should be specific, actionable, and tied to the student's weak areas.
2. Include recommended resources or study strategies.
3. Format as Step 1, Step 2, Step 3.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a concise, expert education advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error generating AI study plan: {str(e)}"
