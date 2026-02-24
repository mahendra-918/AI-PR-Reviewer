# AI PR Reviewer 🤖

> An open-source, self-hostable AI-powered GitHub Pull Request reviewer.  
> Combines static analysis with LLM-driven code review — **no proprietary models required**.

---

## ✨ What It Does

- 🔍 **Code Quality Analysis** — detects smells, enforces style, suggests naming improvements
- 🔐 **Security Scanning** — OWASP-based checks, hardcoded secrets, injection risks (Bandit + Semgrep)
- ♻️ **Refactor Suggestions** — dead code, duplication, modularization opportunities
- 💬 **Inline PR Comments** — posts structured, actionable review comments directly on GitHub
- 🚦 **CI Status Checks** — blocks merges on Critical severity findings

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Celery |
| Database | PostgreSQL + Redis |
| LLM | Ollama (Llama 3 / Mixtral / Qwen2.5-Coder) |
| Embeddings | BGE-large (BAAI) |
| Vector DB | Weaviate |
| Static Analysis | Bandit, Semgrep, ESLint |
| Infra | Docker + Kubernetes |

---

## 🚀 Quick Start (Local Dev)

### 1. Clone & configure
```bash
git clone https://github.com/your-org/ai-pr-reviewer.git
cd ai-pr-reviewer
cp .env.example .env
# Fill in GITHUB_APP_ID, GITHUB_WEBHOOK_SECRET, etc.
```

### 2. Start all services
```bash
make dev
```

### 3. Verify it's running
```bash
curl http://localhost:8000/api/v1/health
# → {"status": "healthy", ...}
```

### 4. Expose webhook via ngrok (for local GitHub testing)
```bash
ngrok http 8000
# Copy the HTTPS URL → set as your GitHub App webhook URL
```

API docs available at **http://localhost:8000/docs**

---

## 📁 Project Structure

```
ai-pr-reviewer/
├── backend/          # FastAPI core, Celery workers, services
├── llm-engine/       # Ollama/vLLM configs and prompt templates
├── vector-db/        # RAG embeddings and Weaviate schema
├── static-analysis/  # Bandit, Semgrep, ESLint wrappers
├── infra/            # Docker Compose + Kubernetes manifests
└── docs/             # Architecture, self-hosting guide
```

---

## 📋 Available Commands

```bash
make dev          # Start all services
make down         # Stop all services
make logs         # Tail backend + worker logs
make test         # Run tests
make lint         # Ruff + mypy
make format       # Auto-format with ruff
make migrate      # Run DB migrations
make seed-vdb     # Seed vector DB with project guidelines
make clean        # Remove containers and volumes
```

---

## 🗺️ Roadmap

See the [30-day build plan](docs/architecture.md) for the full timeline.

| Week | Focus |
|------|-------|
| Week 1 | Foundation — E2E skeleton (webhook → LLM → PR comment) |
| Week 2 | Core Intelligence — static analysis + risk scoring |
| Week 3 | RAG + quality — context-aware reviews |
| Week 4 | Production hardening — k8s, observability, v1.0 |

---

## 📄 License

MIT
# AI-PR-Reviewer
