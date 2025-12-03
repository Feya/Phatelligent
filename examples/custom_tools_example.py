"""
Custom Tools Example
Demonstrates creating and using custom pharmaceutical tools
"""

import asyncio
from pharma_agent import PharmaCompetitiveLandscapeAgent
from pharma_agent.tools.custom_tools import DrugPipelineAnalyzer, CompetitorProfiler


async def custom_tools_example():
    """Example of using custom pharmaceutical tools."""
    
    print("🔧 Custom Tools Example\n")
    
    # Example 1: Drug Pipeline Analyzer
    print("Example 1: Drug Pipeline Analyzer")
    print("-" * 40)
    
    pipeline_analyzer = DrugPipelineAnalyzer()
    
    # Sample pipeline data
    sample_pipeline = [
        {"name": "Drug A", "stage": "Phase 3", "therapeutic_area": "Oncology"},
        {"name": "Drug B", "stage": "Phase 2", "therapeutic_area": "Oncology"},
        {"name": "Drug C", "stage": "Filed", "therapeutic_area": "Vaccines"},
        {"name": "Drug D", "stage": "Phase 1", "therapeutic_area": "Rare Diseases"},
        {"name": "Drug E", "stage": "Phase 3", "therapeutic_area": "Vaccines"},
    ]
    
    analysis = pipeline_analyzer.analyze_pipeline(sample_pipeline)
    
    print(f"Total Drugs: {analysis['total_drugs']}")
    print(f"\nBy Stage:")
    for stage, count in analysis['by_stage'].items():
        if count > 0:
            print(f"  {stage}: {count}")
    
    print(f"\nBy Therapeutic Area:")
    for area, count in analysis['by_therapeutic_area'].items():
        print(f"  {area}: {count}")
    
    print(f"\nPipeline Strength: {analysis['risk_assessment']['pipeline_strength']}")
    print(f"Near-term Launches: {analysis['risk_assessment']['near_term_launches']}")
    
    # Example 2: Competitor Profiler
    print("\n\nExample 2: Competitor Profiler")
    print("-" * 40)
    
    profiler = CompetitorProfiler()
    
    # Sample data for competitor
    competitor_data = {
        "pipeline": sample_pipeline,
        "approvals": [
            {"drug": "DrugX", "date": "2024-03-15"},
            {"drug": "DrugY", "date": "2024-06-20"}
        ],
        "trials": [
            {"trial_id": "NCT001", "phase": "3", "status": "Recruiting"},
            {"trial_id": "NCT002", "phase": "2", "status": "Active"},
            # ... more trials
        ] * 5  # Simulate 10 trials
    }
    
    profile = profiler.build_profile("Pfizer", competitor_data)
    
    print(f"Company: {profile['company']}")
    print(f"Market Position: {profile['market_position']}")
    
    print(f"\nStrengths:")
    for strength in profile['strengths']:
        print(f"  • {strength}")
    
    print(f"\nStrategic Focus:")
    for focus in profile['strategic_focus']:
        print(f"  • {focus}")
    
    # Example 3: Using custom tools with agent
    print("\n\nExample 3: Integration with Main Agent")
    print("-" * 40)
    
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer", "Moderna"],
        therapeutic_areas=["Vaccines"]
    )
    
    print("Running analysis with custom tools...")
    result = await agent.run(
        query="Analyze drug pipelines and competitive positioning"
    )
    
    print(f"✓ Analysis completed: {result['status']}")
    print(f"  Execution time: {result['execution_time']:.2f}s")
    print(f"  Quality score: {result['evaluation'].get('grade', 'N/A')}")
    
    await agent.close()
    
    print("\n✅ Custom tools example complete!")


if __name__ == "__main__":
    asyncio.run(custom_tools_example())
