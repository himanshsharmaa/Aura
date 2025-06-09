import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import random
from collections import deque
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    EPISODIC = "episodic"  # Personal experiences
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # Skills and procedures
    EMOTIONAL = "emotional"  # Emotional experiences
    WORKING = "working"  # Short-term working memory

@dataclass
class Memory:
    """Represents a memory unit"""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    importance: float
    emotional_valence: float
    emotional_intensity: float
    associations: List[str]
    context: Dict[str, Any]
    last_accessed: datetime
    access_count: int
    confidence: float
    source: str
    metadata: Dict[str, Any]

class MemorySystem:
    def __init__(self):
        # Memory storage
        self.long_term_memory = {}  # id -> Memory
        self.short_term_memory = deque(maxlen=100)
        self.working_memory = deque(maxlen=7)  # Miller's Law: 7±2 items
        
        # Memory organization
        self.memory_index = {}  # keyword -> [memory_ids]
        self.associative_network = {}  # memory_id -> [connected_memory_ids]
        self.emotional_context = {}  # emotion -> [memory_ids]
        
        # Memory consolidation parameters
        self.consolidation_threshold = 0.7
        self.consolidation_rate = 0.1
        self.decay_rate = 0.05
        
        # Memory retrieval parameters
        self.retrieval_threshold = 0.5
        self.retrieval_confidence = 0.8
        self.retrieval_context_weight = 0.6
        
        # Learning parameters
        self.learning_rate = 0.1
        self.reinforcement_threshold = 0.7
        self.forgetting_threshold = 0.3
        
    def store_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                    context: Dict[str, Any]) -> str:
        """Store a new memory"""
        # Generate memory ID
        memory_id = self._generate_memory_id()
        
        # Create memory object
        memory = Memory(
            id=memory_id,
            type=memory_type,
            content=content,
            timestamp=datetime.now(),
            importance=self._calculate_importance(content, context),
            emotional_valence=self._calculate_emotional_valence(content, context),
            emotional_intensity=self._calculate_emotional_intensity(content, context),
            associations=self._generate_associations(content, context),
            context=context,
            last_accessed=datetime.now(),
            access_count=0,
            confidence=1.0,
            source=context.get('source', 'unknown'),
            metadata=self._extract_metadata(content, context)
        )
        
        # Store in appropriate memory system
        if memory_type == MemoryType.WORKING:
            self.working_memory.append(memory)
        else:
            self.short_term_memory.append(memory)
            self._index_memory(memory)
            
        return memory_id
        
    def retrieve_memory(self, query: Dict[str, Any], 
                       context: Dict[str, Any]) -> List[Memory]:
        """Retrieve relevant memories"""
        # Search in working memory first
        working_memories = self._search_working_memory(query, context)
        
        # Search in short-term memory
        short_term_memories = self._search_short_term_memory(query, context)
        
        # Search in long-term memory
        long_term_memories = self._search_long_term_memory(query, context)
        
        # Combine and rank results
        all_memories = working_memories + short_term_memories + long_term_memories
        ranked_memories = self._rank_memories(all_memories, query, context)
        
        # Update access statistics
        for memory in ranked_memories:
            self._update_memory_access(memory)
            
        return ranked_memories
        
    def consolidate_memories(self):
        """Consolidate memories from short-term to long-term storage"""
        for memory in list(self.short_term_memory):
            if self._should_consolidate(memory):
                self._consolidate_memory(memory)
                self.short_term_memory.remove(memory)
                
    def forget_memory(self, memory_id: str):
        """Forget a memory"""
        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            self._remove_from_index(memory)
            del self.long_term_memory[memory_id]
            
    def update_memory(self, memory_id: str, updates: Dict[str, Any]):
        """Update an existing memory"""
        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            self._apply_updates(memory, updates)
            self._update_index(memory)
            
    def _generate_memory_id(self) -> str:
        """Generate unique memory ID"""
        return f"mem_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        
    def _calculate_importance(self, content: Dict[str, Any], 
                            context: Dict[str, Any]) -> float:
        """Calculate memory importance"""
        base_importance = 0.5
        
        # Adjust based on content
        if 'importance' in content:
            base_importance = content['importance']
            
        # Adjust based on context
        if 'importance' in context:
            base_importance = max(base_importance, context['importance'])
            
        # Adjust based on emotional intensity
        emotional_intensity = self._calculate_emotional_intensity(content, context)
        base_importance = max(base_importance, emotional_intensity)
        
        return min(1.0, base_importance)
        
    def _calculate_emotional_valence(self, content: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """Calculate emotional valence (-1 to 1)"""
        if 'emotional_valence' in content:
            return content['emotional_valence']
        if 'emotional_valence' in context:
            return context['emotional_valence']
        return 0.0
        
    def _calculate_emotional_intensity(self, content: Dict[str, Any], 
                                     context: Dict[str, Any]) -> float:
        """Calculate emotional intensity (0 to 1)"""
        if 'emotional_intensity' in content:
            return content['emotional_intensity']
        if 'emotional_intensity' in context:
            return context['emotional_intensity']
        return 0.5
        
    def _generate_associations(self, content: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[str]:
        """Generate memory associations"""
        associations = []
        
        # Add content-based associations
        if 'keywords' in content:
            associations.extend(content['keywords'])
            
        # Add context-based associations
        if 'keywords' in context:
            associations.extend(context['keywords'])
            
        # Add emotional associations
        if 'emotions' in content:
            associations.extend(content['emotions'])
            
        return list(set(associations))
        
    def _extract_metadata(self, content: Dict[str, Any], 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract memory metadata"""
        metadata = {
            'source_type': context.get('source_type', 'unknown'),
            'confidence': context.get('confidence', 1.0),
            'reliability': context.get('reliability', 1.0),
            'verification_status': context.get('verification_status', 'unverified'),
            'tags': context.get('tags', []),
            'categories': context.get('categories', []),
            'relationships': context.get('relationships', {}),
            'location': context.get('location', None),
            'participants': context.get('participants', []),
            'duration': context.get('duration', None)
        }
        
        return metadata
        
    def _index_memory(self, memory: Memory):
        """Index memory for retrieval"""
        # Index by type
        if memory.type not in self.memory_index:
            self.memory_index[memory.type] = []
        self.memory_index[memory.type].append(memory.id)
        
        # Index by associations
        for association in memory.associations:
            if association not in self.memory_index:
                self.memory_index[association] = []
            self.memory_index[association].append(memory.id)
            
        # Index by emotional context
        if memory.emotional_valence > 0:
            if 'positive' not in self.emotional_context:
                self.emotional_context['positive'] = []
            self.emotional_context['positive'].append(memory.id)
        elif memory.emotional_valence < 0:
            if 'negative' not in self.emotional_context:
                self.emotional_context['negative'] = []
            self.emotional_context['negative'].append(memory.id)
            
    def _search_working_memory(self, query: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[Memory]:
        """Search in working memory"""
        return [mem for mem in self.working_memory 
                if self._matches_query(mem, query, context)]
                
    def _search_short_term_memory(self, query: Dict[str, Any], 
                                context: Dict[str, Any]) -> List[Memory]:
        """Search in short-term memory"""
        return [mem for mem in self.short_term_memory 
                if self._matches_query(mem, query, context)]
                
    def _search_long_term_memory(self, query: Dict[str, Any], 
                               context: Dict[str, Any]) -> List[Memory]:
        """Search in long-term memory"""
        relevant_ids = self._find_relevant_memory_ids(query, context)
        return [self.long_term_memory[mem_id] for mem_id in relevant_ids 
                if mem_id in self.long_term_memory]
                
    def _matches_query(self, memory: Memory, query: Dict[str, Any], 
                      context: Dict[str, Any]) -> bool:
        """Check if memory matches query"""
        # Check content match
        content_match = self._check_content_match(memory.content, query)
        
        # Check context match
        context_match = self._check_context_match(memory.context, context)
        
        # Check association match
        association_match = self._check_association_match(memory.associations, query)
        
        return content_match or context_match or association_match
        
    def _find_relevant_memory_ids(self, query: Dict[str, Any], 
                                context: Dict[str, Any]) -> List[str]:
        """Find relevant memory IDs"""
        relevant_ids = set()
        
        # Search by type
        if 'type' in query:
            memory_type = query['type']
            if memory_type in self.memory_index:
                relevant_ids.update(self.memory_index[memory_type])
                
        # Search by keywords
        if 'keywords' in query:
            for keyword in query['keywords']:
                if keyword in self.memory_index:
                    relevant_ids.update(self.memory_index[keyword])
                    
        # Search by emotional context
        if 'emotional_context' in query:
            emotional_context = query['emotional_context']
            if emotional_context in self.emotional_context:
                relevant_ids.update(self.emotional_context[emotional_context])
                
        return list(relevant_ids)
        
    def _rank_memories(self, memories: List[Memory], query: Dict[str, Any], 
                      context: Dict[str, Any]) -> List[Memory]:
        """Rank memories by relevance"""
        scored_memories = [(mem, self._calculate_relevance_score(mem, query, context)) 
                          for mem in memories]
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in scored_memories if score >= self.retrieval_threshold]
        
    def _calculate_relevance_score(self, memory: Memory, query: Dict[str, Any], 
                                 context: Dict[str, Any]) -> float:
        """Calculate memory relevance score"""
        # Content relevance
        content_score = self._calculate_content_relevance(memory.content, query)
        
        # Context relevance
        context_score = self._calculate_context_relevance(memory.context, context)
        
        # Temporal relevance
        temporal_score = self._calculate_temporal_relevance(memory.timestamp)
        
        # Emotional relevance
        emotional_score = self._calculate_emotional_relevance(memory, query)
        
        # Combine scores
        final_score = (content_score * 0.4 + 
                      context_score * 0.3 + 
                      temporal_score * 0.2 + 
                      emotional_score * 0.1)
                      
        return final_score
        
    def _should_consolidate(self, memory: Memory) -> bool:
        """Determine if memory should be consolidated"""
        # Check importance
        if memory.importance >= self.consolidation_threshold:
            return True
            
        # Check emotional intensity
        if memory.emotional_intensity >= self.consolidation_threshold:
            return True
            
        # Check access frequency
        if memory.access_count >= 3:
            return True
            
        return False
        
    def _consolidate_memory(self, memory: Memory):
        """Consolidate memory to long-term storage"""
        # Update confidence
        memory.confidence = min(1.0, memory.confidence + self.consolidation_rate)
        
        # Store in long-term memory
        self.long_term_memory[memory.id] = memory
        
        # Update index
        self._index_memory(memory)
        
    def _update_memory_access(self, memory: Memory):
        """Update memory access statistics"""
        memory.last_accessed = datetime.now()
        memory.access_count += 1
        
        # Update confidence based on access
        memory.confidence = min(1.0, memory.confidence + 0.1)
        
    def _remove_from_index(self, memory: Memory):
        """Remove memory from index"""
        # Remove from type index
        if memory.type in self.memory_index:
            self.memory_index[memory.type].remove(memory.id)
            
        # Remove from association index
        for association in memory.associations:
            if association in self.memory_index:
                self.memory_index[association].remove(memory.id)
                
        # Remove from emotional context
        if memory.emotional_valence > 0 and 'positive' in self.emotional_context:
            self.emotional_context['positive'].remove(memory.id)
        elif memory.emotional_valence < 0 and 'negative' in self.emotional_context:
            self.emotional_context['negative'].remove(memory.id)
            
    def _apply_updates(self, memory: Memory, updates: Dict[str, Any]):
        """Apply updates to memory"""
        # Update content
        if 'content' in updates:
            memory.content.update(updates['content'])
            
        # Update importance
        if 'importance' in updates:
            memory.importance = updates['importance']
            
        # Update emotional values
        if 'emotional_valence' in updates:
            memory.emotional_valence = updates['emotional_valence']
        if 'emotional_intensity' in updates:
            memory.emotional_intensity = updates['emotional_intensity']
            
        # Update associations
        if 'associations' in updates:
            memory.associations = updates['associations']
            
        # Update context
        if 'context' in updates:
            memory.context.update(updates['context'])
            
        # Update metadata
        if 'metadata' in updates:
            memory.metadata.update(updates['metadata'])
            
    def _update_index(self, memory: Memory):
        """Update memory index after changes"""
        self._remove_from_index(memory)
        self._index_memory(memory) 