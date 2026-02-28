"""
resume_parser.py — SmartHire AI
Validates uploaded file, checks it's a resume, extracts skills.
No external magic/libmagic dependency — uses file header bytes.
"""

import re
import os

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────
# FILE VALIDATION
# ─────────────────────────────────────────────────────────────────

# Magic bytes (file signatures) for each allowed type
FILE_SIGNATURES = {
    b'%PDF':                        'pdf',   # PDF
    b'\xd0\xcf\x11\xe0\xa1\xb1':   'doc',   # MS Office .doc
    b'PK\x03\x04':                  'docx',  # ZIP-based .docx
}

MAX_FILE_SIZE_MB = 10


def _get_file_type(file) -> str | None:
    """
    Read first 8 bytes to detect real file type.
    Returns 'pdf', 'doc', 'docx', or None if unrecognised.
    """
    file.seek(0)
    header = file.read(8)
    file.seek(0)
    for sig, ftype in FILE_SIGNATURES.items():
        if header.startswith(sig):
            return ftype
    return None


def _get_size_mb(file) -> float:
    file.seek(0, os.SEEK_END)
    size = file.tell() / (1024 * 1024)
    file.seek(0)
    return size


def validate_file(file, filename: str) -> tuple[bool, str]:
    """
    Run all pre-save checks on the uploaded file object.
    Returns (ok: bool, error_message: str).
    """
    # 1. Extension check
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ('pdf', 'doc', 'docx'):
        return False, 'Invalid file type. Please upload a PDF, DOC, or DOCX resume.'

    # 2. Size check
    size_mb = _get_size_mb(file)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f'File too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB.'

    # 3. Real file type (magic bytes) — catches renamed files
    real_type = _get_file_type(file)
    if real_type is None:
        return False, 'File format not recognised. Please upload a valid PDF or Word document.'

    # Extension must match the actual file type
    ext_to_real = {'pdf': 'pdf', 'doc': 'doc', 'docx': 'docx'}
    if ext_to_real.get(ext) != real_type and not (ext == 'docx' and real_type == 'docx'):
        # Allow .docx to be real 'docx' (PK signature)
        if not (real_type == 'docx' and ext in ('docx',)):
            return False, f'File extension ".{ext}" does not match the actual file contents. Please upload a genuine document.'

    return True, ''


# ─────────────────────────────────────────────────────────────────
# TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file. Returns empty string on failure."""
    if not PYPDF2_AVAILABLE:
        print('⚠ PyPDF2 not installed — cannot extract PDF text.')
        return ''
    try:
        text = ''
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text.strip()
    except Exception as e:
        print(f'PDF extraction error: {e}')
        return ''


# ─────────────────────────────────────────────────────────────────
# RESUME CONTENT CHECK
# ─────────────────────────────────────────────────────────────────

# Keywords that appear in virtually every resume
_RESUME_KEYWORDS = [
    'experience', 'education', 'skills', 'work history', 'employment',
    'qualifications', 'summary', 'objective', 'profile', 'projects',
    'achievements', 'certifications', 'contact', 'email', 'phone',
    'linkedin', 'github', 'professional', 'technical skills', 'soft skills',
    'internship', 'intern', 'degree', 'university', 'college', 'btech',
    'bca', 'mca', 'mba', 'bachelor', 'master', 'gpa', 'cgpa',
    'languages', 'frameworks', 'tools', 'references', 'declaration',
    'hobbies', 'interests', 'career', 'position', 'role', 'responsibilities'
]

# Minimum keyword matches required to accept as resume
_MIN_RESUME_KEYWORDS = 3


def is_resume(text: str) -> tuple[bool, list]:
    """
    Check if extracted text looks like a resume.
    Returns (is_resume: bool, matched_keywords: list).
    """
    if not text or len(text.strip()) < 50:
        return False, []

    text_lower = text.lower()
    matched = [kw for kw in _RESUME_KEYWORDS if kw in text_lower]

    return len(matched) >= _MIN_RESUME_KEYWORDS, matched


# ─────────────────────────────────────────────────────────────────
# SKILLS DATABASE
# ─────────────────────────────────────────────────────────────────

# Each key = the skill name stored in data.json
# Each list = words/phrases whose presence in the resume text signals this skill
_SKILLS = {
    # ── Technical ──────────────────────────────────────────────
    'python':          ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit'],
    'java':            ['java', 'spring', 'hibernate', 'maven', 'gradle', 'jvm', 'junit'],
    'javascript':      ['javascript', 'js', 'node.js', 'nodejs', 'es6', 'ecmascript'],
    'typescript':      ['typescript', 'ts'],
    'c':               ['c programming', 'c language'],
    'cpp':             ['c++', 'cpp'],
    'csharp':          ['c#', 'csharp', '.net', 'dotnet', 'asp.net'],
    'go':              ['golang', 'go language', ' go '],
    'ruby':            ['ruby', 'rails', 'ruby on rails'],
    'php':             ['php', 'laravel', 'symfony', 'codeigniter'],
    'kotlin':          ['kotlin'],
    'swift':           ['swift', 'swiftui', 'ios development'],
    'scala':           ['scala', 'akka', 'spark'],
    'rust':            ['rust', 'cargo'],
    'r':               ['r programming', 'rstudio', 'r language', 'tidyverse'],
    'dart':            ['dart', 'flutter'],

    'html':            ['html', 'html5'],
    'css':             ['css', 'css3', 'sass', 'scss', 'less'],
    'react':           ['react', 'reactjs', 'react.js', 'redux', 'next.js', 'nextjs'],
    'angular':         ['angular', 'angularjs'],
    'vue':             ['vue', 'vuejs', 'vue.js', 'nuxt'],
    'spring':          ['spring boot', 'spring mvc', 'spring framework', 'spring security'],
    'django':          ['django'],
    'flask':           ['flask'],
    'nodejs':          ['node.js', 'nodejs', 'express.js', 'express'],
    'bootstrap':       ['bootstrap'],
    'tailwind':        ['tailwind'],

    'sql':             ['sql', 'structured query', 'database query'],
    'mysql':           ['mysql'],
    'postgresql':      ['postgresql', 'postgres'],
    'mongodb':         ['mongodb', 'mongoose'],
    'redis':           ['redis'],
    'sqlite':          ['sqlite'],
    'oracle':          ['oracle db', 'oracle database', 'pl/sql'],
    'nosql':           ['nosql'],
    'firebase':        ['firebase', 'firestore'],
    'elasticsearch':   ['elasticsearch', 'elastic search', 'kibana'],

    'aws':             ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds'],
    'azure':           ['azure', 'microsoft azure'],
    'gcp':             ['gcp', 'google cloud', 'cloud platform'],
    'docker':          ['docker', 'containerization', 'dockerfile'],
    'kubernetes':      ['kubernetes', 'k8s', 'kubectl'],
    'git':             ['git', 'github', 'gitlab', 'version control'],
    'linux':           ['linux', 'ubuntu', 'centos', 'unix', 'bash scripting'],
    'jenkins':         ['jenkins', 'ci/cd', 'pipeline'],
    'terraform':       ['terraform', 'infrastructure as code'],

    'machine learning': ['machine learning', 'ml', 'neural network', 'deep learning', 'ai model',
                         'tensorflow', 'pytorch', 'scikit-learn', 'sklearn', 'keras'],
    'data science':    ['data science', 'data scientist', 'data analysis', 'pandas', 'numpy',
                        'matplotlib', 'seaborn', 'tableau', 'power bi', 'powerbi'],
    'android':         ['android', 'android studio', 'android development'],
    'flutter':         ['flutter', 'dart'],
    'react native':    ['react native'],

    # ── Management ─────────────────────────────────────────────
    'leadership':      ['leadership', 'leader', 'led a team', 'team lead', 'managing team'],
    'team_management': ['team management', 'managed team', 'team of', 'supervised', 'oversaw'],
    'project_management': ['project management', 'project manager', 'pmp', 'agile', 'scrum', 'kanban', 'jira'],
    'communication':   ['communication', 'presented', 'presentation', 'verbal', 'written communication',
                        'stakeholder', 'client communication'],
    'problem_solving': ['problem solving', 'problem-solving', 'troubleshooting', 'analytical',
                        'root cause', 'debugging'],
    'teamwork':        ['teamwork', 'team player', 'collaboration', 'collaborated', 'cross-functional'],
    'time_management': ['time management', 'deadline', 'prioritization', 'organized'],
    'adaptability':    ['adaptability', 'adaptable', 'flexible', 'quick learner', 'fast learner'],
    'critical_thinking': ['critical thinking', 'analytical thinking', 'logical thinking'],
    'decision_making': ['decision making', 'decision-making', 'strategic decisions'],
    'training':        ['training', 'mentoring', 'mentor', 'coached', 'onboarding'],
    'recruitment':     ['recruitment', 'hiring', 'talent acquisition', 'hr', 'human resources'],
    'agile':           ['agile', 'scrum', 'sprint', 'retrospective', 'standup'],
    'conflict_resolution': ['conflict resolution', 'conflict management', 'mediation'],
    'strategic_planning': ['strategic planning', 'strategy', 'roadmap', 'long-term'],
    'risk_management': ['risk management', 'risk assessment', 'mitigation'],
    'negotiation':     ['negotiation', 'negotiated', 'vendor negotiation'],
    'change_management': ['change management', 'organizational change', 'transformation'],
}


def extract_skills(text: str) -> list:
    """
    Match resume text against skills database.
    Returns flat list of skill keys found (e.g. ['python', 'react', 'leadership']).
    """
    if not text:
        return []

    text_lower = text.lower()
    found = []

    for skill_key, signals in _SKILLS.items():
        for signal in signals:
            # Word-boundary match for short single words, substring for multi-word phrases
            if ' ' in signal or len(signal) <= 2:
                if signal in text_lower:
                    found.append(skill_key)
                    break
            else:
                pattern = r'\b' + re.escape(signal) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found.append(skill_key)
                    break

    # Deduplicate while preserving order
    seen = set()
    result = []
    for s in found:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result