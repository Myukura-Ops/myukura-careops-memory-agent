# Official MongoDB MCP Read-Only Smoke Test

**Status:** Not part of the current demo execution path.
**Purpose:** Evaluation notes for official MongoDB MCP Server integration for the Hackathon.

## Background
The MyuKura CareOps Agent prioritizes deterministic safety. The official MongoDB MCP server provides raw database access (`mongodb_query`, `mongodb_update`, `mongodb_aggregate`). If exposed directly to an autonomous LLM, this would violate clinical safety boundaries (e.g. allowing unauthorized deletion of tasks, bypassing `requires_human_approval` flags, or injecting unverified diagnostic codes).

To safely participate in the MongoDB/Rapid Agent hackathon while demonstrating MCP capabilities, we implemented a **Controlled Local Adapter** pattern.

## Architecture

1. **Controlled Local Adapter (Currently Active)**
   - Exposes safe, strict tool definitions (e.g. `create_careops_task`, `search_patient_memory`).
   - The LLM calls these tools.
   - The adapter enforces deterministic business logic (e.g., forces `requires_human_approval = True`) and performs clinical keyword blocking before touching the database.
   - Uses native `motor` to execute the verified operation.

2. **Official MongoDB MCP Server (Read-Only Optional)**
   - Can be run alongside the application strictly in read-only mode.
   - Used for manual verification/troubleshooting by human operators via the MCP trace tools, but *not* exposed to the CareOps Agent's main decision loop.

## Running the Official MCP Server Locally (Read-Only)

If you wish to smoke-test the official server locally without exposing credentials or write permissions:

1. Create a limited read-only user in MongoDB Atlas for the database.
2. Provide the URI via environment variables (do not commit secrets).
3. Run the server using npx or the configured Rapid Agent.

```bash
# Example local test command (requires Node.js)
# Note: Ensure the URI used here only has read privileges.
npx -y @modelcontextprotocol/server-mongodb mongodb+srv://<readonly-user>:<password>@cluster0.mongodb.net/careops_demo
```

### Smoke Test Result
When evaluated locally in read-only mode, the official MCP server successfully responds to `mongodb_list_collections` and `mongodb_query` (e.g., retrieving `patients_demo`). However, we actively decided to keep the **Controlled Local Adapter** as the only active tool layer for the Agent to guarantee no write/delete operations are exposed to the AI model.
