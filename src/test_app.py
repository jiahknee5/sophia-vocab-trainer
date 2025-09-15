#!/usr/bin/env python3
"""
Simple test to verify the application works
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, VocabularyWord, Milestone
from datetime import date

def test_app():
    """Test basic app functionality"""
    print("Testing Sophia's Vocabulary Trainer...")
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")
        
        # Add a test word
        test_word = VocabularyWord(
            word="perseverance",
            definition="persistence in doing something despite difficulty or delay in achieving success"
        )
        db.session.add(test_word)
        db.session.commit()
        print("✓ Test word added")
        
        # Query the word
        word = VocabularyWord.query.filter_by(word="perseverance").first()
        assert word is not None
        print(f"✓ Word retrieved: {word.word}")
        
        # Check milestones
        milestones = Milestone.query.all()
        print(f"✓ Found {len(milestones)} milestones")
        
        # Clean up test data
        db.session.delete(word)
        db.session.commit()
        print("✓ Test data cleaned up")
        
    print("\n✅ All tests passed! The app is ready to use.")
    print("\nRun ./run.sh to start the application")

if __name__ == "__main__":
    test_app()