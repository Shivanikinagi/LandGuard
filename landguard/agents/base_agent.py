"""
Base Agent Class
Foundation for all LandGuard autonomous agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all LandGuard agents"""
    
    def __init__(self, name: str, capabilities: list = None):
        self.name = name
        self.capabilities = capabilities or []
        self.logger = logging.getLogger(f"landguard.agents.{name}")
        self.created_at = datetime.now()
        self.task_history = []
        
    @abstractmethod
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task asynchronously
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Dictionary with processing results
        """
        pass
        
    def log_task(self, task_data: Dict[str, Any], result: Dict[str, Any]):
        """Log task execution"""
        self.task_history.append({
            "timestamp": datetime.now(),
            "task": task_data,
            "result": result
        })
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "tasks_processed": len(self.task_history),
            "created_at": self.created_at.isoformat()
        }
        
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities