# MCP Client/Server Testing

#### Setup
```bash
uv init --bare --python=3.13
uv add mcp[cli] fastmcp
```

Make sure you have a valid `.env` file.

#### Run the server
```bash
uv run src/mcp_credit_server.py
```

```console
2025-11-03 17:06:40,165 - __main__ - INFO - Starting MCP Credit Server...
2025-11-03 17:06:40,165 - __main__ - INFO - Using transport mode: sse
2025-11-03 17:06:40,165 - __main__ - INFO - Log level: INFO
INFO:     Started server process [55132]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### Run the client
```bash
uv run src/mcp_call_tools.py
```

```console
📊 Credit Check Results:
   Credit Score: 500
   Risk Level: high
   Approved Limit: $100,000.05
   Notes:  Spotty financials; consider sector volatility (e.g., hot sectors like tech may need extra scrutiny). Score: 500
```

#### Server output
```console
INFO:     127.0.0.1:61931 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:61933 - "POST /messages/?session_id=28226fb1cd734aca9cb16394023a469a HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61933 - "POST /messages/?session_id=28226fb1cd734aca9cb16394023a469a HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61933 - "POST /messages/?session_id=28226fb1cd734aca9cb16394023a469a HTTP/1.1" 202 Accepted
2025-11-03 17:07:26,825 - mcp.server.lowlevel.server - INFO - Processing request of type CallToolRequest
2025-11-03 17:07:26,825 - __main__ - INFO - credit_check tool is running...
2025-11-03 17:07:26,825 - __main__ - INFO - Requesting token from Experian...
2025-11-03 17:07:28,464 - __main__ - INFO - Successfully obtained token from Experian
2025-11-03 17:07:28,467 - __main__ - INFO - Token obtained successfully.
INFO:     127.0.0.1:61933 - "POST /messages/?session_id=28226fb1cd734aca9cb16394023a469a HTTP/1.1" 202 Accepted
2025-11-03 17:07:29,129 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
```

