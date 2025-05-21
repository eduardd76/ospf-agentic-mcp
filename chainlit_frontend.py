import chainlit as cl
import httpx
import json

API_URL = "http://localhost:8000/troubleshoot"  # update if different port/host

# ------------------------------------------------------------------
# Utility helpers ---------------------------------------------------
# ------------------------------------------------------------------

def ensure_dict(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    try:
        return json.loads(obj)
    except Exception:
        return {}

def join_lines(value):
    if not value:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(str(v) for v in value)
    return str(value)

# ------------------------------------------------------------------
# Chainlit handler --------------------------------------------------
# ------------------------------------------------------------------
@cl.on_message
async def handle_msg(message: cl.Message):
    log_text = message.content.strip()
    if not log_text:
        await cl.Message(content="❗ Please paste an OSPF log or question.").send()
        return

    await cl.Message(content="⏳ Asking MCP API…").send()

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            res = await client.post(API_URL, json={"log": log_text, "router_id": "UI"})
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            await cl.Message(content=f"❌ API returned invalid JSON: {res.text}").send()
            return

    issue   = data.get("issue_type", "unknown")
    root = data.get("diagnosis", "unknown")
    summary = data.get("solution", "unknown")
    cmds = join_lines(data.get("cli_commands", []))

    md = (
        f"### ✅ Issue: `{issue}`\n\n"
        f"**Root Cause:** {root}\n\n"
        f"**Solution:** {summary}\n\n"
        + (f"```bash\n{cmds}\n```" if cmds else "")
    )

    await cl.Message(content=md).send()
