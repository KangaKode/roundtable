"""
RAG (Retrieval-Augmented Generation) infrastructure for the learning system.

  - vector_store.py: ChromaDB wrapper with in-memory fallback
  - embedding_service.py: Multi-provider embeddings with caching
  - preference_retriever.py: Semantic search over learned preferences
"""

from .vector_store import VectorStore
from .embedding_service import EmbeddingService
from .preference_retriever import PreferenceRetriever
