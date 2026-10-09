"""The clinic's MCP server: a separate program the chatbot talks to over MCP.

When Activity 1 is done, it offers two TOOLS and one RESOURCE:
    check_availability(day)        tool      read-only: open slots on a weekday
    book_appointment(day, time)    tool      changes data: books one slot
    clinic://policies              resource  read-only text the app loads

Run it on its own, or test it with the MCP Inspector (needs Node.js):
    mcp dev backend/clinic_server.py
The chatbot starts it for you as a subprocess (see backend/mcp_client.py).

This file imports nothing from the chatbot: it stands for a service that the
clinic's IT team would run, which any MCP client could use.
"""
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("clinic-server")

# Pretend booking system: open counselling slots for this week.
SLOTS = {
    "Monday": ["10:00", "14:00"],
    "Tuesday": ["09:30", "15:00"],
    "Wednesday": [],
    "Thursday": ["11:00"],
    "Friday": ["13:00", "16:00"],
}
BOOKINGS = []

POLICIES = """Clinic policies
- Confidentiality: what students share stays with the counselling team, unless someone is at serious risk of harm.
- Cost: the first consultation is free for students.
- Hours: Monday to Friday, 9am to 5pm.
- Cancelling: cancel or reschedule at least 24 hours before your appointment.
- Emergencies: the clinic is not an emergency service. In a crisis, call your local crisis line or emergency services."""


# ==========================================================================
# Activity 1: tools and a resource
# ==========================================================================
# 1.1  Make this an MCP tool: add the @mcp.tool() decorator and a docstring.
#      The docstring is the description the LLM reads, so say what it does
#      and what it returns. Return the open slots as "09:30, 15:00",
#      or "NO_SLOTS" if that day is full.
def check_availability(day: str) -> str:
    return "NO_SLOTS"                                   # TODO


# 1.2  A second tool that BOOKS a slot (it changes data).
#      If `time` is not open on that day: raise ToolError("... is not available").
#      Otherwise remove it from SLOTS[day], add {"ref", "day", "time"} to BOOKINGS
#      and return f"Booked {day} at {time}. Reference {ref}."
#      with ref = f"BK-{1001 + len(BOOKINGS)}"
def book_appointment(day: str, time: str) -> str:
    raise ToolError("Not implemented yet")              # TODO


# 1.3  Make this a RESOURCE at the URI "clinic://policies":
#      add the @mcp.resource("clinic://policies") decorator and a docstring.
def policies() -> str:
    return POLICIES


if __name__ == "__main__":
    mcp.run()          # stdio: messages travel over stdin and stdout
