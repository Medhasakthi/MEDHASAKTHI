#!/usr/bin/env python3
"""
Local development startup script for MEDHASAKTHI backend
This script handles database setup and starts the server with minimal dependencies
"""

import os
import sys
import sqlite3
from pathlib import Path

def setup_local_environment():
    """Setup local development environment"""
    print("🚀 Setting up MEDHASAKTHI local development environment...")
    
    # Copy local environment file
    env_local = Path(".env.local")
    env_file = Path(".env")
    
    if env_local.exists():
        print("📝 Copying local environment configuration...")
        with open(env_local, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print("📁 Created uploads directory")
    
    # Setup SQLite database
    db_path = Path("medhasakthi_dev.db")
    if not db_path.exists():
        print("🗄️ Creating SQLite database...")
        conn = sqlite3.connect(str(db_path))
        
        # Create basic tables for development
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert a test user
        conn.execute("""
            INSERT OR IGNORE INTO users (email, name, user_type) 
            VALUES ('admin@medhasakthi.com', 'Admin User', 'admin')
        """)
        
        conn.commit()
        conn.close()
        print("✅ SQLite database created with test data")
    else:
        print("✅ SQLite database already exists")

def start_server():
    """Start the FastAPI server"""
    print("\n🌟 Starting MEDHASAKTHI backend server...")
    print("📍 Server will be available at: http://localhost:8080")
    print("📚 API Documentation: http://localhost:8080/docs")
    print("🔄 Auto-reload enabled for development")
    print("\n" + "="*50)
    
    # Start uvicorn server
    os.system("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    try:
        setup_local_environment()
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have installed the requirements: pip install -r requirements.txt")
        sys.exit(1)
