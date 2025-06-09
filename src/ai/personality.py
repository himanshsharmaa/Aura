# Personality modeling 

import sqlite3
import json
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Personality:
    def __init__(self, db_path="data/aura.db"):
        """
        Initialize the personality system with memory storage.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    user_input TEXT,
                    aura_response TEXT,
                    emotion TEXT,
                    context TEXT
                )
            ''')
            
            # Create preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    key TEXT,
                    value TEXT,
                    last_updated DATETIME,
                    UNIQUE(category, key)
                )
            ''')
            
            # Create routines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    schedule TEXT,
                    last_executed DATETIME,
                    is_active BOOLEAN
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
            
    def store_interaction(self, user_input, aura_response, emotion=None, context=None):
        """
        Store a conversation interaction in the database.
        
        Args:
            user_input (str): The user's input
            aura_response (str): Aura's response
            emotion (str): Detected emotion (optional)
            context (str): Additional context (optional)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (timestamp, user_input, aura_response, emotion, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), user_input, aura_response, emotion, context))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            
    def get_recent_interactions(self, limit=10):
        """
        Retrieve recent interactions from the database.
        
        Args:
            limit (int): Number of recent interactions to retrieve
            
        Returns:
            list: List of recent interactions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_input, aura_response, emotion, context
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            interactions = cursor.fetchall()
            conn.close()
            
            return [{
                'timestamp': row[0],
                'user_input': row[1],
                'aura_response': row[2],
                'emotion': row[3],
                'context': row[4]
            } for row in interactions]
            
        except Exception as e:
            logger.error(f"Error retrieving interactions: {e}")
            return []
            
    def update_preference(self, category, key, value):
        """
        Update a user preference in the database.
        
        Args:
            category (str): Preference category (e.g., 'music', 'lighting')
            key (str): Preference key
            value (str): Preference value
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO preferences (category, key, value, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (category, key, value, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating preference: {e}")
            
    def get_preference(self, category, key):
        """
        Retrieve a user preference from the database.
        
        Args:
            category (str): Preference category
            key (str): Preference key
            
        Returns:
            str: Preference value or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM preferences
                WHERE category = ? AND key = ?
            ''', (category, key))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error retrieving preference: {e}")
            return None
            
    def add_routine(self, name, description, schedule, is_active=True):
        """
        Add a new routine to the database.
        
        Args:
            name (str): Routine name
            description (str): Routine description
            schedule (str): Schedule in cron format
            is_active (bool): Whether the routine is active
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO routines (name, description, schedule, is_active)
                VALUES (?, ?, ?, ?)
            ''', (name, description, schedule, is_active))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding routine: {e}")
            
    def get_active_routines(self):
        """
        Retrieve all active routines from the database.
        
        Returns:
            list: List of active routines
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, description, schedule, last_executed
                FROM routines
                WHERE is_active = 1
            ''')
            
            routines = cursor.fetchall()
            conn.close()
            
            return [{
                'name': row[0],
                'description': row[1],
                'schedule': row[2],
                'last_executed': row[3]
            } for row in routines]
            
        except Exception as e:
            logger.error(f"Error retrieving routines: {e}")
            return [] 