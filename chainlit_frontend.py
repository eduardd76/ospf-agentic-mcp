import chainlit as cl
import httpx

API_URL = "http://mcp-api:8000/troubleshoot"  # Docker service name used in docker-compose

@cl.on_message
async def handle_message(message: cl.Message):
    log_text = message.content.strip()

    if not log_text:
        await cl.Message(content="❗ Please enter a valid OSPF log.").send()
        return

    await cl.Message(content="⏳ Sending log to MCP API for analysis...").send()

    # Send the log to the MCP API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json={
                "log": log_text,
                "router_id": "Chainlit-Router"
            })
            response.raise_for_status()
            data = response.json()

            # Build the response message
            diagnosis = data.get("diagnosis", {})
            solution = data.get("solution", {})
            validation = data.get("validation", {})

            msg = f"""✅ **Issue Type**: `{data.get('issue_type', 'Unknown')}`

🧠 **Diagnosis**:
- **Title**: {diagnosis.get('problem_title', 'N/A')}
- **Cause**: {diagnosis.get('root_cause', 'N/A')}
- **Severity**: {diagnosis.get('severity', 'N/A')}
- **Impact**: {diagnosis.get('potential_impact', 'N/A')}

🛠 **Solution Summary**:
{solution.get('solution_summary', 'N/A')}

💻 **CLI Commands**:
```bash
{chr(10).join(solution.get('cli_commands', []))}
```

🔍 **Validation**:
- Valid: {validation.get('is_valid', False)}
- Concerns: {validation.get('concerns', [])}
"""
            await cl.Message(content=msg).send()

        except httpx.HTTPStatusError as e:
            await cl.Message(content=f"❌ API error: {e.response.status_code} - {e.response.text}").send()
        except Exception as e:
            await cl.Message(content=f"❌ Unexpected error: {str(e)}").send()
