"""
Vector Database Client Interface

Abstract interface for vector database operations.
Enables swapping between Pinecone, Weaviate, or other providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID


@dataclass
class VectorSearchResult:
    """
    Result from vector similarity search.
    
    Attributes:
        id: Vector ID
        score: Similarity score (0.0-1.0)
        metadata: Associated metadata
    """
    
    id: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorDBClient(ABC):
    """
    Abstract vector database client.
    
    Provides operations for storing and searching
    emotional context embeddings.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize client and connection."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close client connection."""
        pass
    
    @abstractmethod
    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict,
    ) -> bool:
        """
        Insert or update a vector.
        
        Args:
            id: Unique vector identifier
            vector: Embedding vector
            metadata: Associated metadata
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        vector: list[float],
        top_k: int = 10,
        filter: Optional[dict] = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar vectors.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar vectors with scores
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            id: Vector identifier
            
        Returns:
            True if deleted
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check vector database connectivity."""
        pass
