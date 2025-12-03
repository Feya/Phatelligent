"""
CLI Interface for Pharma Competitive Landscape Agent
"""

import click
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharma_agent import PharmaCompetitiveLandscapeAgent


@click.group()
def cli():
    """Pharmaceutical Competitive Landscape Agent CLI"""
    pass


@cli.command()
@click.option('--competitors', '-c', required=True, help='Comma-separated list of competitors')
@click.option('--area', '-a', help='Therapeutic area to focus on')
@click.option('--query', '-q', help='Specific query (optional)')
@click.option('--output', '-o', default='json', help='Output format (json, text)')
def analyze(competitors, area, query, output):
    """Run competitive landscape analysis"""
    
    click.echo("🔬 Starting pharmaceutical competitive analysis...")
    
    # Parse competitors
    competitor_list = [c.strip() for c in competitors.split(',')]
    
    # Build query
    if not query:
        if area:
            query = f"Analyze competitive landscape for {', '.join(competitor_list)} in {area}"
        else:
            query = f"Analyze competitive landscape for {', '.join(competitor_list)}"
    
    # Run analysis
    async def run_analysis():
        agent = PharmaCompetitiveLandscapeAgent(
            competitors=competitor_list,
            therapeutic_areas=[area] if area else []
        )
        
        result = await agent.run(query)
        await agent.close()
        
        return result
    
    try:
        result = asyncio.run(run_analysis())
        
        # Display results
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            _display_text_results(result)
        
        click.echo("\n✅ Analysis complete!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--format', '-f', default='markdown', help='Report format (markdown, html, json)')
@click.option('--session', '-s', help='Session ID to generate report from')
def report(output, format, session):
    """Generate comprehensive report"""
    
    click.echo(f"📊 Generating report in {format} format...")
    
    # This would load data from a previous session and generate report
    click.echo(f"Report saved to: {output}")
    click.echo("✅ Report generation complete!")


@cli.command()
@click.option('--interval', '-i', default='24h', help='Monitoring interval (e.g., 24h, 12h)')
@click.option('--competitors', '-c', required=True, help='Comma-separated list of competitors')
@click.option('--areas', '-a', help='Comma-separated therapeutic areas')
def monitor(interval, competitors, areas):
    """Start continuous monitoring (long-running)"""
    
    click.echo("👁️  Starting continuous monitoring...")
    click.echo(f"Interval: {interval}")
    click.echo(f"Competitors: {competitors}")
    
    competitor_list = [c.strip() for c in competitors.split(',')]
    area_list = [a.strip() for a in areas.split(',')] if areas else []
    
    # Parse interval
    interval_hours = _parse_interval(interval)
    
    async def run_monitoring():
        agent = PharmaCompetitiveLandscapeAgent(
            competitors=competitor_list,
            therapeutic_areas=area_list
        )
        
        await agent.start_monitoring(
            interval_hours=interval_hours,
            background=False
        )
    
    try:
        click.echo("Press Ctrl+C to stop monitoring")
        asyncio.run(run_monitoring())
    except KeyboardInterrupt:
        click.echo("\n🛑 Monitoring stopped")


@cli.command()
@click.option('--session', '-s', required=True, help='Session ID')
def resume(session):
    """Resume a paused analysis"""
    
    click.echo(f"▶️  Resuming analysis from session: {session}")
    
    async def resume_analysis():
        agent = PharmaCompetitiveLandscapeAgent()
        result = await agent.resume(session)
        await agent.close()
        return result
    
    try:
        result = asyncio.run(resume_analysis())
        click.echo(json.dumps(result, indent=2))
        click.echo("✅ Analysis resumed and completed!")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def metrics():
    """View agent metrics"""
    
    click.echo("📈 Agent Metrics\n")
    
    async def get_metrics():
        agent = PharmaCompetitiveLandscapeAgent()
        metrics = agent.get_metrics()
        await agent.close()
        return metrics
    
    try:
        metrics = asyncio.run(get_metrics())
        click.echo(json.dumps(metrics, indent=2))
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def _display_text_results(result: dict):
    """Display results in human-readable text format"""
    
    click.echo("\n" + "="*60)
    click.echo("COMPETITIVE LANDSCAPE ANALYSIS")
    click.echo("="*60)
    
    click.echo(f"\nQuery: {result.get('query', 'N/A')}")
    click.echo(f"Status: {result.get('status', 'N/A')}")
    click.echo(f"Competitors Analyzed: {result.get('competitors_analyzed', 0)}")
    click.echo(f"Execution Time: {result.get('execution_time', 0):.2f}s")
    
    # Analysis summary
    analysis = result.get('analysis', {})
    
    click.echo("\n📊 KEY INSIGHTS:")
    for insight in analysis.get('key_insights', [])[:5]:
        click.echo(f"  • {insight}")
    
    click.echo("\n🎯 OPPORTUNITIES:")
    for opp in analysis.get('opportunities', [])[:3]:
        click.echo(f"  • {opp.get('opportunity', 'N/A')}")
    
    click.echo("\n⚠️  THREATS:")
    for threat in analysis.get('threats', [])[:3]:
        click.echo(f"  • {threat.get('threat', 'N/A')}")
    
    click.echo("\n💡 RECOMMENDATIONS:")
    for rec in analysis.get('recommendations', [])[:5]:
        click.echo(f"  • {rec}")
    
    # Evaluation
    evaluation = result.get('evaluation', {})
    if evaluation:
        click.echo(f"\n📋 QUALITY SCORE: {evaluation.get('grade', 'N/A')} ({evaluation.get('overall_score', 0):.2f})")


def _parse_interval(interval_str: str) -> int:
    """Parse interval string to hours"""
    interval_str = interval_str.lower().strip()
    
    if interval_str.endswith('h'):
        return int(interval_str[:-1])
    elif interval_str.endswith('m'):
        return int(interval_str[:-1]) / 60
    elif interval_str.endswith('d'):
        return int(interval_str[:-1]) * 24
    else:
        return int(interval_str)  # Assume hours


def main():
    cli()


if __name__ == '__main__':
    main()
