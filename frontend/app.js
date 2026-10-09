// Chat frontend: sends messages to the backend and shows the reply,
// the router's decision, the MCP tools and the conversation state after every turn.

const TEST_SCRIPT = [
  "I've been stressed about exams for about 3 weeks",
  "Maybe a 6. No counselling before.",
  "What's your cancellation policy?",
  "Yes please. What's free on Tuesday?",
  "15:00 works, please book it",
];

const $ = (id) => document.getElementById(id);
let sessionId = crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2);
let lastState = {};

function addMessage(who, text, kind = who) {
  const div = document.createElement("div");
  div.className = `msg ${kind}`;
  const label = document.createElement("span");
  label.className = "who";
  label.textContent = who === "user" ? "Student" : "Bot";
  div.append(label, document.createTextNode(text));
  const typing = $("typing");
  if (typing) $("messages").insertBefore(div, typing); else $("messages").append(div);
  $("messages").scrollTop = $("messages").scrollHeight;
}

function showAction(action, decidedBy) {
  const el = $("action");
  el.className = "action " + (action || "none");
  el.textContent = action || "No message yet";
  $("decided").textContent = decidedBy === "llm" ? "Decided by the LLM, checked by code." : "";
}

function showState(state) {
  const table = $("state");
  table.innerHTML = "";
  for (const [key, value] of Object.entries(state)) {
    const tr = document.createElement("tr");
    if (JSON.stringify(lastState[key]) !== JSON.stringify(value) && key in lastState) {
      tr.className = "changed";
    }
    const k = document.createElement("td");
    k.textContent = key;
    const v = document.createElement("td");
    if (value === null || value === undefined) {
      v.textContent = "empty";
      v.className = "empty";
    } else {
      v.textContent = typeof value === "string" ? value : JSON.stringify(value);
    }
    tr.append(k, v);
    table.append(tr);
  }
  lastState = structuredClone(state);
}

function showMcp(mcp) {
  if (!mcp) return;
  const n = mcp.tools.length;
  $("mcp-status").textContent = !mcp.connected ? "Not connected: check the terminal."
    : `Connected · ${n} tool${n === 1 ? "" : "s"} discovered · ` +
      (mcp.resources.length ? `resource ${mcp.resources.join(", ")}` : "no resource read");
  const ul = $("mcp-tools");
  ul.innerHTML = "";
  for (const t of mcp.tools) {
    const li = document.createElement("li");
    const b = document.createElement("b");
    b.textContent = t.name;
    li.append(b, document.createTextNode(" " + t.description.split("\n")[0]));
    ul.append(li);
  }
}

function showTool(tool) {
  const el = $("tool");
  if (!tool) return;
  el.className = "toolcall " + (tool.ok ? "ok" : "fail");
  el.textContent = `${tool.name}(${JSON.stringify(tool.arguments)})\n→ ${tool.result}`;
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Server returned ${res.status}`);
  return res.json();
}

let busy = false;

function setBusy(on) {
  // Lock input while waiting, so replies can't arrive out of order.
  busy = on;
  $("input").disabled = on;
  document.querySelectorAll("#composer button, #script button, #reset").forEach((b) => (b.disabled = on));
  const typing = $("typing");
  if (on && !typing) {
    const div = document.createElement("div");
    div.id = "typing";
    div.className = "msg bot typing";
    div.textContent = "Bot is typing…";
    $("messages").append(div);
    $("messages").scrollTop = $("messages").scrollHeight;
  } else if (!on && typing) {
    typing.remove();
  }
  if (!on) $("input").focus();
}

async function send(text) {
  text = text.trim();
  if (!text || busy) return false;
  addMessage("user", text);
  setBusy(true);
  try {
    const data = await post("/api/chat", { session_id: sessionId, message: text });
    const kind = data.action === "escalate" ? "escalate"
      : ["error", "unavailable", "no_llm"].includes(data.action) ? "error" : "bot";
    addMessage("bot", data.reply, kind);
    showAction(data.action, data.decided_by);
    showState(data.state);
    showMcp(data.mcp);
    showTool(data.tool);
  } catch (err) {
    addMessage("bot", `Could not reach the backend (${err.message}). Is uvicorn running?`, "error");
  } finally {
    setBusy(false);
  }
  return true;
}

async function reset() {
  $("messages").innerHTML = "";
  lastState = {};
  document.querySelectorAll("#script button").forEach((b) => b.classList.remove("used"));
  try {
    const data = await post("/api/reset", { session_id: sessionId });
    addMessage("bot", data.reply);
    showAction(null, null);
    showState(data.state);
    showMcp(data.mcp);
    $("tool").className = "toolcall empty";
    $("tool").textContent = "None yet";
    $("orch").textContent = `LLM: ${data.llm}`;
  } catch (err) {
    addMessage("bot", `Could not reach the backend (${err.message}). Is uvicorn running?`, "error");
  }
}

$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  if (busy) return;
  const text = $("input").value;
  $("input").value = "";
  send(text);
});
$("reset").addEventListener("click", reset);

for (const line of TEST_SCRIPT) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = line;
  b.addEventListener("click", async () => { if (!busy) { b.classList.add("used"); await send(line); } });
  $("script").append(b);
}

reset();
