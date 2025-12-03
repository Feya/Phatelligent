"""
Tracing - Distributed tracing for agent operations
Demonstrates: OpenTelemetry integration, observability
"""

import logging
import functools
import time
from typing import Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Flag to check if OpenTelemetry is available
OTEL_AVAILABLE = False

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTEL_AVAILABLE = True
except ImportError:
    logger.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")


class AgentTracer:
    """
    Tracer for agent operations.
    Provides distributed tracing capabilities.
    """
    
    def __init__(self, service_name: str = "pharma-agent"):
        self.service_name = service_name
        self.enabled = OTEL_AVAILABLE
        
        if self.enabled:
            self._setup_tracer()
    
    def _setup_tracer(self):
        """Setup OpenTelemetry tracer."""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0"
            })
            
            # Create tracer provider
            provider = TracerProvider(resource=resource)
            
            # Add console exporter for development
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))
            
            # Add OTLP exporter if configured
            import os
            otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            if otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            
            # Set as global tracer provider
            trace.set_tracer_provider(provider)
            
            self.tracer = trace.get_tracer(__name__)
            logger.info("OpenTelemetry tracing initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self.enabled = False
    
    def trace_operation(self, operation_name: str):
        """
        Create a trace span for an operation.
        
        Args:
            operation_name: Name of the operation
        """
        if not self.enabled:
            return DummySpan()
        
        return self.tracer.start_as_current_span(operation_name)


class DummySpan:
    """Dummy span when tracing is not available."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def set_attribute(self, key: str, value: Any):
        pass
    
    def add_event(self, name: str, attributes: dict = None):
        pass


# Global tracer instance
_tracer = AgentTracer()


def trace_agent_execution(func: Callable) -> Callable:
    """
    Decorator to trace agent function execution.
    
    Args:
        func: Function to trace
        
    Returns:
        Wrapped function with tracing
    """
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        span_name = f"{func.__module__}.{func.__name__}"
        
        start_time = time.time()
        
        with _tracer.trace_operation(span_name) as span:
            try:
                # Add attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Record success
                span.set_attribute("status", "success")
                span.set_attribute("execution_time", time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Record error
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.type", type(e).__name__)
                span.add_event("exception", {
                    "exception.message": str(e),
                    "exception.type": type(e).__name__
                })
                raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        span_name = f"{func.__module__}.{func.__name__}"
        
        start_time = time.time()
        
        with _tracer.trace_operation(span_name) as span:
            try:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                result = func(*args, **kwargs)
                
                span.set_attribute("status", "success")
                span.set_attribute("execution_time", time.time() - start_time)
                
                return result
                
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                raise
    
    # Return appropriate wrapper based on whether function is async
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def get_tracer() -> AgentTracer:
    """Get the global tracer instance."""
    return _tracer
