# Agent Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    USER / CLI INTERFACE                                  │
│  • Command-line interface                                                │
│  • Python API                                                            │
│  • Query input                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              MAIN ORCHESTRATOR AGENT (main_agent.py)                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Coordinates workflow                                          │   │
│  │  • Manages sessions & memory                                     │   │
│  │  • Handles pause/resume                                          │   │
│  │  • Orchestrates sub-agents                                       │   │
│  │  • Collects metrics                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────┬───────────────────────────┬───────────────────┬─────────────┘
            │                           │                   │
    ┌───────▼────────┐         ┌───────▼────────┐   ┌──────▼───────┐
    │ RESEARCH AGENT │         │ ANALYSIS AGENT │   │ REPORT AGENT │
    │ (Parallel)     │         │  (Sequential)  │   │ (Sequential) │
    └───────┬────────┘         └───────┬────────┘   └──────┬───────┘
            │                           │                   │
            │                           │                   │
    ┌───────▼──────────────────────────▼───────────────────▼────────┐
    │                    TOOLS & INTEGRATIONS                        │
    │                                                                 │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
    │  │ Google Search│  │  FDA API     │  │ ClinicalTrials.gov │  │
    │  │ (Built-in)   │  │  (OpenAPI)   │  │     (OpenAPI)      │  │
    │  └──────────────┘  └──────────────┘  └────────────────────┘  │
    │                                                                 │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
    │  │ Code Exec    │  │ Drug Pipeline│  │  Competitor        │  │
    │  │ (Built-in)   │  │ Analyzer     │  │  Profiler          │  │
    │  └──────────────┘  └──────────────┘  └────────────────────┘  │
    │                         (Custom Tools)                          │
    └────────────────────────────┬────────────────────────────────────┘
                                 │
         ┌───────────────────────┼────────────────────────┐
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐  ┌────────────────────┐  ┌─────────────────────┐
│  SESSION        │  │  MEMORY BANK       │  │  CONTEXT            │
│  SERVICE        │  │  (Long-term)       │  │  COMPACTION         │
│                 │  │                    │  │                     │
│ • InMemory      │  │ • SQLite Storage   │  │ • Token optimization│
│ • State mgmt    │  │ • Competitor       │  │ • Summarization     │
│ • Checkpoints   │  │   profiles         │  │ • Efficient context │
└─────────────────┘  │ • Analysis history │  └─────────────────────┘
                     │ • Retrieval        │
                     └────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────────┐
│   LOGGING    │      │   TRACING    │      │    METRICS       │
│              │      │              │      │                  │
│ • Structured │      │ • OpenTelem  │      │ • Prometheus     │
│ • JSON logs  │      │ • Distributed│      │ • Counters       │
│ • Multi-level│      │ • Performance│      │ • Histograms     │
└──────────────┘      └──────────────┘      └──────────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │   AGENT EVALUATOR      │
                    │                        │
                    │ • Accuracy scoring     │
                    │ • Completeness check   │
                    │ • Timeliness eval      │
                    │ • Relevance assessment │
                    │ • A-F grading          │
                    └────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │           A2A PROTOCOL                     │
        │  • Peer discovery                          │
        │  • Inter-agent messaging                   │
        │  • Collaborative analysis                  │
        │  • Insight sharing                         │
        └────────────────────────────────────────────┘
```

## Data Flow Diagram

```
USER QUERY
    │
    ▼
[Orchestrator] ─────────────────┐
    │                           │
    │ 1. Load Session           │ 2. Retrieve Memories
    │    & Context              │    from Memory Bank
    ▼                           ▼
[Session Service] ◄─────► [Memory Bank]
    │                           │
    │                           │
    ▼                           ▼
[Research Phase - PARALLEL]
    │
    ├─► [Research Agent 1] ──► Google Search ──┐
    ├─► [Research Agent 2] ──► FDA API ────────┤
    └─► [Research Agent 3] ──► Clinical Trials ┤
                                                │
    ┌───────────────────────────────────────────┘
    │
    ▼
[Aggregate Research Results]
    │
    ▼
[Analysis Phase - SEQUENTIAL]
    │
    └─► [Analysis Agent] ──► Code Execution Tool
                │
                ▼
         [Generate Insights]
                │
                ▼
[Report Phase - SEQUENTIAL]
    │
    └─► [Report Agent] ──► Format & Export
                │
                ▼
         [Comprehensive Report]
                │
                ├─► Store in Memory Bank
                ├─► Update Session
                ├─► Record Metrics
                └─► Evaluate Quality
                        │
                        ▼
                [Return to User]
```

## Component Interaction Flow

```
┌──────────────────────────────────────────────────────────────┐
│ EXECUTION LIFECYCLE                                          │
│                                                              │
│ 1. INITIALIZATION                                            │
│    ├─ Load configuration                                     │
│    ├─ Initialize sub-agents                                  │
│    ├─ Setup tools                                            │
│    └─ Configure observability                                │
│                                                              │
│ 2. SESSION SETUP                                             │
│    ├─ Get or create session                                  │
│    └─ Load historical context                                │
│                                                              │
│ 3. RESEARCH PHASE (Can be parallel)                          │
│    ├─ FOR EACH competitor:                                   │
│    │   ├─ Search Google                                      │
│    │   ├─ Query FDA API                                      │
│    │   ├─ Check Clinical Trials                              │
│    │   └─ Aggregate findings                                 │
│    └─ [CHECKPOINT: Can pause here]                           │
│                                                              │
│ 4. ANALYSIS PHASE (Sequential)                               │
│    ├─ Receive research results                               │
│    ├─ Execute data analysis (code execution)                 │
│    ├─ Identify trends                                        │
│    ├─ Generate insights                                      │
│    └─ [CHECKPOINT: Can pause here]                           │
│                                                              │
│ 5. REPORT PHASE (Sequential)                                 │
│    ├─ Generate executive summary                             │
│    ├─ Create detailed sections                               │
│    ├─ Format output                                          │
│    └─ Export (Markdown/HTML/JSON)                            │
│                                                              │
│ 6. FINALIZATION                                              │
│    ├─ Store results in Memory Bank                           │
│    ├─ Update session state                                   │
│    ├─ Record metrics                                         │
│    ├─ Evaluate quality                                       │
│    └─ Return results                                         │
│                                                              │
│ 7. MONITORING MODE (Optional)                                │
│    └─ LOOP every N hours:                                    │
│        ├─ Run analysis                                       │
│        ├─ Compare with previous                              │
│        └─ Alert on changes                                   │
└──────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│ FRONTEND / INTERFACE                            │
│ • Python CLI (Click)                            │
│ • Python API                                    │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│ AGENT FRAMEWORK                                 │
│ • Google Agent Kit                              │
│ • Google Gemini 2.0 Flash                       │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│ TOOLS & INTEGRATIONS                            │
│ • Google Search API                             │
│ • FDA OpenAPI                                   │
│ • ClinicalTrials.gov API                        │
│ • Custom Python Tools                           │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│ STORAGE & MEMORY                                │
│ • SQLite (Memory Bank)                          │
│ • In-Memory (Sessions)                          │
│ • Redis (Optional)                              │
└─────────────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│ OBSERVABILITY                                   │
│ • Python logging (JSON)                         │
│ • OpenTelemetry (Tracing)                       │
│ • Prometheus (Metrics)                          │
└─────────────────────────────────────────────────┘
```
