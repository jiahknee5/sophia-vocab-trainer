#!/usr/bin/env python3
"""
Database table creation script for Vercel Postgres
Run this after setting up your Vercel Postgres database
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date

# Load environment variables
load_dotenv()

def create_database_tables():
    """Create all necessary tables for the vocabulary trainer"""
    
    # Get database URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    # Fix for Vercel Postgres URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Create engine
    engine = create_engine(database_url)
    
    # SQL statements to create tables
    create_tables_sql = """
    -- Create vocabulary_word table
    CREATE TABLE IF NOT EXISTS vocabulary_word (
        id SERIAL PRIMARY KEY,
        word VARCHAR(100) NOT NULL UNIQUE,
        definition TEXT NOT NULL,
        date_added DATE DEFAULT CURRENT_DATE,
        times_reviewed INTEGER DEFAULT 0,
        times_correct INTEGER DEFAULT 0,
        last_reviewed TIMESTAMP,
        mastery_level INTEGER DEFAULT 0
    );
    
    -- Create quiz_history table
    CREATE TABLE IF NOT EXISTS quiz_history (
        id SERIAL PRIMARY KEY,
        date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        score INTEGER,
        total_questions INTEGER
    );
    
    -- Create milestone table
    CREATE TABLE IF NOT EXISTS milestone (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        target_date DATE NOT NULL,
        target_words INTEGER NOT NULL
    );
    
    -- Insert default milestones if not exist
    INSERT INTO milestone (name, target_date, target_words)
    SELECT 'Winter Goal', '2025-12-31'::date, 365
    WHERE NOT EXISTS (SELECT 1 FROM milestone WHERE name = 'Winter Goal');
    
    INSERT INTO milestone (name, target_date, target_words)
    SELECT 'Spring Goal', '2026-03-31'::date, 455
    WHERE NOT EXISTS (SELECT 1 FROM milestone WHERE name = 'Spring Goal');
    
    INSERT INTO milestone (name, target_date, target_words)
    SELECT 'Summer Goal', '2026-06-30'::date, 545
    WHERE NOT EXISTS (SELECT 1 FROM milestone WHERE name = 'Summer Goal');
    """
    
    try:
        with engine.connect() as conn:
            # Execute the SQL statements
            for statement in create_tables_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
                    conn.commit()
        
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_database_tables()