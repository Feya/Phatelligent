"""
Report Agent - Generates comprehensive reports
Demonstrates: Content generation, formatting, multi-format output
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from google import genai
from google.genai import types

from ..observability.tracing import trace_agent_execution

logger = logging.getLogger(__name__)


class ReportAgent:
    """
    Specialized agent for generating comprehensive competitive landscape reports.
    Creates executive summaries, detailed analyses, and visualizations.
    """
    
    def __init__(self, client: genai.Client, config: Dict[str, Any]):
        self.client = client
        self.config = config
        logger.info("Report Agent initialized")
    
    @trace_agent_execution
    async def generate_report(
        self,
        research_results: List[Dict[str, Any]],
        analysis_result: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive competitive landscape report.
        
        Args:
            research_results: Raw research data
            analysis_result: Analysis insights
            query: Original query
            
        Returns:
            Structured report with multiple sections
        """
        logger.info("Generating competitive landscape report")
        
        try:
            # Create report prompt
            prompt = self._create_report_prompt(
                research_results,
                analysis_result,
                query
            )
            
            # Create agent for report generation
            agent = self.client.agents.create(
                model="gemini-2.0-flash-001",
                instructions="""You are an expert pharmaceutical industry report writer.

Generate a professional, comprehensive competitive landscape report.

Report Structure:
1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - Key findings
   - Critical insights
   - Strategic implications

2. COMPETITIVE OVERVIEW
   - Market landscape
   - Key players
   - Competitive dynamics

3. DETAILED ANALYSIS
   - Pipeline analysis by competitor
   - Therapeutic area deep-dives
   - Clinical trial insights
   - Regulatory updates

4. TRENDS & INSIGHTS
   - Emerging patterns
   - Technology trends
   - Strategic moves

5. OPPORTUNITIES & THREATS
   - Market opportunities
   - Competitive threats
   - Risk factors

6. STRATEGIC RECOMMENDATIONS
   - Actionable insights
   - Monitoring priorities
   - Next steps

Use clear, professional language. Support claims with evidence.
Format for executive audience."""
            )
            
            # Generate report
            response = await agent.run(prompt)
            
            # Structure the report
            report = {
                "title": f"Competitive Landscape Report: {query}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "executive_summary": self._extract_executive_summary(response),
                "competitive_overview": self._extract_section(response, "competitive"),
                "detailed_analysis": analysis_result.get("full_analysis", ""),
                "trends": analysis_result.get("trends", []),
                "opportunities": analysis_result.get("opportunities", []),
                "threats": analysis_result.get("threats", []),
                "recommendations": analysis_result.get("recommendations", []),
                "appendix": {
                    "competitors_analyzed": analysis_result.get("competitors_analyzed", 0),
                    "data_sources": self._collect_sources(research_results),
                    "methodology": "Multi-agent analysis using Google Agent Kit"
                },
                "full_report": str(response),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "query": query,
                    "version": "1.0"
                }
            }
            
            logger.info("Report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_report_prompt(
        self,
        research_results: List[Dict[str, Any]],
        analysis_result: Dict[str, Any],
        query: str
    ) -> str:
        """Create comprehensive report prompt."""
        
        prompt = f"""Generate a professional competitive landscape report.

Query: {query}
Date: {datetime.now().strftime("%B %d, %Y")}

RESEARCH DATA:
Competitors analyzed: {len(research_results)}
"""
        
        # Add research summaries
        for i, result in enumerate(research_results, 1):
            if "error" not in result:
                prompt += f"\n{i}. {result.get('competitor', 'Unknown')}\n"
                prompt += f"   Findings: {str(result.get('findings', {}))[:200]}...\n"
        
        # Add analysis insights
        prompt += f"""

ANALYSIS INSIGHTS:
{analysis_result.get('full_analysis', 'No analysis available')[:1000]}...

Key Insights:
"""
        for insight in analysis_result.get('key_insights', []):
            prompt += f"- {insight}\n"
        
        prompt += f"""

Recommendations:
"""
        for rec in analysis_result.get('recommendations', []):
            prompt += f"- {rec}\n"
        
        prompt += """

Please generate a comprehensive, well-structured report based on this data.
Focus on actionable insights and strategic implications.
"""
        
        return prompt
    
    def _extract_executive_summary(self, response) -> str:
        """Extract executive summary from report."""
        # Parse the executive summary section
        full_text = str(response)
        
        # Simple extraction (in production, use more sophisticated parsing)
        if "EXECUTIVE SUMMARY" in full_text:
            start = full_text.find("EXECUTIVE SUMMARY")
            end = full_text.find("COMPETITIVE OVERVIEW", start)
            if end > start:
                return full_text[start:end].strip()
        
        # Fallback: return first 500 characters
        return full_text[:500] + "..."
    
    def _extract_section(self, response, section_keyword: str) -> str:
        """Extract a specific section from the report."""
        full_text = str(response)
        
        # Simple section extraction
        keyword_upper = section_keyword.upper()
        if keyword_upper in full_text:
            start = full_text.find(keyword_upper)
            # Find next major section
            next_section = start + 100
            return full_text[start:next_section].strip()
        
        return f"Section '{section_keyword}' not found in report."
    
    def _collect_sources(self, research_results: List[Dict[str, Any]]) -> List[str]:
        """Collect all sources used in research."""
        sources = set()
        
        for result in research_results:
            if "sources" in result:
                sources.update(result["sources"])
        
        return list(sources)
    
    async def export_report(
        self,
        report: Dict[str, Any],
        format: str = "markdown"
    ) -> str:
        """
        Export report to specified format.
        
        Args:
            report: Report dictionary
            format: Export format (markdown, html, pdf)
            
        Returns:
            Formatted report string
        """
        
        if format == "markdown":
            return self._export_markdown(report)
        elif format == "html":
            return self._export_html(report)
        elif format == "json":
            import json
            return json.dumps(report, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self, report: Dict[str, Any]) -> str:
        """Export report as Markdown."""
        
        md = f"""# {report['title']}

**Date:** {report['date']}

## Executive Summary

{report['executive_summary']}

## Competitive Overview

{report['competitive_overview']}

## Key Trends

"""
        for trend in report.get('trends', []):
            md += f"- **{trend.get('trend', 'N/A')}** ({trend.get('direction', 'neutral')})\n"
            md += f"  - Confidence: {trend.get('confidence', 0):.0%}\n"
            md += f"  - Evidence: {trend.get('evidence', 'N/A')}\n\n"
        
        md += """
## Opportunities

"""
        for opp in report.get('opportunities', []):
            md += f"- **{opp.get('opportunity', 'N/A')}**\n"
            md += f"  - Rationale: {opp.get('rationale', 'N/A')}\n"
            md += f"  - Priority: {opp.get('priority', 'N/A')}\n\n"
        
        md += """
## Threats

"""
        for threat in report.get('threats', []):
            md += f"- **{threat.get('threat', 'N/A')}**\n"
            md += f"  - Impact: {threat.get('impact', 'N/A')}\n"
            md += f"  - Timeframe: {threat.get('timeframe', 'N/A')}\n\n"
        
        md += """
## Recommendations

"""
        for rec in report.get('recommendations', []):
            md += f"- {rec}\n"
        
        md += f"""

---
*Report generated by Pharma Competitive Landscape Agent*  
*Generated: {report['metadata']['generated_at']}*
"""
        
        return md
    
    def _export_html(self, report: Dict[str, Any]) -> str:
        """Export report as HTML."""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; }}
        .executive-summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{report['title']}</h1>
    <p><strong>Date:</strong> {report['date']}</p>
    
    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <p>{report['executive_summary']}</p>
    </div>
    
    <h2>Competitive Overview</h2>
    <p>{report['competitive_overview']}</p>
    
    <!-- Additional sections would be added here -->
    
    <hr>
    <p><em>Report generated by Pharma Competitive Landscape Agent</em></p>
</body>
</html>"""
        
        return html
