"""
LLM Client -- Provider-agnostic wrapper with automatic prompt caching.

Supports Anthropic (Claude), OpenAI (GPT), and Google (Gemini).
Handles prompt caching, token tracking, retries, and security sanitization.

Usage:
    from .llm import create_client

    client = create_client()  # Auto-detects provider from env
    response = await client.call(prompt="Analyze this", role="analyst")
    print(response.content)
    print(f"Tokens: {response.usage}")
"""

from .client import LLMClient, LLMResponse, CacheablePrompt, create_client
