from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from config import Config
import json
import random

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Association tables
classroom_members = db.Table('classroom_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'), primary_key=True)
)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    hearts = db.Column(db.Integer, default=5)
    level = db.Column(db.Integer, default=1)
    gems = db.Column(db.Integer, default=50)
    last_practice = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    progress = db.relationship('LessonProgress', backref='user', lazy=True)
    owned_classrooms = db.relationship('Classroom', backref='teacher', lazy=True)
    submissions = db.relationship('AssignmentSubmission', backref='student', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_xp(self, amount):
        self.xp += amount
        # Level up every 100 XP
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
            return True  # Leveled up
        return False

    def update_streak(self):
        today = datetime.utcnow().date()
        last = self.last_practice.date() if self.last_practice else None

        if last == today:
            return  # Already practiced today
        elif last == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1

        self.last_practice = datetime.utcnow()

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(10), unique=True, nullable=False)
    language = db.Column(db.String(20), default='spanish')  # spanish, english
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship('User', secondary=classroom_members, backref='classrooms')
    assignments = db.relationship('Assignment', backref='classroom', lazy=True)
    announcements = db.relationship('Announcement', backref='classroom', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(20), nullable=False)  # spanish, english
    category = db.Column(db.String(50))  # basics, food, travel, etc.
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    xp_reward = db.Column(db.Integer, default=10)
    content = db.Column(db.Text)  # JSON content
    order = db.Column(db.Integer, default=0)

    progress = db.relationship('LessonProgress', backref='lesson', lazy=True)

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=100)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lesson = db.relationship('Lesson')
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True)

class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded = db.Column(db.Boolean, default=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer, default=50)

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    achievement = db.relationship('Achievement')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's classrooms
    if current_user.role == 'teacher':
        classrooms = current_user.owned_classrooms
    else:
        classrooms = current_user.classrooms

    # Get available lessons
    lessons = Lesson.query.order_by(Lesson.order).all()

    # Get user progress
    progress = {p.lesson_id: p for p in current_user.progress}

    # Calculate stats
    completed_lessons = len([p for p in current_user.progress if p.completed])
    total_lessons = len(lessons)

    return render_template('dashboard.html',
                         classrooms=classrooms,
                         lessons=lessons,
                         progress=progress,
                         completed=completed_lessons,
                         total=total_lessons)

@app.route('/learn/<language>')
@login_required
def learn(language):
    lessons = Lesson.query.filter_by(language=language).order_by(Lesson.order).all()
    progress = {p.lesson_id: p for p in current_user.progress}

    # Group lessons by category
    categories = {}
    for lesson in lessons:
        if lesson.category not in categories:
            categories[lesson.category] = []
        categories[lesson.category].append(lesson)

    return render_template('learn.html',
                         language=language,
                         categories=categories,
                         progress=progress)

@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    content = json.loads(lesson.content) if lesson.content else []

    return render_template('lesson.html', lesson=lesson, content=content)

@app.route('/api/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.json
    score = data.get('score', 0)

    # Find or create progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)

    progress.attempts += 1
    progress.score = score

    if score > progress.best_score:
        progress.best_score = score

    # Mark as completed if score >= 70%
    if score >= 70:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

        # Award XP
        xp_earned = lesson.xp_reward
        leveled_up = current_user.add_xp(xp_earned)

        # Update streak
        current_user.update_streak()

        db.session.commit()

        return jsonify({
            'success': True,
            'xp_earned': xp_earned,
            'leveled_up': leveled_up,
            'new_level': current_user.level,
            'streak': current_user.streak
        })

    db.session.commit()
    return jsonify({'success': True, 'passed': False})

# Classroom routes
@app.route('/classroom/create', methods=['GET', 'POST'])
@login_required
def create_classroom():
    if current_user.role != 'teacher':
        flash('Only teachers can create classrooms', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        language = request.form.get('language', 'spanish')

        # Generate unique code
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        while Classroom.query.filter_by(code=code).first():
            code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

        classroom = Classroom(
            name=name,
            description=description,
            code=code,
            language=language,
            teacher_id=current_user.id
        )
        db.session.add(classroom)
        db.session.commit()

        flash(f'Classroom created! Code: {code}', 'success')
        return redirect(url_for('view_classroom', classroom_id=classroom.id))

    return render_template('create_classroom.html')

@app.route('/classroom/join', methods=['GET', 'POST'])
@login_required
def join_classroom():
    if request.method == 'POST':
        code = request.form.get('code').upper()
        classroom = Classroom.query.filter_by(code=code).first()

        if not classroom:
            flash('Invalid classroom code', 'error')
            return redirect(url_for('join_classroom'))

        if current_user in classroom.members:
            flash('You are already in this classroom', 'info')
        else:
            classroom.members.append(current_user)
            db.session.commit()
            flash(f'Joined {classroom.name}!', 'success')

        return redirect(url_for('view_classroom', classroom_id=classroom.id))

    return render_template('join_classroom.html')

@app.route('/classroom/<int:classroom_id>')
@login_required
def view_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)

    # Check access
    if current_user != classroom.teacher and current_user not in classroom.members:
        flash('You do not have access to this classroom', 'error')
        return redirect(url_for('dashboard'))

    announcements = Announcement.query.filter_by(classroom_id=classroom_id).order_by(Announcement.created_at.desc()).all()
    assignments = Assignment.query.filter_by(classroom_id=classroom_id).order_by(Assignment.due_date).all()

    return render_template('classroom.html',
                         classroom=classroom,
                         announcements=announcements,
                         assignments=assignments)

@app.route('/classroom/<int:classroom_id>/announcement', methods=['POST'])
@login_required
def create_announcement(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)

    if current_user != classroom.teacher:
        flash('Only teachers can create announcements', 'error')
        return redirect(url_for('view_classroom', classroom_id=classroom_id))

    title = request.form.get('title')
    content = request.form.get('content')

    announcement = Announcement(
        classroom_id=classroom_id,
        title=title,
        content=content
    )
    db.session.add(announcement)
    db.session.commit()

    flash('Announcement posted!', 'success')
    return redirect(url_for('view_classroom', classroom_id=classroom_id))

@app.route('/classroom/<int:classroom_id>/assignment', methods=['GET', 'POST'])
@login_required
def create_assignment(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)

    if current_user != classroom.teacher:
        flash('Only teachers can create assignments', 'error')
        return redirect(url_for('view_classroom', classroom_id=classroom_id))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        points = int(request.form.get('points', 100))
        lesson_id = request.form.get('lesson_id')

        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None

        assignment = Assignment(
            classroom_id=classroom_id,
            title=title,
            description=description,
            due_date=due_date,
            points=points,
            lesson_id=lesson_id if lesson_id else None
        )
        db.session.add(assignment)
        db.session.commit()

        flash('Assignment created!', 'success')
        return redirect(url_for('view_classroom', classroom_id=classroom_id))

    lessons = Lesson.query.filter_by(language=classroom.language).all()
    return render_template('create_assignment.html', classroom=classroom, lessons=lessons)

@app.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    classroom = assignment.classroom

    # Check access
    if current_user != classroom.teacher and current_user not in classroom.members:
        flash('You do not have access to this assignment', 'error')
        return redirect(url_for('dashboard'))

    # Get submission if student
    submission = None
    if current_user.role == 'student':
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.id
        ).first()

    # Get all submissions if teacher
    submissions = []
    if current_user == classroom.teacher:
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()

    return render_template('assignment.html',
                         assignment=assignment,
                         submission=submission,
                         submissions=submissions)

@app.route('/assignment/<int:assignment_id>/submit', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    score = request.form.get('score', 0)

    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()

    if not submission:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            score=score
        )
        db.session.add(submission)
    else:
        submission.score = score
        submission.submitted_at = datetime.utcnow()

    db.session.commit()
    flash('Assignment submitted!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/assignment/<int:assignment_id>/grade/<int:submission_id>', methods=['POST'])
@login_required
def grade_submission(assignment_id, submission_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    if current_user != assignment.classroom.teacher:
        flash('Only teachers can grade', 'error')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))

    submission = AssignmentSubmission.query.get_or_404(submission_id)
    submission.score = int(request.form.get('score', 0))
    submission.feedback = request.form.get('feedback')
    submission.graded = True

    db.session.commit()
    flash('Submission graded!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.xp.desc()).limit(50).all()
    return render_template('leaderboard.html', users=users)

@app.route('/profile')
@login_required
def profile():
    achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', achievements=achievements)

@app.route('/api/practice', methods=['POST'])
@login_required
def practice():
    """Quick practice endpoint for daily practice"""
    current_user.update_streak()
    current_user.add_xp(5)
    db.session.commit()

    return jsonify({
        'streak': current_user.streak,
        'xp': current_user.xp
    })

# Initialize database and sample data
def init_db():
    with app.app_context():
        db.create_all()

        # Check if lessons already exist
        if Lesson.query.first():
            return

        # Spanish lessons
        spanish_lessons = [
            {
                'title': 'Basics 1',
                'description': 'Learn basic Spanish greetings and introductions',
                'language': 'spanish',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 10,
                'order': 1,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you say "Hello" in Spanish?',
                        'options': ['Hola', 'Adiós', 'Gracias', 'Por favor'],
                        'correct': 0,
                        'audio': None
                    },
                    {
                        'type': 'translate',
                        'question': 'Translate to Spanish: "Good morning"',
                        'answer': 'Buenos días',
                        'alternatives': ['buenos dias', 'buenas dias']
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'What does "Gracias" mean?',
                        'options': ['Please', 'Thank you', 'Sorry', 'Hello'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Me ___ Juan. (My name is Juan)',
                        'answer': 'llamo',
                        'hint': 'llamar = to call'
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['Hola', 'Hello'],
                            ['Adiós', 'Goodbye'],
                            ['Por favor', 'Please'],
                            ['Gracias', 'Thank you']
                        ]
                    }
                ])
            },
            {
                'title': 'Basics 2',
                'description': 'Common phrases and expressions',
                'language': 'spanish',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 10,
                'order': 2,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you ask "How are you?" in Spanish?',
                        'options': ['¿Cómo estás?', '¿Dónde estás?', '¿Qué hora es?', '¿Cuánto cuesta?'],
                        'correct': 0
                    },
                    {
                        'type': 'translate',
                        'question': 'Translate: "I am fine"',
                        'answer': 'Estoy bien',
                        'alternatives': ['estoy bien', 'Estoy Bien']
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'What does "Mucho gusto" mean?',
                        'options': ['See you later', 'Nice to meet you', 'Good night', 'I am sorry'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': '¿Cómo te ___? (What is your name?)',
                        'answer': 'llamas',
                        'hint': 'You use "tú" form here'
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'Select the correct response to "¿Cómo estás?"',
                        'options': ['Bien, gracias', 'De nada', 'Hasta luego', 'Mucho gusto'],
                        'correct': 0
                    }
                ])
            },
            {
                'title': 'Numbers',
                'description': 'Learn Spanish numbers 1-20',
                'language': 'spanish',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 15,
                'order': 3,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'What is "cinco" in English?',
                        'options': ['Three', 'Five', 'Seven', 'Nine'],
                        'correct': 1
                    },
                    {
                        'type': 'translate',
                        'question': 'Write the number 12 in Spanish',
                        'answer': 'doce',
                        'alternatives': ['Doce']
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['uno', 'one'],
                            ['diez', 'ten'],
                            ['veinte', 'twenty'],
                            ['quince', 'fifteen']
                        ]
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you say "18" in Spanish?',
                        'options': ['dieciséis', 'diecisiete', 'dieciocho', 'diecinueve'],
                        'correct': 2
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Tres más cuatro son ___ (3 + 4 = ?)',
                        'answer': 'siete',
                        'hint': 'The number 7'
                    }
                ])
            },
            {
                'title': 'Food & Drinks',
                'description': 'Vocabulary for food and beverages',
                'language': 'spanish',
                'category': 'Food',
                'difficulty': 2,
                'xp_reward': 15,
                'order': 4,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'What is "agua" in English?',
                        'options': ['Milk', 'Juice', 'Water', 'Coffee'],
                        'correct': 2
                    },
                    {
                        'type': 'translate',
                        'question': 'Translate: "bread"',
                        'answer': 'pan',
                        'alternatives': ['Pan', 'el pan']
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['manzana', 'apple'],
                            ['leche', 'milk'],
                            ['café', 'coffee'],
                            ['arroz', 'rice']
                        ]
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you say "I want" in Spanish?',
                        'options': ['Yo tengo', 'Yo quiero', 'Yo como', 'Yo bebo'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Quiero ___ café, por favor. (I want a coffee, please)',
                        'answer': 'un',
                        'hint': 'Indefinite article for masculine nouns'
                    }
                ])
            },
            {
                'title': 'Family',
                'description': 'Learn family member vocabulary',
                'language': 'spanish',
                'category': 'Family',
                'difficulty': 2,
                'xp_reward': 15,
                'order': 5,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'What is "madre" in English?',
                        'options': ['Father', 'Mother', 'Sister', 'Brother'],
                        'correct': 1
                    },
                    {
                        'type': 'translate',
                        'question': 'Translate: "brother"',
                        'answer': 'hermano',
                        'alternatives': ['Hermano', 'el hermano']
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['padre', 'father'],
                            ['hermana', 'sister'],
                            ['abuelo', 'grandfather'],
                            ['hijo', 'son']
                        ]
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you say "my family" in Spanish?',
                        'options': ['su familia', 'mi familia', 'tu familia', 'la familia'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Tengo dos ___. (I have two daughters)',
                        'answer': 'hijas',
                        'hint': 'Feminine plural of "hijo"'
                    }
                ])
            },
            {
                'title': 'Travel',
                'description': 'Essential travel vocabulary',
                'language': 'spanish',
                'category': 'Travel',
                'difficulty': 3,
                'xp_reward': 20,
                'order': 6,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': 'What is "aeropuerto" in English?',
                        'options': ['Hotel', 'Airport', 'Restaurant', 'Station'],
                        'correct': 1
                    },
                    {
                        'type': 'translate',
                        'question': 'Translate: "Where is the hotel?"',
                        'answer': '¿Dónde está el hotel?',
                        'alternatives': ['Donde esta el hotel', 'donde está el hotel']
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'How do you say "ticket" in Spanish?',
                        'options': ['billete', 'maleta', 'pasaporte', 'equipaje'],
                        'correct': 0
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['tren', 'train'],
                            ['avión', 'airplane'],
                            ['autobús', 'bus'],
                            ['taxi', 'taxi']
                        ]
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Necesito un ___ para Madrid. (I need a ticket to Madrid)',
                        'answer': 'billete',
                        'hint': 'Another word for "ticket"'
                    }
                ])
            }
        ]

        # English lessons (for Spanish speakers)
        english_lessons = [
            {
                'title': 'Basics 1',
                'description': 'Learn basic English greetings',
                'language': 'english',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 10,
                'order': 1,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se dice "Hola" en inglés?',
                        'options': ['Hello', 'Goodbye', 'Thanks', 'Please'],
                        'correct': 0
                    },
                    {
                        'type': 'translate',
                        'question': 'Traduce al inglés: "Buenos días"',
                        'answer': 'Good morning',
                        'alternatives': ['good morning']
                    },
                    {
                        'type': 'multiple_choice',
                        'question': '¿Qué significa "Thank you"?',
                        'options': ['Por favor', 'Gracias', 'De nada', 'Lo siento'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'My ___ is Maria. (Me llamo Maria)',
                        'answer': 'name',
                        'hint': 'nombre en inglés'
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['Hello', 'Hola'],
                            ['Goodbye', 'Adiós'],
                            ['Please', 'Por favor'],
                            ['Sorry', 'Lo siento']
                        ]
                    }
                ])
            },
            {
                'title': 'Basics 2',
                'description': 'Common English expressions',
                'language': 'english',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 10,
                'order': 2,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se pregunta "¿Cómo estás?" en inglés?',
                        'options': ['How are you?', 'Where are you?', 'What time is it?', 'How much?'],
                        'correct': 0
                    },
                    {
                        'type': 'translate',
                        'question': 'Traduce: "Estoy bien"',
                        'answer': 'I am fine',
                        'alternatives': ["I'm fine", 'i am fine']
                    },
                    {
                        'type': 'multiple_choice',
                        'question': '¿Qué significa "Nice to meet you"?',
                        'options': ['Hasta luego', 'Mucho gusto', 'Buenas noches', 'Lo siento'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'What is your ___? (¿Cómo te llamas?)',
                        'answer': 'name',
                        'hint': 'Lo que identifica a una persona'
                    },
                    {
                        'type': 'multiple_choice',
                        'question': 'Selecciona la respuesta correcta para "How are you?"',
                        'options': ["I'm fine, thanks", "You're welcome", 'See you later', 'Nice to meet you'],
                        'correct': 0
                    }
                ])
            },
            {
                'title': 'Numbers',
                'description': 'Learn English numbers 1-20',
                'language': 'english',
                'category': 'Basics',
                'difficulty': 1,
                'xp_reward': 15,
                'order': 3,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se dice "cinco" en inglés?',
                        'options': ['Three', 'Five', 'Seven', 'Nine'],
                        'correct': 1
                    },
                    {
                        'type': 'translate',
                        'question': 'Escribe el número 12 en inglés',
                        'answer': 'twelve',
                        'alternatives': ['Twelve']
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['one', 'uno'],
                            ['ten', 'diez'],
                            ['twenty', 'veinte'],
                            ['fifteen', 'quince']
                        ]
                    },
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se dice "18" en inglés?',
                        'options': ['sixteen', 'seventeen', 'eighteen', 'nineteen'],
                        'correct': 2
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'Three plus four equals ___',
                        'answer': 'seven',
                        'hint': 'El número 7'
                    }
                ])
            },
            {
                'title': 'Food & Drinks',
                'description': 'Food vocabulary in English',
                'language': 'english',
                'category': 'Food',
                'difficulty': 2,
                'xp_reward': 15,
                'order': 4,
                'content': json.dumps([
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se dice "agua" en inglés?',
                        'options': ['Milk', 'Juice', 'Water', 'Coffee'],
                        'correct': 2
                    },
                    {
                        'type': 'translate',
                        'question': 'Traduce: "pan"',
                        'answer': 'bread',
                        'alternatives': ['Bread']
                    },
                    {
                        'type': 'match',
                        'pairs': [
                            ['apple', 'manzana'],
                            ['milk', 'leche'],
                            ['coffee', 'café'],
                            ['rice', 'arroz']
                        ]
                    },
                    {
                        'type': 'multiple_choice',
                        'question': '¿Cómo se dice "Quiero" en inglés?',
                        'options': ['I have', 'I want', 'I eat', 'I drink'],
                        'correct': 1
                    },
                    {
                        'type': 'fill_blank',
                        'question': 'I want ___ coffee, please.',
                        'answer': 'a',
                        'hint': 'Artículo indefinido'
                    }
                ])
            }
        ]

        # Add all lessons
        for lesson_data in spanish_lessons + english_lessons:
            lesson = Lesson(**lesson_data)
            db.session.add(lesson)

        # Create achievements
        achievements = [
            {'name': 'First Steps', 'description': 'Complete your first lesson', 'icon': 'star', 'xp_reward': 25},
            {'name': 'Week Warrior', 'description': 'Maintain a 7-day streak', 'icon': 'fire', 'xp_reward': 100},
            {'name': 'Perfect Score', 'description': 'Get 100% on a lesson', 'icon': 'trophy', 'xp_reward': 50},
            {'name': 'Social Learner', 'description': 'Join your first classroom', 'icon': 'users', 'xp_reward': 25},
            {'name': 'Rising Star', 'description': 'Reach level 5', 'icon': 'medal', 'xp_reward': 75},
        ]

        for ach_data in achievements:
            achievement = Achievement(**ach_data)
            db.session.add(achievement)

        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
