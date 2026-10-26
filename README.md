# 🏦 Production-Grade Banking AI Agent

An enterprise-ready, stateful AI Assistant built with **FastAPI** and the **Google Gemini SDK (`google-genai`)**. Features context-aware conversation memory, hybrid intent parsing (Fast-Path execution), rate-limit resilience, and operational latency/token analytics.

---

## 🌟 Key Features

* **Hybrid Execution Engine:** Fast-Path regex evaluation for deterministic operations (0ms LLM latency) alongside complex LLM tool reasoning.
* **Persistent Session Memory:** Contextual memory storage (`sessions_db.json`) allowing cross-session context retrieval even after server restarts.
* **Context Pruning & Cost Management:** Automatic context truncation to optimize prompt tokens and maintain low latency.
* **Resilience & Fallbacks:** Graceful handling of API rate limits (`429`) and upstream errors (`503`).
* **Real-time Observability:** Tracks token usage (prompt vs candidate tokens) and request execution latency per interaction.

---

## 🛠️ Architecture Overview

1. **Frontend:** Lightweight HTML5/JS dashboard communicating via REST API (`POST /ai-ask`).
2. **Backend:** FastAPI application running Uvicorn.
3. **Model Layer:** Google Gemini 3.8-flash via official `google-genai` SDK.
4. **Data Layer:** JSON persistence engine for accounts and conversation state.

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+
* Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/banking-ai-agent.git](https://github.com/YOUR_USERNAME/banking-ai-agent.git)
   cd banking-ai-agent