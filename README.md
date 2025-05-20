# cli-chat

A simple, extensible command-line chat application supporting TCP (with planned UDP fallback). Built in Python, it lets you run a server and multiple clients directly from the terminal.

---

## Features

- **TCP Chat**: Real-time, broadcast messaging over TCP sockets.  
- **Graceful Shutdown**: Clients exit cleanly on disconnect; server automatically removes dead connections.  
- **Flexible Usage**: Run as a single script (`chat.py`) or install as a package (`python -m chat`).  
- **Unified CLI**: Argument parsing for server/client modes, host, and port configuration.  
- **Future-Ready**: Designed for UDP fallback, rich prompts, Docker support, and CI testing.  

---

## Prerequisites

- **Python** 3.8 or higher  
- **Git** (optional, for version control)  
- **GitHub CLI** (optional, for repo setup: `gh repo create ...`)  
- Unix-like shell (bash, zsh) or Windows PowerShell/CMD  
