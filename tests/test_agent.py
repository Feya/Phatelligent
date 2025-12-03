"""
Test Suite for Pharma Competitive Landscape Agent
"""

import pytest
import asyncio
from pharma_agent import PharmaCompetitiveLandscapeAgent


@pytest.mark.asyncio
async def test_basic_initialization():
    """Test agent initialization."""
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer", "Moderna"],
        therapeutic_areas=["Vaccines"]
    )
    
    assert agent is not None
    assert len(agent.competitors) == 2
    assert "Vaccines" in agent.therapeutic_areas
    
    await agent.close()


@pytest.mark.asyncio
async def test_analysis_execution():
    """Test basic analysis execution."""
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer"],
        therapeutic_areas=["Vaccines"]
    )
    
    result = await agent.run(
        query="Analyze Pfizer's vaccine pipeline"
    )
    
    assert result['status'] == 'completed'
    assert 'analysis' in result
    assert 'report' in result
    assert 'evaluation' in result
    
    await agent.close()


@pytest.mark.asyncio
async def test_session_management():
    """Test session creation and management."""
    agent = PharmaCompetitiveLandscapeAgent()
    
    session = await agent.session_service.get_or_create_session()
    assert session is not None
    assert 'id' in session
    
    # Update session
    updated = await agent.session_service.update_session(
        session['id'],
        {'test_field': 'test_value'}
    )
    assert updated['test_field'] == 'test_value'
    
    await agent.close()


@pytest.mark.asyncio
async def test_memory_storage():
    """Test memory bank storage and retrieval."""
    agent = PharmaCompetitiveLandscapeAgent()
    
    # Store analysis
    from datetime import datetime
    analysis_id = await agent.memory_bank.store_analysis(
        query="Test query",
        competitors=["Pfizer"],
        results={"key_insights": ["Test insight"]},
        timestamp=datetime.now()
    )
    
    assert analysis_id != ""
    
    # Retrieve memories
    memories = await agent.memory_bank.retrieve_relevant_memories(
        query="Test query",
        competitors=["Pfizer"]
    )
    
    assert memories is not None
    
    await agent.close()


@pytest.mark.asyncio
async def test_evaluation():
    """Test evaluation framework."""
    agent = PharmaCompetitiveLandscapeAgent()
    
    # Mock results
    mock_results = {
        "key_insights": ["Insight 1", "Insight 2"],
        "recommendations": ["Rec 1", "Rec 2"],
        "competitors_analyzed": 1,
        "metrics": {"average_confidence": 0.8}
    }
    
    mock_report = {
        "executive_summary": "Test summary",
        "title": "Test Report"
    }
    
    evaluation = await agent.evaluator.evaluate(
        query="Test query",
        results=mock_results,
        report=mock_report
    )
    
    assert 'scores' in evaluation
    assert 'overall_score' in evaluation
    assert 'grade' in evaluation
    
    await agent.close()


def test_metrics_collection():
    """Test metrics collector."""
    from pharma_agent.observability.metrics import MetricsCollector
    
    metrics = MetricsCollector()
    
    # Record execution
    metrics.record_execution(
        agent_name="test_agent",
        execution_time=1.5,
        success=True
    )
    
    # Get metrics
    all_metrics = metrics.get_all_metrics()
    
    assert all_metrics['total_executions'] == 1
    assert all_metrics['successful_executions'] == 1
    assert all_metrics['success_rate'] == 1.0


def test_context_compaction():
    """Test context compaction."""
    from pharma_agent.memory.context_compaction import ContextCompactor
    
    config = {
        "memory": {
            "context_compaction": {
                "enabled": True,
                "max_context_size": 1000,
                "compression_ratio": 0.3
            }
        }
    }
    
    compactor = ContextCompactor(config)
    
    # Create large context
    large_context = {
        "previous_analyses": [{"data": "x" * 1000} for _ in range(10)],
        "summary": "Test summary"
    }
    
    # Compact
    compacted = compactor.compact(large_context)
    
    assert compacted is not None
    assert "summary" in compacted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
