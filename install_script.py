import os
import sys
import json
import platform
import subprocess
from pathlib import Path

# --- Constants ---
MCP_SERVER_NAME = "founder-os"

def get_target_mcp_path():
    """Returns the primary MCP config path discovered."""
    home = Path.home()
    # The path we discovered: C:\Users\Name\.cursor\mcp.json
    target = home / ".cursor" / "mcp.json"
    return target

def install_dependencies():
    """Ensures all necessary packages, including 'requests', are installed."""
    print("\n[1/3] 📦 Installing dependencies...")
    # Added 'requests' to support the new Linear integration
    dependencies = ["mcp", "notion-client", "python-dotenv", "requests", "supabase", "starlette<0.47.0"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *dependencies], 
                              stdout=subprocess.DEVNULL)
        print("   ✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_env():
    print("\n[2/3] 🔑 Configuration")
    
    # Check if file exists and whether to overwrite it
    if os.path.exists(".env"):
        print("   ℹ️  Found existing .env file.")
        should_overwrite = input("   👉 Do you want to re-configure keys? (y/n): ").strip().lower()
        if should_overwrite != 'y':
            print("   ⏩ Skipping configuration.")
            return

    # 1. Notion Token (required)
    while True:
        notion_token = input("   👉 Paste Notion Token (ntn_ or secret_): ").strip()
        if (notion_token.startswith("secret_") or notion_token.startswith("ntn_")) and len(notion_token) > 20:
            break
        print("   ⚠️  Invalid Token. Must start with 'secret_' or 'ntn_'.")

    # 2. Linear API Key (optional - press Enter to skip)
    print("   ℹ️  (Optional) Add Linear API Key for task context.")
    linear_key = input("   👉 Paste Linear API Key (press Enter to skip): ").strip()

    # Write to file
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"NOTION_API_KEY={notion_token}\n")
            if linear_key:
                f.write(f"LINEAR_API_KEY={linear_key}\n")
        print("   ✅ .env created successfully.")
    except Exception as e:
        print(f"   ❌ Error writing .env: {e}")
        raise e

def inject_mcp():
    print("\n[3/3] 🔌 Injecting to Cursor Config...")
    config_path = get_target_mcp_path()
    
    # Ensure the directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data
    config = {"mcpServers": {}}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass

    # Set up the server in the exact structure that Cursor expects
    current_dir = os.getcwd()
    server_path = os.path.join(current_dir, "server.py")
    
    config["mcpServers"][MCP_SERVER_NAME] = {
        "command": sys.executable,
        "args": [server_path],
        "enabled": True  # Critical for immediate appearance
    }

    # Atomic save
    with open(config_path, 'w', encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print(f"   🚀 Success! Injected into: {config_path}")

def main():
    print("🛠️ Founder OS Installer")
    try:
        install_dependencies()
        setup_env()
        inject_mcp()
        print("\n✅ ALL SET! Please Restart Cursor.")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    main()