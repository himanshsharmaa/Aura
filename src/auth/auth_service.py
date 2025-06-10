import os
import json
import secrets
import requests
from datetime import datetime, timedelta
from pathlib import Path
from utils.logger import setup_logger
from auth.user_manager import UserManager

logger = setup_logger(__name__)

class AuthService:
    def __init__(self, config_path='config.json'):
        self.logger = setup_logger(__name__)
        self.config = self._load_config(config_path)
        self.user_manager = UserManager()
        self._ensure_data_dir()
        self._load_tokens()
    
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Ensure required config sections exist
                if 'auth' not in config:
                    config['auth'] = {
                        'providers': {
                            'google': {
                                'client_id': '',
                                'client_secret': '',
                                'redirect_uri': 'http://localhost:8000/auth/google/callback'
                            },
                            'github': {
                                'client_id': '',
                                'client_secret': '',
                                'redirect_uri': 'http://localhost:8000/auth/github/callback'
                            }
                        },
                        'session_secret': secrets.token_hex(32),
                        'token_expiry': 3600  # 1 hour
                    }
                return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {
                'auth': {
                    'providers': {
                        'google': {
                            'client_id': '',
                            'client_secret': '',
                            'redirect_uri': 'http://localhost:8000/auth/google/callback'
                        },
                        'github': {
                            'client_id': '',
                            'client_secret': '',
                            'redirect_uri': 'http://localhost:8000/auth/github/callback'
                        }
                    },
                    'session_secret': secrets.token_hex(32),
                    'token_expiry': 3600
                }
            }
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.tokens_dir = Path('data/auth/tokens')
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_tokens(self):
        """Load stored tokens"""
        try:
            with open(self.tokens_dir / 'tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading tokens: {e}")
            self.tokens = {}
    
    def _save_tokens(self):
        """Save tokens to file"""
        try:
            with open(self.tokens_dir / 'tokens.json', 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving tokens: {e}")
    
    def get_auth_url(self, provider):
        """Get authentication URL for provider"""
        if provider not in self.config['auth']['providers']:
            return None
        
        provider_config = self.config['auth']['providers'][provider]
        
        if provider == 'google':
            return (
                'https://accounts.google.com/o/oauth2/v2/auth'
                '?client_id={}'
                '&redirect_uri={}'
                '&response_type=code'
                '&scope=email profile'
                '&access_type=offline'
                '&prompt=consent'
            ).format(
                provider_config['client_id'],
                provider_config['redirect_uri']
            )
        
        elif provider == 'github':
            return (
                'https://github.com/login/oauth/authorize'
                '?client_id={}'
                '&redirect_uri={}'
                '&scope=user:email'
            ).format(
                provider_config['client_id'],
                provider_config['redirect_uri']
            )
        
        return None
    
    def handle_callback(self, provider, code):
        """Handle OAuth callback"""
        if provider not in self.config['auth']['providers']:
            return False, "Invalid provider"
        
        provider_config = self.config['auth']['providers'][provider]
        
        try:
            if provider == 'google':
                # Exchange code for tokens
                token_response = requests.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'client_id': provider_config['client_id'],
                        'client_secret': provider_config['client_secret'],
                        'code': code,
                        'redirect_uri': provider_config['redirect_uri'],
                        'grant_type': 'authorization_code'
                    }
                )
                token_data = token_response.json()
                
                # Get user info
                user_response = requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f"Bearer {token_data['access_token']}"}
                )
                user_data = user_response.json()
                
                email = user_data['email']
                name = user_data.get('name', '')
                
            elif provider == 'github':
                # Exchange code for tokens
                token_response = requests.post(
                    'https://github.com/login/oauth/access_token',
                    data={
                        'client_id': provider_config['client_id'],
                        'client_secret': provider_config['client_secret'],
                        'code': code,
                        'redirect_uri': provider_config['redirect_uri']
                    },
                    headers={'Accept': 'application/json'}
                )
                token_data = token_response.json()
                
                # Get user info
                user_response = requests.get(
                    'https://api.github.com/user',
                    headers={'Authorization': f"token {token_data['access_token']}"}
                )
                user_data = user_response.json()
                
                # Get email
                email_response = requests.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f"token {token_data['access_token']}"}
                )
                email_data = email_response.json()
                email = next(e['email'] for e in email_data if e['primary'])
                name = user_data.get('name', '')
            
            # Create or update user
            success, user_id = self.user_manager.create_user(
                email,
                provider=provider
            )
            
            if not success and user_id == "User already exists":
                # Update existing user
                user = self.user_manager.get_user(email)
                user_id = user['id']
            
            # Store tokens
            self.tokens[email] = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': (
                    datetime.now() + 
                    timedelta(seconds=token_data.get('expires_in', 3600))
                ).isoformat(),
                'provider': provider
            }
            self._save_tokens()
            
            return True, {
                'user_id': user_id,
                'email': email,
                'name': name,
                'provider': provider
            }
            
        except Exception as e:
            self.logger.error(f"Error handling {provider} callback: {e}")
            return False, str(e)
    
    def refresh_token(self, email):
        """Refresh access token"""
        if email not in self.tokens:
            return False, "No tokens found"
        
        token_data = self.tokens[email]
        provider = token_data['provider']
        provider_config = self.config['auth']['providers'][provider]
        
        try:
            if provider == 'google':
                response = requests.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'client_id': provider_config['client_id'],
                        'client_secret': provider_config['client_secret'],
                        'refresh_token': token_data['refresh_token'],
                        'grant_type': 'refresh_token'
                    }
                )
                new_tokens = response.json()
                
                # Update tokens
                self.tokens[email].update({
                    'access_token': new_tokens['access_token'],
                    'expires_at': (
                        datetime.now() + 
                        timedelta(seconds=new_tokens.get('expires_in', 3600))
                    ).isoformat()
                })
                self._save_tokens()
                return True, new_tokens['access_token']
            
            elif provider == 'github':
                # GitHub tokens don't expire, no need to refresh
                return True, token_data['access_token']
            
            return False, "Unsupported provider"
            
        except Exception as e:
            self.logger.error(f"Error refreshing token: {e}")
            return False, str(e)
    
    def get_valid_token(self, email):
        """Get valid access token for user"""
        if email not in self.tokens:
            return None
        
        token_data = self.tokens[email]
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        
        if datetime.now() >= expires_at:
            success, token = self.refresh_token(email)
            if not success:
                return None
            return token
        
        return token_data['access_token']
    
    def logout(self, email):
        """Logout user"""
        if email in self.tokens:
            del self.tokens[email]
            self._save_tokens()
        return True 