# 🗄️ Vercel Postgres Setup Guide

## Why Vercel Postgres?

The serverless function crashed because SQLite (file-based database) doesn't persist between function invocations in Vercel's serverless environment. Vercel Postgres provides a persistent, managed database solution.

## Step-by-Step Setup

### 1. Create Vercel Postgres Database

1. Go to your Vercel project dashboard: https://vercel.com/jiahknee5/sophia-vocab-trainer
2. Click on the **"Storage"** tab
3. Click **"Create Database"**
4. Select **"Postgres"**
5. Choose a database name (e.g., `sophia-vocab-db`)
6. Select the closest region to you
7. Click **"Create"**

### 2. Environment Variables

After creating the database, Vercel will automatically add these environment variables to your project:
- `POSTGRES_URL` - The connection string
- `POSTGRES_PRISMA_URL` - For Prisma ORM (we don't need this)
- `POSTGRES_URL_NON_POOLING` - Direct connection (we don't need this)
- `POSTGRES_USER` - Database username
- `POSTGRES_HOST` - Database host
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DATABASE` - Database name

### 3. Update Environment Variables

1. In the Vercel dashboard, go to **"Settings"** → **"Environment Variables"**
2. Add a new variable:
   - Name: `DATABASE_URL`
   - Value: Copy the value from `POSTGRES_URL`
   - Environment: Production, Preview, Development

### 4. Initialize Database Tables

#### Option A: Using Vercel CLI (Recommended)
```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Pull environment variables
vercel env pull .env.local

# Run the table creation script
python create_tables.py
```

#### Option B: Using Vercel's Query Interface
1. In your Vercel project, go to **"Storage"** → Your database
2. Click on **"Query"** tab
3. Copy and run this SQL:

```sql
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

-- Insert default milestones
INSERT INTO milestone (name, target_date, target_words)
VALUES 
    ('Winter Goal', '2025-12-31', 365),
    ('Spring Goal', '2026-03-31', 455),
    ('Summer Goal', '2026-06-30', 545)
ON CONFLICT DO NOTHING;
```

### 5. Deploy the Updated Code

```bash
# Commit the changes
git add .
git commit -m "feat: migrate to Vercel Postgres for persistent storage"
git push origin main
```

Vercel will automatically redeploy with the new PostgreSQL configuration.

## Troubleshooting

### Connection Issues
- Make sure `DATABASE_URL` environment variable is set
- The app automatically converts `postgres://` to `postgresql://` for compatibility
- Connection pooling is enabled with `pool_pre_ping` for reliability

### Migration from SQLite
If you had existing data in SQLite, you'll need to manually re-enter it in the new PostgreSQL database.

### Performance
- PostgreSQL queries might be slightly slower than local SQLite
- But you get persistence and reliability in serverless environment
- Connection pooling helps maintain performance

## Local Development

For local development, you can either:
1. Use the Vercel Postgres database (pull env vars with `vercel env pull`)
2. Use a local PostgreSQL instance
3. Keep using SQLite locally (it will still work)

## Verification

After deployment, verify everything works:
1. Visit https://home.johnnycchung.com (or your Vercel URL)
2. Add a test vocabulary word
3. Refresh the page - the word should persist
4. Try the quiz feature
5. Check progress tracking

## Data Backup

Consider setting up regular backups:
1. Vercel Postgres includes automatic daily backups (Pro plan)
2. You can manually export data using pg_dump
3. The Query interface allows CSV exports