"""
Google Search Tool - Uses Google Search API for competitive intelligence
"""

import logging
import os
from typing import Dict, Any, List
import requests

logger = logging.getLogger(__name__)


class GoogleSearchTool:
    """Tool for searching Google using Custom Search API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.max_results = config.get("tools", {}).get("google_search", {}).get("max_results", 10)
    
    def search(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        """
        Execute Google search.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API credentials not configured")
            return []
        
        num = num_results or self.max_results
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num, 10)  # API limit per request
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": item.get("displayLink")
                })
            
            logger.info(f"Google Search returned {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Google Search error: {e}")
            return []
    
    def as_tool(self):
        """Convert to Google Genai Tool format."""
        from google.genai import types
        
        return types.Tool(
            google_search=types.GoogleSearch()
        )
