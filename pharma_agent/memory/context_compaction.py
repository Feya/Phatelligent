"""
Context Compaction - Intelligent context summarization
Demonstrates: Context engineering, efficient memory usage
"""

import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)


class ContextCompactor:
    """
    Compacts large context to fit within token limits while preserving key information.
    Implements context engineering strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("memory", {}).get("context_compaction", {}).get("enabled", True)
        self.max_context_size = config.get("memory", {}).get("context_compaction", {}).get("max_context_size", 100000)
        self.compression_ratio = config.get("memory", {}).get("context_compaction", {}).get("compression_ratio", 0.3)
        
        logger.info(f"Context Compactor initialized (max size: {self.max_context_size})")
    
    def compact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compact context while preserving important information.
        
        Args:
            context: Full context dictionary
            
        Returns:
            Compacted context
        """
        if not self.enabled:
            return context
        
        # Estimate context size
        context_str = json.dumps(context)
        current_size = len(context_str)
        
        if current_size <= self.max_context_size:
            logger.debug(f"Context within limits ({current_size} chars)")
            return context
        
        logger.info(f"Compacting context from {current_size} to ~{int(current_size * self.compression_ratio)} chars")
        
        # Apply compaction strategies
        compacted = self._apply_compaction_strategies(context, current_size)
        
        return compacted
    
    def _apply_compaction_strategies(
        self,
        context: Dict[str, Any],
        current_size: int
    ) -> Dict[str, Any]:
        """Apply multiple compaction strategies."""
        
        compacted = {}
        
        # Strategy 1: Summarize previous analyses
        if "previous_analyses" in context:
            compacted["previous_analyses"] = self._summarize_analyses(
                context["previous_analyses"]
            )
        
        # Strategy 2: Keep only recent competitor profiles
        if "competitor_profiles" in context:
            compacted["competitor_profiles"] = self._compact_profiles(
                context["competitor_profiles"]
            )
        
        # Strategy 3: Keep summary
        if "summary" in context:
            compacted["summary"] = context["summary"]
        
        # Strategy 4: Extract key insights only
        compacted["key_points"] = self._extract_key_points(context)
        
        return compacted
    
    def _summarize_analyses(
        self,
        analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Summarize previous analyses to key points."""
        
        summarized = []
        
        # Keep only the most recent ones
        recent_analyses = analyses[:3]
        
        for analysis in recent_analyses:
            summarized.append({
                "id": analysis.get("id"),
                "query": analysis.get("query"),
                "summary": analysis.get("results_summary", "")[:200],  # Truncate
                "timestamp": analysis.get("timestamp")
            })
        
        return summarized
    
    def _compact_profiles(
        self,
        profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Compact competitor profiles to essential information."""
        
        compacted = {}
        
        for competitor, profile_data in profiles.items():
            data = profile_data.get("data", {})
            
            # Keep only essential fields
            compacted[competitor] = {
                "last_updated": profile_data.get("last_updated"),
                "last_known_state": data.get("last_known_state", {}),
                "recent_trend": self._get_recent_trend(data.get("history", []))
            }
        
        return compacted
    
    def _get_recent_trend(self, history: List[Dict[str, Any]]) -> str:
        """Extract most recent trend from history."""
        if not history:
            return "No trend data"
        
        recent = history[-1]
        insights = recent.get("insights", [])
        
        if insights:
            return insights[0] if isinstance(insights, list) else str(insights)[:100]
        
        return "No specific trend"
    
    def _extract_key_points(self, context: Dict[str, Any]) -> List[str]:
        """Extract key points from context."""
        
        key_points = []
        
        # Extract from summary
        if "summary" in context:
            key_points.append(context["summary"])
        
        # Extract from analyses
        if "previous_analyses" in context:
            for analysis in context["previous_analyses"][:2]:
                if "results_summary" in analysis:
                    key_points.append(analysis["results_summary"][:100])
        
        return key_points[:5]  # Keep top 5 points
    
    def estimate_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for context.
        Rough estimation: 1 token ≈ 4 characters
        """
        context_str = json.dumps(context)
        return len(context_str) // 4
    
    def should_compact(self, context: Dict[str, Any]) -> bool:
        """Check if context needs compaction."""
        estimated_tokens = self.estimate_token_count(context)
        max_tokens = self.max_context_size // 4
        
        return estimated_tokens > max_tokens
