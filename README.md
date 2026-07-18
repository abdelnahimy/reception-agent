# 🏢 Reception Automation Agent

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-v2.0.0-green.svg)](https://adk.dev/)
[![LLM: Gemini Flash](https://img.shields.io/badge/Model-Gemini%20Flash-orange.svg)](https://deepmind.google/technologies/gemini/)

An intelligent, AI-powered reception automation assistant designed to streamline front-desk operations. Built on the **Google Agent Development Kit (ADK)** and powered by **Gemini Flash**, this agent interacts with guests via natural language to manage bookings, check room/table availability, and answer common office frequently asked questions (FAQs).

---

## 🌟 Key Features

*   📅 **Seamless Booking Management** — Create, list, and cancel reservations for rooms or tables in real-time.
*   🔍 **Conflict Resolution** — Automatic overlap detection prevents double-booking of any office resources.
*   💬 **Smart FAQ Auto-Responder** — Instant answers to common inquiries (e.g., Guest Wi-Fi password, opening hours, parking instructions, office address, and contact details).
*   🛡️ **Safety Guardrails** — Enforces business constraints such as preventing past bookings, bookings outside of reception hours (8 AM - 6 PM), and requiring user confirmations before finalized actions.
*   📊 **Interactive Local Playground** — Spin up a local UI to test and interact with the agent in real time.
*   🧪 **Robust Evaluation Suite** — Measure quality using LLM-as-a-judge metrics, regression testing, and automatic prompt optimization.

---

## 🛠️ Technology Stack & Architecture

- **Core Framework**: [Google Agent Development Kit (ADK)](https://adk.dev/)
- **LLM Orchestration**: Gemini Flash (`gemini-flash-latest` via Vertex AI / Google AI Studio)
- **Database**: SQLite (local storage for resources, active bookings, FAQs, and interaction logs)
- **Backend API**: FastAPI (with built-in telemetry, OpenTelemetry instrumentations, and feedback endpoints)
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (extremely fast Rust-based Python dependency management)

```
reception-agent/
├── app/                        # Core Agent Application
│   ├── app_utils/              # Telemetry, typing, and configuration helpers
│   ├── agent.py                # Main agent definition, prompt, and tool registration
│   ├── database.py             # SQLite schema definition, initialization, and seed data
│   ├── fast_api_app.py         # FastAPI service setup for agent playground & API integration
│   └── tools.py                # Core Python functions exposed as tools to the LLM
├── tests/                      # Automated Verification
│   ├── unit/                   # Unit testing for tools and utility functions
│   ├── integration/            # Test runs combining database and agent behaviors
│   └── eval/                   # ADK Evaluation datasets and criteria
├── pyproject.toml              # Dependencies, linter configurations, and build settings
└── agents-cli-manifest.yaml    # ADK/Agents-CLI project configuration
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
1.  **Python** (v3.11, v3.12, or v3.13)
2.  **uv** (Python package manager) — [Install Guide](https://docs.astral.sh/uv/getting-started/installation/)
3.  **Google Cloud SDK** (if deploying to GCP) — [Install Guide](https://cloud.google.com/sdk/docs/install)

### 1. Installation

Install the `google-agents-cli` tool globally:
```bash
uv tool install google-agents-cli
```

Initialize project dependencies:
```bash
agents-cli install
```

### 2. Configure Environment

Ensure you have set up authentication to Gemini. You can use either Google AI Studio or Vertex AI:

**Using Gemini API Key (AI Studio):**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Linux/macOS
export GEMINI_API_KEY="your_api_key_here"
```

**Using Vertex AI (GCP Service Account / Application Default Credentials):**
```bash
gcloud auth application-default login
```

### 3. Launching the Local Playground

Run the agent in a local interactive playground:
```bash
agents-cli playground
```
This boots up a FastAPI backend and redirects you to a beautiful interactive dashboard where you can converse with the reception agent and view real-time logs.

---

## 🧪 Testing & Quality Evaluation

Quality testing is divided into traditional test suites and LLM evaluations.

### Run Automated Tests
```bash
# Run unit and integration tests using pytest
uv run pytest tests/unit tests/integration
```

### Run Agent Evaluations (ADK Eval Loop)
Assess agent performance using synthesized datasets and LLM-as-a-judge scorers:

```bash
# 1. Synthesize multi-turn agent interaction scenarios
agents-cli eval dataset synthesize

# 2. Run agent against dataset and generate interaction traces
agents-cli eval generate

# 3. Grade the traces using configured quality metrics
agents-cli eval grade

# 4. Compare performance or analyze failure clusters
agents-cli eval compare
agents-cli eval analyze
```

---

## 📋 Commands Reference

| Command | Description |
| :--- | :--- |
| `agents-cli install` | Install Python dependencies via `uv`. |
| `agents-cli playground` | Launch local development server & chat playground. |
| `agents-cli lint` | Run quality checkers (`ruff`, `codespell`, etc.). |
| `agents-cli eval` | Access the agent evaluation suite. |
| `agents-cli deploy` | Deploy your agent to Google Cloud Platform. |
| `agents-cli scaffold enhance` | Extend project with CI/CD pipelines and Terraform IAC. |

---

## ☁️ Deployment & Monitoring

Deploy the reception agent to Google Cloud Platform with:
```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

The agent is pre-configured with **OpenTelemetry** for observability, exporting metrics, traces, and logs directly to **Cloud Trace**, **BigQuery**, and **Cloud Logging**.

