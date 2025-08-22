# Paper Pulse

A daily research paper digest system that automatically discovers, processes, and delivers AI/ML research summaries to Slack.

## Prerequisites

- Python 3.11+
- UV package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd paper-pulse
```

2. Install dependencies using UV:
```bash
uv sync
```

## Running the Application

### Main Pipeline

Run the complete paper discovery and processing pipeline:

```bash
uv run main.py
```

## Pipeline Overview

The main pipeline (`main.py`) runs a six-node LangGraph workflow:

1. **Paper Discovery**: Fetches papers from HuggingFace API
2. **Map Extraction**: Distributes papers for parallel processing
3. **Extract Single Paper**: PDF content extraction (TODO)
4. **Analyze Single Paper**: LLM-based analysis (TODO)
5. **Collect Results**: Aggregates processed papers
6. **Delivery**: Formats and sends to Slack (TODO)


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.