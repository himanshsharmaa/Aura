import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

class UserManager:
    def __init__(self, data_dir='data/users'):
        self.logger = setup_logger(__name__)
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / 'users.json'
        self.sessions_file = self.data_dir / 'sessions.json'
        self._ensure_data_dir()
        self._load_data()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.users_file.exists():
            self._save_users({})
        if not self.sessions_file.exists():
            self._save_sessions({})
    
    def _load_data(self):
        """Load users and sessions data"""
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading user data: {e}")
            self.users = {}
            self.sessions = {}
    
    def _save_users(self, users=None):
        """Save users data"""
        if users is not None:
            self.users = users
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")
    
    def _save_sessions(self, sessions=None):
        """Save sessions data"""
        if sessions is not None:
            self.sessions = sessions
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving sessions: {e}")
    
    def create_user(self, email, provider='local'):
        """Create a new user"""
        if email in self.users:
            return False, "User already exists"
        
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'email': email,
            'provider': provider,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'settings': {
                'hotword_threshold': 0.5,
                'sound_event_threshold': 0.5,
                'sample_rate': 16000
            }
        }
        
        self.users[email] = user_data
        self._save_users()
        return True, user_id
    
    def get_user(self, email):
        """Get user data"""
        return self.users.get(email)
    
    def update_user_settings(self, email, settings):
        """Update user settings"""
        if email not in self.users:
            return False, "User not found"
        
        self.users[email]['settings'].update(settings)
        self._save_users()
        return True, "Settings updated"
    
    def create_session(self, email):
        """Create a new session for user"""
        if email not in self.users:
            return False, "User not found"
        
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'user_email': email,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'data': {
                'hotword_samples': [],
                'sound_events': [],
                'training_data': []
            }
        }
        
        self.sessions[session_id] = session_data
        self._save_sessions()
        return True, session_id
    
    def get_session(self, session_id):
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id, data):
        """Update session data"""
        if session_id not in self.sessions:
            return False, "Session not found"
        
        self.sessions[session_id]['data'].update(data)
        self.sessions[session_id]['last_active'] = datetime.now().isoformat()
        self._save_sessions()
        return True, "Session updated"
    
    def get_user_sessions(self, email):
        """Get all sessions for a user"""
        return {
            session_id: session_data
            for session_id, session_data in self.sessions.items()
            if session_data['user_email'] == email
        }
    
    def delete_session(self, session_id):
        """Delete a session"""
        if session_id not in self.sessions:
            return False, "Session not found"
        
        del self.sessions[session_id]
        self._save_sessions()
        return True, "Session deleted"
    
    def get_user_training_data(self, email):
        """Get all training data for a user"""
        training_data = []
        for session in self.get_user_sessions(email).values():
            training_data.extend(session['data']['training_data'])
        return training_data
    
    def add_training_sample(self, session_id, sample_type, audio_data, metadata=None):
        """Add a training sample to a session"""
        if session_id not in self.sessions:
            return False, "Session not found"
        
        sample = {
            'id': str(uuid.uuid4()),
            'type': sample_type,
            'timestamp': datetime.now().isoformat(),
            'audio_data': audio_data,
            'metadata': metadata or {}
        }
        
        self.sessions[session_id]['data']['training_data'].append(sample)
        self._save_sessions()
        return True, sample['id']
    
    def get_training_samples(self, session_id, sample_type=None):
        """Get training samples from a session"""
        if session_id not in self.sessions:
            return []
        
        samples = self.sessions[session_id]['data']['training_data']
        if sample_type:
            samples = [s for s in samples if s['type'] == sample_type]
        return samples 