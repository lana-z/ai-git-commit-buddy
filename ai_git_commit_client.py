#!/usr/bin/env python3
import asyncio
import json
import sys
import subprocess
import time
import re
import argparse
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import JSONRPCRequest

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate commit messages from git diffs')
    parser.add_argument('--diff', '-d', type=str, help='The diff to generate a commit message for')
    parser.add_argument('--file', '-f', type=str, help='File containing the diff')
    parser.add_argument('--git', '-g', action='store_true', help='Get diff from git staged changes')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='Timeout in seconds (default: 10)')
    parser.add_argument('--server', '-s', type=str, 
                        default='/Users/lanazumbrunn/projects/first-mcp-server/ai-git-commit-buddy/simple_mcp_server.py',
                        help='Path to the server script')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--fallback', action='store_true', help='Use fallback mechanism if JSON-RPC fails')
    return parser.parse_args()

def get_git_diff():
    """Get the diff of staged changes from git"""
    try:
        result = subprocess.run(['git', 'diff', '--staged'], 
                               capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        sys.exit(1)

def read_diff_file(file_path):
    """Read diff from a file"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading diff file: {e}")
        sys.exit(1)

async def generate_commit_message(diff, server_path, timeout=10, debug=False, fallback=False):
    """Generate a commit message using the MCP protocol"""
    print("Starting client")
    
    try:
        # Set up the server parameters
        server = StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            env={"PYTHONUNBUFFERED": "1"}
        )
        
        # Connect to the server
        print("Connecting to server...")
        async with stdio_client(server) as (read, write):
            # Send initialize request
            print("Sending initialize request...")
            await write.send(JSONRPCRequest(
                jsonrpc="2.0",
                id=1,
                method="initialize",
                params={
                    "protocolVersion": "1.0",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "ai-git-commit-client",
                        "version": "1.0.0"
                    }
                }
            ))
            
            # Get initialization response
            init_response = await asyncio.wait_for(read.receive(), timeout=timeout)
            if debug:
                print(f"Init Response: {init_response}")
            await asyncio.sleep(1.0)  

            # List tools to give server time
            print("Listing tools...")
            await write.send(JSONRPCRequest(
                jsonrpc="2.0",
                id=2,
                method="tools/list",
                params={}
            ))
            list_response = await asyncio.wait_for(read.receive(), timeout=timeout)
            if debug:
                print(f"Tool list response: {list_response}")

            # Then send your actual tool request
            print("Sending tool request...")
            await write.send(JSONRPCRequest(
                jsonrpc="2.0",
                id=3,
                method="tools/call",
                params={
                    "name": "generate_commit_message",
                    "arguments": {"diff": diff}
                }
            ))
            
            # Get tool response
            print("Waiting for response...")
            try:
                tool_response = await asyncio.wait_for(read.receive(), timeout=timeout)
                if debug:
                    print(f"Tool Response: {tool_response}")
                
                # Extract the commit message from the response
                if hasattr(tool_response, 'result') and tool_response.result:
                    if isinstance(tool_response.result, list) and len(tool_response.result) > 0:
                        if hasattr(tool_response.result[0], 'text'):
                            return tool_response.result[0].text
                    elif isinstance(tool_response.result, dict) and 'text' in tool_response.result:
                        return tool_response.result['text']
                
                # If we couldn't extract a message, return a generic one
                return f"feat: {diff[:50]}"
                
            except asyncio.TimeoutError:
                print(f"Timed out waiting for tool response after {timeout} seconds")
                if fallback:
                    return f"feat: {diff[:50]}"
                else:
                    return "Failed to generate commit message (timeout)"
    
    except Exception as e:
        print(f"Error during MCP communication: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        
        if fallback:
            print("Using fallback mechanism")
            # Generate a simple commit message based on the diff
            if "add" in diff.lower() or "new" in diff.lower() or "implement" in diff.lower():
                return f"feat: {diff[:50]}"
            elif "fix" in diff.lower() or "bug" in diff.lower() or "issue" in diff.lower():
                return f"fix: {diff[:50]}"
            elif "refactor" in diff.lower():
                return f"refactor: {diff[:50]}"
            elif "doc" in diff.lower():
                return f"docs: {diff[:50]}"
            else:
                return f"chore: {diff[:50]}"
        else:
            return f"Failed to generate commit message: {str(e)}"

async def main():
    args = parse_arguments()
    
    # Get the diff
    diff = None
    if args.diff:
        diff = args.diff
    elif args.file:
        diff = read_diff_file(args.file)
    elif args.git:
        diff = get_git_diff()
    else:
        print("Error: No diff provided. Use --diff, --file, or --git")
        sys.exit(1)
    
    # Always enable fallback for now until server issues are resolved
    fallback_enabled = True
    
    # Generate commit message
    commit_message = await generate_commit_message(
        diff, 
        args.server, 
        timeout=args.timeout, 
        debug=args.debug,
        fallback=fallback_enabled
    )
    
    # Print the commit message
    print("\nGenerated Commit Message:")
    print(commit_message)

if __name__ == "__main__":
    asyncio.run(main())