# Healthcare Multi-Agent Copilot

**Genpact Giga Academy Cohort IV - Project #6**

A smart multi-agent system that takes healthcare business questions and turns them into professional deliverables with citations and verification. Built with LangGraph and Claude API.

---

## What This Does

You ask a healthcare question, and the system:

1. Breaks it down into research tasks
2. Finds relevant information from documents
3. Writes a professional summary, email, and action items
4. Verifies everything against the sources
5. Tells you if something isn't backed up by evidence

The whole process takes about a minute and gives you ready-to-send deliverables.

---

## Key Features

**Four AI Agents Working Together:**

- **Planner** - Figures out what research is needed
- **Research** - Finds relevant info from healthcare documents
- **Writer** - Creates executive summaries, emails, and action lists
- **Verifier** - Makes sure nothing is made up

**Two Output Modes:**

- **Executive** - Strategic, high-level for leadership
- **Analyst** - Detailed, technical for data teams

**What You Get:**

- Executive summary (under 150 words)
- Professional email ready to send
- Action items with owners and deadlines
- Full citations showing where info came from
- Clear warnings when info isn't in the documents

---

## How the System Works

User asks a question → Planner breaks it into smaller research questions → Research agent searches documents and summarizes findings → Writer creates deliverables → Verifier checks everything is supported by sources → Done!

The system tracks which documents were used, what pages, and flags anything that can't be verified.

---

## Quick Start

**What You Need:**

- Python 3.9 or higher
- Anthropic API key (for Claude)

**Setup (takes about 5 minutes):**

1. Clone and enter the project folder

```bash
gh repo clone Rinakadishani/multiagent
cd multiagent
```

2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Add your API key

```bash
# Create a .env file and add:
ANTHROPIC_API_KEY=your_key_here
MODEL_NAME=claude-sonnet-4-20250514
```

4. Run the app

```bash
cd app
streamlit run streamlit_app.py
```

That's it! Your browser will open with the interface.

---

## Using the System

**Best queries** (we have infection control documents):

- "What are the best practices for hand hygiene in healthcare settings?"
- "How can hospitals prevent C. difficile infections?"
- "What infection control measures are needed for NICUs?"

**In the web interface:**

1. Type your question
2. Choose Executive or Analyst mode
3. Click Execute
4. Wait about 60-90 seconds
5. Browse results in the tabs
6. Download if needed (JSON, TXT, or CSV)

---

## Project Structure

```
multiagent/
├── app/                  - Streamlit web interface
├── agents/              - The 4 AI agents + workflow
├── retrieval/           - Document loading and vector search
├── data/                - Healthcare PDFs (7 documents)
├── eval/                - Test queries and evaluation scripts
├── chroma_db/           - Vector database
└── README.md            - This file
```

**Main Files:**

- `agents/graph.py` - Connects all agents with LangGraph
- `app/streamlit_app.py` - Web UI
- `retrieval/vector_store.py` - Document search
- `eval/test_queries.json` - 10 test questions

---

## What the Project Requirements Asked For

**System Architecture:** Built all 4 required agents with Plan → Research → Draft → Verify workflow

**Data:** Using 7 public healthcare PDFs about infection control, with proper citations (document name + page + chunk ID)

**Deliverables:** Executive summary, client email, action items with owners and dates, full source list

**Nice-to-haves (picked 2):**

1. Multi-output mode - Executive vs Analyst
2. Observability tracking - Shows latency, tokens, errors for each agent

**Everything works:** Agents route correctly, citations are included, verifier catches unsupported claims, trace logs show everything

---

## Evaluation Results

Tested with 10 healthcare queries. Here's a sample run with 3 queries:

- All 3 completed successfully
- Average time: 73 seconds per query
- Average API cost: $0.04 per query
- Summaries averaged 122 words
- Each generated 5 action items and cited 4 source documents

The verifier correctly identifies when questions don't match our documents and flags unsupported claims.

Full results in `eval/eval_results_*.csv`

---

## Tech Stack

- **LangGraph** - Orchestrates the agents
- **Claude Sonnet 4** - The AI doing the thinking
- **ChromaDB** - Stores document embeddings for search
- **Streamlit** - Makes the web interface
- **PyPDF** - Reads the healthcare PDFs
- **HuggingFace Embeddings** - Free local embeddings (no API needed)

---

## Performance Notes

A typical query uses:

- About 70 seconds total
- Around 12,000 tokens (~$0.04)
- Research agent uses the most time (searching documents)
- Verifier uses the least time

The system is honest - if information isn't in the documents, it says so clearly instead of making things up.

---

## Known Limitations

- Documents are about infection control, so questions about other topics get limited results
- No revision loop yet (verifier doesn't send feedback to writer)
- Can't upload your own documents through the UI (yet)
- Only works with PDFs currently

---

## Future Ideas

- Add ability to upload custom documents
- Implement revision loop so verifier can improve outputs
- Export to Word/PDF
- Add more document types
- Make it faster with parallel processing

---

## About This Project

**Author:** Rina Kadishani  
**Program:** Genpact Giga Academy Cohort IV  
**Submission:** February 16, 2026

Built as Project #6 for the Giga Academy program. The goal was to create a production-ready multi-agent system that generates business deliverables grounded in evidence.

---

## Running It Yourself

**Streamlit UI (recommended):**

```bash
cd app
streamlit run streamlit_app.py
```

**Command line:**

```bash
cd agents
python3 graph.py
```

**Run evaluations:**

```bash
cd eval
python3 run_evaluation.py
```
