# Tutorial 2 Exercise: Connect the Chatbot to MCP

The Tutorial 1 chatbot works and remembers the intake. Now it should check open counselling slots, book one and answer policy questions, all through the clinic's **MCP server**. Right now the server offers nothing, and the client discovers nothing.

In pairs, build the **server** (Activity 1) and the **client** (Activity 2).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate    # Windows: python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Add your API key at the top of `backend/llm.py` (the same key as Tutorial 1):

```python
LLM_PROVIDER = "anthropic"
ANTHROPIC_API_KEY = "sk-ant-..."
```

Run the app and open **http://localhost:8000**. Stop it with **Ctrl + C**.

```bash
python -m uvicorn backend.app:app --reload
```

Click the **Test script** buttons. The intake works, but the MCP panel shows **0 tools discovered**, policy questions get "the counsellor can explain", and booking "isn't available yet".

## Activity 1: The MCP server (8 min) · `backend/clinic_server.py`

1. **`check_availability(day)`:** add `@mcp.tool()` and a docstring. Return the open slots, such as `"09:30, 15:00"`, or `"NO_SLOTS"`.
2. **`book_appointment(day, time)`:** add `@mcp.tool()` and a docstring. Raise `ToolError` if the slot isn't open. Otherwise remove it from `SLOTS`, add it to `BOOKINGS` and return the reference.
3. **`policies()`:** add `@mcp.resource("clinic://policies")` and a docstring.

**Check it:** `pytest tests/test_server.py`. The app's MCP panel still shows 0 tools until Activity 2. If you have Node.js, also try the MCP Inspector: `mcp dev backend/clinic_server.py`.

## Activity 2: The MCP client (12 min) · `backend/mcp_client.py` and `backend/orchestrator.py`

In `mcp_client.py`:

1. **`discover()`:** call `list_tools()` and keep each tool's name, description and input schema.
2. **`read_policies()`:** call `read_resource("clinic://policies")` and keep the text.
3. **`call(name, arguments)`:** call `call_tool(...)` and return `(ok, text)`.

In `orchestrator.py`:

4. **`run_tool()`:** call `check_tool()` first. If it allows the call, run it with `client.call()`. Save the call in `state["last_tool"]`, and save a successful booking in `state["booking"]`.

The app restarts by itself when you save (`--reload`); watch the terminal for errors. **Done when** the MCP panel shows 2 tools and the resource, and the test script ends with a booking reference in the state.

## Check

```bash
pytest
```

You start at 21 passing. After Activity 1, 28 pass. When both activities are done, all 37 pass.

## If something breaks

- **0 tools after Activity 1:** that's expected. The app only shows tools once `discover()` works (Activity 2.1).
- **`bad interpreter`:** delete `.venv` and redo the setup.
- **`No module named mcp`:** activate `.venv`, then run `pip install -r requirements.txt`.
- **Errors in the chat:** read the terminal running uvicorn; the real error is there.

> This is a teaching prototype. Use only made-up messages, never real personal information.
