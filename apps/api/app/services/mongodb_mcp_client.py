"""Client for the official MongoDB MCP Server.

Spawns the Node-based ``mongodb-mcp-server`` over stdio (MCP protocol) and
exposes a narrow ``find`` API used for operational memory reads. The server
is always started with ``--readOnly``: writes can never travel through this
path, which keeps the clinical-safety write scoping in the controlled tool
adapter.
"""
import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import settings

logger = logging.getLogger(__name__)


class MongoDBMCPUnavailable(Exception):
    """Raised when the official MCP server cannot serve the request."""


def _server_params() -> StdioServerParameters:
    args = [a.strip() for a in settings.mongodb_mcp_args.split(",") if a.strip()]
    if "--readOnly" not in args:
        args.append("--readOnly")
    env = dict(os.environ)
    env.update({
        "MDB_MCP_CONNECTION_STRING": settings.mongodb_uri,
        "MDB_MCP_READ_ONLY": "true",
        "MDB_MCP_TELEMETRY": "disabled",
    })
    return StdioServerParameters(
        command=settings.mongodb_mcp_command,
        args=args,
        env=env,
    )


def _from_ejson(value: Any) -> Any:
    """Collapse MongoDB Extended JSON wrappers into plain JSON values."""
    if isinstance(value, dict):
        if len(value) == 1:
            key = next(iter(value))
            if key in ("$date", "$oid", "$numberLong", "$numberInt", "$numberDouble", "$numberDecimal"):
                inner = value[key]
                if key in ("$numberLong", "$numberInt"):
                    try:
                        return int(inner)
                    except (TypeError, ValueError):
                        return inner
                if key in ("$numberDouble", "$numberDecimal"):
                    try:
                        return float(inner)
                    except (TypeError, ValueError):
                        return inner
                return _from_ejson(inner)
        return {k: _from_ejson(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_from_ejson(v) for v in value]
    return value


# Server >=1.12 wraps document payloads in injection-defense boundary tags.
_UNTRUSTED_DATA_RE = re.compile(
    r"<untrusted-user-data-([0-9a-fA-F-]+)>\s*(.*?)\s*</untrusted-user-data-\1>",
    re.DOTALL,
)


def _parse_find_result(result: Any) -> List[Dict[str, Any]]:
    """Extract documents from an MCP ``find`` tool result.

    The server returns a summary block plus a block whose document array
    (Extended JSON) is wrapped in ``<untrusted-user-data-...>`` boundary
    tags. Older server versions return bare JSON blocks; both are handled.
    """
    docs: List[Dict[str, Any]] = []
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if not text:
            continue
        
        # Robustly extract JSON by ignoring boundary tags completely and looking for a top-level array or object
        parsed = None
        # Try to find something that looks like an array or an object
        start_idx_arr = text.find('[')
        start_idx_obj = text.find('{')
        
        # Find the outermost JSON structure
        start_idx = -1
        if start_idx_arr != -1 and start_idx_obj != -1:
            start_idx = min(start_idx_arr, start_idx_obj)
        elif start_idx_arr != -1:
            start_idx = start_idx_arr
        elif start_idx_obj != -1:
            start_idx = start_idx_obj
            
        if start_idx != -1:
            # We found a potential JSON start. Let's find the end.
            end_idx_arr = text.rfind(']')
            end_idx_obj = text.rfind('}')
            
            end_idx = -1
            if start_idx == start_idx_arr and end_idx_arr != -1:
                end_idx = end_idx_arr
            elif start_idx == start_idx_obj and end_idx_obj != -1:
                end_idx = end_idx_obj
                
            if end_idx != -1 and end_idx > start_idx:
                try:
                    candidate = text[start_idx:end_idx+1]
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    pass
                    
        # Fallback to the old regex method if the structural extraction failed
        if parsed is None:
            candidates = [m.group(2) for m in _UNTRUSTED_DATA_RE.finditer(text)] or [text]
            for candidate in candidates:
                try:
                    parsed = json.loads(candidate)
                    break
                except (json.JSONDecodeError, TypeError):
                    continue
                    
        if parsed is None:
            continue
            
        parsed = _from_ejson(parsed)
        if isinstance(parsed, list):
            docs.extend(d for d in parsed if isinstance(d, dict))
        elif isinstance(parsed, dict):
            # Some server versions wrap documents in a {"documents": [...]} envelope
            if isinstance(parsed.get("documents"), list):
                docs.extend(d for d in parsed["documents"] if isinstance(d, dict))
            else:
                docs.append(parsed)
    for doc in docs:
        doc.pop("_id", None)
    return docs


async def mcp_find(
    collection: str,
    filter: Optional[Dict[str, Any]] = None,
    *,
    limit: int = 50,
    sort: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """Run a read-only ``find`` through the official MongoDB MCP Server."""
    if not settings.mongodb_mcp_enabled:
        raise MongoDBMCPUnavailable("mongodb_mcp_disabled")

    arguments: Dict[str, Any] = {
        "database": settings.mongodb_database,
        "collection": collection,
        "filter": filter or {},
        "limit": limit,
    }
    if sort:
        arguments["sort"] = sort

    total_timeout = (
        settings.mongodb_mcp_startup_timeout_seconds
        + settings.mongodb_mcp_call_timeout_seconds
    )
    docs: Optional[List[Dict[str, Any]]] = None
    try:
        async with asyncio.timeout(total_timeout):
            async with stdio_client(_server_params()) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool("find", arguments=arguments)
                    if getattr(result, "isError", False):
                        raise MongoDBMCPUnavailable(f"mcp_tool_error:{collection}")
                    docs = _parse_find_result(result)
    except (KeyboardInterrupt, SystemExit):
        raise
    except MongoDBMCPUnavailable:
        raise
    except BaseException as exc:
        # The stdio transport can raise ExceptionGroup noise while tearing
        # down the subprocess. If the call already succeeded, keep the result.
        if docs is None:
            logger.warning("Official MongoDB MCP find failed (%s): %s", collection, exc)
            raise MongoDBMCPUnavailable(f"{type(exc).__name__}: {exc}") from exc
        logger.debug("Ignoring MCP transport teardown noise for %s: %s", collection, exc)
    return docs
