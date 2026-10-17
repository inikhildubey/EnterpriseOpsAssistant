# EnterpriseOpsAssistant 🚀

EnterpriseOpsAssistant is a production-ready enterprise operations assistant built with **LangChain** and **LangGraph**. It combines Retrieval-Augmented Generation (RAG) and agentic tool-calling to automate and streamline operational support tasks, with a focus on billing, account management, and general enterprise support.

## ✨ Key Features

- **Multi-Agent Orchestration**: Powered by **LangGraph**, the system uses a sophisticated routing mechanism to classify user requests and dispatch them to the most appropriate specialized agent (Billing, Accounts, or Support).
- **Specialized Agent Domains**:
    - **Billing Agent**: Investigates discrepancies by coordinating tools to fetch invoices, payment statuses, and subscription details.
    - **Accounts Agent**: Manages and queries account-specific status and subscription information.
    - **Support Agent**: Handles general support requests and issue descriptions.
- **RAG Pipeline**: A complete Retrieval-Augmented Generation implementation that ingests enterprise knowledge bases (Markdown) into a **ChromaDB** vector store for context-aware, policy-based responses.
- **Robust Local Model Support**: Includes custom **Agent Middleware** to repair tool-call "hallucinations" (JSON text in content) common in smaller local models (e.g., Llama 3.2 3B), ensuring stable agentic loops.
- **Modular Provider Factory**: A factory-based architecture for LLMs and Embeddings, allowing seamless switching between providers (e.g., Ollama, OpenAI, Anthropic) without changing business logic.
- **Structured Output**: Deep integration with **Pydantic** for strictly typed responses, ensuring reliability for downstream automated systems.

## 🛠 Tech Stack

- **Language**: Python 3.11+
- **Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Local LLM/Embeddings**: [Ollama](https://ollama.com/)
- **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Package Management**: [uv](https://github.com/astral-sh/uv)

## 📂 Project Structure

```text
chat-bot-assistant/
├── app/
│   ├── agents/       # Agent logic, system prompts, and custom middleware
│   ├── config/       # Application settings and environment configuration
│   ├── data/         # Source knowledge base (.md) and local vector store
│   ├── embeddings/   # Embedding model factory
│   ├── graph/        # LangGraph definitions (Router, State, and specialized graphs)
│   ├── models/       # LLM provider factory
│   ├── prompts/      # Dedicated prompt templates for agents
│   ├── rag/           # RAG pipeline: ingestion, loading, retrieval, and chains
│   ├── schema/       # Pydantic schemas for structured outputs
│   ├── tools/        # Tool definitions for agentic function calling
│   └── main.py       # Application entry point and scenario test suite
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

Create a `.env` file in the root directory:

```env
MODEL_PROVIDER=ollama
MODEL_NAME=llama3
TEMPERATURE=0.0
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
```

### Running the Assistant

Execute the `main.py` script to run the test scenarios and verify the routing and agent capabilities:

```bash
uv run python app/main.py
```

## 🧠 How it Works

The system follows a tiered reasoning flow to resolve user queries:

1. **Routing (LangGraph)**: 
   - The `RouterState` captures the initial question.
   - A `router_node` classifies the request into `billing`, `accounts`, `support`, or `unknown`.
   - The graph conditionally routes the state to the corresponding specialized agent node.

2. **Agentic Execution**:
   - The specialized agent (e.g., **Billing Agent**) uses a loop of tool-calling and reasoning.
   - If the model produces a tool call as plain text (common in small models), the `InlineToolCallRepairMiddleware` intercepts and converts it into a valid tool call.
   - Tools retrieve real-time data from simulated enterprise systems.

3. **Knowledge Integration (RAG)**:
   - For general policy questions, the system utilizes the RAG pipeline.
   - Documents are split by Markdown headers $\to$ embedded $\to$ stored in ChromaDB $\to$ retrieved based on semantic similarity.

4. **Synthesis**:
   - The agent combines tool outputs, retrieved RAG context, and internal reasoning to generate a final, factual response.
