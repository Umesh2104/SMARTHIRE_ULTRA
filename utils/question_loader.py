"""
question_loader.py - Loads questions from CSV
"""
import csv
import random
import os
import html
import re
from collections import defaultdict

CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'interview_questions_complete.csv')
_question_cache = None

def clean_question(question):
    """Clean HTML entities and tags"""
    if not question:
        return question
    question = html.unescape(question)
    question = re.sub('<.*?>', '', question)
    return ' '.join(question.split())

def load_questions_from_csv():
    """Load all questions from CSV"""
    global _question_cache
    
    if _question_cache:
        return _question_cache
    
    questions_by_topic = defaultdict(list)
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"⚠️ CSV not found at {CSV_FILE_PATH}")
        return {}
    
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                topic = row['Topic'].strip().lower()
                question = clean_question(row['Question'])
                if question:
                    questions_by_topic[topic].append(question)
        
        _question_cache = dict(questions_by_topic)
        return _question_cache
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return {}

def get_questions_for_skills(skills, num_questions=5):
    """Get questions for selected skills"""
    all_questions = load_questions_from_csv()
    
    if not all_questions:
        return get_fallback_questions()[:num_questions]
    
    selected = []
    skills = [s.lower().replace('_', ' ') for s in skills]
    
    for skill in skills:
        # Try direct match
        if skill in all_questions:
            selected.extend(all_questions[skill])
        # Try underscore version
        elif skill.replace(' ', '_') in all_questions:
            selected.extend(all_questions[skill.replace(' ', '_')])
        # Try common mappings
        else:
            mappings = {
                'python': 'python', 'java': 'java', 'javascript': 'javascript',
                'html': 'html', 'css': 'css', 'sql': 'sql', 'react': 'react',
                'leadership': 'leadership', 'teamwork': 'teamwork',
                'communication': 'communication', 'problem solving': 'problem_solving'
            }
            for key, value in mappings.items():
                if key in skill and value in all_questions:
                    selected.extend(all_questions[value])
                    break
    
    # Remove duplicates
    seen = set()
    unique = []
    for q in selected:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    
    random.shuffle(unique)
    return unique[:num_questions]

def get_fallback_questions():
    """Fallback questions"""
    return [
        "Tell me about yourself.",
        "What are your strengths?",
        "What are your weaknesses?",
        "Why do you want this job?",
        "Where do you see yourself in 5 years?",
        "Describe a challenge you overcame.",
        "Tell me about a team project.",
        "How do you handle stress?",
        "What motivates you?",
        "Why should we hire you?"
    ]