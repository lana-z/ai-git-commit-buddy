# AI Git Commit Buddy

Project to learn about and implement MCP. A git commit message generator that creates conventional commit messages from diffs.

## Overview

This project implements a Model Context Protocol (MCP) server and client for generating Git commit messages. Currently works with Windsurf IDE as the Client. Progress toward working with non-agentic IDEs by providing a simple interface for generating commit messages based on code changes. For learning purposed only, given that agentic IDEs already do this. 


## Integration with Windsurf

The MCP server is configured to work with Windsurf through the `mcp_config.json` file. The server has been successfully integrated with Windsurf and shows as green in the MCP server list. 


## MCP Implementation

The project uses the Model Context Protocol (MCP) which allows AI tools to be integrated with various clients. The server is implemented using the MCP server library, and the client uses the MCP client library for communication.

The current implementation of the client outside of Windsurf needs work. It has issues with the synchronization between client and server.

## Usage

```bash
# Generate a commit message from staged changes
python ai_git_commit_client.py --git

# Generate a commit message from a specific diff
python ai_git_commit_client.py --diff "Add new feature for commit message generation"

# Generate a commit message from a file containing a diff
python ai_git_commit_client.py --file path/to/diff.txt

# Enable debug mode
python ai_git_commit_client.py --diff "Fix bug" --debug

# Force fallback mechanism
python ai_git_commit_client.py --diff "Fix bug" --fallback
```