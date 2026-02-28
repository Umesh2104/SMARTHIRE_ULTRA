"""
question_generator.py - Generates questions from CSV bank
"""
import random
from utils.question_loader import get_questions_for_skills

def generate_questions_from_skills_with_counts(skill_counts=None, used_questions=None):
    """
    Generate questions based on selected skills with specific counts
    """
    used_questions = used_questions or []
    skill_counts = skill_counts or {}
    
    all_questions = []
    used_set = set(used_questions)
    
    for skill, count in skill_counts.items():
        if count > 0:
            skill_questions = get_questions_for_skills([skill], count * 3)
            available = [q for q in skill_questions if q not in used_set]
            selected = available[:count]
            all_questions.extend(selected)
            used_set.update(selected)
    
    random.shuffle(all_questions)
    return all_questions