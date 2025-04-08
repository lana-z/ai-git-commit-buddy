import asyncio
import json
from mcp.types import JSONRPCRequest

async def main():
    print("🚀 Client: Starting...")
    process = await asyncio.create_subprocess_exec(
        ".venv_isolated/bin/python", "ai_git_commit_server.py",
        cwd=".",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        text=True,
    )

    print("🔌 Client: Connected")

    # Initialize
    init_request = JSONRPCRequest(
        jsonrpc="2.0",
        id=1,
        method="initialize",
        params={
            "protocolVersion": "1.0",
            "capabilities": {},
            "clientInfo": {}
        }
    )
    init_json = json.dumps(init_request.model_dump())
    print(f"📤 Client: Sending initialize request: {init_json}")
    process.stdin.write(init_json + "\n")
    await process.stdin.drain()
    await process.stdout.flush()
    print("📤 Client: Sent initialize")

    await asyncio.sleep(0.1)
    response_lines = await process.stdout.readlines()
    response = "".join(response_lines)
    print(f"📥 Client: Got initialize response: {response}")

    # Call tool
    tool_request = JSONRPCRequest(
        jsonrpc="2.0",
        id=2,
        method="callTool",
        params={
            "name": "generate_commit_message",
            "arguments": {"diff": "print('Hello')"}
        }
    )
    tool_json = json.dumps(tool_request.model_dump())
    print(f"📤 Client: Sending tool request: {tool_json}")
    process.stdin.write(tool_json + "\n")
    await process.stdin.drain()
    await process.stdout.flush()
    print("📤 Client: Sent tool request")

    await asyncio.sleep(0.1)
    response_lines = await process.stdout.readlines()
    response = "".join(response_lines)
    print(f"📥 Client: Got call tool response: {response}")

    process.stdin.close()
    try:
        await asyncio.wait_for(process.wait(), timeout=5)
    except asyncio.TimeoutError:
        print("Client: Timeout waiting for process to finish")
        process.terminate()
