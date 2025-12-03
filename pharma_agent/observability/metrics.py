"""
Metrics Collection - Performance and usage metrics
Demonstrates: Prometheus-compatible metrics, monitoring
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# Check if prometheus_client is available
PROMETHEUS_AVAILABLE = False
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("Prometheus client not available")


class MetricsCollector:
    """
    Collects and exposes metrics for monitoring agent performance.
    Compatible with Prometheus.
    """
    
    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE
        self._metrics_data = defaultdict(list)
        self._lock = threading.Lock()
        
        if self.enabled:
            self._setup_prometheus_metrics()
        
        logger.info("Metrics Collector initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        try:
            # Agent execution metrics
            self.execution_counter = Counter(
                'agent_executions_total',
                'Total number of agent executions',
                ['agent_name', 'status']
            )
            
            self.execution_duration = Histogram(
                'agent_execution_duration_seconds',
                'Agent execution duration in seconds',
                ['agent_name']
            )
            
            self.active_sessions = Gauge(
                'agent_active_sessions',
                'Number of active agent sessions'
            )
            
            self.memory_usage = Gauge(
                'agent_memory_entries',
                'Number of entries in memory bank'
            )
            
            self.tool_usage = Counter(
                'agent_tool_usage_total',
                'Tool usage count',
                ['tool_name']
            )
            
            logger.info("Prometheus metrics configured")
            
        except Exception as e:
            logger.error(f"Failed to setup Prometheus metrics: {e}")
            self.enabled = False
    
    def record_execution(
        self,
        agent_name: str,
        execution_time: float,
        success: bool,
        error: str = None
    ):
        """
        Record an agent execution.
        
        Args:
            agent_name: Name of the agent
            execution_time: Execution time in seconds
            success: Whether execution was successful
            error: Error message if failed
        """
        status = "success" if success else "error"
        
        # Store in internal metrics
        with self._lock:
            self._metrics_data["executions"].append({
                "agent": agent_name,
                "time": execution_time,
                "status": status,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
        
        # Update Prometheus metrics
        if self.enabled:
            self.execution_counter.labels(
                agent_name=agent_name,
                status=status
            ).inc()
            
            self.execution_duration.labels(
                agent_name=agent_name
            ).observe(execution_time)
        
        logger.debug(f"Recorded execution: {agent_name} - {status} - {execution_time:.2f}s")
    
    def record_tool_usage(self, tool_name: str):
        """Record usage of a tool."""
        with self._lock:
            self._metrics_data["tools"].append({
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            })
        
        if self.enabled:
            self.tool_usage.labels(tool_name=tool_name).inc()
    
    def update_active_sessions(self, count: int):
        """Update active sessions count."""
        if self.enabled:
            self.active_sessions.set(count)
    
    def update_memory_entries(self, count: int):
        """Update memory bank entries count."""
        if self.enabled:
            self.memory_usage.set(count)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of metrics
        """
        with self._lock:
            # Calculate aggregates
            executions = self._metrics_data.get("executions", [])
            
            successful = sum(1 for e in executions if e["status"] == "success")
            failed = sum(1 for e in executions if e["status"] == "error")
            
            avg_time = (
                sum(e["time"] for e in executions) / len(executions)
                if executions else 0
            )
            
            return {
                "total_executions": len(executions),
                "successful_executions": successful,
                "failed_executions": failed,
                "success_rate": successful / len(executions) if executions else 0,
                "average_execution_time": avg_time,
                "tool_usage": len(self._metrics_data.get("tools", [])),
                "recent_executions": executions[-10:] if executions else []
            }
    
    def get_prometheus_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.
        
        Returns:
            Metrics in Prometheus text format
        """
        if not self.enabled:
            return b"# Prometheus metrics not available\n"
        
        return generate_latest(REGISTRY)
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ('json' or 'prometheus')
            
        Returns:
            Formatted metrics
        """
        if format == "json":
            import json
            return json.dumps(self.get_all_metrics(), indent=2)
        elif format == "prometheus":
            return self.get_prometheus_metrics().decode()
        else:
            raise ValueError(f"Unsupported format: {format}")
