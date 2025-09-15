"""
Sophia's PSAT/SHSAT Vocabulary Trainer
A simple web application to help Sophia learn vocabulary words for test prep
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
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
    """Model for vocabulary words"""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.Date, default=date.today)
    times_reviewed = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    last_reviewed = db.Column(db.DateTime)
    mastery_level = db.Column(db.Integer, default=0)  # 0-100

    def get_accuracy(self):
        """Calculate accuracy percentage"""
        if self.times_reviewed == 0:
            return 0
        return int((self.times_correct / self.times_reviewed) * 100)

class QuizHistory(db.Model):
    """Model for quiz history"""
    id = db.Column(db.Integer, primary_key=True)
    date_taken = db.Column(db.DateTime, default=datetime.now)
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    
class Milestone(db.Model):
    """Model for learning milestones"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    target_words = db.Column(db.Integer, nullable=False)
    
# Routes
@app.route('/')
def index():
    """Home page with dashboard"""
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
    
    return render_template('index.html', 
                         total_words=total_words,
                         words_today=words_today,
                         progress_percentage=progress_percentage,
                         milestones=milestones,
                         avg_mastery=avg_mastery)

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    """Add a new vocabulary word"""
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        definition = request.form.get('definition', '').strip()
        
        if word and definition:
            # Check if word already exists
            existing = VocabularyWord.query.filter_by(word=word).first()
            if existing:
                flash(f'The word "{word}" already exists!', 'warning')
            else:
                new_word = VocabularyWord(word=word, definition=definition)
                db.session.add(new_word)
                db.session.commit()
                flash(f'Successfully added "{word}"!', 'success')
                return redirect(url_for('view_words'))
        else:
            flash('Please provide both word and definition!', 'error')
    
    return render_template('add_word.html')

@app.route('/words')
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
    
    return render_template('view_words.html', words=words, sort_by=sort_by)

@app.route('/delete_word/<int:word_id>')
def delete_word(word_id):
    """Delete a vocabulary word"""
    word = VocabularyWord.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    flash(f'Deleted "{word.word}"', 'info')
    return redirect(url_for('view_words'))

@app.route('/quiz')
def quiz():
    """Start a vocabulary quiz"""
    # Get words that need review (prioritize less mastered words)
    words = VocabularyWord.query.order_by(VocabularyWord.mastery_level.asc()).limit(10).all()
    
    if len(words) < 4:
        flash('You need at least 4 words to start a quiz!', 'warning')
        return redirect(url_for('index'))
    
    # Select a random word for the question
    question_word = random.choice(words)
    
    # Create multiple choice options
    options = [question_word]
    other_words = [w for w in words if w.id != question_word.id]
    options.extend(random.sample(other_words, min(3, len(other_words))))
    random.shuffle(options)
    
    return render_template('quiz.html', 
                         question_word=question_word,
                         options=options)

@app.route('/quiz/check', methods=['POST'])
def check_quiz():
    """Check quiz answer"""
    word_id = request.form.get('word_id', type=int)
    answer_id = request.form.get('answer_id', type=int)
    
    word = VocabularyWord.query.get_or_404(word_id)
    word.times_reviewed += 1
    word.last_reviewed = datetime.now()
    
    is_correct = (word_id == answer_id)
    if is_correct:
        word.times_correct += 1
        word.mastery_level = min(word.mastery_level + 10, 100)
        message = "Correct! Great job! 🌟"
    else:
        word.mastery_level = max(word.mastery_level - 5, 0)
        correct_word = VocabularyWord.query.get(word_id)
        message = f"Not quite. The answer was: {correct_word.definition}"
    
    db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'message': message,
        'mastery_level': word.mastery_level
    })

@app.route('/progress')
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
    
    return render_template('progress.html',
                         total_words=len(words),
                         total_reviews=total_reviews,
                         overall_accuracy=overall_accuracy,
                         mastery_levels=mastery_levels,
                         recent_quizzes=recent_quizzes)

@app.route('/milestones')
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
    
    return render_template('milestones.html', 
                         milestone_data=milestone_data,
                         total_words=total_words)

# Initialize database and add default milestones
def initialize_database():
    """Create tables and add default milestones"""
    with app.app_context():
        db.create_all()
        
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

# Call initialization when module loads
with app.app_context():
    initialize_database()

if __name__ == '__main__':
    # Run on all interfaces for Tailscale access
    # use_reloader=False to avoid path issues
    app.run(host='0.0.0.0', port=5005, debug=True, use_reloader=False)