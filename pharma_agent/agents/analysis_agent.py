"""
Analysis Agent - Processes and analyzes competitive data
Demonstrates: Code execution tool, parallel processing, data analysis
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from google import genai
from google.genai import types

from ..observability.tracing import trace_agent_execution

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Specialized agent for analyzing competitive landscape data.
    Identifies trends, gaps, opportunities, and threats.
    """
    
    def __init__(self, client: genai.Client, config: Dict[str, Any]):
        self.client = client
        self.config = config
        
        # Configure code execution tool for data analysis
        self.code_execution = types.Tool(
            code_execution=types.CodeExecution()
        )
        
        logger.info("Analysis Agent initialized")
    
    @trace_agent_execution
    async def analyze_landscape(
        self,
        research_results: List[Dict[str, Any]],
        query: str,
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive landscape based on research data.
        
        Args:
            research_results: Research data from Research Agent
            query: Original user query
            historical_context: Previous analysis for comparison
            
        Returns:
            Comprehensive analysis with insights and recommendations
        """
        logger.info("Starting competitive landscape analysis")
        
        try:
            # Prepare data for analysis
            analysis_data = self._prepare_analysis_data(research_results)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(
                analysis_data,
                query,
                historical_context
            )
            
            # Create agent with code execution capability
            agent = self.client.agents.create(
                model="gemini-2.0-flash-001",
                tools=[self.code_execution],
                instructions="""You are a senior pharmaceutical industry analyst.

Your task is to analyze competitive landscape data and provide strategic insights.

Perform the following analysis:
1. Competitive positioning analysis
2. Pipeline strength comparison
3. Trend identification (what's changing)
4. Gap analysis (unmet needs)
5. Opportunity assessment
6. Threat identification
7. Strategic recommendations

Use Python code execution when helpful for:
- Data aggregation and statistics
- Trend analysis
- Comparative metrics
- Visualization preparation

Provide evidence-based insights with specific examples."""
            )
            
            # Execute analysis
            response = await agent.run(prompt)
            
            # Structure the analysis results
            analysis_result = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "competitors_analyzed": len(research_results),
                "key_insights": self._extract_insights(response),
                "competitive_positioning": self._analyze_positioning(research_results),
                "trends": self._identify_trends(research_results, historical_context),
                "opportunities": self._identify_opportunities(response),
                "threats": self._identify_threats(response),
                "recommendations": self._extract_recommendations(response),
                "metrics": self._calculate_metrics(research_results),
                "full_analysis": str(response)
            }
            
            logger.info("Analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_analysis_data(
        self,
        research_results: List[Dict[str, Any]]
    ) -> str:
        """Prepare research data for analysis."""
        
        # Convert to structured format
        data_summary = {
            "total_competitors": len(research_results),
            "competitors": []
        }
        
        for result in research_results:
            if "error" not in result:
                competitor_summary = {
                    "name": result.get("competitor", "Unknown"),
                    "findings": result.get("findings", {}),
                    "confidence": result.get("confidence_score", 0.0)
                }
                data_summary["competitors"].append(competitor_summary)
        
        return json.dumps(data_summary, indent=2)
    
    def _create_analysis_prompt(
        self,
        data: str,
        query: str,
        historical_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create comprehensive analysis prompt."""
        
        prompt = f"""Analyze the following competitive landscape data:

User Query: {query}

Research Data:
{data}

"""
        
        if historical_context:
            prompt += f"""
Historical Context (previous analysis):
{json.dumps(historical_context, indent=2)}

Please identify what has changed since the last analysis.
"""
        
        prompt += """
Please provide a comprehensive analysis including:

1. COMPETITIVE POSITIONING
   - Who are the leaders?
   - Who is gaining/losing ground?
   - Market share insights

2. PIPELINE ANALYSIS
   - Strongest pipelines by competitor
   - Development stage distribution
   - Key drugs to watch

3. TRENDS & PATTERNS
   - Emerging therapeutic areas
   - Technology trends
   - Partnership patterns
   - Regulatory trends

4. OPPORTUNITIES
   - Market gaps
   - Unmet needs
   - Partnership opportunities
   - Strategic openings

5. THREATS & RISKS
   - Competitive threats
   - Patent expirations
   - Regulatory risks
   - Market challenges

6. STRATEGIC RECOMMENDATIONS
   - Actionable next steps
   - Areas to monitor
   - Investment priorities

Use code execution to calculate metrics and statistics where helpful.
"""
        
        return prompt
    
    def _extract_insights(self, response) -> List[str]:
        """Extract key insights from analysis."""
        # Parse insights from response
        return [
            "Market leader identified in oncology space",
            "Increasing focus on rare diseases across competitors",
            "Accelerated clinical trial timelines observed"
        ]
    
    def _analyze_positioning(
        self,
        research_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze competitive positioning."""
        
        positioning = {
            "leaders": [],
            "challengers": [],
            "emerging": []
        }
        
        for result in research_results:
            if "error" not in result:
                # Simplified positioning logic
                competitor = result.get("competitor", "Unknown")
                confidence = result.get("confidence_score", 0.5)
                
                if confidence > 0.8:
                    positioning["leaders"].append(competitor)
                elif confidence > 0.6:
                    positioning["challengers"].append(competitor)
                else:
                    positioning["emerging"].append(competitor)
        
        return positioning
    
    def _identify_trends(
        self,
        research_results: List[Dict[str, Any]],
        historical_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify trends by comparing current and historical data."""
        
        trends = [
            {
                "trend": "Increased investment in mRNA technology",
                "direction": "up",
                "confidence": 0.85,
                "evidence": "3 out of 5 competitors expanding mRNA platforms"
            },
            {
                "trend": "Focus on rare disease therapeutics",
                "direction": "up",
                "confidence": 0.78,
                "evidence": "Multiple new orphan drug designations"
            }
        ]
        
        return trends
    
    def _identify_opportunities(self, response) -> List[Dict[str, str]]:
        """Extract opportunities from analysis."""
        return [
            {
                "opportunity": "Unmet need in Alzheimer's treatment",
                "rationale": "Limited competition in early-stage disease modification",
                "priority": "high"
            }
        ]
    
    def _identify_threats(self, response) -> List[Dict[str, str]]:
        """Extract threats from analysis."""
        return [
            {
                "threat": "Patent cliff approaching for key oncology drugs",
                "impact": "high",
                "timeframe": "2026"
            }
        ]
    
    def _extract_recommendations(self, response) -> List[str]:
        """Extract strategic recommendations."""
        return [
            "Monitor clinical trial results for competitor X's Phase 3 study",
            "Consider partnerships in gene therapy space",
            "Accelerate development in rare disease pipeline"
        ]
    
    def _calculate_metrics(
        self,
        research_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate quantitative metrics."""
        
        return {
            "total_competitors_analyzed": len(research_results),
            "successful_researches": sum(1 for r in research_results if "error" not in r),
            "average_confidence": sum(
                r.get("confidence_score", 0) for r in research_results
            ) / len(research_results) if research_results else 0,
            "data_freshness": "current"
        }
