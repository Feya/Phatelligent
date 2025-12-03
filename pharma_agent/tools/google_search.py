"""
SerpAPI Search Tool - Uses SerpAPI for competitive intelligence
"""

import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class GoogleSearchTool:
    """Tool for searching Google using SerpAPI."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = os.getenv("SERPAPI_KEY")
        self.max_results = config.get("tools", {}).get("google_search", {}).get("max_results", 10)
    
    def search(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        """
        Execute Google search using SerpAPI.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.api_key:
            logger.warning("SerpAPI key not configured")
            return []
        
        num = num_results or self.max_results
        
        try:
            from serpapi import GoogleSearch
            
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": num,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            data = search.get_dict()
            
            results = []
            
            for item in data.get("organic_results", [])[:num]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": item.get("displayed_link", item.get("link"))
                })
            
            logger.info(f"SerpAPI Search returned {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"SerpAPI Search error: {e}")
            return []
    
    def as_tool(self):
        """Convert to Google Genai Tool format."""
        from google.generativeai import types
        
        return types.Tool(
            google_search=types.GoogleSearch()
        )
