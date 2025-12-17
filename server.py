import os
import sys
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from notion_client import Client, APIResponseError


# 1. Setup & Config
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

if not NOTION_API_KEY:
    print("CRITICAL: NOTION_API_KEY is missing.", file=sys.stderr)
    raise ValueError("NOTION_API_KEY is missing from .env file.")

mcp = FastMCP("Notion Context Gateway")


# 2. Parsing Logic
def _extract_text_from_block(block: Dict[str, Any]) -> Optional[str]:
    """Parses a single block and returns formatted text."""
    block_type = block.get("type")

    # Supported types map to their prefix formatting
    # e.g. Bullet points get "- ", To-do get "[ ] "
    prefixes = {
        "paragraph": "",
        "heading_1": "# ",
        "heading_2": "## ",
        "heading_3": "### ",
        "bulleted_list_item": "- ",
        "numbered_list_item": "1. ",
        "quote": "> ",
        "callout": "💡 ",
        "toggle": "> ",
    }

    if block_type not in prefixes and block_type != "to_do":
        # Skipping unsupported block types
        return None

    content_obj = block.get(block_type, {})
    rich_text = content_obj.get("rich_text", [])
    if not rich_text:
        return None

    plain_text = "".join([t.get("plain_text", "") for t in rich_text])

    # Handle Checkboxes specifically
    if block_type == "to_do":
        checked = content_obj.get("checked", False)
        prefix = "[x] " if checked else "[ ] "
        return f"{prefix}{plain_text}"

    # Handle standard prefixes
    return f"{prefixes.get(block_type, '')}{plain_text}"


# 3. Tool Definition
@mcp.tool()
def fetch_project_context(page_id: str) -> str:
    """
    Fetches title and content from a Notion page.
    Supports paragraphs, headings, lists, and todos.
    """
    print(f"DEBUG: Fetching page_id={page_id}", file=sys.stderr)

    if not page_id or not page_id.strip():
        return "Error: page_id cannot be empty."

    try:
        notion = Client(auth=NOTION_API_KEY)

        # A. Fetch Page Metadata (Title)
        page = notion.pages.retrieve(page_id=page_id)
        title_obj = page.get("properties", {}).get("title", {}).get("title", [])
        page_title = (
            "".join([t.get("plain_text", "") for t in title_obj])
            if title_obj
            else "Untitled Page"
        )

        # B. Fetch Page Content (Blocks)
        response = notion.blocks.children.list(block_id=page_id)
        blocks = response.get("results", [])

        print(f"DEBUG: Found {len(blocks)} blocks.", file=sys.stderr)
        content_lines = []
        for block in blocks:
            text = _extract_text_from_block(block)
            if text:
                content_lines.append(text)

        full_text = f"Title: {page_title}\n\n" + "\n".join(content_lines)
        return full_text
    except APIResponseError as e:
        print(f"API ERROR: {e}", file=sys.stderr)
        return f"Notion API Error: {e.message}"
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        return f"Internal Server Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
