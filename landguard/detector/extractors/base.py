"""
Base extractor interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExtractor(ABC):
    """Abstract base class for document extractors."""
    
    @abstractmethod
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from a file.
        
        Args:
            file_path: Path to the file to extract
            
        Returns:
            Dictionary containing extracted data
        """
        pass