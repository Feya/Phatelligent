"""
Basic Usage Example
Demonstrates simple competitive landscape analysis
"""

import asyncio
from pharma_agent import PharmaCompetitiveLandscapeAgent


async def main():
    print("🔬 Pharma Competitive Landscape Agent - Basic Example\n")
    
    # Initialize agent
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer", "Moderna", "BioNTech"],
        therapeutic_areas=["Vaccines", "Oncology"]
    )
    
    # Run analysis
    print("Starting analysis...")
    result = await agent.run(
        query="Analyze the competitive landscape for COVID-19 vaccine developers"
    )
    
    # Display results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nStatus: {result['status']}")
    print(f"Competitors Analyzed: {result['competitors_analyzed']}")
    print(f"Execution Time: {result['execution_time']:.2f}s")
    
    # Key insights
    print("\n📊 KEY INSIGHTS:")
    analysis = result.get('analysis', {})
    for insight in analysis.get('key_insights', [])[:5]:
        print(f"  • {insight}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    for rec in analysis.get('recommendations', [])[:5]:
        print(f"  • {rec}")
    
    # Evaluation
    evaluation = result.get('evaluation', {})
    print(f"\n📋 QUALITY SCORE: {evaluation.get('grade', 'N/A')} ({evaluation.get('overall_score', 0):.2f})")
    
    # Export report
    report = result.get('report', {})
    if report:
        print("\n📄 Generating report...")
        from pharma_agent.agents.report_agent import ReportAgent
        
        report_agent = ReportAgent(agent.client, agent.config)
        markdown_report = await report_agent.export_report(report, format="markdown")
        
        # Save to file
        with open("competitive_landscape_report.md", "w") as f:
            f.write(markdown_report)
        
        print("   Report saved to: competitive_landscape_report.md")
    
    # Cleanup
    await agent.close()
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())
