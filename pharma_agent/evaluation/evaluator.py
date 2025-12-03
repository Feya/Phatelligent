"""
Agent Evaluator - Evaluation framework for agent performance
Demonstrates: Agent evaluation, quality metrics
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentEvaluator:
    """
    Evaluates agent performance based on multiple criteria.
    Provides metrics for accuracy, completeness, timeliness, and relevance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("evaluation", {}).get("enabled", True)
        self.metrics = config.get("evaluation", {}).get("metrics", [
            "accuracy", "completeness", "timeliness", "relevance"
        ])
        
        logger.info(f"Agent Evaluator initialized (metrics: {', '.join(self.metrics)})")
    
    async def evaluate(
        self,
        query: str,
        results: Dict[str, Any],
        report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate agent output quality.
        
        Args:
            query: Original query
            results: Analysis results
            report: Generated report
            
        Returns:
            Evaluation scores and feedback
        """
        if not self.enabled:
            return {"enabled": False}
        
        logger.info("Evaluating agent performance")
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "scores": {},
            "feedback": [],
            "overall_score": 0.0
        }
        
        # Evaluate each metric
        if "accuracy" in self.metrics:
            evaluation["scores"]["accuracy"] = self._evaluate_accuracy(results)
        
        if "completeness" in self.metrics:
            evaluation["scores"]["completeness"] = self._evaluate_completeness(results, report)
        
        if "timeliness" in self.metrics:
            evaluation["scores"]["timeliness"] = self._evaluate_timeliness(results)
        
        if "relevance" in self.metrics:
            evaluation["scores"]["relevance"] = self._evaluate_relevance(query, results)
        
        # Calculate overall score
        scores = list(evaluation["scores"].values())
        evaluation["overall_score"] = sum(scores) / len(scores) if scores else 0.0
        
        # Generate feedback
        evaluation["feedback"] = self._generate_feedback(evaluation["scores"])
        
        # Add grade
        evaluation["grade"] = self._calculate_grade(evaluation["overall_score"])
        
        logger.info(f"Evaluation complete: {evaluation['grade']} ({evaluation['overall_score']:.2f})")
        
        return evaluation
    
    def _evaluate_accuracy(self, results: Dict[str, Any]) -> float:
        """
        Evaluate accuracy of results.
        Based on confidence scores and data quality indicators.
        """
        # Check for errors
        if "error" in results:
            return 0.3
        
        # Check confidence metrics
        metrics = results.get("metrics", {})
        avg_confidence = metrics.get("average_confidence", 0.7)
        
        # Check for supporting evidence
        has_sources = len(results.get("key_insights", [])) > 0
        
        # Calculate accuracy score
        accuracy = avg_confidence * 0.7
        if has_sources:
            accuracy += 0.3
        
        return min(accuracy, 1.0)
    
    def _evaluate_completeness(self, results: Dict[str, Any], report: Dict[str, Any]) -> float:
        """
        Evaluate completeness of analysis.
        Checks if all required sections are present.
        """
        completeness = 0.0
        required_sections = [
            "key_insights",
            "competitive_positioning",
            "trends",
            "opportunities",
            "threats",
            "recommendations"
        ]
        
        present_sections = sum(
            1 for section in required_sections 
            if section in results and results[section]
        )
        
        completeness = present_sections / len(required_sections)
        
        # Check report completeness
        if "executive_summary" in report and report["executive_summary"]:
            completeness += 0.2
        
        return min(completeness, 1.0)
    
    def _evaluate_timeliness(self, results: Dict[str, Any]) -> float:
        """
        Evaluate timeliness of data.
        Based on data freshness indicators.
        """
        # Check metrics
        metrics = results.get("metrics", {})
        freshness = metrics.get("data_freshness", "unknown")
        
        if freshness == "current":
            return 1.0
        elif freshness == "recent":
            return 0.8
        elif freshness == "historical":
            return 0.6
        else:
            return 0.7  # Default
    
    def _evaluate_relevance(self, query: str, results: Dict[str, Any]) -> float:
        """
        Evaluate relevance of results to query.
        Simple keyword matching and result count check.
        """
        # Check if we have relevant results
        competitors_count = results.get("competitors_analyzed", 0)
        
        if competitors_count == 0:
            return 0.2
        
        # Check for insights
        insights = results.get("key_insights", [])
        if not insights:
            return 0.5
        
        # Simple relevance score based on output quantity
        relevance = 0.7
        
        if len(insights) > 3:
            relevance += 0.15
        
        if len(results.get("recommendations", [])) > 2:
            relevance += 0.15
        
        return min(relevance, 1.0)
    
    def _generate_feedback(self, scores: Dict[str, float]) -> List[str]:
        """Generate actionable feedback based on scores."""
        feedback = []
        
        for metric, score in scores.items():
            if score < 0.6:
                feedback.append(f"LOW {metric.upper()}: Score {score:.2f} - needs improvement")
            elif score < 0.8:
                feedback.append(f"{metric.title()}: Score {score:.2f} - good, can be enhanced")
            else:
                feedback.append(f"{metric.title()}: Score {score:.2f} - excellent")
        
        return feedback
    
    def _calculate_grade(self, overall_score: float) -> str:
        """Calculate letter grade from score."""
        if overall_score >= 0.9:
            return "A"
        elif overall_score >= 0.8:
            return "B"
        elif overall_score >= 0.7:
            return "C"
        elif overall_score >= 0.6:
            return "D"
        else:
            return "F"
    
    def compare_evaluations(
        self,
        eval1: Dict[str, Any],
        eval2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two evaluations to track improvement.
        
        Args:
            eval1: First evaluation
            eval2: Second evaluation
            
        Returns:
            Comparison results
        """
        comparison = {
            "score_diff": eval2["overall_score"] - eval1["overall_score"],
            "grade_change": f"{eval1['grade']} → {eval2['grade']}",
            "metric_changes": {}
        }
        
        for metric in eval1.get("scores", {}):
            if metric in eval2.get("scores", {}):
                diff = eval2["scores"][metric] - eval1["scores"][metric]
                comparison["metric_changes"][metric] = {
                    "change": diff,
                    "direction": "improved" if diff > 0 else "declined" if diff < 0 else "same"
                }
        
        return comparison
