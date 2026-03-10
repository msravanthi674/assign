from models import Question, UserSession, UserResponse
from bson import ObjectId
import random

def seed_questions(db):
    questions_count = db.questions.count_documents({})
    if questions_count > 0:
        return {"message": "Database already seeded"}

    sample_questions = [
        {
            "text": "If x + 2y = 10 and 2x + y = 11, what is the value of x + y?",
            "options": ["5", "6", "7", "8"],
            "correct_answer": "7",
            "difficulty": 0.3,
            "topic": "Algebra",
            "tags": ["Linear Equations", "Quantitative"]
        },
        {
            "text": "Which word is most nearly opposite in meaning to 'EPHEMERAL'?",
            "options": ["Short-lived", "Eternal", "Translucent", "Fragmentary"],
            "correct_answer": "Eternal",
            "difficulty": 0.4,
            "topic": "Vocabulary",
            "tags": ["Antonyms", "Verbal"]
        },
        {
            "text": "A circle has a radius of 5. What is its area?",
            "options": ["10pi", "25pi", "50pi", "100pi"],
            "correct_answer": "25pi",
            "difficulty": 0.2,
            "topic": "Geometry",
            "tags": ["Circles", "Quantitative"]
        },
        {
            "text": "The price of an item increased from $80 to $100. What was the percentage increase?",
            "options": ["20%", "25%", "80%", "100%"],
            "correct_answer": "25%",
            "difficulty": 0.3,
            "topic": "Arithmetic",
            "tags": ["Percentages", "Quantitative"]
        },
        {
            "text": "Choose the word that best completes: The scientist's report was _____, leaving no doubt about the results.",
            "options": ["Ambiguous", "Equivocal", "Unequivocal", "Tentative"],
            "correct_answer": "Unequivocal",
            "difficulty": 0.5,
            "topic": "Vocabulary",
            "tags": ["Sentence Equivalence", "Verbal"]
        },
        {
            "text": "If 3^x = 81, what is x?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "difficulty": 0.4,
            "topic": "Algebra",
            "tags": ["Exponents", "Quantitative"]
        },
        {
            "text": "Find the average of 12, 15, 18, 21, and 24.",
            "options": ["16", "18", "20", "22"],
            "correct_answer": "18",
            "difficulty": 0.3,
            "topic": "Arithmetic",
            "tags": ["Statistics", "Quantitative"]
        },
        {
            "text": "Which of these is a synonym for 'LOQUACIOUS'?",
            "options": ["Silent", "Garrulous", "Hesitant", "Brief"],
            "correct_answer": "Garrulous",
            "difficulty": 0.6,
            "topic": "Vocabulary",
            "tags": ["Synonyms", "Verbal"]
        },
        {
            "text": "In a triangle, two angles are 45 and 45 degrees. What is the third angle?",
            "options": ["45", "60", "90", "180"],
            "correct_answer": "90",
            "difficulty": 0.2,
            "topic": "Geometry",
            "tags": ["Triangles", "Quantitative"]
        },
        {
            "text": "A car travels 120 miles in 2 hours. What is its speed in mph?",
            "options": ["50", "60", "70", "80"],
            "correct_answer": "60",
            "difficulty": 0.2,
            "topic": "Arithmetic",
            "tags": ["Rate", "Quantitative"]
        },
        {
            "text": "Simplify: 4(x - 3) + 2x = ?",
            "options": ["6x - 3", "6x - 12", "4x - 12", "2x - 3"],
            "correct_answer": "6x - 12",
            "difficulty": 0.4,
            "topic": "Algebra",
            "tags": ["Simplification", "Quantitative"]
        },
        {
            "text": "What is the square root of 225?",
            "options": ["13", "14", "15", "16"],
            "correct_answer": "15",
            "difficulty": 0.2,
            "topic": "Arithmetic",
            "tags": ["Roots", "Quantitative"]
        },
        {
            "text": "The word 'MITIGATE' most nearly means:",
            "options": ["Aggravate", "Alleviate", "Intensify", "Ignore"],
            "correct_answer": "Alleviate",
            "difficulty": 0.5,
            "topic": "Vocabulary",
            "tags": ["Context", "Verbal"]
        },
        {
            "text": "If a rectangle has length 8 and width 3, what is its perimeter?",
            "options": ["11", "22", "24", "44"],
            "correct_answer": "22",
            "difficulty": 0.3,
            "topic": "Geometry",
            "tags": ["Perimeter", "Quantitative"]
        },
        {
            "text": "What is 15% of 200?",
            "options": ["15", "20", "25", "30"],
            "correct_answer": "30",
            "difficulty": 0.3,
            "topic": "Arithmetic",
            "tags": ["Percentages", "Quantitative"]
        },
        {
            "text": "A standard deck of cards has 52 cards. What is the probability of drawing an Ace?",
            "options": ["1/13", "1/26", "1/52", "4/13"],
            "correct_answer": "1/13",
            "difficulty": 0.5,
            "topic": "Probability",
            "tags": ["Probability", "Quantitative"]
        },
        {
            "text": "Which word means 'to deceive by a false appearance'?",
            "options": ["Dissemble", "Revere", "Amplify", "Clarify"],
            "correct_answer": "Dissemble",
            "difficulty": 0.8,
            "topic": "Vocabulary",
            "tags": ["Advanced", "Verbal"]
        },
        {
            "text": "If 2x - 5 = 11, what is x?",
            "options": ["3", "6", "8", "16"],
            "correct_answer": "8",
            "difficulty": 0.3,
            "topic": "Algebra",
            "tags": ["Equations", "Quantitative"]
        },
        {
            "text": "The median of the set {3, 1, 9, 7, 5} is:",
            "options": ["1", "3", "5", "7"],
            "correct_answer": "5",
            "difficulty": 0.4,
            "topic": "Arithmetic",
            "tags": ["Median", "Quantitative"]
        },
        {
            "text": "What is the next number in the sequence: 2, 4, 8, 16, ...?",
            "options": ["20", "24", "30", "32"],
            "correct_answer": "32",
            "difficulty": 0.3,
            "topic": "Arithmetic",
            "tags": ["Sequences", "Quantitative"]
        }
    ]
    
    db.questions.insert_many(sample_questions)
    return {"message": "Database seeded with 20 questions"}
