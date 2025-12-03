"""
Main Orchestrator Agent for Pharmaceutical Competitive Landscape Analysis
Demonstrates: Multi-agent orchestration, Sessions, Memory, Long-running operations
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

from google import genai
from google.genai import types

from .agents.research_agent import ResearchAgent
from .agents.analysis_agent import AnalysisAgent
from .agents.report_agent import ReportAgent
from .memory.session_service import SessionService
from .memory.memory_bank import MemoryBank
from .memory.context_compaction import ContextCompactor
from .observability.logging_config import setup_logging
from .observability.tracing import trace_agent_execution
from .observability.metrics import MetricsCollector
from .evaluation.evaluator import AgentEvaluator

logger = logging.getLogger(__name__)


class PharmaCompetitiveLandscapeAgent:
    """
    Main orchestrator agent that coordinates research, analysis, and reporting
    for pharmaceutical competitive landscape monitoring.
    
    Features:
    - Multi-agent orchestration (sequential and parallel)
    - Session management
    - Long-term memory
    - Pause/resume capability
    - Comprehensive observability
    """
    
    def __init__(
        self,
        competitors: List[str] = None,
        therapeutic_areas: List[str] = None,
        config_path: str = "config/agent_config.yaml"
    ):
        """Initialize the orchestrator agent with configuration."""
        
        # Setup logging
        setup_logging()
        logger.info("Initializing Pharma Competitive Landscape Agent")
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.competitors = competitors or self.config["competitors"]
        self.therapeutic_areas = therapeutic_areas or self.config["therapeutic_areas"]
        
        # Initialize Google Genai client
        self.client = genai.Client()
        
        # Initialize sub-agents
        self.research_agent = ResearchAgent(self.client, self.config)
        self.analysis_agent = AnalysisAgent(self.client, self.config)
        self.report_agent = ReportAgent(self.client, self.config)
        
        # Initialize memory and session management
        self.session_service = SessionService(self.config)
        self.memory_bank = MemoryBank(self.config)
        self.context_compactor = ContextCompactor(self.config)
        
        # Initialize observability
        self.metrics = MetricsCollector()
        self.evaluator = AgentEvaluator(self.config)
        
        # State for long-running operations
        self._is_paused = False
        self._checkpoint = None
        
        logger.info(f"Agent initialized with {len(self.competitors)} competitors")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "competitors": [],
            "therapeutic_areas": [],
            "monitoring": {"update_interval": "24h"},
            "tools": {"google_search": {"enabled": True}},
            "memory": {"session_service": {"type": "InMemory"}},
            "observability": {"logging": {"level": "INFO"}},
        }
    
    @trace_agent_execution
    async def run(
        self,
        query: str,
        session_id: Optional[str] = None,
        enable_parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Main execution method for competitive landscape analysis.
        
        Args:
            query: Natural language query for analysis
            session_id: Optional session ID for continuity
            enable_parallel: Whether to enable parallel execution
            
        Returns:
            Dictionary containing analysis results and report
        """
        start_time = datetime.now()
        logger.info(f"Starting analysis for query: {query}")
        
        try:
            # Get or create session
            session = await self.session_service.get_or_create_session(session_id)
            
            # Load relevant memories from memory bank
            historical_context = await self.memory_bank.retrieve_relevant_memories(
                query, self.competitors
            )
            
            # Compact context if needed
            if historical_context:
                historical_context = self.context_compactor.compact(historical_context)
            
            # Step 1: Research Phase (can be parallel)
            logger.info("Phase 1: Research - Gathering competitive intelligence")
            
            if enable_parallel:
                # Parallel research for multiple competitors
                research_tasks = [
                    self.research_agent.research_competitor(
                        competitor, 
                        self.therapeutic_areas,
                        historical_context
                    )
                    for competitor in self.competitors
                ]
                research_results = await asyncio.gather(*research_tasks)
            else:
                # Sequential research
                research_results = []
                for competitor in self.competitors:
                    result = await self.research_agent.research_competitor(
                        competitor,
                        self.therapeutic_areas,
                        historical_context
                    )
                    research_results.append(result)
            
            # Check for pause
            if self._is_paused:
                await self._save_checkpoint({
                    "phase": "research_complete",
                    "research_results": research_results,
                    "query": query
                })
                return {"status": "paused", "checkpoint_saved": True}
            
            # Step 2: Analysis Phase (sequential - depends on research)
            logger.info("Phase 2: Analysis - Processing competitive data")
            
            analysis_result = await self.analysis_agent.analyze_landscape(
                research_results,
                query,
                historical_context
            )
            
            # Check for pause
            if self._is_paused:
                await self._save_checkpoint({
                    "phase": "analysis_complete",
                    "research_results": research_results,
                    "analysis_result": analysis_result,
                    "query": query
                })
                return {"status": "paused", "checkpoint_saved": True}
            
            # Step 3: Report Generation (sequential - depends on analysis)
            logger.info("Phase 3: Report - Generating comprehensive report")
            
            report = await self.report_agent.generate_report(
                research_results,
                analysis_result,
                query
            )
            
            # Save to memory bank for future reference
            await self.memory_bank.store_analysis(
                query=query,
                competitors=self.competitors,
                results=analysis_result,
                timestamp=datetime.now()
            )
            
            # Update session
            await self.session_service.update_session(
                session["id"],
                {
                    "last_query": query,
                    "last_update": datetime.now().isoformat(),
                    "analysis_count": session.get("analysis_count", 0) + 1
                }
            )
            
            # Collect metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_execution(
                agent_name="orchestrator",
                execution_time=execution_time,
                success=True
            )
            
            # Evaluate results
            evaluation = await self.evaluator.evaluate(
                query=query,
                results=analysis_result,
                report=report
            )
            
            logger.info(f"Analysis completed in {execution_time:.2f} seconds")
            
            return {
                "status": "completed",
                "query": query,
                "research_results": research_results,
                "analysis": analysis_result,
                "report": report,
                "evaluation": evaluation,
                "session_id": session["id"],
                "execution_time": execution_time,
                "competitors_analyzed": len(self.competitors)
            }
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            self.metrics.record_execution(
                agent_name="orchestrator",
                execution_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error=str(e)
            )
            raise
    
    async def run_with_session(
        self,
        query: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Run analysis with an existing session."""
        return await self.run(query, session_id=session_id)
    
    async def pause(self):
        """Pause the current execution (for long-running operations)."""
        logger.info("Pausing agent execution")
        self._is_paused = True
    
    async def resume(self, checkpoint_id: str = None):
        """Resume from a saved checkpoint."""
        logger.info(f"Resuming agent execution from checkpoint: {checkpoint_id}")
        self._is_paused = False
        
        if checkpoint_id:
            checkpoint = await self._load_checkpoint(checkpoint_id)
            if checkpoint:
                return await self._resume_from_checkpoint(checkpoint)
        
        raise ValueError("No valid checkpoint found to resume from")
    
    async def _save_checkpoint(self, state: Dict[str, Any]) -> str:
        """Save current execution state."""
        checkpoint_id = f"checkpoint_{datetime.now().timestamp()}"
        self._checkpoint = {
            "id": checkpoint_id,
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to persistent storage (implementation depends on storage backend)
        await self.session_service.save_checkpoint(self._checkpoint)
        
        logger.info(f"Checkpoint saved: {checkpoint_id}")
        return checkpoint_id
    
    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a saved checkpoint."""
        return await self.session_service.load_checkpoint(checkpoint_id)
    
    async def _resume_from_checkpoint(self, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Resume execution from a checkpoint."""
        state = checkpoint["state"]
        phase = state["phase"]
        
        logger.info(f"Resuming from phase: {phase}")
        
        if phase == "research_complete":
            # Continue from analysis
            analysis_result = await self.analysis_agent.analyze_landscape(
                state["research_results"],
                state["query"],
                None
            )
            
            report = await self.report_agent.generate_report(
                state["research_results"],
                analysis_result,
                state["query"]
            )
            
            return {
                "status": "completed",
                "resumed_from": checkpoint["id"],
                "analysis": analysis_result,
                "report": report
            }
        
        elif phase == "analysis_complete":
            # Continue from report generation
            report = await self.report_agent.generate_report(
                state["research_results"],
                state["analysis_result"],
                state["query"]
            )
            
            return {
                "status": "completed",
                "resumed_from": checkpoint["id"],
                "report": report
            }
    
    async def start_monitoring(
        self,
        interval_hours: int = 24,
        background: bool = True
    ):
        """
        Start continuous monitoring (long-running operation).
        
        Args:
            interval_hours: How often to check for updates
            background: Whether to run in background
        """
        logger.info(f"Starting continuous monitoring (interval: {interval_hours}h)")
        
        async def monitoring_loop():
            while not self._is_paused:
                try:
                    # Run periodic analysis
                    result = await self.run(
                        query=f"Check for updates in competitive landscape",
                        enable_parallel=True
                    )
                    
                    logger.info(f"Monitoring cycle completed: {result['status']}")
                    
                    # Wait for next interval
                    await asyncio.sleep(interval_hours * 3600)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        
        if background:
            # Run in background task
            asyncio.create_task(monitoring_loop())
            return {"status": "monitoring_started", "background": True}
        else:
            # Run in foreground
            await monitoring_loop()
    
    async def create_session(self):
        """Create a new session context manager."""
        return self.session_service.create_session_context()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.get_all_metrics()
    
    async def close(self):
        """Cleanup resources."""
        logger.info("Closing agent and releasing resources")
        await self.session_service.close()
        await self.memory_bank.close()
