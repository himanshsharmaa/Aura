import random
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import json
import os
import asyncio
import logging
from dataclasses import dataclass
from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class Action:
    """Represents a proactive action that can be taken"""
    name: str
    description: str
    priority: int  # 1-10, higher is more important
    trigger_conditions: Dict[str, Any]  # Conditions that trigger this action
    action_func: Callable  # Function to execute when triggered
    cooldown: int = 300  # Seconds between repeated actions
    last_triggered: Optional[datetime] = None
    enabled: bool = True

class ProactiveBehavior:
    def __init__(self, personality):
        self.personality = personality
        self.last_interaction = datetime.now()
        self.interaction_cooldown = timedelta(minutes=5)
        self.context = {
            'time_of_day': None,
            'user_activity': None,
            'conversation_topic': None,
            'user_emotion': None
        }
        
        self.proactive_triggers = {
            'time_based': {
                'morning': {
                    'condition': lambda: datetime.now().hour < 12,
                    'responses': [
                        "Good morning! How did you sleep?",
                        "Rise and shine! Ready for a new day?",
                        "Morning! What's on your agenda today?",
                        "Good morning! Would you like to hear about today's weather?",
                        "Morning! How about we start the day with some positive thoughts?"
                    ]
                },
                'evening': {
                    'condition': lambda: datetime.now().hour >= 20,
                    'responses': [
                        "Getting late! Have you prepared for tomorrow?",
                        "Evening! How was your day?",
                        "Night is falling. Would you like to reflect on your day?",
                        "Evening! Time to wind down. How are you feeling?",
                        "Good evening! Shall we plan for tomorrow?"
                    ]
                },
                'lunch_time': {
                    'condition': lambda: 11 <= datetime.now().hour <= 14,
                    'responses': [
                        "Lunch time! Have you eaten yet?",
                        "Time for a break! How's your day going?",
                        "Lunch break! Need any recommendations?",
                        "Midday check-in! How are you feeling?",
                        "Lunch time! Would you like to discuss something interesting?"
                    ]
                },
                'weekend': {
                    'condition': lambda: datetime.now().weekday() >= 5,
                    'responses': [
                        "Weekend vibes! Any fun plans?",
                        "Weekend! Time to relax. How are you?",
                        "Weekend check-in! What are you up to?",
                        "Weekend! Perfect time for hobbies. What interests you?",
                        "Weekend! Shall we explore something new?"
                    ]
                }
            },
            'emotion_based': {
                'sad': {
                    'condition': lambda emotions: emotions.get('sad', 0) > 0.6,
                    'responses': [
                        "I notice you seem down. Would you like to talk?",
                        "I sense you're feeling low. How can I help?",
                        "You seem sad. Would you like to share what's on your mind?",
                        "I'm here if you need someone to talk to.",
                        "Would you like to do something to lift your spirits?"
                    ]
                },
                'happy': {
                    'condition': lambda emotions: emotions.get('happy', 0) > 0.6,
                    'responses': [
                        "Your happiness is contagious! What's making you smile?",
                        "You seem really happy! Care to share the good news?",
                        "I love seeing you this happy! What's the occasion?",
                        "Your positive energy is amazing! What's up?",
                        "You're radiating joy! What's making your day special?"
                    ]
                },
                'stressed': {
                    'condition': lambda emotions: emotions.get('angry', 0) > 0.5 or emotions.get('fear', 0) > 0.5,
                    'responses': [
                        "You seem a bit tense. Would you like to take a break?",
                        "I notice you're stressed. How can I help you relax?",
                        "Would you like to try some stress-relief techniques?",
                        "Let's take a moment to breathe. How are you feeling?",
                        "I'm here to help you manage this stress."
                    ]
                },
                'focused': {
                    'condition': lambda emotions: emotions.get('neutral', 0) > 0.7,
                    'responses': [
                        "You seem very focused. Need any assistance?",
                        "I notice you're in the zone. How's it going?",
                        "Would you like to take a short break?",
                        "You're doing great! Need anything?",
                        "I'm here if you need any support."
                    ]
                }
            },
            'topic_based': {
                'work': {
                    'condition': lambda context: 'work' in context.get('current_activity', ''),
                    'responses': [
                        "How's your work going?",
                        "Need any help with your tasks?",
                        "Would you like to discuss your project?",
                        "How about a short break?",
                        "I'm here if you need any work-related assistance."
                    ]
                },
                'learning': {
                    'condition': lambda context: 'study' in context.get('current_activity', ''),
                    'responses': [
                        "How's your learning going?",
                        "Would you like to discuss what you're studying?",
                        "Need any clarification on your topic?",
                        "How about a learning break?",
                        "I'm here to help with your studies."
                    ]
                },
                'relaxation': {
                    'condition': lambda context: 'relax' in context.get('current_activity', ''),
                    'responses': [
                        "Enjoying your relaxation time?",
                        "Would you like some calming music?",
                        "How about some meditation?",
                        "Need any relaxation tips?",
                        "I'm here to enhance your relaxation."
                    ]
                }
            },
            'activity_based': {
                'typing': {
                    'condition': lambda context: context.get('is_typing', False),
                    'responses': [
                        "Need any help with your writing?",
                        "Would you like some writing suggestions?",
                        "How's your document coming along?",
                        "Need any research assistance?",
                        "I'm here to help with your writing."
                    ]
                },
                'reading': {
                    'condition': lambda context: context.get('is_reading', False),
                    'responses': [
                        "Enjoying your reading?",
                        "Would you like to discuss the book?",
                        "Need any reading recommendations?",
                        "How about a reading break?",
                        "I'm here to enhance your reading experience."
                    ]
                },
                'music': {
                    'condition': lambda context: context.get('is_listening_to_music', False),
                    'responses': [
                        "Enjoying the music?",
                        "Would you like some music recommendations?",
                        "How about exploring new genres?",
                        "Need any music-related information?",
                        "I'm here to enhance your music experience."
                    ]
                }
            },
            'environment_based': {
                'weather_change': {
                    'condition': lambda context: context.get('weather_changed', False),
                    'responses': [
                        "Notice the weather change?",
                        "How's the new weather treating you?",
                        "Would you like some weather-appropriate suggestions?",
                        "Need any weather-related information?",
                        "I'm here to help you adapt to the weather."
                    ]
                },
                'noise_level': {
                    'condition': lambda context: context.get('noise_level', 0) > 0.7,
                    'responses': [
                        "It's quite noisy. Would you like some quiet time?",
                        "Need help focusing despite the noise?",
                        "Would you like some noise-canceling suggestions?",
                        "How about moving to a quieter space?",
                        "I'm here to help you manage the noise."
                    ]
                },
                'lighting': {
                    'condition': lambda context: context.get('lighting_changed', False),
                    'responses': [
                        "Notice the lighting change?",
                        "How's the new lighting working for you?",
                        "Would you like some lighting suggestions?",
                        "Need any lighting-related information?",
                        "I'm here to help you optimize your lighting."
                    ]
                }
            },
            'health_based': {
                'posture': {
                    'condition': lambda context: context.get('poor_posture', False),
                    'responses': [
                        "I notice your posture. Would you like some ergonomic tips?",
                        "How about a quick posture check?",
                        "Would you like some stretching exercises?",
                        "Need any ergonomic suggestions?",
                        "I'm here to help you maintain good posture."
                    ]
                },
                'screen_time': {
                    'condition': lambda context: context.get('screen_time', 0) > 3600,
                    'responses': [
                        "You've been on screen for a while. Time for a break?",
                        "Would you like some eye exercises?",
                        "How about a screen-free activity?",
                        "Need any screen-time management tips?",
                        "I'm here to help you manage screen time."
                    ]
                },
                'hydration': {
                    'condition': lambda context: context.get('last_water_reminder', 0) > 3600,
                    'responses': [
                        "Time for some water?",
                        "Would you like a hydration reminder?",
                        "How about a quick water break?",
                        "Need any hydration tips?",
                        "I'm here to help you stay hydrated."
                    ]
                }
            }
        }
        
    def update_context(self, **kwargs):
        """Update the current context"""
        for key, value in kwargs.items():
            if key in self.context:
                self.context[key] = value
                
    def should_initiate(self) -> bool:
        """Determine if Aura should initiate an interaction"""
        # Check cooldown
        if datetime.now() - self.last_interaction < self.interaction_cooldown:
            return False
            
        # Base probability from personality
        base_probability = (
            self.personality.traits['assertiveness'] * 0.4 +
            self.personality.traits['curiosity'] * 0.3 +
            self.personality.traits['warmth'] * 0.3
        )
        
        # Adjust based on mood
        mood_factor = (
            self.personality.mood['energy'] * 0.4 +
            self.personality.mood['interest'] * 0.3 +
            (1 - self.personality.mood['stress']) * 0.3
        )
        
        return random.random() < (base_probability * mood_factor)
        
    def get_proactive_response(self) -> Optional[str]:
        """Get a proactive response based on context"""
        if not self.should_initiate():
            return None
            
        # Collect all valid triggers
        valid_triggers = []
        for category in self.proactive_triggers.values():
            for trigger in category.values():
                if trigger['condition'](self.context):
                    valid_triggers.extend(trigger['responses'])
                    
        if not valid_triggers:
            return None
            
        # Update last interaction time
        self.last_interaction = datetime.now()
        
        # Select and return a response
        return random.choice(valid_triggers)
        
    def adjust_cooldown(self, minutes: int):
        """Adjust the interaction cooldown period"""
        self.interaction_cooldown = timedelta(minutes=minutes)
        
    def save_state(self, filepath: str):
        """Save proactive behavior state"""
        state = {
            'last_interaction': self.last_interaction.isoformat(),
            'interaction_cooldown': self.interaction_cooldown.total_seconds(),
            'context': self.context
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)
            
    def load_state(self, filepath: str):
        """Load proactive behavior state"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.last_interaction = datetime.fromisoformat(state['last_interaction'])
            self.interaction_cooldown = timedelta(seconds=state['interaction_cooldown'])
            self.context = state['context']

    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn and adapt proactive triggers and responses from feedback."""
        if 'emotion' in feedback and 'response' in feedback:
            emotion = feedback['emotion']
            response = feedback['response']
            if emotion in self.proactive_triggers['emotion_based']:
                self.proactive_triggers['emotion_based'][emotion]['responses'].append(response)
        if 'context' in feedback and 'response' in feedback:
            context = feedback['context']
            response = feedback['response']
            if context in self.proactive_triggers['topic_based']:
                self.proactive_triggers['topic_based'][context]['responses'].append(response)
        # Optionally, adjust conditions or add new triggers
        if 'new_trigger' in feedback:
            self.proactive_triggers['custom'] = self.proactive_triggers.get('custom', [])
            self.proactive_triggers['custom'].append(feedback['new_trigger'])

    def continual_learning(self, feedback: Dict[str, Any]):
        self.learn_from_feedback(feedback)

class ProactiveSystem:
    def __init__(self):
        """Initialize proactive system"""
        self.actions: List[Action] = []
        self.running = False
        self.check_interval = 60  # Check for actions every minute
        self.context = {}  # Current context for action evaluation
        
    def register_action(self, action: Action):
        """Register a new proactive action"""
        self.actions.append(action)
        logger.info(f"Registered proactive action: {action.name}")
        
    def update_context(self, context: Dict[str, Any]):
        """Update the current context for action evaluation"""
        self.context.update(context)
        
    def _should_trigger(self, action: Action) -> bool:
        """Check if an action should be triggered based on conditions"""
        if not action.enabled:
            return False
            
        # Check cooldown
        if action.last_triggered:
            time_since_last = (datetime.now() - action.last_triggered).total_seconds()
            if time_since_last < action.cooldown:
                return False
                
        # Check trigger conditions
        for key, value in action.trigger_conditions.items():
            if key not in self.context:
                return False
            if self.context[key] != value:
                return False
                
        return True
        
    async def check_actions(self):
        """Check for actions that should be triggered"""
        for action in sorted(self.actions, key=lambda x: x.priority, reverse=True):
            if self._should_trigger(action):
                try:
                    logger.info(f"Triggering proactive action: {action.name}")
                    await action.action_func()
                    action.last_triggered = datetime.now()
                except Exception as e:
                    logger.error(f"Error executing action {action.name}: {e}")
                    
    async def start(self):
        """Start the proactive system"""
        self.running = True
        while self.running:
            await self.check_actions()
            await asyncio.sleep(self.check_interval)
            
    def stop(self):
        """Stop the proactive system"""
        self.running = False
        
    def get_available_actions(self) -> List[Action]:
        """Get list of available actions"""
        return [action for action in self.actions if action.enabled]
        
    def enable_action(self, action_name: str):
        """Enable a specific action"""
        for action in self.actions:
            if action.name == action_name:
                action.enabled = True
                logger.info(f"Enabled action: {action_name}")
                return
                
    def disable_action(self, action_name: str):
        """Disable a specific action"""
        for action in self.actions:
            if action.name == action_name:
                action.enabled = False
                logger.info(f"Disabled action: {action_name}")
                return
                
    def get_action_status(self, action_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific action"""
        for action in self.actions:
            if action.name == action_name:
                return {
                    'enabled': action.enabled,
                    'last_triggered': action.last_triggered,
                    'cooldown_remaining': (
                        action.cooldown - (datetime.now() - action.last_triggered).total_seconds()
                        if action.last_triggered else 0
                    )
                }
        return None 