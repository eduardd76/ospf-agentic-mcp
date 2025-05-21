# OSPF Agentic MCP – Virtual Edy 🧠🛠️

> AI-Powered Troubleshooting Agent for OSPF logs – Built by Eduard Dulharu

[![Built with LangChain](https://img.shields.io/badge/Built%20with-LangChain-blue)](https://www.langchain.com/)
[![Powered by OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-brightgreen)](https://platform.openai.com/)
[![Chainlit UI](https://img.shields.io/badge/Frontend-Chainlit-orange)](https://www.chainlit.io/)

---

## 🚀 What it does

- Parses OSPF syslogs (ex: `%OSPF-5-ADJCHG: ...`)
- Detects issues (e.g., MTU mismatch, authentication errors)
- Uses LangChain Tools:
  - 🔍 `analyze_log_pattern`
  - 📚 `search_ospf_knowledge` (FAISS + RAG)
  - 🛠️ `suggest_fix`
  - 🧪 `validate_cisco_commands`
- Answers in structured JSON: `issue_type`, `diagnosis`, `solution`, `validation`
- REST API + Chat UI

---

## 🧠 How it works

*🟡 Demo GIF coming soon...*

---

## 💻 Local Run (Docker)

```bash
git clone https://github.com/eduardd76/ospf-agentic-mcp.git
cd ospf-agentic-mcp
docker-compose up --build
