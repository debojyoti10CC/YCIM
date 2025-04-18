from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
import json
from datetime import datetime

app = FastAPI(title="Mental Health Assessment API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Option(BaseModel):
    text: str
    depressionWeight: int
    anxietyWeight: int

class Question(BaseModel):
    id: int
    question: str
    options: List[Option]

class Response(BaseModel):
    questionId: int
    selectedOptionIndex: int

class AssessmentRequest(BaseModel):
    responses: List[Response]

class ScoreResult(BaseModel):
    depression: int
    anxiety: int
    timestamp: str
    recommendations: Dict[str, List[str]]

# Database of questions with mental health classifications
questions_database = [
    {
        "id": 1,
        "question": "How often have you felt overwhelmed by your responsibilities in the past two weeks?",
        "options": [
            {"text": "Not at all", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Several days", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "More than half the days", "depressionWeight": 2, "anxietyWeight": 2},
            {"text": "Nearly every day", "depressionWeight": 3, "anxietyWeight": 3}
        ]
    },
    {
        "id": 2,
        "question": "How would you rate your energy levels throughout the day?",
        "options": [
            {"text": "Consistently high", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Moderate with some fluctuation", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Low with occasional bursts", "depressionWeight": 2, "anxietyWeight": 1},
            {"text": "Constantly depleted", "depressionWeight": 3, "anxietyWeight": 2}
        ]
    },
    {
        "id": 3,
        "question": "How often do you find yourself worrying about future events?",
        "options": [
            {"text": "Rarely or never", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasionally", "depressionWeight": 0, "anxietyWeight": 1},
            {"text": "Frequently", "depressionWeight": 1, "anxietyWeight": 2},
            {"text": "Almost constantly", "depressionWeight": 2, "anxietyWeight": 3}
        ]
    },
    {
        "id": 4,
        "question": "How would you describe your sleep pattern recently?",
        "options": [
            {"text": "Regular and restful", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasional difficulty", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Frequently disrupted", "depressionWeight": 2, "anxietyWeight": 2},
            {"text": "Severe insomnia or excessive sleeping", "depressionWeight": 3, "anxietyWeight": 2}
        ]
    },
    {
        "id": 5,
        "question": "How often do you experience physical symptoms of stress (headaches, muscle tension, etc.)?",
        "options": [
            {"text": "Rarely or never", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasionally", "depressionWeight": 0, "anxietyWeight": 1},
            {"text": "Weekly", "depressionWeight": 1, "anxietyWeight": 2},
            {"text": "Daily", "depressionWeight": 2, "anxietyWeight": 3}
        ]
    },
    {
        "id": 6,
        "question": "How would you rate your ability to concentrate on tasks?",
        "options": [
            {"text": "Excellent", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Good with minor distractions", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Difficult with frequent distractions", "depressionWeight": 2, "anxietyWeight": 2},
            {"text": "Very poor concentration", "depressionWeight": 3, "anxietyWeight": 2}
        ]
    },
    {
        "id": 7,
        "question": "How often do you feel a sense of hopelessness about the future?",
        "options": [
            {"text": "Never", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasionally", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Frequently", "depressionWeight": 2, "anxietyWeight": 1},
            {"text": "Most of the time", "depressionWeight": 3, "anxietyWeight": 2}
        ]
    },
    {
        "id": 8,
        "question": "How would you describe your interest in activities you usually enjoy?",
        "options": [
            {"text": "Strong interest and enjoyment", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Somewhat interested", "depressionWeight": 1, "anxietyWeight": 0},
            {"text": "Limited interest", "depressionWeight": 2, "anxietyWeight": 1},
            {"text": "No interest or enjoyment", "depressionWeight": 3, "anxietyWeight": 1}
        ]
    },
    {
        "id": 9,
        "question": "How often do you experience racing thoughts or difficulty controlling worry?",
        "options": [
            {"text": "Rarely or never", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasionally", "depressionWeight": 0, "anxietyWeight": 1},
            {"text": "Frequently", "depressionWeight": 1, "anxietyWeight": 2},
            {"text": "Almost constantly", "depressionWeight": 1, "anxietyWeight": 3}
        ]
    },
    {
        "id": 10,
        "question": "How would you rate your overall mood on most days?",
        "options": [
            {"text": "Generally positive", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Neutral", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Mildly negative", "depressionWeight": 2, "anxietyWeight": 1},
            {"text": "Predominantly negative", "depressionWeight": 3, "anxietyWeight": 2}
        ]
    },
    {
        "id": 11,
        "question": "How often do you feel irritable or easily annoyed?",
        "options": [
            {"text": "Rarely or never", "depressionWeight": 0, "anxietyWeight": 0},
            {"text": "Occasionally", "depressionWeight": 1, "anxietyWeight": 1},
            {"text": "Frequently", "depressionWeight": 2, "anxietyWeight": 2},
            {"text": "Most of the time", "depressionWeight": 3, "anxietyWeight": 3}
        ]
    }
]

# Motivational quotes database
motivational_quotes = [
    "The greatest glory in living lies not in never falling, but in rising every time we fall. – Nelson Mandela",
    "The way to get started is to quit talking and begin doing. – Walt Disney",
    "Your time is limited, don't waste it living someone else's life. – Steve Jobs",
    "If life were predictable it would cease to be life, and be without flavor. – Eleanor Roosevelt",
    "Spread love everywhere you go. Let no one ever come to you without leaving happier. – Mother Teresa",
    "When you reach the end of your rope, tie a knot in it and hang on. – Franklin D. Roosevelt",
    "Always remember that you are absolutely unique. Just like everyone else. – Margaret Mead",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "You will face many defeats in life, but never let yourself be defeated. – Maya Angelou",
    "In the middle of difficulty lies opportunity. – Albert Einstein"
]

def get_recommendations(depression_score: int, anxiety_score: int) -> Dict[str, List[str]]:
    recommendations = {
        "depression": [],
        "anxiety": []
    }
    
    # Depression recommendations
    if depression_score <= 5:
        recommendations["depression"] = [
            "Maintain regular physical activity",
            "Practice mindfulness for 10 minutes daily",
            "Keep a gratitude journal"
        ]
    elif depression_score <= 10:
        recommendations["depression"] = [
            "Consider speaking with a mental health professional",
            "Establish consistent sleep patterns",
            "Engage in activities that previously brought joy",
            "Connect with supportive friends or family"
        ]
    else:
        recommendations["depression"] = [
            "Consult with a healthcare provider about your symptoms",
            "Join a support group",
            "Limit alcohol and caffeine consumption",
            "Create daily structure with small, achievable goals"
        ]
    
    # Anxiety recommendations
    if anxiety_score <= 5:
        recommendations["anxiety"] = [
            "Practice deep breathing exercises",
            "Limit exposure to negative news",
            "Maintain regular physical activity"
        ]
    elif anxiety_score <= 10:
        recommendations["anxiety"] = [
            "Try progressive muscle relaxation techniques",
            "Consider speaking with a mental health professional",
            "Keep a worry journal to identify patterns",
            "Establish healthy boundaries in stressful situations"
        ]
    else:
        recommendations["anxiety"] = [
            "Consult with a healthcare provider about your symptoms",
            "Try cognitive behavioral techniques",
            "Practice daily meditation",
            "Consider limiting stimulants like caffeine"
        ]
    
    return recommendations

@app.get("/questions/", response_model=List[Question])
async def get_questions(count: int = 10):
    """Get a random set of questions for the assessment"""
    if count > len(questions_database):
        raise HTTPException(status_code=400, detail="Requested count exceeds available questions")
    
    selected_questions = random.sample(questions_database, count)
    return selected_questions

@app.post("/assess/", response_model=ScoreResult)
async def assess_responses(assessment: AssessmentRequest):
    """Calculate depression and anxiety scores based on responses"""
    depression_score = 0
    anxiety_score = 0
    
    # Calculate scores
    for response in assessment.responses:
        question = next((q for q in questions_database if q["id"] == response.questionId), None)
        if not question:
            continue
            
        selected_option = question["options"][response.selectedOptionIndex]
        depression_score += selected_option["depressionWeight"]
        anxiety_score += selected_option["anxietyWeight"]
    
    # Get recommendations
    recommendations = get_recommendations(depression_score, anxiety_score)
    
    return {
        "depression": depression_score,
        "anxiety": anxiety_score,
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations
    }

@app.get("/quote/")
async def get_random_quote():
    """Get a random motivational quote"""
    return {"quote": random.choice(motivational_quotes)}