# Pharmaceutical Competitive Landscape Agent

A sophisticated multi-agent system built with Google Agent Kit to monitor and analyze competitive landscapes in the pharmaceutical industry.

## 🏆 Competition Requirements Met

This agent demonstrates the following key concepts:

### 1. Multi-agent System ✅
- **Main Orchestrator Agent**: Coordinates the overall workflow
- **Research Agent**: Gathers competitive intelligence using Google Search
- **Analysis Agent**: Analyzes data and identifies trends
- **Report Agent**: Generates comprehensive reports
- **Sequential & Parallel Execution**: Uses both sequential workflows and parallel data gathering

### 2. Tools ✅
- **MCP (Model Context Protocol)**: For structured data exchange
- **Custom Tools**: 
  - Drug pipeline analyzer
  - Clinical trial tracker
  - Competitor profiler
- **Built-in Tools**:
  - Google Search for market intelligence
  - Code Execution for data analysis
- **OpenAPI Tools**: Integration with FDA API and ClinicalTrials.gov

### 3. Long-running Operations ✅
- Pause/resume capability for long-running market analysis
- Background monitoring with state persistence

### 4. Sessions & Memory ✅
- **InMemorySessionService**: Manages session state
- **Memory Bank**: Long-term storage of competitor profiles and historical trends
- **Context Compaction**: Intelligent summarization of large datasets

### 5. Observability ✅
- Comprehensive logging system
- Distributed tracing with OpenTelemetry
- Performance metrics and analytics
- Agent evaluation framework

### 6. A2A Protocol ✅
- Agent-to-Agent communication for distributed analysis
- Inter-agent coordination and data sharing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Orchestrator Agent (Main)                     │
│  - Coordinates workflow                                 │
│  - Manages sessions & memory                            │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Research   │  │  Analysis   │  │   Report    │
│   Agent     │─▶│   Agent     │─▶│   Agent     │
│             │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
       │               │               │
       ▼               ▼               ▼
┌─────────────────────────────────────────────────┐
│              Tools & APIs                       │
│  - Google Search    - FDA API                   │
│  - MCP Tools        - ClinicalTrials.gov        │
│  - Custom Tools     - Code Execution            │
└─────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│         Memory & State Management               │
│  - Session Service  - Memory Bank               │
│  - Context Compaction                           │
└─────────────────────────────────────────────────┘
```

## 📋 Features

- **Competitor Monitoring**: Track pharmaceutical companies and their drug pipelines
- **Clinical Trial Analysis**: Monitor ongoing trials and their status
- **Patent Intelligence**: Track patent filings and expirations
- **Market Intelligence**: Analyze market share and trends
- **Regulatory Updates**: Monitor FDA approvals and regulatory changes
- **Automated Reporting**: Generate comprehensive landscape reports

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Google Cloud Platform account
- API keys for:
  - Google Search API
  - FDA API (optional, public access available)
  - ClinicalTrials.gov API

### Installation

```bash
# Clone the repository
cd /home/yangfan0/feya-grocery/20251201AgentPractice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `config/agent_config.yaml` to customize:
- Competitor list
- Therapeutic areas to monitor
- Update frequency
- Report settings

## 💻 Usage

### Basic Usage

```python
from pharma_agent import PharmaCompetitiveLandscapeAgent

# Initialize agent
agent = PharmaCompetitiveLandscapeAgent(
    competitors=["Pfizer", "Moderna", "J&J"],
    therapeutic_areas=["Oncology", "Vaccines"]
)

# Run analysis
result = await agent.run(
    query="Analyze competitive landscape for COVID-19 vaccines"
)

print(result.report)
```

### Advanced Usage with Sessions

```python
from pharma_agent import PharmaCompetitiveLandscapeAgent
from google.generativeai import agent_executor

# Create session for long-running analysis
async with agent.create_session() as session:
    # Start analysis
    result = await agent.run_with_session(
        query="Monitor Q4 2025 pipeline updates",
        session=session
    )
    
    # Agent can be paused and resumed
    await session.save_checkpoint()
    
    # Resume later
    await session.resume_from_checkpoint()
```

### CLI Usage

```bash
# Run competitive analysis
python -m pharma_agent.cli analyze --competitors "Pfizer,Moderna" --area "Vaccines"

# Generate report
python -m pharma_agent.cli report --output report.pdf

# Start monitoring (long-running)
python -m pharma_agent.cli monitor --interval 24h
```

## 📊 Evaluation

The agent includes an evaluation framework:

```bash
# Run evaluation suite
python -m pharma_agent.evaluation.run_tests

# View metrics
python -m pharma_agent.evaluation.view_metrics
```

## 📁 Project Structure

```
.
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── config/
│   └── agent_config.yaml
├── pharma_agent/
│   ├── __init__.py
│   ├── main_agent.py          # Orchestrator
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── analysis_agent.py
│   │   └── report_agent.py
│   ├── tools/
│   │   ├── mcp_tools.py
│   │   ├── custom_tools.py
│   │   ├── google_search.py
│   │   └── openapi_tools.py
│   ├── memory/
│   │   ├── session_service.py
│   │   ├── memory_bank.py
│   │   └── context_compaction.py
│   ├── observability/
│   │   ├── logging_config.py
│   │   ├── tracing.py
│   │   └── metrics.py
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   └── test_cases.py
│   ├── a2a/
│   │   └── protocol.py
│   └── cli.py
├── tests/
│   └── test_agent.py
└── examples/
    ├── basic_usage.py
    ├── advanced_monitoring.py
    └── custom_tools_example.py
```

## 🔧 Custom Tools

The agent includes custom pharmaceutical tools:

- **DrugPipelineAnalyzer**: Analyzes drug development pipelines
- **ClinicalTrialTracker**: Monitors clinical trial status
- **CompetitorProfiler**: Builds comprehensive competitor profiles
- **PatentMonitor**: Tracks patent filings and expirations
- **RegulatoryTracker**: Monitors FDA and EMA updates

## 📈 Monitoring & Observability

- **Logs**: Structured JSON logs in `logs/` directory
- **Traces**: OpenTelemetry traces exported to configured backend
- **Metrics**: Prometheus-compatible metrics at `/metrics`
- **Dashboard**: Grafana dashboard configuration included

## 🤝 Contributing

This is a competition submission. For questions or suggestions, please contact the author.

## 📄 License

MIT License

## 🙏 Acknowledgments

- Google Agent Kit team
- Competition organizers
- Pharmaceutical data providers

## 📞 Contact

For questions about this submission, please reach out through the competition platform.
