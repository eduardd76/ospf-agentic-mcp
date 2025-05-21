import json
from pathlib import Path
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.tools import tool
from langchain.tools.base import ToolException
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

# -----------------------------------------------------------------------------
#  Load persistent FAISS index -------------------------------------------------
# -----------------------------------------------------------------------------
INDEX_PATH = Path("indices/ospf_faiss")
if not INDEX_PATH.exists():
    raise RuntimeError("Vector index not found. Run `python build_kb.py` first.")

vector_store = FAISS.load_local(
    INDEX_PATH.as_posix(),
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)

# -----------------------------------------------------------------------------
#  Tools ----------------------------------------------------------------------
# -----------------------------------------------------------------------------

@tool
def search_ospf_knowledge(query: str) -> str:
    """Semantic search in the OSPF knowledge base and return the top chunks."""
    try:
        docs = vector_store.similarity_search(query, k=3)
        return "\n\n".join(d.page_content for d in docs)
    except Exception as e:
        raise ToolException(str(e))

@tool
def analyze_log_pattern(log: str) -> str:
    """Classify common OSPF log patterns (MTU mismatch, auth failure, etc.)."""
    l = log.lower()
    if "seq number mismatch" in l or "exchange to exstart" in l:
        return "MTU Mismatch"
    if "authentication" in l and "mismatch" in l:
        return "Authentication Mismatch"
    return "Unknown"

@tool
def validate_cisco_commands(commands: List[str]) -> str:
    """Check Cisco CLI commands for obvious mistakes/warnings."""
    good, warn = [], []
    for c in commands:
        c = c.strip()
        if not c:
            continue
        if c.startswith(("interface", "ip ", "show")):
            good.append(c)
        else:
            warn.append(f"Unusual: {c}")
    return "Valid: " + str(len(good)) + "\n" + "\n".join(good + warn)

# -----------------------------------------------------------------------------
#  Agent setup ----------------------------------------------------------------
# -----------------------------------------------------------------------------
TOOLS = [search_ospf_knowledge, analyze_log_pattern, validate_cisco_commands]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

system_prompt = (
    "You are an expert OSPF troubleshooter. "
    "Use the tools when helpful, think step‑by‑step and finally respond with JSON ONLY (no markdown) having keys: "
    "issue_type, diagnosis, solution, validation."
)

agent_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

ospf_agent = create_openai_tools_agent(llm, TOOLS, agent_prompt)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=ospf_agent,
    tools=TOOLS,
    memory=memory,
    verbose=True,
)

# -----------------------------------------------------------------------------
#  Helper to clean JSON --------------------------------------------------------
# -----------------------------------------------------------------------------

def _clean_json(raw):
    if isinstance(raw, dict):
        return raw
    txt = str(raw).strip()
    txt = txt.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(txt)

# -----------------------------------------------------------------------------
#  Public function used by FastAPI -------------------------------------------
# -----------------------------------------------------------------------------

def troubleshoot_ospf_issue(log_content: str, router_id: str = "unknown") -> dict:
    try:
        resp = agent_executor.invoke(
            {
                "input": f"Router ID: {router_id}\nLog:\n{log_content}"
            }
        )
        return _clean_json(resp["output"])
    except Exception as e:
        return {
            "issue_type": "error",
            "diagnosis": {
                "problem_title": "Error",
                "root_cause": str(e),
                "severity": "",
                "potential_impact": "",
            },
            "solution": {},
            "validation": {"is_valid": False, "concerns": []},
        }
