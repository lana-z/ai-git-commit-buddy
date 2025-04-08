import asyncio
import json
import sys
import traceback
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class AICodeCommitMessageTool:
    def __init__(self, server):
        self.server = server

    async def generate_commit_message(self, diff: str) -> str:
        print(f"⚙️ Server: generate_commit_message called with diff: {diff}")
        return f"Generated commit message for diff: {diff}"


# Set up logging to file
with open('/tmp/ai_git_commit_server.log', 'a') as f:
    f.write(f"Starting server at {__file__}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Arguments: {sys.argv}\n")


# Print to both stdout and log file
def log(message):
    print(message)
    with open('/tmp/ai_git_commit_server.log', 'a') as f:
        f.write(f"{message}\n")


log("🧠 Server file is running")

app = Server("git-commit-buddy")


@app.list_tools()
async def list_tools():
    log("🔍 Server: Listing tools")
    log("🔍 Server: list_tools function called")
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
        log("✅ Server: Tool list created")
        log(f"Tools: {tools}")
        log("🔍 Server: list_tools function returning tools")
        return tools
    except Exception as e:
        log(f"Server: Failed to list tools: {e}")
        traceback.print_exc()
        with open('/tmp/ai_git_commit_server.log', 'a') as f:
            traceback.print_exc(file=f)
        return []


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"🛠️ Server: Calling tool {name}")
    log(f"Arguments: {arguments}")
    try:
        if name == "generate_commit_message":
            diff = arguments.get("diff", "")
            log(f"Diff: {diff}")
            log(f"🛠️ Server: Generating commit message for {name}")
            
            # Generate a more meaningful commit message based on the diff
            message_prefix = ""
            if diff.startswith("feat"):
                message_prefix = "feat: "
            elif diff.startswith("fix"):
                message_prefix = "fix: "
            else:
                # Try to infer the type from the content
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
            
            return [TextContent(type="text", text=commit_message)]
        log(f"🛠️ Server: Unknown tool {name}")
        raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        log(f"Error in call_tool: {e}")
        traceback.print_exc()
        with open('/tmp/ai_git_commit_server.log', 'a') as f:
            traceback.print_exc(file=f)
        raise


async def main():
    log("🚀 Server: Starting main")
    log("🚀 Server: main function called")
    try:
        async with stdio_server() as streams:
            log("🔌 Server: Connected to stdio")
            try:
                log("⏳ Server: About to run app...")
                log(f"Streams: {streams}")
                log(f"Streams[0]: {streams[0]}, Streams[1]: {streams[1]}")
                
                # Initialize capabilities and other settings here
                log("⚙️ Server: Initializing...")
                
                # Create proper initialization options with server capabilities
                init_options = app.create_initialization_options(
                    experimental_capabilities={"git-commit-buddy": {}}
                )
                log(f"Created initialization options: {init_options}")
                
                # Run the app without a timeout to avoid potential timeout issues
                log("🚀 Server: Running app without timeout")
                await app.run(streams[0], streams[1], init_options)
                log("✅ Server: App finished running")
            except Exception as e:
                log(f"💥 Server crashed: {e}")
                traceback.print_exc()
                with open('/tmp/ai_git_commit_server.log', 'a') as f:
                    traceback.print_exc(file=f)
    except Exception as e:
        log(f"💥 Fatal error in main: {e}")
        traceback.print_exc()
        with open('/tmp/ai_git_commit_server.log', 'a') as f:
            traceback.print_exc(file=f)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        traceback.print_exc()
        with open('/tmp/ai_git_commit_server.log', 'a') as f:
            f.write(f"💥 Fatal error: {e}\n")
            traceback.print_exc(file=f)
