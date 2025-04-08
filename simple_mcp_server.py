#!/usr/bin/env python3
import asyncio
import json
import sys
import traceback
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging to file
with open('/tmp/simple_mcp_server.log', 'a') as f:
    f.write(f"Starting simple server at {__file__}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Arguments: {sys.argv}\n")

# Print to stderr and log file
def log(message):
    print(message, file=sys.stderr)  # Send to stderr
    with open('/tmp/simple_mcp_server.log', 'a') as f:
        f.write(f"{message}\n")

log(" Simple MCP Server starting")

# Create a simple server
app = Server("git-commit-buddy")

@app.list_tools()
async def list_tools():
    log(" Listing tools")
    try:
        tools = [
            Tool(
                name="generate_commit_message",
                description="Generate a Git commit message from diff",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "diff": {"type": "string"}
                    },
                    "required": ["diff"]
                }
            )
        ]
        log(f"Tools created: {tools}")
        return tools
    except Exception as e:
        log(f"Error listing tools: {e}")
        traceback.print_exc()
        with open('/tmp/simple_mcp_server.log', 'a') as f:
            traceback.print_exc(file=f)
        return []

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"🛠️ call_tool called with name={name} and arguments={arguments}")
    try:
        if name == "generate_commit_message":
            diff = arguments.get("diff", "")
            log(f"🧪 diff = {diff} (type: {type(diff)})")
            
            # Generate a more meaningful commit message based on the diff
            message_prefix = ""
            if "add" in diff.lower() or "new" in diff.lower() or "implement" in diff.lower():
                message_prefix = "feat: "
            elif "fix" in diff.lower() or "bug" in diff.lower() or "issue" in diff.lower():
                message_prefix = "fix: "
            elif "refactor" in diff.lower():
                message_prefix = "refactor: "
            elif "doc" in diff.lower():
                message_prefix = "docs: "
            else:
                message_prefix = "chore: "
            
            # Create the commit message
            commit_message = message_prefix + diff[:100]
            log(f"Generated commit message: {commit_message}")
            
            # Return the result properly formatted
            return [TextContent(type="text", text=commit_message)]
        
        log(f"Unknown tool name: {name}")
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    except Exception as e:
        log(f"💥 Exception in call_tool: {e}")
        traceback.print_exc()
        with open('/tmp/simple_mcp_server.log', 'a') as f:
            traceback.print_exc(file=f)
        # Return an error message instead of raising an exception
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    log(" Main function started")
    try:
        async with stdio_server() as streams:
            log(" Connected to stdio")
            log(f"Streams: {streams}")
            log(f"Streams[0]: {streams[0]}, Streams[1]: {streams[1]}")
            
            # Create proper initialization options with server capabilities
            init_options = app.create_initialization_options(
                experimental_capabilities={"git-commit-buddy": {}}
            )
            log(f"Created initialization options: {init_options}")
            
            # Run without timeout to avoid issues
            try:
                log(" Starting app.run")
                # Wait for initialization to complete
                await app.run(streams[0], streams[1], init_options)
                log(" Server completed successfully")
            except Exception as e:
                log(f" Error during app.run: {e}")
                traceback.print_exc()
                with open('/tmp/simple_mcp_server.log', 'a') as f:
                    traceback.print_exc(file=f)
    except Exception as e:
        log(f" Error: {e}")
        traceback.print_exc()
        with open('/tmp/simple_mcp_server.log', 'a') as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log(f" Fatal error: {e}")
        traceback.print_exc()
        with open('/tmp/simple_mcp_server.log', 'a') as f:
            f.write(f" Fatal error: {e}\n")
            traceback.print_exc(file=f)
