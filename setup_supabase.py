#!/usr/bin/env python3
"""
Setup script for Supabase database
"""
import os
import sys
from urllib.parse import urlparse, parse_qs

def setup_supabase():
    print("🚀 Supabase Setup for Sophia's Vocabulary Trainer")
    print("=" * 50)
    
    # Supabase project details
    project_ref = "xxvawcehwzpyeggpfvth"
    
    print(f"\n📋 Your Supabase project reference: {project_ref}")
    print("\n⚡ To get your database password:")
    print("1. Go to https://app.supabase.com/project/xxvawcehwzpyeggpfvth")
    print("2. Navigate to Settings → Database")
    print("3. Copy your database password\n")
    
    # Get password from user
    password = input("Please enter your Supabase database password: ").strip()
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    # Construct the DATABASE_URL
    database_url = f"postgresql://postgres:{password}@db.xxvawcehwzpyeggpfvth.supabase.co:5432/postgres"
    
    print(f"\n✅ Your DATABASE_URL has been constructed!")
    print("\n📝 Next steps:")
    print("1. Add this to Vercel environment variables:")
    print(f"   vercel env add DATABASE_URL production")
    print(f"   (paste the URL when prompted)")
    
    print("\n2. Or add it manually in Vercel dashboard:")
    print("   - Go to your Vercel project settings")
    print("   - Navigate to Environment Variables")
    print("   - Add DATABASE_URL with the value above")
    
    # Ask if user wants to save locally for testing
    save_local = input("\n💾 Save to .env.local for local testing? (y/n): ").strip().lower()
    
    if save_local == 'y':
        with open('.env.local', 'w') as f:
            f.write(f"DATABASE_URL={database_url}\n")
        print("✅ Saved to .env.local")
        
    print("\n🔧 Once you've added the DATABASE_URL to Vercel, run:")
    print("   python create_tables.py")
    print("   to create the database tables!\n")

if __name__ == "__main__":
    setup_supabase()