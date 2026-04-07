---
title: Contract Clause Analyzer OpenEnv
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---
# Contract Clause Analyzer — OpenEnv Environment

A real-world **legal contract clause analysis** environment built on the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework. AI agents evaluate contract clauses for risk, compliance, and completeness.

## 🎯 Tasks

| Task | Difficulty | Description | Max Steps |
|------|-----------|-------------|-----------|
| `clause-classify` | Easy | Classify a clause into one of 10 legal categories | 1 |
| `risk-assess` | Medium | Assess risk levels and identify issues across 3-4 clauses | 4 |
| `clause-rewrite` | Hard | Rewrite problematic clauses with justification | 3 |

## 🏗️ Architecture

```
├── models.py                   ← Pydantic: Action, Observation, State
├── client.py                   ← EnvClient for remote consumers
├── server/
│   ├── environment.py          ← Core environment (reset/step/state)
│   ├── app.py                  ← FastAPI server
│   ├── tasks/                  ← Task definitions (easy/medium/hard)
│   ├── graders/                ← Deterministic graders per task
│   └── data/contracts.py       ← Embedded clause dataset
├── security/                   ← Rate limiting, CSP, bot detection
├── inference.py                ← Inference script (Gemini 3 Pro)
├── openenv.yaml                ← OpenEnv manifest
├── pyproject.toml              ← Project metadata & entry point
├── uv.lock                     ← Locked dependencies
├── Dockerfile                  ← Container definition
└── requirements.txt            ← Dependencies
```

## 🚀 Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set environment variables
```bash
export API_BASE_URL="your-active-endpoint"
export MODEL_NAME="your-active-model"
export HF_TOKEN="your-huggingface-api-key"
```

### Run inference
```bash
python inference.py
```

### Run server locally
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

### Docker
```bash
docker build -t contract-env .
docker run -p 7860:7860 -e HF_TOKEN=xxx contract-env
```

## 📊 Grading

All graders are **deterministic** and return scores in `[0.0, 1.0]`:

- **Easy**: Exact match (1.0) or related type (0.3) for classification
- **Medium**: Weighted partial-credit across risk level accuracy (0.4) and issue identification (0.6), with anti-loop penalty
- **Hard**: Multi-signal scoring — issue identification (0.25), rewrite quality (0.50), justification (0.25)

## 🔒 Security

- Rate limiting via SlowAPI
- CSP / HSTS / security headers
- Prompt injection detection
- Honeypot bot detection
- Non-root container execution

## 📝 License

MIT
