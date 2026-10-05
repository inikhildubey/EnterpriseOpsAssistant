# EnterpriseOpsAssistant 🚀

EnterpriseOpsAssistant is a production-ready enterprise operations assistant built with **LangChain** and **LangGraph**. It combines Retrieval-Augmented Generation (RAG) and agentic tool-calling to automate and streamline operational support tasks, with a primary focus on billing and account management.

## ✨ Key Features

- **Specialized Billing Agent**: An intelligent agent capable of investigating billing discrepancies by coordinating multiple tools to fetch invoices, payment statuses, and subscription details.
- **RAG Pipeline**: A complete RAG (Retrieval-Augmented Generation) implementation that ingests enterprise knowledge bases (Markdown) into a vector store for context-aware responses.
- **Modular Model Factory**: A factory-based architecture for LLMs and Embeddings, allowing seamless switching between providers (e.g., Ollama, OpenAI, Anthropic).
- **Structured Output**: Integration with Pydantic for strictly typed and structured responses, ensuring reliability for downstream applications.
- **Tool-Driven Investigation**: The assistant doesn't guess; it uses a set of dedicated tools to retrieve real-time data from simulated enterprise systems.

## 🛠 Tech Stack

- **Language**: Python 3.11+
- **Orchestration**: [LangChain](https://www.langchain.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Local LLM/Embeddings**: [Ollama](https://ollama.com/)
- **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Package Management**: [uv](https://github.com/astral-sh/uv)

## 📂 Project Structure

```text
chat-bot-assistant/
├── app/
│   ├── agents/       # Agent logic and system prompts (e.g., Billing Agent)
│   ├── config/       # Application settings and environment configuration
│   ├── data/         # Source knowledge base (.md) and local vector store
│   ├── embeddings/   # Embedding model factory
│   ├── models/       # LLM provider factory
│   ├── prompts/      # Dedicated prompt templates for agents
│   ├── rag/           # RAG pipeline: ingestion, loading, retrieval, and chains
│   ├── schema/       # Pydantic schemas for structured outputs
│   ├── tools/        # Tool definitions for agentic function calling
│   └── main.py       # Application entry point and test suite
├── pyproject.toml    # Project dependencies and metadata
└── uv.lock           # Deterministic lockfile for dependencies
```

## 🚀 Getting Started

### Prerequisites

1. Install **Python 3.11+**.
2. Install **uv** for fast package management:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install and run **Ollama** with your preferred model (e.g., `llama3`):
   ```bash
   ollama run llama3
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chat-bot-assistant
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Configuration

Create a `.env` file in the root directory and add the following variables:

```env
MODEL_PROVIDER=ollama
MODEL_NAME=llama3
TEMPERATURE=0.0
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
```

### Running the Assistant

You can run the `main.py` script to execute the test suite and verify the agent's capabilities:

```bash
uv run python app/main.py
```

## 🧠 How it Works

1. **Ingestion**: The RAG pipeline loads Markdown files from `app/data/billing/`, splits them into chunks, and stores them in ChromaDB.
2. **Retrieval**: When a user asks a general question, the `billing_chain` retrieves relevant context from the vector store.
3. **Agentic Reasoning**: For specific customer queries (e.g., "Why is my bill high?"), the **Billing Agent** analyzes the request and decides which tools to call (`get_invoice`, `get_subscription`, etc.).
4. **Synthesis**: The agent combines tool outputs and RAG context to provide a factual, reasoned answer to the user.
