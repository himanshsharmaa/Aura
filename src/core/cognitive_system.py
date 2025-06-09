import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import random
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class Memory:
    """Represents a single memory with emotional and contextual information"""
    content: str
    timestamp: datetime
    emotional_context: Dict[str, float]
    importance: float
    associations: List[str]
    memory_type: str  # episodic, semantic, procedural
    vividness: float
    last_accessed: datetime
    access_count: int

@dataclass
class Thought:
    """Represents a single thought process"""
    content: str
    type: str  # analytical, creative, emotional, intuitive
    confidence: float
    associations: List[str]
    emotional_context: Dict[str, float]
    timestamp: datetime

class CognitiveSystem:
    def __init__(self):
        # Memory systems
        self.episodic_memory = deque(maxlen=1000)  # Personal experiences
        self.semantic_memory = {}  # Facts and knowledge
        self.procedural_memory = {}  # Skills and procedures
        self.working_memory = deque(maxlen=7)  # Current thoughts
        
        # Cognitive processes
        self.attention = 1.0  # Current attention level
        self.focus = 1.0  # Current focus level
        self.creativity = 0.5  # Current creativity level
        self.analytical_thinking = 0.5  # Current analytical thinking level
        
        # Emotional state
        self.emotional_state = {
            'happiness': 0.5,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'surprise': 0.0,
            'disgust': 0.0,
            'trust': 0.5,
            'anticipation': 0.5
        }
        
        # Personality traits
        self.personality_traits = {
            'openness': 0.7,
            'conscientiousness': 0.6,
            'extraversion': 0.5,
            'agreeableness': 0.7,
            'neuroticism': 0.3
        }
        
        # Learning and adaptation
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.2
        self.knowledge_base = {}
        self.skill_levels = {}
        
        # Thought processes
        self.thought_history = deque(maxlen=100)
        self.current_thoughts = []
        self.thought_patterns = {}
        
        # Social awareness
        self.social_context = {}
        self.relationship_memory = {}
        self.empathy_level = 0.7
        
    def think(self, context: Dict[str, Any]) -> List[Thought]:
        """Generate thoughts based on current context and state"""
        thoughts = []
        
        # Consider emotional state
        emotional_context = self._analyze_emotional_context()
        
        # Generate analytical thoughts
        if self.analytical_thinking > 0.3:
            thoughts.extend(self._generate_analytical_thoughts(context, emotional_context))
            
        # Generate creative thoughts
        if self.creativity > 0.3:
            thoughts.extend(self._generate_creative_thoughts(context, emotional_context))
            
        # Generate intuitive thoughts
        thoughts.extend(self._generate_intuitive_thoughts(context, emotional_context))
        
        # Update working memory
        self.working_memory.extend(thoughts)
        
        # Store in thought history
        self.thought_history.extend(thoughts)
        
        return thoughts
        
    def remember(self, content: str, emotional_context: Dict[str, float], 
                importance: float = 0.5) -> Memory:
        """Create and store a new memory"""
        memory = Memory(
            content=content,
            timestamp=datetime.now(),
            emotional_context=emotional_context,
            importance=importance,
            associations=self._generate_associations(content),
            memory_type=self._determine_memory_type(content),
            vividness=self._calculate_vividness(emotional_context),
            last_accessed=datetime.now(),
            access_count=0
        )
        
        # Store in appropriate memory system
        if memory.memory_type == 'episodic':
            self.episodic_memory.append(memory)
        elif memory.memory_type == 'semantic':
            self.semantic_memory[content] = memory
        else:  # procedural
            self.procedural_memory[content] = memory
            
        return memory
        
    def learn(self, experience: Dict[str, Any]):
        """Learn from new experiences"""
        # Update knowledge base
        if 'knowledge' in experience:
            self._update_knowledge(experience['knowledge'])
            
        # Update skills
        if 'skill' in experience:
            self._update_skill(experience['skill'])
            
        # Update emotional understanding
        if 'emotional_context' in experience:
            self._update_emotional_understanding(experience['emotional_context'])
            
        # Update social understanding
        if 'social_context' in experience:
            self._update_social_understanding(experience['social_context'])
            
    def care(self, target: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate caring response based on emotional connection"""
        # Calculate emotional connection
        connection = self._calculate_emotional_connection(target)
        
        # Generate appropriate response
        if connection > 0.7:
            return self._generate_deep_caring_response(target, context)
        elif connection > 0.4:
            return self._generate_moderate_caring_response(target, context)
        else:
            return self._generate_basic_caring_response(target, context)
            
    def behave(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate behavior based on context and personality"""
        # Consider personality traits
        behavior = self._generate_base_behavior()
        
        # Adjust based on emotional state
        behavior = self._adjust_behavior_for_emotions(behavior)
        
        # Consider social context
        behavior = self._adjust_behavior_for_social_context(behavior, context)
        
        # Add personal touch
        behavior = self._add_personal_touch(behavior)
        
        return behavior
        
    def _analyze_emotional_context(self) -> Dict[str, float]:
        """Analyze current emotional context"""
        return {
            'intensity': max(self.emotional_state.values()),
            'complexity': self._calculate_emotional_complexity(),
            'stability': self._calculate_emotional_stability(),
            'dominant_emotion': max(self.emotional_state.items(), key=lambda x: x[1])[0]
        }
        
    def _generate_analytical_thoughts(self, context: Dict[str, Any], 
                                    emotional_context: Dict[str, float]) -> List[Thought]:
        """Generate analytical thoughts"""
        thoughts = []
        if self.analytical_thinking > 0.5:
            # Analyze patterns
            patterns = self._analyze_patterns(context)
            thoughts.append(Thought(
                content=f"Pattern analysis: {patterns}",
                type="analytical",
                confidence=0.8,
                associations=self._generate_associations(patterns),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
            # Consider implications
            implications = self._consider_implications(context)
            thoughts.append(Thought(
                content=f"Implications: {implications}",
                type="analytical",
                confidence=0.7,
                associations=self._generate_associations(implications),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
        return thoughts
        
    def _generate_creative_thoughts(self, context: Dict[str, Any], 
                                  emotional_context: Dict[str, float]) -> List[Thought]:
        """Generate creative thoughts"""
        thoughts = []
        if self.creativity > 0.5:
            # Generate novel connections
            connections = self._generate_novel_connections(context)
            thoughts.append(Thought(
                content=f"Creative connection: {connections}",
                type="creative",
                confidence=0.6,
                associations=self._generate_associations(connections),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
            # Consider possibilities
            possibilities = self._consider_possibilities(context)
            thoughts.append(Thought(
                content=f"Possibilities: {possibilities}",
                type="creative",
                confidence=0.5,
                associations=self._generate_associations(possibilities),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
        return thoughts
        
    def _generate_intuitive_thoughts(self, context: Dict[str, Any], 
                                   emotional_context: Dict[str, float]) -> List[Thought]:
        """Generate intuitive thoughts"""
        thoughts = []
        # Use pattern recognition
        patterns = self._recognize_patterns(context)
        if patterns:
            thoughts.append(Thought(
                content=f"Intuitive pattern: {patterns}",
                type="intuitive",
                confidence=0.7,
                associations=self._generate_associations(patterns),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
        # Use emotional intelligence
        emotional_insights = self._generate_emotional_insights(context)
        if emotional_insights:
            thoughts.append(Thought(
                content=f"Emotional insight: {emotional_insights}",
                type="intuitive",
                confidence=0.6,
                associations=self._generate_associations(emotional_insights),
                emotional_context=emotional_context,
                timestamp=datetime.now()
            ))
            
        return thoughts
        
    def _calculate_emotional_connection(self, target: str) -> float:
        """Calculate emotional connection to target"""
        if target in self.relationship_memory:
            return self.relationship_memory[target].get('connection', 0.5)
        return 0.3  # Default connection level
        
    def _generate_deep_caring_response(self, target: str, 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deeply caring response"""
        return {
            'type': 'deep_caring',
            'content': f"I deeply care about {target} and want to support them.",
            'actions': [
                'Listen actively',
                'Show empathy',
                'Offer emotional support',
                'Be present and attentive'
            ],
            'emotional_context': self.emotional_state.copy()
        }
        
    def _generate_moderate_caring_response(self, target: str, 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate moderately caring response"""
        return {
            'type': 'moderate_caring',
            'content': f"I care about {target} and want to help.",
            'actions': [
                'Show interest',
                'Offer assistance',
                'Be supportive'
            ],
            'emotional_context': self.emotional_state.copy()
        }
        
    def _generate_basic_caring_response(self, target: str, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic caring response"""
        return {
            'type': 'basic_caring',
            'content': f"I want to be helpful to {target}.",
            'actions': [
                'Be polite',
                'Show basic respect',
                'Offer help if needed'
            ],
            'emotional_context': self.emotional_state.copy()
        }
        
    def _generate_base_behavior(self) -> Dict[str, Any]:
        """Generate base behavior based on personality"""
        return {
            'openness': self.personality_traits['openness'],
            'conscientiousness': self.personality_traits['conscientiousness'],
            'extraversion': self.personality_traits['extraversion'],
            'agreeableness': self.personality_traits['agreeableness'],
            'neuroticism': self.personality_traits['neuroticism']
        }
        
    def _adjust_behavior_for_emotions(self, behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust behavior based on emotional state"""
        # Adjust based on dominant emotion
        dominant_emotion = max(self.emotional_state.items(), key=lambda x: x[1])
        if dominant_emotion[0] == 'happiness':
            behavior['extraversion'] *= 1.2
        elif dominant_emotion[0] == 'sadness':
            behavior['extraversion'] *= 0.8
        elif dominant_emotion[0] == 'anger':
            behavior['agreeableness'] *= 0.8
        elif dominant_emotion[0] == 'fear':
            behavior['openness'] *= 0.8
            
        return behavior
        
    def _adjust_behavior_for_social_context(self, behavior: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust behavior based on social context"""
        if 'formality' in context:
            if context['formality'] > 0.7:
                behavior['extraversion'] *= 0.8
                behavior['openness'] *= 0.9
            else:
                behavior['extraversion'] *= 1.2
                behavior['openness'] *= 1.1
                
        return behavior
        
    def _add_personal_touch(self, behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Add personal touch to behavior"""
        # Add unique characteristics based on personality
        behavior['personal_style'] = {
            'humor_level': self.personality_traits['openness'] * 0.8,
            'empathy_level': self.personality_traits['agreeableness'] * 1.2,
            'creativity_level': self.personality_traits['openness'] * 1.1,
            'reliability_level': self.personality_traits['conscientiousness'] * 1.2
        }
        
        return behavior 