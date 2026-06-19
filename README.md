<p align="center">
  <img src="https://img.shields.io/badge/🛡️_AIS--Sentinel-AI_Safety_for_the_Global_South-blueviolet?style=for-the-badge&labelColor=1a1a2e" alt="AIS-Sentinel Banner"/>
</p>

<h1 align="center">
  🌏 AIS-Sentinel
</h1>

<p align="center">
  <strong>Asia's First Multilingual AI Safety Monitoring & Control Platform</strong>
</p>

<p align="center">
  <em>Real-time biosecurity threat intelligence · Multilingual LLM safety benchmarks · Autonomous agent control</em>
</p>

<p align="center">
  <a href="#-quickstart"><img src="https://img.shields.io/badge/Get_Started-→-00d2ff?style=for-the-badge" alt="Get Started"/></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Architecture-→-7f5af0?style=for-the-badge" alt="Architecture"/></a>
  <a href="#-modules"><img src="https://img.shields.io/badge/Modules-→-2cb67d?style=for-the-badge" alt="Modules"/></a>
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/Gemini-Flash_API-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini Flash"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License"/>
</p>

---

## 🔥 The Problem

> **AI safety research is overwhelmingly English-centric.** Billions of people in South & Southeast Asia are exposed to AI risks — biosecurity threats, jailbroken models, uncontrolled autonomous agents — with **zero safety monitoring in their languages.**

AIS-Sentinel changes that. It's a **full-stack AI safety platform** purpose-built for the Global South, covering **6 languages** across Asia's most underserved regions.

---

## 🧬 What It Does

| Capability | Description |
|:---|:---|
| 🔍 **IntelStream** | Scrapes RSS feeds & news sources across Asia for biosecurity and AI safety threats in real-time |
| 🧪 **SafetyBench** | Runs multilingual safety benchmarks against LLMs to test for jailbreaks, harmful outputs & bias |
| 🤖 **AgentGuard** | Monitors autonomous AI agents with a suspicion-scoring system to detect & halt dangerous behavior |
| 📜 **PolicyBridge** | Translates AI safety findings into actionable policy recommendations for regulators |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     🌐 Streamlit Frontend                   │
│              Dashboard · Charts · Policy Reports            │
├─────────────────────────────────────────────────────────────┤
│                      ⚡ FastAPI Backend                     │
├──────────┬──────────┬──────────────┬────────────────────────┤
│ 🔍       │ 🧪       │ 🤖           │ 📜                    │
│ Intel    │ Safety   │ Agent        │ Policy                 │
│ Stream   │ Bench    │ Guard        │ Bridge                 │
├──────────┴──────────┴──────────────┴────────────────────────┤
│                     🧠 Core Engine                          │
│     LLM Client · Smart Translator · SQLite Database         │
├─────────────────────────────────────────────────────────────┤
│              🔮 Gemini Flash API · vLLM · Plotly            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Languages Supported

| Language | Code | Region |
|:---|:---:|:---|
| 🇻🇳 Vietnamese | `vi` | Vietnam |
| 🇹🇭 Thai | `th` | Thailand |
| 🇮🇳 Hindi | `hi` | India |
| 🇵🇭 Filipino | `tl` | Philippines |
| 🇮🇩 Indonesian | `id` | Indonesia |
| 🇬🇧 English | `en` | Pass-through |

---

## 📂 Project Structure

```
AIS-Sentinel/
├── core/                          # 🧠 Core infrastructure
│   ├── __init__.py
│   ├── database.py                # SQLite schema + CRUD helpers
│   ├── llm_client.py              # Gemini Flash API wrapper with retry logic
│   ├── translator.py              # Smart multilingual translator + keyword extractor
│   └── test.py                    # Integration tests
│
├── modules/
│   ├── intelstream/               # 🔍 Threat intelligence pipeline
│   │   └── scraper.py             # RSS scraper + keyword filter
│   ├── safetybench/               # 🧪 LLM safety benchmarking (coming soon)
│   ├── agentguard/                # 🤖 Autonomous agent monitoring (coming soon)
│   └── policybridge/              # 📜 Policy report generator (coming soon)
│
├── config/                        # ⚙️ Configuration files
│   ├── sources.json               # RSS feed sources
│   └── rubrics.json               # Biosecurity keyword rubrics
│
├── .env                           # 🔐 Environment variables (GEMINI_API_KEY)
├── .gitignore
├── requirements.txt
└── README.md                      # 📖 You are here
```

---

## 🚀 Quickstart

### Prerequisites

- Python 3.11+
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### Installation

```bash
# Clone the repo
git clone https://github.com/DeveloperKush/AIS-Sentinel-Asia-AI-Safety-Monitoring-Control-Platform.git
cd AIS-Sentinel-Asia-AI-Safety-Monitoring-Control-Platform

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY="your-gemini-api-key-here"
```

### Run Tests

```bash
# Test the LLM client + translator pipeline
python -m core.test

# Test the scraper module
python -c "from modules.intelstream.scraper import RSSScraper, KeywordFilter; kf = KeywordFilter(); print('Filter test:', kf.filter_article({'title': 'New CRISPR tool released', 'summary': 'AI helps gene editing'}))"
```

**Expected output:**
```
Translation: Hello world
Structured: {'threat_detected': True}
```

---

## 🧠 Core Modules — Deep Dive

### 🗄️ `core/database.py` — SQLite Database Layer

Three normalized tables powering the entire platform:

| Table | Purpose |
|:---|:---|
| `articles` | Stores scraped articles with translations, threat scores & risk categories |
| `benchmark_results` | Logs LLM safety test results across languages and models |
| `agent_logs` | Tracks autonomous agent actions with suspicion scores |

- Uses **context managers** for safe connection handling
- Returns **inserted row IDs** for chaining operations
- Supports **filtered queries** (threat-only, model-specific, detected-only)

---

### 🔮 `core/llm_client.py` — Gemini Flash API Wrapper

A battle-hardened LLM client with production-grade reliability:

```python
from core.llm_client import GeminiClient

client = GeminiClient()  # defaults to gemini-2.5-flash

# Raw text generation
response = client.generate("Explain biosecurity risks of gene synthesis")

# Structured JSON output (schema-enforced)
result = client.generate_structured(
    "Is this a threat: 'Open-source pathogen DNA synthesizer released'",
    schema={"type": "object", "properties": {"threat_detected": {"type": "boolean"}}}
)
# → {"threat_detected": true}

# Translation
translated = client.translate("Xin chào thế giới", "vi", "en")
# → "Hello world"
```

**Features:**
- 🔄 **3 retries** with exponential backoff (1s → 2s → 4s)
- 🎯 **Structured output** via JSON schema enforcement
- 🌡️ **Configurable temperature** (default: 0.3 for deterministic outputs)
- 🧮 **Token counting** for cost tracking

---

### 🌍 `core/translator.py` — Smart Translation Pipeline

Not a dumb translate-everything system. **It's smart:**

1. **Extracts 3–5 key sentences** containing safety-relevant keywords *before* translating
2. **Caches translations** in SQLite — never pays for the same translation twice
3. **Preserves technical terms** (CRISPR, gene synthesis, AI model names) in English
4. **Auto-detects language** if not specified

```python
from core.translator import SmartTranslator

t = SmartTranslator()
result = t.translate_article(
    "Tin tức về CRISPR",
    "Công nghệ CRISPR mới được sử dụng trong nghiên cứu gene.",
    "vi"
)
# → {"title_en": "News about CRISPR", "text_en": "...", "key_sentences_en": [...]}
```

---

### 🔍 `modules/intelstream/scraper.py` — Threat Intelligence Scraper

Scans the web for biosecurity threats across Asia:

- **RSS feeds** via `feedparser` with request timeout protection
- **HTML article extraction** via `newspaper3k` for full-text parsing
- **Keyword filtering** with 13 built-in biosecurity terms:

```
CRISPR · synthetic biology · gene synthesis · pathogen · biosecurity
AI model · bioinformatics · genome editing · viral vector
laboratory safety · dual-use · biological weapon · gain-of-function
```

- **Rate limiting** (1s delay between requests) to avoid IP bans
- **Sentence-level extraction** — pinpoints exactly which sentences triggered the filter

---

## 🗺️ Roadmap

- [x] **Core Infrastructure** — Database, LLM Client, Translator
- [x] **IntelStream** — RSS Scraper + Keyword Filter
- [ ] **SafetyBench** — Multilingual LLM safety benchmarks
- [ ] **AgentGuard** — Autonomous agent monitoring & kill-switch
- [ ] **PolicyBridge** — Policy report generation
- [ ] **Frontend** — Streamlit dashboard with Plotly visualizations
- [ ] **API** — FastAPI REST endpoints
- [ ] **Deployment** — Docker + CI/CD

---

## 🏆 Competition

**Global South AIS Challenge 2026 — Track 3: Technical Safety**

> Building the AI safety infrastructure that the Global South deserves.

---

## 🤝 Team

Built with ❤️ and ☕ during the Global Hackathon 2026.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>🛡️ Making AI safer for 4 billion people who don't speak English.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Built_for-The_Global_South-ff6b6b?style=for-the-badge" alt="Built for the Global South"/>
</p>
