# aiscaffold v3

**Production-Ready AI Agent Platform Scaffold -- Secure, Scalable, Language-Agnostic**

One command to set up a new AI agent project with everything built in: API gateway for external agents in any language, multi-agent round table and chat orchestrator, prompt caching, deployment infrastructure (Docker + Kubernetes), vanilla learning system, security hardened at every boundary, and 14 AI subagents for development.

Every project scaffolded by aiscaffold v3 is designed to be:
- **Secure** -- SSRF protection, prompt injection defense, rate limiting, HMAC webhooks, input validation at every boundary
- **Hallucination-resistant** -- evidence requirements in every agent prompt, cross-checking in chat, full deliberation in round table
- **Scalable** -- Docker, docker-compose, Kubernetes with HPA, external agents over HTTP in any language
- **Cost-efficient** -- automatic prompt caching (90% token savings on stable prefixes), token tracking per call
- **Learning** -- feedback tracking, trust scores, preference graduation, permission-based adaptation
- **Human-in-the-loop** -- approval gates, check-in system, escalation from chat to round table

---

## Quick Start

```bash
# Install
pip install copier

# Create a new project
copier copy gh:KangaKode/aiscaffold my-project --trust

# Follow the prompts: name, type, layers, LLM provider, persistence, options
# Then:
cd my-project
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pre-commit install
make test       # Architecture tests pass from day 1
make serve      # Start the API gateway
```

---

## What You Get

Every scaffolded project includes **47+ Python source files** across 8 modules:

### Two Interaction Modes

- **Round Table** -- Full 4-phase multi-agent deliberation (Strategy, Independent Analysis, Challenge, Synthesis + Voting). For complex decisions needing all perspectives.
- **Chat Orchestrator** -- Lightweight real-time chat. A lead agent selectively consults 1-3 specialists, cross-checks for agreement, and escalates to the round table when needed.

### API Gateway (FastAPI)

10 route modules exposing everything over HTTP:

- `POST /api/v1/round-table/tasks` -- Submit task for full multi-agent deliberation
- `POST /api/v1/chat` -- Send message to chat orchestrator
- `POST /api/v1/chat/stream` -- Same, with Server-Sent Events streaming
- `POST /api/v1/agents` -- Register external agent (any language)
- `GET  /api/v1/agents` -- List registered agents with health status
- `POST /api/v1/feedback` -- Record user feedback signal
- `GET  /api/v1/preferences` -- List learned preferences
- `GET  /api/v1/preferences/search?q=` -- Semantic preference search
- `GET  /api/v1/checkins` -- List pending check-ins
- `GET  /health` -- Liveness, readiness, and metrics

### External Agent Support (Any Language)

External agents implement 3 HTTP endpoints in any language:

```
POST /analyze   -- Independent analysis with evidence
POST /challenge -- Challenge other agents' findings
POST /vote      -- Vote on synthesis
```

The `RemoteAgent` adapter wraps these as `AgentProtocol` -- the round table and chat orchestrator see no difference between local Python agents and remote TypeScript/Go/Rust agents.

### LLM Client with Prompt Caching

Provider-agnostic client (Anthropic, OpenAI, Google) with automatic prompt caching:
- `CacheablePrompt(system, context, user_message)` separates stable prefix from dynamic content
- Anthropic: `cache_control` for 90% input token savings
- OpenAI: prefix caching for 50% savings
- Token tracking per call (input, output, cached, estimated USD cost)
- Auto-retry with exponential backoff

### Vanilla Learning System (opt-in)

Teaches your project to learn from user interactions:
- **Feedback Tracker** -- Accept/reject/modify/rate signals per agent
- **Agent Trust** -- EMA-based trust scores, used for routing
- **Check-in Manager** -- Never adapts silently; asks permission first
- **User Profile** -- Aggregates preferences into context bundles for LLM prompts
- **RAG** -- ChromaDB vector search over preferences (in-memory fallback)
- **Graduation** -- Promotes stable patterns to global profile across projects

### Security (Baked In Everywhere)

- SSRF protection on agent registration (blocks private IPs, non-http schemes)
- Prompt injection defense (all external agent responses sanitized)
- Input size limits on every endpoint
- Rate limiting per client IP
- HMAC-SHA256 webhook signature verification
- API key auth with production enforcement
- CORS restricted to configured origins

### Deployment Infrastructure

- **Dockerfile** -- Multi-stage build, non-root user, health check
- **docker-compose.yml** -- App + Postgres, one command to run
- **Kubernetes** -- Deployment, Service, HPA (auto-scale 2-10 pods), ConfigMap

### 14 AI Subagents (`.cursor/agents/`)

| Agent | Role |
|-------|------|
| **solution-architect** | Must be consulted before any new feature is coded |
| **codebase-scout** | Searches existing code before allowing new code to be written |
| **data-flow-guardian** | Validates data paths, source of truth, transaction safety |
| **minimalist** | Prevents over-engineering and AI code bloat |
| **code-reviewer** | Quality, security, maintainability review |
| **red-team** | Adversarial pre-commit security gate (BLOCKS on findings) |
| **security-hardener** | Blue team -- proactive defensive security |
| **prompt-engineer** | 2026 Anthropic Skills patterns for prompt design |
| **ai-engineer** | Multi-agent architecture and orchestration |
| **test-architect** | Test strategy, eval design, coverage analysis |
| **debugger** | Systematic root cause analysis |
| **project-curator** | Directory structure and root cleanliness |
| **sql-pro** | Database optimization (conditional on persistence choice) |
| **ux-researcher** | User workflow optimization (conditional on project type) |

### Architecture Enforcement + Red Team

- `tests/test_architecture.py` -- Enforces dependency direction rules, file size limits
- `scripts/red_team_check.py` -- Pre-commit hook: secrets, SQL injection, dangerous functions

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `project_type` | `web-app` | `web-app`, `cli-tool`, `multi-agent`, `api-service` |
| `llm_provider` | `anthropic` | `anthropic`, `openai`, `google`, `multi` |
| `persistence` | `sqlite` | `sqlite`, `postgres`, `none` |
| `include_evals` | `true` | Eval infrastructure |
| `include_state_management` | `true` | Task tracker + progress notes |
| `include_llm_client` | `true` | LLM client with prompt caching |
| `include_api_gateway` | `true` | FastAPI gateway + external agent support |
| `include_deployment` | `true` | Dockerfile, docker-compose, K8s manifests |
| `include_learning` | `false` | Learning system (feedback, trust, preferences, RAG) |

---

## Makefile

```bash
make help          # Show all commands
make test          # Run all tests
make test-arch     # Architecture enforcement
make serve         # Start API gateway (dev mode with auto-reload)
make serve-prod    # Start API gateway (production, 4 workers)
make docker-build  # Build Docker image
make docker-run    # Run with docker-compose
make k8s-deploy    # Deploy to Kubernetes
make red-team      # Run red team on all source files
make lint          # Run linters
make format        # Format code
make doctor        # Full project health check
make clean         # Remove caches
```

---

## Architecture

```
aiscaffold/
  copier.yml            # Template configuration and questions
  README.md             # This file

  template/             # Copier template (generates project files)
    {{project_slug}}/
      src/{{project_slug}}/
        agents/         # Agent implementations (local + remote adapter + registry)
        api/            # FastAPI gateway (routes, models, middleware)
        harness/        # Session lifecycle (Item/Turn/Thread + Initializer/Worker)
        llm/            # LLM client with prompt caching (Anthropic/OpenAI/Google)
        orchestration/  # Round Table + Chat Orchestrator + Agent Router
        security/       # Prompt guard, validators, SSRF protection
        learning/       # Feedback, trust, preferences, RAG, graduation (opt-in)
      deploy/k8s/       # Kubernetes manifests
      .cursor/agents/   # 14 subagent definitions
      docs/             # Progressive disclosure docs
      tests/            # Architecture enforcement tests
      scripts/          # Red team pre-commit hook
      evals/            # Eval infrastructure

  core/                 # Shared utilities (install via pip)
    src_aiscaffold/     # Python package
      cli.py            # CLI: init, doctor, add, update
      task_tracker.py   # JSON-based task tracking
      progress_notes.py # Session progress logging
      eval_harness.py   # Evaluation infrastructure
```

---

## Based On

Built from insights in:

- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Anthropic: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)
- [subagents.cc](https://subagents.cc/browse) -- Agent catalog

---

## License

MIT
