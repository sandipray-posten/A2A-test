"""
Gravitee Gateway Configuration for A2A Agents

All credentials loaded from environment variables for security.
"""

import os
from typing import Optional


class GraviteeConfig:
    """Gravitee gateway configuration - all values from environment"""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize Gravitee config from environment variables.
        
        Required env vars:
            GRAVITEE_BASE_URL: Gravitee gateway base URL
            GRAVITEE_API_KEY: Gravitee API key
            GRAVITEE_API_PLATFORM_KEY: Platform API key (defaults to GRAVITEE_API_KEY)
            LLM_MODEL: Model identifier (optional, defaults to demo-openai:gpt-4.1)
        """
        self.base_url = os.getenv("GRAVITEE_BASE_URL")
        self.api_key = os.getenv("GRAVITEE_API_KEY")
        self.api_platform_key = os.getenv("GRAVITEE_API_PLATFORM_KEY") or self.api_key
        self.model = model or os.getenv("LLM_MODEL", "demo-openai:gpt-4.1")
        
        # Validate required configuration
        if not self.base_url:
            raise ValueError("GRAVITEE_BASE_URL environment variable is required")
        if not self.api_key:
            raise ValueError("GRAVITEE_API_KEY environment variable is required")
    
    def get_headers(self) -> dict:
        """Get default headers for Gravitee requests"""
        return {
            "x-api-platform-api-key": self.api_platform_key,
        }
    
    def is_configured(self) -> bool:
        """Check if Gravitee is properly configured"""
        return bool(self.base_url and self.api_key)
    
    def __repr__(self) -> str:
        return (
            f"GraviteeConfig(base_url={self.base_url[:50]}..., "
            f"api_key={'***' if self.api_key else 'NOT SET'}, "
            f"model={self.model})"
        )
