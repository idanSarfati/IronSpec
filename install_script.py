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
    # הנתיב שגילינו: C:\Users\Name\.cursor\mcp.json
    target = home / ".cursor" / "mcp.json"
    return target

def install_dependencies():
    print("\n[1/3] 📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          stdout=subprocess.DEVNULL)
    print("   ✅ Done.")

def setup_env():
    if not os.path.exists(".env"):
        print("\n[2/3] 🔑 Configuration")
        token = input("   👉 Paste Notion Token (ntn_ or secret_): ").strip()
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"NOTION_API_KEY={token}\n")
        print("   ✅ .env created.")

def inject_mcp():
    print("\n[3/3] 🔌 Injecting to Cursor Config...")
    config_path = get_target_mcp_path()
    
    # וודא שהתיקייה קיימת
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # טעינת נתונים קיימים
    config = {"mcpServers": {}}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass

    # הגדרת השרת במבנה המדויק ש-Cursor אוהב
    current_dir = os.getcwd()
    server_path = os.path.join(current_dir, "server.py")
    
    config["mcpServers"][MCP_SERVER_NAME] = {
        "command": sys.executable,
        "args": [server_path],
        "enabled": True  # קריטי להופעה מיידית
    }

    # שמירה אטומית
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