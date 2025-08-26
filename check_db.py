#!/usr/bin/env python3
"""
Check and fix database schema
"""

import sqlite3

def check_schema():
    conn = sqlite3.connect('routes.db')
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check job table structure
    try:
        cursor.execute("PRAGMA table_info(job);")
        columns = cursor.fetchall()
        print("\nJob table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) - NOT NULL: {col[3]}, PK: {col[5]}")
    except:
        print("Job table doesn't exist")
    
    # Check user table structure
    try:
        cursor.execute("PRAGMA table_info(user);")
        columns = cursor.fetchall()
        print("\nUser table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) - NOT NULL: {col[3]}, PK: {col[5]}")
    except:
        print("User table doesn't exist")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
