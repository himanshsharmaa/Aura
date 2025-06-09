import json
import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CloudSync:
    def __init__(self, api_key: str = None, endpoint: str = None):
        """
        Initialize cloud sync module.
        
        Args:
            api_key: API key for cloud service
            endpoint: Cloud service endpoint URL
        """
        self.api_key = api_key or os.getenv('AURA_CLOUD_API_KEY')
        self.endpoint = endpoint or os.getenv('AURA_CLOUD_ENDPOINT', 'https://api.aura.ai/v1')
        self.session = None
        self.sync_interval = 300  # 5 minutes
        self.last_sync = None
        self.pending_changes = []
        
    async def initialize(self):
        """Initialize cloud connection"""
        if not self.api_key:
            logger.warning("No API key provided for cloud sync")
            return False
            
        try:
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize cloud sync: {e}")
            return False
            
    async def sync_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Sync user data to cloud.
        
        Args:
            user_id: Unique user identifier
            data: User data to sync
            
        Returns:
            bool: Success status
        """
        if not self.session:
            if not await self.initialize():
                return False
                
        try:
            # Add metadata
            data['_metadata'] = {
                'last_modified': datetime.utcnow().isoformat(),
                'device_id': self._get_device_id(),
                'version': '1.0'
            }
            
            # Upload to cloud
            async with self.session.put(
                f"{self.endpoint}/users/{user_id}/data",
                json=data
            ) as response:
                if response.status == 200:
                    self.last_sync = datetime.utcnow()
                    logger.info(f"Successfully synced data for user {user_id}")
                    return True
                else:
                    logger.error(f"Failed to sync data: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error syncing user data: {e}")
            return False
            
    async def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user data from cloud.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Optional[Dict[str, Any]]: User data if successful, None otherwise
        """
        if not self.session:
            if not await self.initialize():
                return None
                
        try:
            async with self.session.get(
                f"{self.endpoint}/users/{user_id}/data"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved data for user {user_id}")
                    return data
                else:
                    logger.error(f"Failed to get data: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
            
    async def sync_memory(self, user_id: str, memory_data: Dict[str, Any]) -> bool:
        """
        Sync memory data to cloud.
        
        Args:
            user_id: Unique user identifier
            memory_data: Memory data to sync
            
        Returns:
            bool: Success status
        """
        if not self.session:
            if not await self.initialize():
                return False
                
        try:
            # Add metadata
            memory_data['_metadata'] = {
                'last_modified': datetime.utcnow().isoformat(),
                'device_id': self._get_device_id(),
                'type': 'memory'
            }
            
            # Upload to cloud
            async with self.session.post(
                f"{self.endpoint}/users/{user_id}/memories",
                json=memory_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully synced memory for user {user_id}")
                    return True
                else:
                    logger.error(f"Failed to sync memory: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error syncing memory: {e}")
            return False
            
    async def get_memories(self, user_id: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Optional[list]:
        """
        Retrieve memories from cloud.
        
        Args:
            user_id: Unique user identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Optional[list]: List of memories if successful, None otherwise
        """
        if not self.session:
            if not await self.initialize():
                return None
                
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()
                
            async with self.session.get(
                f"{self.endpoint}/users/{user_id}/memories",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved memories for user {user_id}")
                    return data
                else:
                    logger.error(f"Failed to get memories: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return None
            
    async def sync_preferences(self, user_id: str, 
                             preferences: Dict[str, Any]) -> bool:
        """
        Sync user preferences to cloud.
        
        Args:
            user_id: Unique user identifier
            preferences: User preferences to sync
            
        Returns:
            bool: Success status
        """
        if not self.session:
            if not await self.initialize():
                return False
                
        try:
            # Add metadata
            preferences['_metadata'] = {
                'last_modified': datetime.utcnow().isoformat(),
                'device_id': self._get_device_id(),
                'type': 'preferences'
            }
            
            # Upload to cloud
            async with self.session.put(
                f"{self.endpoint}/users/{user_id}/preferences",
                json=preferences
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully synced preferences for user {user_id}")
                    return True
                else:
                    logger.error(f"Failed to sync preferences: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error syncing preferences: {e}")
            return False
            
    def _get_device_id(self) -> str:
        """Get unique device identifier"""
        # In a real implementation, this would be a unique device ID
        # For now, use a combination of hostname and MAC address
        import platform
        import uuid
        
        hostname = platform.node()
        mac = uuid.getnode()
        return f"{hostname}-{mac}"
        
    async def close(self):
        """Close cloud connection"""
        if self.session:
            await self.session.close()
            self.session = None 