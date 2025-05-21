from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent_cu_mcp import troubleshoot_ospf_issue  # vezi ca acest fișier e în același director sau instalat ca modul
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogInput(BaseModel):
    log: str
    router_id: str = "unknown"

@app.post("/troubleshoot")
async def troubleshoot(input: LogInput):
    result = troubleshoot_ospf_issue(log_content=input.log, router_id=input.router_id)
    return JSONResponse(content=result)

@app.get("/")
async def health():
    return {"message": "MCP OSPF Troubleshooting API is running!"}
