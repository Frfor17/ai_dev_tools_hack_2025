import sys
import os

# Add the project root directory to sys.path to make 'app' importable
sys.path.insert(0, 'e:/project')

from app.mcp_module.server import run_mcp_server_sync

if __name__ == "__main__":
    run_mcp_server_sync()