"""
Pinecone Vector Database Client

Implementation of vector database client for Pinecone.
Handles emotional history storage and similarity search.
"""

from typing import Optional

from pinecone import Pinecone, ServerlessSpec

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.infrastructure.vector_db.client import VectorDBClient, VectorSearchResult

logger = get_logger(__name__)


class PineconeVectorClient(VectorDBClient):
    """
    Pinecone vector database client.
    
    Manages emotional context embeddings for:
    - Storing user emotional states
    - Retrieving similar past experiences
    - Pattern detection support
    
    Usage:
        client = PineconeVectorClient()
        await client.initialize()
        await client.upsert(id="...", vector=[...], metadata={...})
        results = await client.search(vector=[...])
    """
    
    # Embedding dimension (must match model output)
    DIMENSION = 384  # all-MiniLM-L6-v2
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
    ) -> None:
        """
        Initialize Pinecone client.
        
        Args:
            api_key: Pinecone API key (defaults to settings)
            index_name: Index name (defaults to settings)
        """
        settings = get_settings()
        
        self._api_key = api_key or settings.pinecone.api_key.get_secret_value()
        self._index_name = index_name or settings.pinecone.index_name
        self._environment = settings.pinecone.environment
        
        self._pc: Optional[Pinecone] = None
        self._index = None
        self._initialized = False
    
    @property
    def provider_name(self) -> str:
        return "pinecone"
    
    async def initialize(self) -> None:
        """Initialize Pinecone client and ensure index exists."""
        if self._initialized:
            return
        
        if not self._api_key or self._api_key == "CHANGE_ME":
            logger.warning("Pinecone API key not configured")
            return
        
        try:
            self._pc = Pinecone(api_key=self._api_key)
            
            # Check if index exists, create if not
            existing_indexes = self._pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self._index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self._index_name}")
                self._pc.create_index(
                    name=self._index_name,
                    dimension=self.DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1",
                    ),
                )
            
            self._index = self._pc.Index(self._index_name)
            self._initialized = True
            logger.info("Pinecone client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def close(self) -> None:
        """Close Pinecone connection."""
        # Pinecone client doesn't require explicit close
        self._index = None
        self._pc = None
        self._initialized = False
    
    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict,
    ) -> bool:
        """
        Insert or update emotional context embedding.
        
        Args:
            id: Unique identifier (usually UUID)
            vector: Embedding vector (384 dimensions)
            metadata: Context metadata (user_id, timestamp, etc.)
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._index:
            logger.warning("Pinecone not available, skipping upsert")
            return False
        
        try:
            self._index.upsert(
                vectors=[(id, vector, metadata)],
            )
            
            logger.debug(f"Upserted vector: {id}")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            return False
    
    async def search(
        self,
        vector: list[float],
        top_k: int = 10,
        filter: Optional[dict] = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar emotional contexts.
        
        Args:
            vector: Query embedding
            top_k: Number of results
            filter: Metadata filter (e.g., {"user_id": "..."})
            
        Returns:
            List of similar contexts with scores
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._index:
            logger.warning("Pinecone not available, returning empty results")
            return []
        
        try:
            response = self._index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
            )
            
            results = [
                VectorSearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata or {},
                )
                for match in response.matches
            ]
            
            logger.debug(f"Vector search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    async def delete(self, id: str) -> bool:
        """Delete vector by ID."""
        if not self._initialized:
            await self.initialize()
        
        if not self._index:
            return False
        
        try:
            self._index.delete(ids=[id])
            return True
        except Exception as e:
            logger.error(f"Pinecone delete failed: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check Pinecone connectivity."""
        if not self._initialized:
            try:
                await self.initialize()
            except Exception:
                return False
        
        return self._initialized and self._index is not None
    
    async def search_by_user(
        self,
        vector: list[float],
        user_id: str,
        top_k: int = 10,
    ) -> list[VectorSearchResult]:
        """
        Search for similar contexts for a specific user.
        
        Convenience method that filters by user_id.
        
        Args:
            vector: Query embedding
            user_id: User ID to filter by
            top_k: Number of results
            
        Returns:
            Similar contexts for this user
        """
        return await self.search(
            vector=vector,
            top_k=top_k,
            filter={"user_id": user_id},
        )
