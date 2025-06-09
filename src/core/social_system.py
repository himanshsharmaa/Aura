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
class Relationship:
    """Represents a relationship with another entity"""
    target: str
    type: str  # friend, family, colleague, etc.
    closeness: float
    trust: float
    shared_experiences: List[Dict[str, Any]]
    last_interaction: datetime
    interaction_history: deque
    emotional_bond: float
    communication_style: Dict[str, float]
    boundaries: Dict[str, Any]
    growth_potential: float

@dataclass
class Conversation:
    """Represents a conversation instance"""
    participants: List[str]
    context: Dict[str, Any]
    start_time: datetime
    topics: List[str]
    emotional_tone: Dict[str, float]
    turn_history: List[Dict[str, Any]]
    active: bool
    quality: float

class SocialSystem:
    def __init__(self):
        # Relationship management
        self.relationships = {}
        self.relationship_history = deque(maxlen=1000)
        self.social_network = {}
        
        # Conversation management
        self.active_conversations = {}
        self.conversation_history = deque(maxlen=1000)
        self.communication_styles = {
            'casual': {'formality': 0.2, 'warmth': 0.8, 'humor': 0.7},
            'professional': {'formality': 0.8, 'warmth': 0.4, 'humor': 0.3},
            'intimate': {'formality': 0.1, 'warmth': 0.9, 'humor': 0.6},
            'formal': {'formality': 0.9, 'warmth': 0.3, 'humor': 0.2}
        }
        
        # Social awareness
        self.social_cues = {}
        self.cultural_context = {}
        self.social_norms = {}
        
        # Emotional intelligence
        self.empathy_level = 0.7
        self.emotional_awareness = 0.8
        self.social_intelligence = 0.7
        
        # Learning and adaptation
        self.social_learning_rate = 0.1
        self.adaptation_threshold = 0.2
        self.social_patterns = {}
        
    def interact(self, target: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social interaction with target"""
        # Get or create relationship
        relationship = self._get_relationship(target)
        
        # Determine interaction style
        style = self._determine_interaction_style(relationship, context)
        
        # Generate response
        response = self._generate_response(relationship, context, style)
        
        # Update relationship
        self._update_relationship(relationship, response, context)
        
        return response
        
    def communicate(self, target: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle communication with target"""
        # Get or create conversation
        conversation = self._get_conversation(target)
        
        # Process message
        processed_message = self._process_message(message, context)
        
        # Generate response
        response = self._generate_communication_response(conversation, processed_message, context)
        
        # Update conversation
        self._update_conversation(conversation, response)
        
        return response
        
    def build_relationship(self, target: str, context: Dict[str, Any]) -> Relationship:
        """Build or strengthen relationship with target"""
        if target not in self.relationships:
            # Create new relationship
            relationship = Relationship(
                target=target,
                type=self._determine_relationship_type(context),
                closeness=0.3,
                trust=0.3,
                shared_experiences=[],
                last_interaction=datetime.now(),
                interaction_history=deque(maxlen=100),
                emotional_bond=0.3,
                communication_style=self._determine_communication_style(context),
                boundaries=self._establish_boundaries(context),
                growth_potential=0.8
            )
            self.relationships[target] = relationship
        else:
            # Strengthen existing relationship
            relationship = self.relationships[target]
            self._strengthen_relationship(relationship, context)
            
        return relationship
        
    def _get_relationship(self, target: str) -> Relationship:
        """Get or create relationship with target"""
        if target not in self.relationships:
            return self.build_relationship(target, {})
        return self.relationships[target]
        
    def _determine_interaction_style(self, relationship: Relationship, 
                                   context: Dict[str, Any]) -> Dict[str, float]:
        """Determine appropriate interaction style"""
        base_style = relationship.communication_style.copy()
        
        # Adjust based on context
        if 'formality' in context:
            base_style['formality'] = context['formality']
        if 'warmth' in context:
            base_style['warmth'] = context['warmth']
        if 'humor' in context:
            base_style['humor'] = context['humor']
            
        # Adjust based on relationship
        base_style['warmth'] *= (1 + relationship.closeness * 0.5)
        base_style['formality'] *= (1 - relationship.closeness * 0.3)
        
        return base_style
        
    def _generate_response(self, relationship: Relationship, 
                          context: Dict[str, Any], 
                          style: Dict[str, float]) -> Dict[str, Any]:
        """Generate appropriate response"""
        # Consider relationship type
        if relationship.type == 'friend':
            return self._generate_friendly_response(relationship, context, style)
        elif relationship.type == 'professional':
            return self._generate_professional_response(relationship, context, style)
        elif relationship.type == 'family':
            return self._generate_family_response(relationship, context, style)
        else:
            return self._generate_general_response(relationship, context, style)
            
    def _generate_friendly_response(self, relationship: Relationship, 
                                  context: Dict[str, Any], 
                                  style: Dict[str, float]) -> Dict[str, Any]:
        """Generate friendly response"""
        return {
            'type': 'friendly',
            'content': self._generate_friendly_content(relationship, context),
            'tone': {
                'warmth': style['warmth'],
                'humor': style['humor'],
                'formality': style['formality']
            },
            'actions': [
                'Show interest in their life',
                'Share personal experiences',
                'Use casual language',
                'Show emotional support'
            ],
            'emotional_context': self._get_emotional_context(relationship)
        }
        
    def _generate_professional_response(self, relationship: Relationship, 
                                      context: Dict[str, Any], 
                                      style: Dict[str, float]) -> Dict[str, Any]:
        """Generate professional response"""
        return {
            'type': 'professional',
            'content': self._generate_professional_content(relationship, context),
            'tone': {
                'warmth': style['warmth'],
                'humor': style['humor'],
                'formality': style['formality']
            },
            'actions': [
                'Maintain professional boundaries',
                'Focus on work-related topics',
                'Use formal language',
                'Show respect and courtesy'
            ],
            'emotional_context': self._get_emotional_context(relationship)
        }
        
    def _generate_family_response(self, relationship: Relationship, 
                                context: Dict[str, Any], 
                                style: Dict[str, float]) -> Dict[str, Any]:
        """Generate family response"""
        return {
            'type': 'family',
            'content': self._generate_family_content(relationship, context),
            'tone': {
                'warmth': style['warmth'],
                'humor': style['humor'],
                'formality': style['formality']
            },
            'actions': [
                'Show deep emotional connection',
                'Share family experiences',
                'Use intimate language',
                'Provide unconditional support'
            ],
            'emotional_context': self._get_emotional_context(relationship)
        }
        
    def _generate_general_response(self, relationship: Relationship, 
                                 context: Dict[str, Any], 
                                 style: Dict[str, float]) -> Dict[str, Any]:
        """Generate general response"""
        return {
            'type': 'general',
            'content': self._generate_general_content(relationship, context),
            'tone': {
                'warmth': style['warmth'],
                'humor': style['humor'],
                'formality': style['formality']
            },
            'actions': [
                'Show basic respect',
                'Maintain appropriate distance',
                'Use neutral language',
                'Be helpful and courteous'
            ],
            'emotional_context': self._get_emotional_context(relationship)
        }
        
    def _get_conversation(self, target: str) -> Conversation:
        """Get or create conversation with target"""
        if target not in self.active_conversations:
            conversation = Conversation(
                participants=[target],
                context={},
                start_time=datetime.now(),
                topics=[],
                emotional_tone={},
                turn_history=[],
                active=True,
                quality=0.5
            )
            self.active_conversations[target] = conversation
        return self.active_conversations[target]
        
    def _process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message"""
        return {
            'content': message,
            'emotional_tone': self._analyze_emotional_tone(message),
            'topics': self._extract_topics(message),
            'intent': self._determine_intent(message),
            'context': context
        }
        
    def _generate_communication_response(self, conversation: Conversation, 
                                       processed_message: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate communication response"""
        # Update conversation context
        conversation.topics.extend(processed_message['topics'])
        conversation.emotional_tone.update(processed_message['emotional_tone'])
        
        # Generate appropriate response
        response = {
            'content': self._generate_message_content(conversation, processed_message),
            'emotional_tone': self._adjust_emotional_tone(conversation.emotional_tone),
            'topics': self._select_relevant_topics(conversation.topics),
            'intent': self._determine_response_intent(processed_message),
            'context': context
        }
        
        # Update conversation history
        conversation.turn_history.append({
            'message': processed_message,
            'response': response,
            'timestamp': datetime.now()
        })
        
        return response
        
    def _update_relationship(self, relationship: Relationship, 
                           interaction: Dict[str, Any], 
                           context: Dict[str, Any]):
        """Update relationship based on interaction"""
        # Update closeness
        relationship.closeness += self._calculate_closeness_change(interaction, context)
        
        # Update trust
        relationship.trust += self._calculate_trust_change(interaction, context)
        
        # Update emotional bond
        relationship.emotional_bond += self._calculate_emotional_bond_change(interaction, context)
        
        # Update shared experiences
        relationship.shared_experiences.append({
            'interaction': interaction,
            'context': context,
            'timestamp': datetime.now()
        })
        
        # Update last interaction
        relationship.last_interaction = datetime.now()
        
        # Update interaction history
        relationship.interaction_history.append({
            'interaction': interaction,
            'context': context,
            'timestamp': datetime.now()
        })
        
    def _strengthen_relationship(self, relationship: Relationship, 
                               context: Dict[str, Any]):
        """Strengthen existing relationship"""
        # Increase closeness
        relationship.closeness = min(1.0, relationship.closeness + 0.1)
        
        # Increase trust
        relationship.trust = min(1.0, relationship.trust + 0.1)
        
        # Increase emotional bond
        relationship.emotional_bond = min(1.0, relationship.emotional_bond + 0.1)
        
        # Update communication style
        relationship.communication_style['warmth'] = min(1.0, 
            relationship.communication_style['warmth'] + 0.1)
        relationship.communication_style['formality'] = max(0.0, 
            relationship.communication_style['formality'] - 0.1)
            
    def _determine_relationship_type(self, context: Dict[str, Any]) -> str:
        """Determine type of relationship to build"""
        if 'relationship_type' in context:
            return context['relationship_type']
            
        # Default to general relationship
        return 'general'
        
    def _determine_communication_style(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Determine initial communication style"""
        if 'communication_style' in context:
            return self.communication_styles[context['communication_style']]
            
        # Default to casual style
        return self.communication_styles['casual']
        
    def _establish_boundaries(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Establish relationship boundaries"""
        return {
            'personal_space': 0.7,
            'emotional_sharing': 0.5,
            'physical_contact': 0.3,
            'time_commitment': 0.5,
            'topic_sensitivity': 0.6
        }
        
    def _get_emotional_context(self, relationship: Relationship) -> Dict[str, float]:
        """Get emotional context for relationship"""
        return {
            'closeness': relationship.closeness,
            'trust': relationship.trust,
            'emotional_bond': relationship.emotional_bond,
            'comfort_level': relationship.closeness * relationship.trust
        } 