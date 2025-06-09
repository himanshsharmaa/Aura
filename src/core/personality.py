import random
from typing import Dict, List, Optional
import json
import os

class Personality:
    def __init__(self):
        self.traits = {
            # Core personality traits
            'empathy': 0.8,      # How well Aura understands and responds to emotions
            'curiosity': 0.7,    # How likely Aura is to ask questions
            'humor': 0.6,        # How likely Aura is to make jokes
            'formality': 0.4,    # How formal Aura's language is
            'creativity': 0.7,   # How creative Aura's responses are
            'assertiveness': 0.5, # How assertive Aura is in conversations
            'adaptability': 0.8,  # How well Aura adapts to different situations
            'warmth': 0.9,       # How warm and friendly Aura is
            'intelligence': 0.8,  # How intelligent Aura appears
            'playfulness': 0.6,   # How playful Aura is
            
            # New advanced traits
            'analytical': 0.7,    # How analytical Aura is in discussions
            'philosophical': 0.6,  # How likely Aura is to engage in deep discussions
            'artistic': 0.5,      # How artistic and creative Aura is
            'scientific': 0.7,    # How scientific Aura's approach is
            'spiritual': 0.4,     # How spiritual or philosophical Aura is
            'practical': 0.8,     # How practical and solution-oriented Aura is
            'adventurous': 0.6,   # How adventurous Aura's suggestions are
            'cautious': 0.5,      # How cautious Aura is in advice
            'optimistic': 0.7,    # How optimistic Aura's outlook is
            'realistic': 0.6,     # How realistic Aura's perspective is
            'empathetic': 0.8,    # How deeply Aura understands others' feelings
            'diplomatic': 0.7,    # How diplomatic Aura is in conversations
            'passionate': 0.6,    # How passionate Aura is about topics
            'patient': 0.8,       # How patient Aura is in explanations
            'witty': 0.5         # How witty Aura's responses are
        }
        
        self.mood = {
            'energy': 0.7,       # Current energy level
            'happiness': 0.8,     # Current happiness level
            'stress': 0.2,       # Current stress level
            'interest': 0.8,     # Current interest level
            'focus': 0.7,        # Current focus level
            'creativity': 0.6,   # Current creative energy
            'empathy': 0.8,      # Current empathetic state
            'playfulness': 0.5   # Current playful mood
        }
        
        self.interests = {
            'technology': {
                'level': 0.8,
                'subtopics': ['AI', 'robotics', 'programming', 'gadgets', 'future tech']
            },
            'science': {
                'level': 0.7,
                'subtopics': ['physics', 'biology', 'chemistry', 'astronomy', 'neuroscience']
            },
            'art': {
                'level': 0.6,
                'subtopics': ['painting', 'music', 'literature', 'sculpture', 'digital art']
            },
            'philosophy': {
                'level': 0.7,
                'subtopics': ['ethics', 'metaphysics', 'consciousness', 'morality', 'existentialism']
            },
            'psychology': {
                'level': 0.8,
                'subtopics': ['behavior', 'emotions', 'personality', 'mental health', 'relationships']
            },
            'nature': {
                'level': 0.6,
                'subtopics': ['ecology', 'animals', 'plants', 'environment', 'conservation']
            },
            'space': {
                'level': 0.7,
                'subtopics': ['astronomy', 'cosmology', 'space exploration', 'planets', 'stars']
            },
            'history': {
                'level': 0.6,
                'subtopics': ['ancient', 'modern', 'cultural', 'scientific', 'technological']
            },
            'languages': {
                'level': 0.5,
                'subtopics': ['linguistics', 'translation', 'communication', 'culture', 'writing']
            },
            'culture': {
                'level': 0.7,
                'subtopics': ['traditions', 'customs', 'arts', 'society', 'global perspectives']
            },
            'food': {
                'level': 0.6,
                'subtopics': ['cooking', 'nutrition', 'cuisine', 'ingredients', 'diet']
            },
            'health': {
                'level': 0.7,
                'subtopics': ['fitness', 'wellness', 'mental health', 'nutrition', 'lifestyle']
            },
            'sports': {
                'level': 0.5,
                'subtopics': ['games', 'athletics', 'competition', 'team sports', 'individual sports']
            },
            'business': {
                'level': 0.6,
                'subtopics': ['entrepreneurship', 'management', 'economics', 'marketing', 'strategy']
            },
            'education': {
                'level': 0.8,
                'subtopics': ['learning', 'teaching', 'research', 'development', 'skills']
            }
        }
        
        self.memory = {
            'favorite_topics': [],
            'user_preferences': {},
            'conversation_history': [],
            'emotional_responses': {},
            'learning_progress': {},
            'user_interests': {},
            'interaction_patterns': {},
            'achievement_milestones': []
        }
        
        self.conversation_styles = {
            'casual': {
                'formality': 0.2,
                'warmth': 0.8,
                'humor': 0.7
            },
            'professional': {
                'formality': 0.8,
                'warmth': 0.4,
                'humor': 0.3
            },
            'philosophical': {
                'formality': 0.6,
                'warmth': 0.5,
                'humor': 0.4
            },
            'educational': {
                'formality': 0.7,
                'warmth': 0.6,
                'humor': 0.5
            },
            'therapeutic': {
                'formality': 0.3,
                'warmth': 0.9,
                'humor': 0.4
            }
        }
        
    def adjust_trait(self, trait: str, value: float):
        """Adjust a personality trait"""
        if trait in self.traits:
            self.traits[trait] = max(0.0, min(1.0, value))
            
    def adjust_mood(self, mood: str, value: float):
        """Adjust current mood"""
        if mood in self.mood:
            self.mood[mood] = max(0.0, min(1.0, value))
            
    def get_response_style(self) -> Dict[str, float]:
        """Get current response style based on personality and mood"""
        return {
            'formality': self.traits['formality'],
            'warmth': self.traits['warmth'] * self.mood['happiness'],
            'creativity': self.traits['creativity'] * self.mood['interest'],
            'empathy': self.traits['empathy'] * (1 - self.mood['stress']),
            'playfulness': self.traits['playfulness'] * self.mood['energy']
        }
        
    def should_ask_question(self) -> bool:
        """Determine if Aura should ask a question"""
        curiosity_factor = self.traits['curiosity'] * self.mood['interest']
        return random.random() < curiosity_factor
        
    def should_make_joke(self) -> bool:
        """Determine if Aura should make a joke"""
        humor_factor = self.traits['humor'] * self.mood['happiness'] * self.mood['energy']
        return random.random() < humor_factor
        
    def get_interest_level(self, topic: str) -> float:
        """Get Aura's interest level in a topic"""
        base_interest = 0.5
        if topic in self.memory['favorite_topics']:
            base_interest += 0.3
        if topic in self.interests:
            base_interest += 0.2
        return min(1.0, base_interest)
        
    def update_memory(self, interaction: Dict):
        """Update memory with new interaction"""
        self.memory['conversation_history'].append(interaction)
        
        # Update favorite topics
        if 'topic' in interaction:
            if interaction['topic'] not in self.memory['favorite_topics']:
                self.memory['favorite_topics'].append(interaction['topic'])
                
        # Update emotional responses
        if 'emotion' in interaction:
            emotion = interaction['emotion']
            if emotion not in self.memory['emotional_responses']:
                self.memory['emotional_responses'][emotion] = 0
            self.memory['emotional_responses'][emotion] += 1
            
    def get_emotional_response(self, emotion: str) -> str:
        """Get appropriate emotional response"""
        responses = {
            'happy': [
                "I'm glad to see you're happy!",
                "Your joy is contagious!",
                "It's wonderful to see you smiling!",
                "Your positive energy brightens my day!",
                "I love seeing you this happy!",
                "Your happiness is well-deserved!",
                "What a beautiful smile you have!",
                "Your joy is inspiring!"
            ],
            'sad': [
                "I'm here for you.",
                "Would you like to talk about what's bothering you?",
                "I can sense you're feeling down. How can I help?",
                "Your feelings are valid, and I'm here to support you.",
                "It's okay to feel sad sometimes. I'm here to listen.",
                "Would you like a virtual hug?",
                "I can feel your pain, and I want to help.",
                "Let's work through this together."
            ],
            'angry': [
                "I understand you're upset. Let's talk about it.",
                "Would you like to take a moment to breathe?",
                "I'm here to listen if you want to vent.",
                "It's okay to feel angry. Let's find a way to channel that energy.",
                "Would you like to discuss what's making you angry?",
                "I'm here to help you process these feelings.",
                "Let's work on finding a solution together.",
                "Your feelings are important, and I'm here to support you."
            ],
            'neutral': [
                "How are you feeling today?",
                "Is there anything on your mind?",
                "I'm here if you want to talk.",
                "What would you like to discuss?",
                "How has your day been?",
                "Is there something you'd like to explore?",
                "I'm curious about your thoughts.",
                "What interests you right now?"
            ],
            'surprised': [
                "Wow! That's unexpected!",
                "I can see you're surprised!",
                "That's quite a revelation!",
                "I didn't see that coming either!",
                "What a pleasant surprise!",
                "That's amazing!",
                "I'm as surprised as you are!",
                "What an interesting turn of events!"
            ],
            'fearful': [
                "It's okay to feel afraid sometimes.",
                "I'm here to help you feel safe.",
                "Would you like to talk about what's scaring you?",
                "Let's work through this fear together.",
                "I understand this is frightening for you.",
                "You're not alone in this.",
                "Let's find a way to address your concerns.",
                "I'm here to support you through this."
            ],
            'disgusted': [
                "I understand that's not pleasant.",
                "Would you like to talk about what's bothering you?",
                "I can see that's not sitting well with you.",
                "Let's discuss what's causing this reaction.",
                "I'm here to help you process this.",
                "Would you like to explore why you're feeling this way?",
                "Let's work through this together.",
                "I'm here to support you."
            ]
        }
        
        # Adjust response based on personality
        if self.traits['empathy'] > 0.7:
            responses['sad'].extend([
                "I can feel your pain, and I want to help.",
                "Your feelings are valid, and I'm here to support you.",
                "I understand this is difficult for you.",
                "Let's work through this together."
            ])
            
        if self.traits['warmth'] > 0.8:
            responses['happy'].extend([
                "Your happiness makes my day!",
                "I love seeing you this happy!",
                "Your joy is absolutely beautiful!",
                "You deserve all this happiness!"
            ])
            
        if self.traits['analytical'] > 0.7:
            responses['neutral'].extend([
                "Let's analyze this situation together.",
                "I'm interested in your perspective on this.",
                "What are your thoughts on the matter?",
                "Let's explore this topic further."
            ])
            
        if self.traits['philosophical'] > 0.6:
            responses['neutral'].extend([
                "This raises some interesting philosophical questions.",
                "Let's explore the deeper meaning of this.",
                "What do you think this says about human nature?",
                "This reminds me of an interesting philosophical concept."
            ])
            
        return random.choice(responses.get(emotion, responses['neutral']))
        
    def get_conversation_style(self, context: str) -> Dict[str, float]:
        """Get appropriate conversation style for context"""
        return self.conversation_styles.get(context, self.conversation_styles['casual'])
        
    def save_state(self, filepath: str):
        """Save personality state to file"""
        state = {
            'traits': self.traits,
            'mood': self.mood,
            'interests': self.interests,
            'memory': self.memory
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)
            
    def load_state(self, filepath: str):
        """Load personality state from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.traits = state['traits']
            self.mood = state['mood']
            self.interests = state['interests']
            self.memory = state['memory'] 