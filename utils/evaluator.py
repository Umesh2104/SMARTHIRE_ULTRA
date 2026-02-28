"""
evaluator.py - Evaluates interview answers
"""

def evaluate_answers(questions):
    """Evaluate a list of questions with answers"""
    
    tech_scores = []
    comm_scores = []
    per_question = []
    feedback_parts = []

    for i, q in enumerate(questions):
        answer = q.get('answer', '').strip()
        
        if not answer:
            ts, cs = 0, 0
            qf = "No answer provided"
        else:
            word_count = len(answer.split())
            cs = min(100, word_count * 4)  # Communication score based on length
            ts = min(100, len(set(q['question'].lower().split()) & set(answer.lower().split())) * 10)
            qf = get_feedback(word_count)

        tech_scores.append(ts)
        comm_scores.append(cs)
        per_question.append({
            'technical_score': round(ts, 1),
            'communication_score': round(cs, 1),
            'feedback': qf
        })
        
        status = '❌ Not Answered' if not answer else f"Tech: {round(ts,1)}% | Comm: {round(cs,1)}%"
        feedback_parts.append(f"Q{i+1} [{status}]: {qf}")

    avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0
    avg_comm = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0
    overall = round((avg_tech * 0.6 + avg_comm * 0.4), 1)

    scores = {
        'technical': avg_tech,
        'communication': avg_comm,
        'overall': overall,
        'per_question': per_question
    }

    answered = sum(1 for q in questions if q.get('answer', '').strip())
    summary = f"✅ Answered {answered}/{len(questions)} questions"
    
    return scores, summary + '\n\n' + '\n\n'.join(feedback_parts)

def get_feedback(word_count):
    if word_count < 10:
        return "Very brief. Add more details."
    elif word_count < 30:
        return "Good start, needs more depth."
    elif word_count < 60:
        return "Good answer. Add examples."
    else:
        return "Excellent, detailed answer."