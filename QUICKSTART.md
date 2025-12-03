# Quick Start Guide

Welcome to the Pharmaceutical Competitive Landscape Agent! This guide will get you up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- Google Cloud account (for Google Agent Kit)
- Basic knowledge of pharmaceutical industry (helpful but not required)

## Installation (5 minutes)

### Step 1: Clone or navigate to the project
```bash
cd /home/yangfan0/feya-grocery/20251201AgentPractice
```

### Step 2: Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for enhanced features)
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

**How to get Google API Key:**
1. Go to https://aistudio.google.com/
2. Click "Get API Key"
3. Create a new project or select existing
4. Copy the API key to your `.env` file

## Quick Test (2 minutes)

### Test 1: Basic Analysis
```bash
python examples/basic_usage.py
```

This will:
- Initialize the agent
- Analyze 3 pharmaceutical companies
- Generate insights and recommendations
- Create a report

### Test 2: CLI Interface
```bash
python -m pharma_agent.cli analyze \
  --competitors "Pfizer,Moderna" \
  --area "Vaccines" \
  --query "Recent developments in mRNA technology"
```

## Common Use Cases

### 1. Competitive Analysis
```python
from pharma_agent import PharmaCompetitiveLandscapeAgent
import asyncio

async def analyze():
    agent = PharmaCompetitiveLandscapeAgent(
        competitors=["Pfizer", "Moderna", "BioNTech"],
        therapeutic_areas=["Vaccines"]
    )
    
    result = await agent.run(
        query="Compare COVID-19 vaccine portfolios"
    )
    
    print(f"Status: {result['status']}")
    print(f"Key Insights: {result['analysis']['key_insights']}")
    
    await agent.close()

asyncio.run(analyze())
```

### 2. Continuous Monitoring
```bash
# Monitor every 24 hours
python -m pharma_agent.cli monitor \
  --interval 24h \
  --competitors "Pfizer,Moderna,J&J,AstraZeneca" \
  --areas "Vaccines,Oncology"
```

### 3. Custom Analysis with Tools
```python
from pharma_agent.tools.custom_tools import DrugPipelineAnalyzer

analyzer = DrugPipelineAnalyzer()

pipeline = [
    {"name": "Drug A", "stage": "Phase 3", "therapeutic_area": "Oncology"},
    {"name": "Drug B", "stage": "Phase 2", "therapeutic_area": "Vaccines"}
]

analysis = analyzer.analyze_pipeline(pipeline)
print(f"Pipeline Strength: {analysis['risk_assessment']['pipeline_strength']}")
```

## Understanding the Output

When you run an analysis, you'll get:

```json
{
  "status": "completed",
  "query": "Your query",
  "competitors_analyzed": 3,
  "execution_time": 15.2,
  "analysis": {
    "key_insights": ["Insight 1", "Insight 2", ...],
    "competitive_positioning": {...},
    "trends": [...],
    "opportunities": [...],
    "threats": [...],
    "recommendations": [...]
  },
  "report": {
    "executive_summary": "...",
    "full_report": "..."
  },
  "evaluation": {
    "grade": "A",
    "overall_score": 0.85,
    "scores": {
      "accuracy": 0.9,
      "completeness": 0.85,
      "timeliness": 0.8,
      "relevance": 0.85
    }
  }
}
```

## Configuration

Customize the agent by editing `config/agent_config.yaml`:

```yaml
competitors:
  - "Pfizer"
  - "Moderna"
  # Add more...

therapeutic_areas:
  - "Oncology"
  - "Vaccines"
  # Add more...

monitoring:
  update_interval: "24h"
  
tools:
  google_search:
    enabled: true
    max_results: 10
```

## Troubleshooting

### Issue: "Google API key not found"
**Solution:** Make sure you've set `GOOGLE_API_KEY` in your `.env` file

### Issue: "Module not found" errors
**Solution:** Install missing dependencies:
```bash
pip install -r requirements.txt
```

### Issue: OpenTelemetry warnings
**Solution:** These are optional. Install for full observability:
```bash
pip install opentelemetry-api opentelemetry-sdk
```

### Issue: Prometheus warnings
**Solution:** Optional feature. Install with:
```bash
pip install prometheus-client
```

## Next Steps

1. **Explore Examples**: Check `examples/` directory for more use cases
2. **Read Documentation**: See `README.md` for comprehensive guide
3. **Competition Details**: Read `SUBMISSION.md` for technical details
4. **Customize**: Modify `config/agent_config.yaml` for your needs
5. **Test**: Run `pytest tests/test_agent.py` to verify installation

## Key Features Demonstrated

✅ **Multi-agent System**: Orchestrator + Research + Analysis + Report agents  
✅ **Multiple Tools**: Google Search, FDA API, Clinical Trials, Custom tools  
✅ **Long-running Ops**: Pause/resume, background monitoring  
✅ **Memory**: Sessions, Memory Bank, Context compaction  
✅ **Observability**: Logging, Tracing, Metrics  
✅ **Evaluation**: Automated quality scoring  
✅ **A2A Protocol**: Inter-agent communication  

## CLI Commands Reference

```bash
# Analysis
python -m pharma_agent.cli analyze \
  --competitors "Company1,Company2" \
  --area "TherapeuticArea" \
  --query "Your question"

# Monitoring
python -m pharma_agent.cli monitor \
  --interval 24h \
  --competitors "Company1,Company2"

# Resume paused analysis
python -m pharma_agent.cli resume --session SESSION_ID

# View metrics
python -m pharma_agent.cli metrics

# Generate report
python -m pharma_agent.cli report \
  --output report.md \
  --format markdown
```

## Support

For questions or issues:
1. Check `README.md` for detailed documentation
2. Review `examples/` for code samples
3. Read `SUBMISSION.md` for technical architecture

## Competition Submission

This project fulfills all requirements for the "Create Your Own Agent" competition:
- ✅ 7/7 required features implemented
- ✅ Production-ready code
- ✅ Comprehensive documentation
- ✅ Real-world pharmaceutical use case

---

**Ready to analyze the pharmaceutical competitive landscape! 🔬**
