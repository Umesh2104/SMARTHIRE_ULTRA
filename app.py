import os
import uuid
import json
import datetime
import random
import csv
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, Response
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------------------------------------------------
# JSON Data Manager
# -------------------------------------------------------------------
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {'users': {}, 'candidates': {}}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'users': {}, 'candidates': {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# -------------------------------------------------------------------
# Question Bank Loader
# -------------------------------------------------------------------
QUESTION_BANK = {}

# Comprehensive skills list for resume parsing
SKILLS_DATABASE = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c', 'cpp', 'c++', 'csharp', 'c#', 
    'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'perl', 'r', 'dart',
    'lua', 'haskell', 'elixir', 'clojure', 'f#', 'groovy', 'julia', 'matlab',
    
    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue', 'node', 'nodejs', 'express', 
    'django', 'flask', 'spring', 'bootstrap', 'tailwind', 'jquery', 'sass', 'less',
    'webpack', 'babel', 'redux', 'nextjs', 'gatsby', 'graphql', 'rest', 'ajax',
    'json', 'xml', 'dom', 'jsp', 'servlets', 'hibernate', 'jpa', 'thymeleaf',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'nosql',
    'cassandra', 'firebase', 'mariadb', 'elasticsearch', 'dynamodb', 'couchdb',
    'neo4j', 'influxdb', 'memcached', 'cockroachdb', 'snowflake', 'bigquery',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'gitlab', 'bitbucket', 'linux', 'unix', 'ansible', 'terraform', 'prometheus',
    'grafana', 'nginx', 'apache', 'circleci', 'travis', 'chef', 'puppet', 'saltstack',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
    'pandas', 'numpy', 'scikit', 'matplotlib', 'seaborn', 'nlp', 'computer vision',
    'tableau', 'power bi', 'spark', 'hadoop', 'data visualization', 'statistics',
    'probability', 'linear algebra', 'calculus', 'data mining', 'etl',
    
    # Mobile Development
    'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic', 'cordova',
    'swiftui', 'jetpack compose', 'objective-c', 'mobile ui/ux',
    
    # Management Skills
    'leadership', 'team management', 'project management', 'strategic planning',
    'decision making', 'problem solving', 'conflict resolution', 'change management',
    'risk management', 'stakeholder management', 'time management', 'negotiation',
    'delegation', 'mentoring', 'coaching', 'performance management', 'goal setting',
    'prioritization', 'agile', 'scrum', 'kanban', 'waterfall', 'pmp', 'prince2',
    
    # HR Management
    'recruitment', 'talent acquisition', 'training', 'development', 'employee relations',
    'compensation', 'benefits', 'hr policies', 'workforce planning', 'diversity',
    'inclusion', 'employee engagement', 'succession planning', 'hr analytics',
    'labor laws', 'onboarding', 'offboarding', 'payroll',
    
    # Operations
    'supply chain', 'logistics', 'inventory management', 'quality management',
    'process improvement', 'six sigma', 'lean', 'capacity planning', 'procurement',
    'vendor management', 'facility management',
    
    # Soft Skills
    'communication', 'teamwork', 'collaboration', 'emotional intelligence',
    'empathy', 'networking', 'relationship building', 'trust building',
    'cultural awareness', 'diplomacy', 'patience', 'adaptability', 'resilience',
    'creativity', 'critical thinking', 'professionalism', 'integrity',
    'reliability', 'punctuality', 'accountability', 'initiative', 'dependability',
    'honesty', 'confidentiality', 'respect', 'work ethic',
    
    # Aptitude Topics
    'percentages', 'averages', 'ratios', 'time and work', 'time speed distance',
    'profit loss', 'simple interest', 'compound interest', 'probability',
    'permutations', 'combinations', 'number system', 'hcf', 'lcm', 'geometry',
    'mensuration', 'trigonometry', 'algebra', 'logarithms', 'sets', 'progressions',
    'quadratic equations', 'inequalities', 'mixtures', 'alligations', 'boats',
    'streams', 'pipes', 'cisterns', 'races', 'blood relations', 'coding decoding',
    'direction sense', 'series', 'analogies', 'venn diagrams', 'syllogisms',
    'data sufficiency', 'puzzles', 'input output', 'ranking', 'seating arrangement',
    'cube and dice', 'clock and calendar', 'cause and effect', 'reading comprehension',
    'grammar', 'vocabulary', 'sentence correction', 'para jumbles', 'cloze test',
    'synonyms', 'antonyms', 'idioms', 'phrases', 'spellings', 'active passive',
    'direct indirect', 'error spotting'
]

def load_questions_from_csv():
    """Load questions from CSV file"""
    global QUESTION_BANK
    csv_path = 'interview_questions_complete.csv'
    
    if not os.path.exists(csv_path):
        print(f"⚠️ CSV file not found. Please run generate_complete_csv.py first.")
        # Create minimal default questions
        QUESTION_BANK = {
            'python': ['What is Python?', 'What are lists and tuples?'],
            'java': ['What is JVM?', 'What is inheritance?'],
            'javascript': ['What is closure?', 'What is event loop?'],
            'html': ['What is HTML?', 'What are semantic tags?'],
            'css': ['What is CSS box model?', 'What is flexbox?'],
            'sql': ['What is JOIN?', 'What is primary key?'],
            'leadership': ['How do you lead a team?', 'How do you handle conflicts?'],
            'communication': ['How do you handle difficult conversations?'],
            'problem_solving': ['How do you approach complex problems?'],
            'teamwork': ['How do you handle team conflicts?'],
            'percentages': ['What is 20% of 150?', 'If 30% of a number is 60, what is the number?'],
            'averages': ['Find average of 5,10,15,20', 'The average of 4 numbers is 15.'],
            'probability': ['What is probability of getting heads?']
        }
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                topic = row['Topic'].strip().lower()
                question = row['Question'].strip()
                
                if topic not in QUESTION_BANK:
                    QUESTION_BANK[topic] = []
                QUESTION_BANK[topic].append(question)
        
        print(f"✅ Loaded {sum(len(q) for q in QUESTION_BANK.values())} questions from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")

# Load questions on startup
load_questions_from_csv()

# Smart skill → CSV topic mapper (fixes 0-questions bug)
SKILL_TOPIC_MAP = {
    'machine_learning': 'problem_solving_soft',
    'machine learning': 'problem_solving_soft',
    'deep_learning': 'problem_solving_soft',
    'deep learning': 'problem_solving_soft',
    'problem_solving': ['problem_solving_soft', 'problem_solving_mgmt'],
    'problem solving': ['problem_solving_soft', 'problem_solving_mgmt'],
    'critical_thinking': 'critical_thinking',
    'critical thinking': 'critical_thinking',
    'time_management': 'time_management',
    'time management': 'time_management',
    'teamwork': 'teamwork',
    'leadership': 'leadership',
    'communication': 'communication',
    'adaptability': 'adaptability',
    'emotional_intelligence': 'emotional_intelligence',
    'emotional intelligence': 'emotional_intelligence',
    'work_ethic': 'work_ethic',
    'work ethic': 'work_ethic',
    'creativity': 'creativity',
    'negotiation': 'negotiation',
    'stress_management': 'stress_management',
    'stress management': 'stress_management',
    'training': 'training_development',
    'training_development': 'training_development',
    'recruitment': 'recruitment',
    'risk_management': 'risk_management',
    'risk management': 'risk_management',
    'project_management': 'project_management',
    'project management': 'project_management',
    'team_management': 'team_management',
    'team management': 'team_management',
    'strategic_planning': 'strategic_planning',
    'strategic planning': 'strategic_planning',
    'decision_making': 'decision_making',
    'decision making': 'decision_making',
    'conflict_resolution': 'conflict_resolution',
    'conflict resolution': 'conflict_resolution',
    'performance_management': 'performance_management',
    'change_management': 'change_management',
    'employee_relations': 'employee_relations',
    'interpersonal_skills': 'interpersonal_skills',
    'cultural_awareness': 'cultural_awareness',
    'ethics': 'ethics',
    'dependability': 'dependability',
    'initiative': 'initiative',
    'numpy': 'python',
    'pandas': 'python',
    'tensorflow': 'python',
    'pytorch': 'python',
    'keras': 'python',
    'node': 'nodejs',
    'express': 'express',
    'c++': 'cpp',
    'cpp': 'cpp',
    'c#': 'csharp',
    'csharp': 'csharp',
    'r': None,  # too generic — skip
}

def _resolve_topics(skill):
    """Map a skill name to its CSV topic(s). Returns list of valid topic keys."""
    s = skill.lower().strip()
    # Direct CSV key?
    if s in QUESTION_BANK and QUESTION_BANK[s]:
        return [s]
    # Map lookup
    mapped = SKILL_TOPIC_MAP.get(s)
    if mapped is None and s in SKILL_TOPIC_MAP:
        return []  # explicitly skipped
    if mapped:
        if isinstance(mapped, list):
            return [t for t in mapped if t in QUESTION_BANK]
        if mapped in QUESTION_BANK:
            return [mapped]
    # Try underscore ↔ space
    for v in [s.replace(' ', '_'), s.replace('_', ' ')]:
        if v in QUESTION_BANK and QUESTION_BANK[v]:
            return [v]
    return []

# -------------------------------------------------------------------
# Resume Parser Functions
# -------------------------------------------------------------------
def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.lower()
    except:
        # If PyPDF2 not installed or error, return filename as fallback
        return os.path.basename(filepath).lower()

def extract_skills_from_text(text):
    """Extract skills from text by matching against skills database"""
    found_skills = []
    text_lower = text.lower()
    
    for skill in SKILLS_DATABASE:
        # Create pattern to match whole words
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Convert to consistent format (replace spaces with underscores for IDs)
            skill_id = skill.replace(' ', '_').replace('+', 'p').replace('#', 'sharp')
            found_skills.append(skill_id)
    
    # Remove duplicates
    return list(set(found_skills))

# -------------------------------------------------------------------
# Auth Helpers
# -------------------------------------------------------------------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            if role:
                data = load_data()
                user = data['users'].get(session['user_id'])
                if not user or user['role'] != role:
                    flash('Unauthorized access', 'danger')
                    return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role = request.form.get('role', 'candidate')

        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))

        data = load_data()
        for u in data['users'].values():
            if u['email'] == email:
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))

        user_id = str(uuid.uuid4())
        data['users'][user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': role,
            'created_at': datetime.datetime.now().isoformat()
        }
        if role == 'candidate':
            data['candidates'][user_id] = {
                'user_id': user_id,
                'resume_text': '',
                'skills': [],
                'interviews': [],
                'asked_questions': []
            }
        save_data(data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        data = load_data()
        user = None
        for u in data['users'].values():
            if u['email'] == email:
                user = u
                break
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required()
def dashboard():
    data = load_data()
    user_id = session['user_id']
    user = data['users'].get(user_id)
    
    if user['role'] == 'admin':
        candidates = data['candidates']
        stats = {
            'total_candidates': len(candidates),
            'total_interviews': sum(len(c.get('interviews', [])) for c in candidates.values())
        }
        return render_template('dashboard.html', role='admin', stats=stats)
    else:
        candidate = data['candidates'].get(user_id, {'interviews': [], 'skills': []})
        interviews = candidate.get('interviews', [])
        avg_score = 0
        if interviews:
            avg_score = round(sum(iv['scores']['overall'] for iv in interviews) / len(interviews), 1)
        stats = {
            'total_interviews': len(interviews),
            'avg_score': avg_score
        }
        user_name = user.get('name', 'User')
        avatar_initials = ''.join(p[0].upper() for p in user_name.split()[:2])
        return render_template('dashboard.html', role='candidate', stats=stats,
                               candidate=candidate, user_name=user_name,
                               avatar_initials=avatar_initials)

# ── File validation helpers (no external library needed) ─────────
_FILE_SIGS = {
    b'%PDF':                           'pdf',
    b'\xd0\xcf\x11\xe0\xa1\xb1': 'doc',
    b'PK\x03\x04':                   'docx',
}
_RESUME_KW = [
    'experience','education','skills','employment','qualifications',
    'summary','objective','profile','projects','achievements',
    'certifications','email','phone','linkedin','github',
    'internship','degree','university','college','btech','bca',
    'mca','mba','bachelor','master','cgpa','gpa','responsibilities',
    'declaration','frameworks','tools','languages','career'
]

def _validate_resume_file(file, filename):
    """Check extension, size, and magic bytes. Returns (ok, error_msg)."""
    ext = filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    if ext not in ('pdf','doc','docx'):
        return False, 'Invalid file type. Please upload PDF, DOC, or DOCX only.'
    file.seek(0, os.SEEK_END)
    mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if mb > 10:
        return False, f'File too large ({mb:.1f} MB). Maximum allowed is 10 MB.'
    header = file.read(8)
    file.seek(0)
    real_type = next((t for sig, t in _FILE_SIGS.items() if header.startswith(sig)), None)
    if real_type is None:
        return False, 'File format not recognised. Please upload a genuine PDF or Word document.'
    return True, ''

def _text_is_resume(text):
    """Returns True if extracted text contains at least 3 resume keywords."""
    if not text or len(text.strip()) < 50:
        return False
    tl = text.lower()
    return sum(1 for kw in _RESUME_KW if kw in tl) >= 3

@app.route('/upload_resume', methods=['POST'])
@login_required(role='candidate')
def upload_resume():
    # Step 1 — file present?
    if 'resume' not in request.files or request.files['resume'].filename == '':
        flash('No file selected. Please choose a PDF, DOC, or DOCX resume.', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['resume']
    original_name = file.filename

    # Step 2 — extension, size, magic bytes
    ok, err = _validate_resume_file(file, original_name)
    if not ok:
        flash(f'❌ {err}', 'danger')
        return redirect(url_for('dashboard'))

    # Step 3 — save to disk
    filename = secure_filename(f"{session['user_id']}_{original_name}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Step 4 — extract text
    text = extract_text_from_pdf(filepath)
    if not text or len(text.strip()) < 50:
        try: os.remove(filepath)
        except: pass
        flash('❌ Could not read text from this file. It may be scanned, image-based, or password-protected. Please upload a text-based PDF.', 'danger')
        return redirect(url_for('dashboard'))

    # Step 5 — is it actually a resume?
    if not _text_is_resume(text):
        try: os.remove(filepath)
        except: pass
        flash('❌ This file does not appear to be a resume. Please upload your actual CV/Resume — it should contain sections like Skills, Education, Experience, Projects.', 'danger')
        return redirect(url_for('dashboard'))

    # Step 6 — extract skills
    skills = extract_skills_from_text(text)[:25]

    # Step 7 — save
    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    if not candidate:
        data['candidates'][session['user_id']] = {
            'user_id': session['user_id'],
            'resume_text': text[:1500],
            'skills': skills,
            'resume_filename': original_name,
            'interviews': [],
            'asked_questions': []
        }
    else:
        candidate['resume_text'] = text[:1500]
        candidate['skills'] = skills
        candidate['resume_filename'] = original_name
    save_data(data)

    session['has_resume'] = len(skills) > 0

    # Step 8 — flash result
    if skills:
        preview = ', '.join(skills[:6])
        flash(f'✅ Resume verified and uploaded! Found {len(skills)} skills: {preview}{"..." if len(skills) > 6 else "."}', 'success')
    else:
        flash('✅ Resume verified! No skills auto-detected — you can select topics manually on the Configure Interview page.', 'info')

    return redirect(url_for('dashboard'))

@app.route('/configure-interview')
@login_required(role='candidate')
def configure_interview():
    data = load_data()
    candidate = data['candidates'].get(session['user_id'], {})
    resume_skills = candidate.get('skills', [])
    
    # Pass both resume_skills and a flag indicating if resume exists
    return render_template('configure_interview.html', 
                         resume_skills=resume_skills,
                         has_resume=len(resume_skills) > 0)

@app.route('/start_interview', methods=['POST'])
@login_required(role='candidate')
def start_interview():
    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    
    if not candidate:
        flash('Candidate profile not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Collect selected topics and their counts
    selected_skills = {}
    
    # Debug print
    print("\n" + "="*50)
    print("FORM DATA RECEIVED:")
    
    # Process all form data
    for key, value in request.form.items():
        if key.startswith('tech_count_') or key.startswith('mgmt_count_') or \
           key.startswith('apt_count_') or key.startswith('soft_count_'):
            if value and int(value) > 0:
                skill = key.replace('tech_count_', '').replace('mgmt_count_', '')\
                          .replace('apt_count_', '').replace('soft_count_', '')
                selected_skills[skill] = int(value)
                print(f"  - {skill}: {value} questions")
    
    total_questions = sum(selected_skills.values())
    print(f"\nTOTAL QUESTIONS: {total_questions}")
    print("="*50)
    
    if total_questions == 0:
        flash('Please select at least one topic and set question count', 'warning')
        return redirect(url_for('configure_interview'))
    
    # Generate questions from bank
    questions = []
    used = set(candidate.get('asked_questions', []))
    
    for skill, count in selected_skills.items():
        topics = _resolve_topics(skill)
        if topics:
            # Gather pool from all resolved topics
            pool = []
            for topic in topics:
                pool.extend(QUESTION_BANK.get(topic, []))
            available = [q for q in pool if q not in used]
            random.shuffle(available)
            if len(available) >= count:
                picked = available[:count]
            else:
                picked = available[:]
                remaining = count - len(picked)
                for i in range(remaining):
                    picked.append(pool[i % len(pool)] if pool else f"Describe your experience with {skill.replace('_',' ')}.")
            questions.extend(picked)
            used.update(picked)
            print(f"✅ Added {count} questions for '{skill}' → topics: {topics}")
        else:
            print(f"⚠️ No CSV topic for '{skill}', using generic questions")
            label = skill.replace('_', ' ').title()
            fallbacks = [
                f"Describe your experience with {label}.",
                f"What are best practices in {label}?",
                f"Give an example of applying {label} in a real project.",
                f"What challenges have you faced with {label}?",
                f"How have you improved your {label} skills?",
            ]
            for i in range(count):
                questions.append(fallbacks[i % len(fallbacks)])
    
    # Shuffle all questions
    random.shuffle(questions)
    
    print(f"\n📝 Total questions generated: {len(questions)}")
    
    # Save to candidate
    candidate.setdefault('asked_questions', []).extend(questions)
    
    interview_id = str(uuid.uuid4())
    interview = {
        'id': interview_id,
        'date': datetime.datetime.now().isoformat(),
        'type': 'Custom Interview',
        'questions': [{'question': q, 'answer': ''} for q in questions],
        'scores': {'technical': 0, 'communication': 0, 'overall': 0},
        'result': 'pending',
        'feedback': '',
        'duration_seconds': 0
    }
    
    candidate['interviews'].append(interview)
    save_data(data)
    
    session['current_interview_id'] = interview_id
    session['interview_start_time'] = datetime.datetime.now().isoformat()
    
    flash(f'🎯 Interview started with {len(questions)} questions! Good luck!', 'success')
    return redirect(url_for('interview'))

@app.route('/interview')
@login_required(role='candidate')
def interview():
    interview_id = session.get('current_interview_id')
    if not interview_id:
        flash('No active interview', 'warning')
        return redirect(url_for('dashboard'))

    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    if not candidate:
        flash('Candidate not found', 'danger')
        return redirect(url_for('dashboard'))

    interview = None
    for iv in candidate.get('interviews', []):
        if iv['id'] == interview_id:
            interview = iv
            break
    
    if not interview:
        flash('Interview not found', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('interview.html', interview=interview)

@app.route('/save_answer', methods=['POST'])
@login_required(role='candidate')
def save_answer():
    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    interview_id = session.get('current_interview_id')
    interview = None
    for iv in candidate.get('interviews', []):
        if iv['id'] == interview_id:
            interview = iv
            break
    
    if not interview:
        return jsonify({'error': 'Interview not found'}), 404

    q_index = int(request.form.get('q_index', 0))
    answer = request.form.get('answer', '').strip()

    if 0 <= q_index < len(interview['questions']):
        interview['questions'][q_index]['answer'] = answer
        save_data(data)
        return jsonify({'status': 'ok'})
    
    return jsonify({'error': 'Invalid question index'}), 400

@app.route('/submit_interview', methods=['POST'])
@login_required(role='candidate')
def submit_interview():
    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    if not candidate:
        flash('Candidate not found', 'danger')
        return redirect(url_for('dashboard'))

    interview_id = session.get('current_interview_id')
    interview = None
    for iv in candidate.get('interviews', []):
        if iv['id'] == interview_id:
            interview = iv
            break
    
    if not interview:
        flash('Interview not found', 'danger')
        return redirect(url_for('dashboard'))

    # Calculate duration
    if session.get('interview_start_time'):
        start = datetime.datetime.fromisoformat(session['interview_start_time'])
        duration = int((datetime.datetime.now() - start).total_seconds())
        interview['duration_seconds'] = duration

    # Evaluate answers
    questions = interview['questions']
    tech_scores = []
    comm_scores = []
    per_question = []
    
    for q in questions:
        answer = q.get('answer', '').strip()
        if answer:
            word_count = len(answer.split())
            # Technical score based on length and keyword matching
            q_words = set(q['question'].lower().split())
            a_words = set(answer.lower().split())
            overlap = len(q_words & a_words)
            tech = min(100, word_count * 4 + overlap * 5)
            # Communication score based on length and structure
            comm = min(100, word_count * 3 + (10 if '.' in answer else 0) + (10 if ',' in answer else 0))
        else:
            tech, comm = 0, 0
        
        tech_scores.append(min(100, tech))
        comm_scores.append(min(100, comm))
        
        # Generate feedback
        if not answer:
            feedback = "❌ No answer provided. Always attempt every question."
        elif word_count < 15:
            feedback = "⚠️ Very brief answer. Add more details and examples."
        elif word_count < 30:
            feedback = "📝 Good start. Could include more specific examples."
        elif word_count < 60:
            feedback = "✅ Good answer. Well structured."
        else:
            feedback = "🌟 Excellent answer! Detailed and well explained."
        
        per_question.append({
            'technical_score': round(min(100, tech), 1),
            'communication_score': round(min(100, comm), 1),
            'feedback': feedback
        })
    
    avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0
    avg_comm = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0
    overall = round((avg_tech * 0.6 + avg_comm * 0.4), 1)
    
    interview['scores'] = {
        'technical': avg_tech,
        'communication': avg_comm,
        'overall': overall,
        'per_question': per_question
    }
    
    answered = sum(1 for q in questions if q.get('answer', '').strip())
    
    # Generate summary feedback
    feedback_lines = [
        f"✅ You answered {answered}/{len(questions)} questions.",
        f"📊 Overall Score: {overall}%",
        "",
        "📈 Performance Summary:"
    ]
    
    if avg_tech < 50:
        feedback_lines.append("• Technical knowledge needs improvement. Review core concepts.")
    else:
        feedback_lines.append("• Good technical understanding demonstrated.")
    
    if avg_comm < 50:
        feedback_lines.append("• Work on structuring answers with more clarity.")
    else:
        feedback_lines.append("• Clear communication style.")
    
    if answered < len(questions):
        feedback_lines.append(f"• {len(questions) - answered} questions left unanswered.")
    
    feedback_lines.append("")
    feedback_lines.append("📝 Detailed Feedback:")
    
    for i, pq in enumerate(per_question):
        status = "✓" if questions[i].get('answer', '').strip() else "✗"
        feedback_lines.append(f"Q{i+1} {status} [Tech: {pq['technical_score']}% | Comm: {pq['communication_score']}%]: {pq['feedback']}")
    
    interview['feedback'] = "\n".join(feedback_lines)
    interview['result'] = 'selected' if overall >= 60 else 'rejected'
    
    save_data(data)
    
    session.pop('current_interview_id', None)
    session.pop('interview_start_time', None)
    
    flash('Interview submitted successfully!', 'success')
    return redirect(url_for('results', interview_id=interview_id))

@app.route('/results/<interview_id>')
@login_required()
def results(interview_id):
    data = load_data()
    user_id = session['user_id']
    user = data['users'].get(user_id)

    interview = None
    candidate_name = user['name']

    if user['role'] == 'admin':
        for cid, cand in data['candidates'].items():
            for iv in cand.get('interviews', []):
                if iv['id'] == interview_id:
                    interview = iv
                    candidate_name = data['users'].get(cid, {}).get('name', 'Candidate')
                    break
            if interview:
                break
    else:
        candidate = data['candidates'].get(user_id, {})
        for iv in candidate.get('interviews', []):
            if iv['id'] == interview_id:
                interview = iv
                break

    if not interview:
        flash('Interview not found', 'danger')
        return redirect(url_for('dashboard'))

    first_name = candidate_name.split()[0] if candidate_name else 'Candidate'
    return render_template('results.html', interview=interview,
                           candidate_name=candidate_name, first_name=first_name)

@app.route('/admin')
@login_required(role='admin')
def admin_panel():
    data = load_data()
    candidates_list = []
    
    for uid, user in data['users'].items():
        if user['role'] == 'candidate':
            cand = data['candidates'].get(uid, {})
            interviews = cand.get('interviews', [])
            last = interviews[-1] if interviews else None
            candidates_list.append({
                'id': uid,
                'name': user['name'],
                'email': user['email'],
                'skills': cand.get('skills', [])[:5],  # Show first 5 skills
                'total_interviews': len(interviews),
                'last_score': last['scores']['overall'] if last else 'N/A',
                'result': last['result'] if last else 'N/A',
                'interview_id': last['id'] if last else None
            })
    
    return render_template('admin.html', candidates=candidates_list)

@app.route('/delete_candidate/<user_id>', methods=['POST'])
@login_required(role='admin')
def delete_candidate(user_id):
    data = load_data()
    if user_id in data['users'] and data['users'][user_id]['role'] == 'candidate':
        del data['users'][user_id]
        data['candidates'].pop(user_id, None)
        save_data(data)
        flash('Candidate deleted successfully', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/export_results')
@login_required(role='admin')
def export_results():
    import csv
    import io

    data = load_data()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Date', 'Score', 'Result', 'Duration (min)'])

    for uid, user in data['users'].items():
        if user['role'] == 'candidate':
            cand = data['candidates'].get(uid, {})
            for iv in cand.get('interviews', []):
                writer.writerow([
                    user['name'],
                    user['email'],
                    iv['date'][:10],
                    iv['scores']['overall'],
                    iv['result'],
                    iv.get('duration_seconds', 0)//60
                ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=smarthire_results.csv'}
    )
@app.route('/remove_resume', methods=['POST'])
@login_required(role='candidate')
def remove_resume():
    """Remove uploaded resume and clear skills"""
    data = load_data()
    candidate = data['candidates'].get(session['user_id'])
    
    if candidate:
        # Clear resume data
        candidate['resume_text'] = ''
        candidate['skills'] = []
        save_data(data)
        flash('Resume removed successfully. You can upload a new one anytime.', 'success')
    else:
        flash('Candidate not found', 'danger')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Check if PyPDF2 is installed
    try:
        import PyPDF2
    except ImportError:
        print("⚠️ PyPDF2 not installed. Resume parsing will be basic.")
        print("   Install with: pip install PyPDF2")
        
    
    app.run(debug=True)