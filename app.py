"""
Sophia's PSAT/SHSAT Vocabulary Trainer - Root App for Vercel
"""

import os
import random
import math
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app with explicit paths
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sophia-vocab-trainer-2024')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:////tmp/vocab_trainer.db')
# Fix for Vercel Postgres URL format
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class VocabularyWord(db.Model):
    """Model for vocabulary words with adaptive learning features"""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.Text, nullable=False)
    synonyms = db.Column(db.Text, default='')  # Comma-separated list
    antonyms = db.Column(db.Text, default='')  # Comma-separated list
    example_sentence = db.Column(db.Text, default='')  # Example usage
    date_added = db.Column(db.Date, default=date.today)
    times_reviewed = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    last_reviewed = db.Column(db.DateTime)
    mastery_level = db.Column(db.Integer, default=0)  # 0-100

    # Adaptive learning fields
    difficulty_score = db.Column(db.Float, default=50.0)  # 0-100, dynamically calculated
    streak = db.Column(db.Integer, default=0)  # Consecutive correct answers
    last_response_time = db.Column(db.Float)  # Seconds to answer
    review_interval = db.Column(db.Integer, default=1)  # Days until next review (spaced repetition)
    next_review_date = db.Column(db.Date)

    def get_accuracy(self):
        """Calculate accuracy percentage"""
        if self.times_reviewed == 0:
            return 0
        return int((self.times_correct / self.times_reviewed) * 100)

    def calculate_difficulty(self):
        """Calculate difficulty based on community performance"""
        if self.times_reviewed < 3:
            return 50.0  # Default for new words

        accuracy = self.get_accuracy()
        # Inverse relationship: lower accuracy = higher difficulty
        base_difficulty = 100 - accuracy

        # Adjust based on response time (if available)
        if self.last_response_time:
            if self.last_response_time > 10:  # Slow response
                base_difficulty += 10
            elif self.last_response_time < 3:  # Fast response
                base_difficulty -= 10

        return max(10, min(100, base_difficulty))

    def update_spaced_repetition(self, correct):
        """Update spaced repetition interval based on performance"""
        if correct:
            # Fibonacci-like sequence for increasing intervals
            intervals = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
            current_idx = min(self.streak, len(intervals) - 1)
            self.review_interval = intervals[current_idx]
        else:
            # Reset to frequent review on mistake
            self.review_interval = 1

        self.next_review_date = date.today() + timedelta(days=self.review_interval)

class QuizHistory(db.Model):
    """Model for quiz history"""
    id = db.Column(db.Integer, primary_key=True)
    date_taken = db.Column(db.DateTime, default=datetime.now)
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    difficulty_level = db.Column(db.String(20))  # Easy, Medium, Hard, Expert
    avg_response_time = db.Column(db.Float)

class UserProfile(db.Model):
    """Model for user gamification profile"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), default="Sophia")

    # Gamification metrics
    level = db.Column(db.Integer, default=1)
    experience_points = db.Column(db.Integer, default=0)
    total_words_learned = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date)

    # Adaptive learning parameters
    current_difficulty = db.Column(db.Float, default=30.0)  # 0-100
    confidence_score = db.Column(db.Float, default=50.0)  # 0-100
    learning_rate = db.Column(db.Float, default=1.0)  # Multiplier for XP

    # Achievements
    badges_earned = db.Column(db.Text, default="")  # JSON string of badge IDs

    def calculate_level(self):
        """Calculate level based on XP using logarithmic progression"""
        # Level up formula: Level = floor(sqrt(XP/100))
        import math
        return max(1, int(math.sqrt(self.experience_points / 100)) + 1)

    def add_experience(self, base_xp, difficulty_multiplier=1.0):
        """Add experience with difficulty multiplier"""
        xp_gained = int(base_xp * difficulty_multiplier * self.learning_rate)
        self.experience_points += xp_gained

        # Check for level up
        new_level = self.calculate_level()
        if new_level > self.level:
            self.level = new_level
            return True, xp_gained  # Level up occurred
        return False, xp_gained

    def update_confidence(self, performance):
        """Update confidence based on recent performance"""
        # Exponential moving average
        alpha = 0.3  # Learning rate for confidence
        self.confidence_score = (alpha * performance) + ((1 - alpha) * self.confidence_score)
        self.confidence_score = max(0, min(100, self.confidence_score))

class Milestone(db.Model):
    """Model for learning milestones"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    target_words = db.Column(db.Integer, nullable=False)
    
# Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'database_url': bool(os.environ.get('DATABASE_URL')),
        'template_folder': app.template_folder,
        'root_path': app.root_path,
        'cwd': os.getcwd(),
        'dir_contents': os.listdir('.')
    })

@app.route('/')
def home():
    """Main landing page with menu"""
    return render_template('home.html')

@app.route('/vocabulary')
def vocabulary_index():
    """Vocabulary trainer dashboard"""
    total_words = VocabularyWord.query.count()
    words_today = VocabularyWord.query.filter_by(date_added=date.today()).count()
    
    # Calculate progress
    start_date = date(2024, 1, 1)  # Adjust as needed
    days_elapsed = (date.today() - start_date).days
    target_pace = days_elapsed  # 1 word per day
    progress_percentage = min((total_words / target_pace * 100) if target_pace > 0 else 0, 100)
    
    # Get milestones
    milestones = Milestone.query.order_by(Milestone.target_date).all()
    
    # Calculate average mastery
    words = VocabularyWord.query.all()
    avg_mastery = sum(w.mastery_level for w in words) / len(words) if words else 0
    
    return render_template('vocabulary/index.html', 
                         total_words=total_words,
                         words_today=words_today,
                         progress_percentage=progress_percentage,
                         milestones=milestones,
                         avg_mastery=avg_mastery)

@app.route('/vocabulary/add_word', methods=['GET', 'POST'])
def add_word():
    """Add a new vocabulary word"""
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        definition = request.form.get('definition', '').strip()
        synonyms = request.form.get('synonyms', '').strip()
        antonyms = request.form.get('antonyms', '').strip()
        example_sentence = request.form.get('example_sentence', '').strip()

        if word and definition:
            # Check if word already exists
            existing = VocabularyWord.query.filter_by(word=word).first()
            if existing:
                flash(f'The word "{word}" already exists!', 'warning')
            else:
                new_word = VocabularyWord(
                    word=word,
                    definition=definition,
                    synonyms=synonyms,
                    antonyms=antonyms,
                    example_sentence=example_sentence,
                    next_review_date=date.today() + timedelta(days=1)
                )
                db.session.add(new_word)
                db.session.commit()
                flash(f'Successfully added "{word}"!', 'success')
                return redirect(url_for('view_words'))
        else:
            flash('Please provide both word and definition!', 'error')

    return render_template('vocabulary/add_word.html')

@app.route('/vocabulary/words')
def view_words():
    """View all vocabulary words"""
    sort_by = request.args.get('sort', 'date_desc')
    
    if sort_by == 'date_asc':
        words = VocabularyWord.query.order_by(VocabularyWord.date_added.asc()).all()
    elif sort_by == 'alpha':
        words = VocabularyWord.query.order_by(VocabularyWord.word.asc()).all()
    elif sort_by == 'mastery':
        words = VocabularyWord.query.order_by(VocabularyWord.mastery_level.desc()).all()
    else:  # date_desc
        words = VocabularyWord.query.order_by(VocabularyWord.date_added.desc()).all()
    
    return render_template('vocabulary/view_words.html', words=words, sort_by=sort_by)

@app.route('/vocabulary/edit_word/<int:word_id>', methods=['GET', 'POST'])
def edit_word(word_id):
    """Edit an existing vocabulary word"""
    word = VocabularyWord.query.get_or_404(word_id)

    if request.method == 'POST':
        word.word = request.form.get('word', '').strip()
        word.definition = request.form.get('definition', '').strip()
        word.synonyms = request.form.get('synonyms', '').strip()
        word.antonyms = request.form.get('antonyms', '').strip()
        word.example_sentence = request.form.get('example_sentence', '').strip()

        if word.word and word.definition:
            db.session.commit()
            flash(f'Successfully updated "{word.word}"!', 'success')
            return redirect(url_for('view_words'))
        else:
            flash('Word and definition are required!', 'error')

    return render_template('vocabulary/edit_word.html', word=word)

@app.route('/vocabulary/delete_word/<int:word_id>')
def delete_word(word_id):
    """Delete a vocabulary word - with protection for important words"""
    word = VocabularyWord.query.get_or_404(word_id)

    # Optional: Add protection for high-mastery words
    if word.mastery_level >= 80:
        flash(f'Are you sure you want to delete "{word.word}"? It has {word.mastery_level}% mastery!', 'warning')

    word_name = word.word
    db.session.delete(word)
    db.session.commit()
    flash(f'Deleted "{word_name}"', 'info')
    return redirect(url_for('view_words'))

@app.route('/vocabulary/quiz')
def quiz():
    """Start an adaptive vocabulary quiz"""
    # Get or create user profile
    user = UserProfile.query.first()
    if not user:
        user = UserProfile()
        db.session.add(user)
        db.session.commit()

    # Check streak
    if user.last_study_date != date.today():
        if user.last_study_date == date.today() - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_study_date = date.today()
        user.longest_streak = max(user.longest_streak, user.current_streak)
        db.session.commit()

    # Adaptive word selection based on user's current difficulty level
    all_words = VocabularyWord.query.all()

    if len(all_words) < 4:
        flash('You need at least 4 words to start a quiz!', 'warning')
        return redirect(url_for('vocabulary_index'))

    # Calculate each word's priority score for selection
    word_priorities = []
    for word in all_words:
        # Factors for word selection:
        # 1. Spaced repetition: Is it time to review?
        days_since_review = (date.today() - word.last_reviewed.date()).days if word.last_reviewed else 999
        needs_review = days_since_review >= word.review_interval

        # 2. Difficulty match: How close is word difficulty to user's level?
        word.difficulty_score = word.calculate_difficulty()
        difficulty_match = 100 - abs(word.difficulty_score - user.current_difficulty)

        # 3. Mastery gap: Lower mastery = higher priority
        mastery_gap = 100 - word.mastery_level

        # 4. Recent mistakes: Boost if recently answered incorrectly
        mistake_boost = 50 if word.streak == 0 and word.times_reviewed > 0 else 0

        # Calculate priority score
        priority = (
            (needs_review * 100) +  # Highest weight for spaced repetition
            (difficulty_match * 0.5) +  # Medium weight for difficulty matching
            (mastery_gap * 0.3) +  # Lower weight for mastery
            mistake_boost
        )

        word_priorities.append((word, priority))

    # Sort by priority and select top words for quiz pool
    word_priorities.sort(key=lambda x: x[1], reverse=True)
    quiz_pool = [w[0] for w in word_priorities[:min(20, len(word_priorities))]]

    # Select question word with some randomness to avoid predictability
    if random.random() < 0.8:  # 80% chance to pick from top priority
        question_word = quiz_pool[0]
    else:  # 20% chance for variety
        question_word = random.choice(quiz_pool[:5])

    # Adaptive difficulty for wrong answers
    difficulty_level = get_difficulty_level(user.confidence_score)

    # Create multiple choice options with adaptive difficulty
    options = [question_word]

    # Get distractor words based on difficulty
    other_words = [w for w in all_words if w.id != question_word.id]

    if difficulty_level == "Expert":
        # Expert: Very similar meanings or commonly confused words
        # Sort by similarity (you could implement semantic similarity here)
        distractors = random.sample(other_words, min(3, len(other_words)))
    elif difficulty_level == "Hard":
        # Hard: Mix of similar and different words
        distractors = random.sample(other_words, min(3, len(other_words)))
    elif difficulty_level == "Medium":
        # Medium: Reasonably different words
        distractors = sorted(other_words, key=lambda w: abs(w.mastery_level - 50))[:10]
        distractors = random.sample(distractors, min(3, len(distractors)))
    else:  # Easy
        # Easy: Very different, well-mastered words as distractors
        distractors = sorted(other_words, key=lambda w: -w.mastery_level)[:10]
        distractors = random.sample(distractors, min(3, len(distractors)))

    options.extend(distractors)
    random.shuffle(options)

    return render_template('vocabulary/quiz.html',
                         question_word=question_word,
                         options=options,
                         user=user,
                         difficulty=difficulty_level)

def get_difficulty_level(confidence_score):
    """Get difficulty level based on confidence score"""
    if confidence_score >= 80:
        return "Expert"
    elif confidence_score >= 60:
        return "Hard"
    elif confidence_score >= 40:
        return "Medium"
    else:
        return "Easy"

@app.route('/vocabulary/quiz/check', methods=['POST'])
def check_quiz():
    """Check quiz answer with adaptive learning updates"""
    word_id = request.form.get('word_id', type=int)
    answer_id = request.form.get('answer_id', type=int)
    response_time = request.form.get('response_time', type=float, default=5.0)

    word = VocabularyWord.query.get_or_404(word_id)
    user = UserProfile.query.first()
    if not user:
        user = UserProfile()
        db.session.add(user)

    # Update word statistics
    word.times_reviewed += 1
    word.last_reviewed = datetime.now()
    word.last_response_time = response_time

    is_correct = (word_id == answer_id)

    # Calculate XP and difficulty adjustments
    base_xp = 10
    difficulty_bonus = 1.0

    if is_correct:
        word.times_correct += 1
        word.streak += 1

        # Adaptive mastery increase based on streak
        mastery_increase = 10 + (word.streak * 2)  # Bonus for streaks
        word.mastery_level = min(word.mastery_level + mastery_increase, 100)

        # XP calculation with bonuses
        if response_time < 3:
            difficulty_bonus = 1.5  # Fast response bonus
            message = "⚡ Lightning fast! Excellent! 🌟"
        elif response_time < 5:
            difficulty_bonus = 1.2
            message = "Correct! Great job! 🌟"
        else:
            message = "Correct! Well done! ✨"

        # Streak bonus
        if word.streak >= 3:
            difficulty_bonus += 0.5
            message += f" (🔥 {word.streak} streak!)"

        # Update user confidence (increase)
        user.update_confidence(min(100, user.confidence_score + 5))

        # Adjust difficulty upward if doing well
        if user.confidence_score > 70:
            user.current_difficulty = min(100, user.current_difficulty + 2)

    else:
        word.streak = 0
        word.mastery_level = max(word.mastery_level - 5, 0)
        correct_word = VocabularyWord.query.get(word_id)
        message = f"Not quite. The answer was: {correct_word.definition}"

        # Reduce XP for incorrect answers
        base_xp = 3

        # Update user confidence (decrease)
        user.update_confidence(max(0, user.confidence_score - 10))

        # Adjust difficulty downward if struggling
        if user.confidence_score < 30:
            user.current_difficulty = max(10, user.current_difficulty - 5)
        else:
            user.current_difficulty = max(10, user.current_difficulty - 2)

    # Update spaced repetition
    word.update_spaced_repetition(is_correct)
    word.difficulty_score = word.calculate_difficulty()

    # Add experience points
    level_up, xp_gained = user.add_experience(base_xp, difficulty_bonus)

    # Check for achievements
    achievements = []
    if level_up:
        achievements.append({"type": "level_up", "level": user.level})
    if word.mastery_level >= 100 and is_correct:
        achievements.append({"type": "word_mastered", "word": word.word})
    if word.streak == 5:
        achievements.append({"type": "streak_5", "word": word.word})

    db.session.commit()

    return jsonify({
        'correct': is_correct,
        'message': message,
        'mastery_level': word.mastery_level,
        'correct_definition': word.definition,
        'xp_gained': xp_gained,
        'user_level': user.level,
        'user_xp': user.experience_points,
        'streak': word.streak,
        'achievements': achievements,
        'confidence': user.confidence_score,
        'difficulty': get_difficulty_level(user.confidence_score)
    })

@app.route('/vocabulary/quiz/complete', methods=['POST'])
def complete_quiz():
    """Record quiz completion"""
    score = request.form.get('score', type=int)
    total = request.form.get('total', type=int)

    if score is not None and total is not None:
        quiz_result = QuizHistory(
            score=score,
            total_questions=total,
            date_taken=datetime.now()
        )
        db.session.add(quiz_result)
        db.session.commit()

    return jsonify({'success': True})

@app.route('/vocabulary/progress')
def progress():
    """View learning progress"""
    words = VocabularyWord.query.all()
    
    # Calculate statistics
    total_reviews = sum(w.times_reviewed for w in words)
    total_correct = sum(w.times_correct for w in words)
    overall_accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
    
    # Words by mastery level
    mastery_levels = {
        'Learning (0-25%)': len([w for w in words if w.mastery_level <= 25]),
        'Practicing (26-50%)': len([w for w in words if 25 < w.mastery_level <= 50]),
        'Good (51-75%)': len([w for w in words if 50 < w.mastery_level <= 75]),
        'Mastered (76-100%)': len([w for w in words if w.mastery_level > 75])
    }
    
    # Recent quiz history
    recent_quizzes = QuizHistory.query.order_by(QuizHistory.date_taken.desc()).limit(10).all()
    
    return render_template('vocabulary/progress.html',
                         total_words=len(words),
                         total_reviews=total_reviews,
                         overall_accuracy=overall_accuracy,
                         mastery_levels=mastery_levels,
                         recent_quizzes=recent_quizzes)

@app.route('/vocabulary/milestones')
def milestones():
    """View and manage milestones"""
    milestones = Milestone.query.order_by(Milestone.target_date).all()
    total_words = VocabularyWord.query.count()

    milestone_data = []
    for milestone in milestones:
        days_until = (milestone.target_date - date.today()).days
        words_needed = milestone.target_words - total_words
        words_per_day = words_needed / days_until if days_until > 0 else 0

        milestone_data.append({
            'milestone': milestone,
            'days_until': days_until,
            'words_needed': max(0, words_needed),
            'words_per_day': max(1, int(words_per_day + 0.5))  # Round up
        })

    return render_template('vocabulary/milestones.html',
                         milestone_data=milestone_data,
                         total_words=total_words)

@app.route('/vocabulary/milestones/add', methods=['GET', 'POST'])
def add_milestone():
    """Add a new milestone"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        target_date_str = request.form.get('target_date')
        target_words = request.form.get('target_words', type=int)

        if name and target_date_str and target_words:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                new_milestone = Milestone(name=name, target_date=target_date, target_words=target_words)
                db.session.add(new_milestone)
                db.session.commit()
                flash(f'Successfully added milestone "{name}"!', 'success')
                return redirect(url_for('milestones'))
            except ValueError:
                flash('Invalid date format!', 'error')
        else:
            flash('Please fill in all fields!', 'error')

    return render_template('vocabulary/add_milestone.html')

@app.route('/vocabulary/milestones/edit/<int:milestone_id>', methods=['GET', 'POST'])
def edit_milestone(milestone_id):
    """Edit an existing milestone"""
    milestone = Milestone.query.get_or_404(milestone_id)
    total_words = VocabularyWord.query.count()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        target_date_str = request.form.get('target_date')
        target_words = request.form.get('target_words', type=int)

        if name and target_date_str and target_words:
            try:
                milestone.name = name
                milestone.target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                milestone.target_words = target_words
                db.session.commit()
                flash(f'Successfully updated milestone "{name}"!', 'success')
                return redirect(url_for('milestones'))
            except ValueError:
                flash('Invalid date format!', 'error')
        else:
            flash('Please fill in all fields!', 'error')

    # Calculate words needed info for display
    days_until = (milestone.target_date - date.today()).days
    words_needed = milestone.target_words - total_words

    return render_template('vocabulary/edit_milestone.html',
                         milestone=milestone,
                         total_words=total_words,
                         days_until=days_until,
                         words_needed=words_needed)

@app.route('/vocabulary/milestones/delete/<int:milestone_id>')
def delete_milestone(milestone_id):
    """Delete a milestone"""
    milestone = Milestone.query.get_or_404(milestone_id)
    db.session.delete(milestone)
    db.session.commit()
    flash(f'Deleted milestone "{milestone.name}"', 'info')
    return redirect(url_for('milestones'))

# Initialize database and add default milestones
def initialize_database():
    """Create tables and add default milestones with migration support"""
    try:
        # Create all tables (won't affect existing ones)
        db.create_all()

        # Safely add missing columns for existing tables
        try:
            # Test if columns exist by trying to query them
            test_word = VocabularyWord.query.first()
            if test_word:
                # Try to access new fields - will error if they don't exist
                _ = test_word.difficulty_score
        except:
            # If error, columns don't exist - need migration
            try:
                # Try to add missing columns
                with db.engine.begin() as conn:
                    # SQLite doesn't support information_schema, so we try each column
                    migration_commands = [
                        "ALTER TABLE vocabulary_word ADD COLUMN difficulty_score FLOAT DEFAULT 50.0",
                        "ALTER TABLE vocabulary_word ADD COLUMN streak INTEGER DEFAULT 0",
                        "ALTER TABLE vocabulary_word ADD COLUMN last_response_time FLOAT",
                        "ALTER TABLE vocabulary_word ADD COLUMN review_interval INTEGER DEFAULT 1",
                        "ALTER TABLE vocabulary_word ADD COLUMN next_review_date DATE",
                        "ALTER TABLE vocabulary_word ADD COLUMN synonyms TEXT DEFAULT ''",
                        "ALTER TABLE vocabulary_word ADD COLUMN antonyms TEXT DEFAULT ''",
                        "ALTER TABLE vocabulary_word ADD COLUMN example_sentence TEXT DEFAULT ''"
                    ]
                    for cmd in migration_commands:
                        try:
                            conn.execute(db.text(cmd))
                        except:
                            pass  # Column already exists
            except Exception as e:
                print(f"Migration warning: {e}")

        # Ensure UserProfile exists
        if UserProfile.query.count() == 0:
            default_user = UserProfile()
            db.session.add(default_user)
            db.session.commit()

        # Add default milestones if they don't exist
        if Milestone.query.count() == 0:
            milestones = [
                Milestone(name="Winter Goal", target_date=date(2025, 12, 31), target_words=365),
                Milestone(name="Spring Goal", target_date=date(2026, 3, 31), target_words=455),
                Milestone(name="Summer Goal", target_date=date(2026, 6, 30), target_words=545)
            ]
            for m in milestones:
                db.session.add(m)
            db.session.commit()
    except Exception as e:
        # In serverless, database might not be ready yet
        print(f"Database initialization warning: {e}")

# Track if database has been initialized
_db_initialized = False

@app.before_request
def ensure_database():
    """Ensure database is initialized before handling requests"""
    global _db_initialized
    if not _db_initialized and request.endpoint not in ['health', 'debug']:
        try:
            initialize_database()
            _db_initialized = True
        except Exception as e:
            app.logger.warning(f"Database initialization deferred: {e}")

# For local development, initialize immediately
if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    # Run on all interfaces for Tailscale access
    app.run(host='0.0.0.0', port=5005, debug=True)