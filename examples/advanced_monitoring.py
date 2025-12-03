"""
Advanced Monitoring Example
Demonstrates long-running operations, sessions, and pause/resume
"""

import asyncio
from pharma_agent import PharmaCompetitiveLandscapeAgent


async def monitoring_example():
    """Example of continuous monitoring with pause/resume."""
    
    print("👁️  Advanced Monitoring Example\n")
    
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer", "Moderna", "J&J", "AstraZeneca"],
        therapeutic_areas=["Vaccines", "Oncology", "Rare Diseases"]
    )
    
    # Example 1: Using sessions for continuity
    print("Example 1: Session Management")
    print("-" * 40)
    
    async with agent.create_session() as session:
        print(f"Created session: {session['id']}")
        
        # First analysis
        result1 = await agent.run_with_session(
            query="What are the latest developments in mRNA technology?",
            session_id=session['id']
        )
        
        print(f"Analysis 1 completed. Session analysis count: {session.get('analysis_count', 0)}")
        
        # Second analysis in same session (has context from first)
        result2 = await agent.run_with_session(
            query="How has the competitive landscape changed?",
            session_id=session['id']
        )
        
        print(f"Analysis 2 completed (with historical context)")
    
    # Example 2: Long-running operation with pause/resume
    print("\nExample 2: Pause and Resume")
    print("-" * 40)
    
    # Start a long analysis
    analysis_task = asyncio.create_task(
        agent.run(
            query="Comprehensive pipeline analysis for all competitors",
            enable_parallel=True
        )
    )
    
    # Simulate pausing after some time
    await asyncio.sleep(2)
    print("Pausing analysis...")
    await agent.pause()
    
    try:
        result = await asyncio.wait_for(analysis_task, timeout=5)
        if result.get('status') == 'paused':
            print(f"✓ Analysis paused. Checkpoint saved: {result.get('checkpoint_saved')}")
            
            # Resume later
            print("\nResuming analysis...")
            checkpoint_id = "checkpoint_from_previous"  # Would be saved
            resumed_result = await agent.resume(checkpoint_id)
            print("✓ Analysis resumed and completed")
    except asyncio.TimeoutError:
        print("Analysis in progress...")
    
    # Example 3: Continuous monitoring
    print("\nExample 3: Continuous Monitoring (background)")
    print("-" * 40)
    
    # Start background monitoring
    monitoring_status = await agent.start_monitoring(
        interval_hours=24,
        background=True
    )
    
    print(f"✓ Monitoring started: {monitoring_status}")
    print("  Agent will check for updates every 24 hours")
    print("  Running in background...")
    
    # Simulate running for a bit
    await asyncio.sleep(5)
    
    # Stop monitoring
    await agent.pause()
    print("\n✓ Monitoring stopped")
    
    # View metrics
    print("\nExample 4: Metrics")
    print("-" * 40)
    metrics = agent.get_metrics()
    
    print(f"Total Executions: {metrics.get('total_executions', 0)}")
    print(f"Success Rate: {metrics.get('success_rate', 0):.1%}")
    print(f"Average Time: {metrics.get('average_execution_time', 0):.2f}s")
    
    # Cleanup
    await agent.close()
    print("\n✅ Advanced monitoring example complete!")


if __name__ == "__main__":
    asyncio.run(monitoring_example())
