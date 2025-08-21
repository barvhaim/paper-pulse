## Design

### Core Features

- Automated daily paper discovery from Hugging Face
- Advanced PDF parsing and content extraction using Docling
- Intelligent summarization with key insights extraction
- Direct Slack delivery of research digests

### Core Agents
- Paper Discovery Agent - Fetches papers from Hugging Face and arxiv by user preferences
- Content Extraction Agent - Handles PDF parsing with Docling (pure extraction, no analysis)
- Research Analyzer Agent - Performs LLM-based analysis on extracted content
- Delivery Agent - Formats and sends to Slack

### Separation of Concerns:
#### Content Extraction focuses solely on:
- PDF downloading
- Docling parsing
- Structured text extraction
- Handling figures, tables, equations
- Output: Clean JSON structure

#### Research Analyzer handles all intelligence tasks:
- Identifying research problems
- Extracting key contributions
- Analyzing methodology
- Generating executive summaries
- Finding technical insights
- Identifying applications
- Using LLM for deep understanding

### Daily Service Workflow

Single Daily Execution
- Service runs once daily at scheduled time (e.g., 9:00 AM)
- Batch processes all papers published that day
- Parallel processing for efficiency
- Delivers comprehensive digest to Slack channels