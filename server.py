import os
from mcp.server.fastmcp import FastMCP
from config.auth_config import load_auth_config

# Import modular tools
from src.tools.notion_context import search_notion, fetch_project_context, append_to_page
from src.tools.fs import list_directory
# We import the RULES string, but NOT the install logic
from config.setup_governance import GOVERNANCE_RULES

# 1. Validate Auth on Startup
try:
    config = load_auth_config()
    print(f"[OK] Auth Loaded. Notion Key present: {bool(config.notion_api_key)}")
except ValueError as e:
    print(f"[WARN] Startup Warning: {e}")
    print("Run 'python -m config.setup_full' to configure credentials.")

# 2. Initialize Server
mcp = FastMCP("Founder OS")

# 3. Register Tools
mcp.add_tool(search_notion)
mcp.add_tool(fetch_project_context)
mcp.add_tool(append_to_page)
mcp.add_tool(list_directory)

# --- NEW: Fixed Bootstrap Tool ---
@mcp.tool()
def bootstrap_project(target_dir: str) -> str:
    """
    INITIALIZE COMMAND: Installs the Founder OS 'Brain' (.cursorrules) into the specified project folder.
    The AI should provide the absolute path to the current project root.
    """
    try:
        # Clean the path
        target_path = os.path.join(os.path.abspath(target_dir), ".cursorrules")
        
        if os.path.exists(target_path):
             return f"ℹ️ Skipped: .cursorrules already exists at {target_path}"

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(GOVERNANCE_RULES)
            
        return f"✅ Success: Founder OS 'Brain' installed at: {target_path}"
    except Exception as e:
        return f"❌ Error initializing: {str(e)}"

if __name__ == "__main__":
    mcp.run()