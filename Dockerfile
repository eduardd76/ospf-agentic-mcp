FROM python:3.11-slim

WORKDIR /app

# Install system deps and pip dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY . .

# No virtualenv needed in container!
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000 8001

CMD ["bash", "-c", "python build_kb.py && uvicorn mcp_ospf_api:app --host 0.0.0.0 --port 8000 & chainlit run chainlit_frontend.py --port 8001 --host 0.0.0.0"]
