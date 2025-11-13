#!/usr/bin/env python3
"""Database initialization script.

Creates required tables if they do not already exist.

Run: python3 init_db.py
"""
from db_config import get_db_connection
import mysql.connector
from datetime import datetime


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table (used by app.py)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        First_Name VARCHAR(100) NOT NULL,
        Last_Name VARCHAR(100),
        email_id VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        phone VARCHAR(25),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    ''')

    # Study plans - metadata for a user's submitted plan (start/end dates, preferred days, status)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Study_Plans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        plan_name VARCHAR(255),
        start_date DATE,
        end_date DATE,
        -- comma-separated preferred days e.g. 'Mon,Tue,Sat' or JSON string
        preferred_days VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(32) DEFAULT 'draft',
        FOREIGN KEY (user_id) REFERENCES User_Data(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    # Subjects table - one row per subject for a user (now optionally tied to a Study_Plans entry)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Study_Subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        plan_id INT,
        subject_name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User_Data(id) ON DELETE CASCADE,
        FOREIGN KEY (plan_id) REFERENCES Study_Plans(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    # Topics table - topics under a subject as added by user (initial plan)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Study_Topics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_id INT NOT NULL,
        topic_name VARCHAR(255) NOT NULL,
        initial_weightage FLOAT DEFAULT 0,
        normalized_weightage FLOAT DEFAULT 0,
        from_date DATE,
        to_date DATE,
        skipped_days INT DEFAULT 0,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES Study_Subjects(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    # Schedule entries - generated timetable entries (subject + topic + dates + weightage)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Study_Schedule (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        subject VARCHAR(255) NOT NULL,
        topic VARCHAR(255) NOT NULL,
        from_date DATE NOT NULL,
        to_date DATE NOT NULL,
        weightage FLOAT DEFAULT 0,
        normalized_weightage FLOAT DEFAULT 0,
        skipped_days INT DEFAULT 0,
        status VARCHAR(32) DEFAULT 'scheduled',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User_Data(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    # Daily progress aggregation used by dashboard (one row per user per day)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Daily_Progress (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        day_date DATE NOT NULL,
        total_tasks INT DEFAULT 0,
        completed_tasks INT DEFAULT 0,
        pending_from_previous INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY user_day_unique (user_id, day_date),
        FOREIGN KEY (user_id) REFERENCES User_Data(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    # Account changes (for email change verification flow)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Account_Changes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        field_changed VARCHAR(64) NOT NULL,
        old_value VARCHAR(255),
        new_value VARCHAR(255),
        verification_token VARCHAR(512),
        token_expires_at DATETIME,
        processed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User_Data(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print('Initializing database and creating tables if they do not exist...')
    try:
        create_tables()
        print('Done: tables ensured.')
    except mysql.connector.Error as e:
        print('MySQL Error:', e)
    except Exception as e:
        print('Error:', e)
