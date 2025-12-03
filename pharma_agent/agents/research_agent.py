"""
Research Agent - Gathers competitive intelligence
Demonstrates: Google Search tool, MCP tools, OpenAPI integration
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from google import genai
from google.genai import types

from ..tools.google_search import GoogleSearchTool
from ..tools.openapi_tools import FDAApiTool, ClinicalTrialsTool
from ..tools.custom_tools import DrugPipelineAnalyzer
from ..observability.tracing import trace_agent_execution

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Specialized agent for gathering pharmaceutical competitive intelligence.
    Uses Google Search, FDA API, and ClinicalTrials.gov to collect data.
    """
    
    def __init__(self, client: genai.Client, config: Dict[str, Any]):
        self.client = client
        self.config = config
        
        # Initialize tools
        self.google_search = GoogleSearchTool(config)
        self.fda_api = FDAApiTool(config)
        self.clinical_trials = ClinicalTrialsTool(config)
        self.pipeline_analyzer = DrugPipelineAnalyzer()
        
        # Configure agent with tools
        self.tools = self._setup_tools()
        
        logger.info("Research Agent initialized with tools")
    
    def _setup_tools(self) -> List[types.Tool]:
        """Setup available tools for the agent."""
        tools = []
        
        # Google Search tool
        if self.config.get("tools", {}).get("google_search", {}).get("enabled"):
            tools.append(self.google_search.as_tool())
        
        # FDA API tool
        if self.config.get("tools", {}).get("openapi", {}).get("fda", {}).get("enabled"):
            tools.append(self.fda_api.as_tool())
        
        # Clinical Trials tool
        if self.config.get("tools", {}).get("openapi", {}).get("clinicaltrials", {}).get("enabled"):
            tools.append(self.clinical_trials.as_tool())
        
        # Custom pipeline analyzer
        tools.append(self.pipeline_analyzer.as_tool())
        
        return tools
    
    @trace_agent_execution
    async def research_competitor(
        self,
        competitor: str,
        therapeutic_areas: List[str],
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Research a single competitor across multiple dimensions.
        
        Args:
            competitor: Company name
            therapeutic_areas: List of therapeutic areas to focus on
            historical_context: Previous knowledge about this competitor
            
        Returns:
            Comprehensive research data
        """
        logger.info(f"Researching competitor: {competitor}")
        
        try:
            # Create research prompt
            prompt = self._create_research_prompt(
                competitor,
                therapeutic_areas,
                historical_context
            )
            
            # Create agent with tools
            agent = self.client.agents.create(
                model="gemini-2.0-flash-001",
                tools=self.tools,
                instructions=f"""You are a pharmaceutical research specialist.
                
Your task is to gather comprehensive competitive intelligence about {competitor}.
Focus on:
1. Drug pipeline and development stages
2. Clinical trials status and results
3. FDA approvals and regulatory updates
4. Patent information
5. Market position and recent news
6. Partnerships and collaborations

Use all available tools to gather factual, up-to-date information.
Be thorough and cite sources when possible."""
            )
            
            # Execute research
            response = await agent.run(prompt)
            
            # Parse and structure the results
            research_data = {
                "competitor": competitor,
                "timestamp": datetime.now().isoformat(),
                "therapeutic_areas": therapeutic_areas,
                "findings": self._parse_research_results(response),
                "sources": self._extract_sources(response),
                "confidence_score": self._calculate_confidence(response)
            }
            
            logger.info(f"Research completed for {competitor}")
            return research_data
            
        except Exception as e:
            logger.error(f"Error researching {competitor}: {e}")
            return {
                "competitor": competitor,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_research_prompt(
        self,
        competitor: str,
        therapeutic_areas: List[str],
        historical_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create a detailed research prompt."""
        
        areas_str = ", ".join(therapeutic_areas)
        
        prompt = f"""Research {competitor} in the following therapeutic areas: {areas_str}

Please gather information on:
1. Current drug pipeline (by development phase)
2. Recent clinical trial results and ongoing trials
3. FDA approvals in the last 12 months
4. Key patents and intellectual property
5. Recent partnerships or acquisitions
6. Market share and competitive positioning
7. Recent news and press releases

"""
        
        if historical_context:
            prompt += f"\n\nHistorical context (use this to identify what's new):\n"
            prompt += f"{historical_context.get('summary', 'No previous data')}\n"
        
        prompt += "\n\nUse Google Search, FDA API, and Clinical Trials database to find accurate information."
        
        return prompt
    
    def _parse_research_results(self, response) -> Dict[str, Any]:
        """Parse and structure the research results."""
        # This would parse the agent's response into structured data
        # Implementation depends on response format
        
        return {
            "pipeline": {},
            "clinical_trials": [],
            "fda_approvals": [],
            "patents": [],
            "partnerships": [],
            "market_intelligence": {},
            "raw_response": str(response)
        }
    
    def _extract_sources(self, response) -> List[str]:
        """Extract cited sources from the response."""
        # Parse sources from the agent's response
        return []
    
    def _calculate_confidence(self, response) -> float:
        """Calculate confidence score based on source quality and data freshness."""
        # Simple confidence calculation
        return 0.8
    
    async def research_therapeutic_area(
        self,
        therapeutic_area: str,
        competitors: List[str]
    ) -> Dict[str, Any]:
        """Research a specific therapeutic area across multiple competitors."""
        
        logger.info(f"Researching therapeutic area: {therapeutic_area}")
        
        prompt = f"""Analyze the competitive landscape in {therapeutic_area}.

Focus on:
1. Key players and market leaders
2. Emerging treatments and technologies
3. Recent clinical trial results
4. Market size and growth projections
5. Unmet medical needs
6. Regulatory trends

Consider these competitors: {', '.join(competitors)}
"""
        
        agent = self.client.agents.create(
            model="gemini-2.0-flash-001",
            tools=self.tools,
            instructions="You are a pharmaceutical market analyst specializing in therapeutic area research."
        )
        
        response = await agent.run(prompt)
        
        return {
            "therapeutic_area": therapeutic_area,
            "competitors": competitors,
            "analysis": str(response),
            "timestamp": datetime.now().isoformat()
        }
