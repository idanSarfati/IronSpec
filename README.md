
# 🚀 IronSpec: Blocks risky AI changes before they hit main

IronSpec is a GitHub Action that reviews pull requests (including AI-generated changes) against your specs and governance rules, then blocks risky code before it lands.

It catches things like unsafe `fetch` calls, forbidden libraries, and architecture violations, while still letting you override with a clear audit trail when needed.

---

## ⚡ Quickstart: GitHub Action

Add IronSpec to your repository to validate every pull request:

```yaml
name: IronSpec Governance
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  governance:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: 🛡️ Run IronSpec Governance
        uses: idanSarfati/IronSpec@v2.0.0
        with:
          linear_api_key: ${{ secrets.LINEAR_API_KEY }}
          notion_api_key: ${{ secrets.NOTION_API_KEY }}
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
```

### Required Secrets

| GitHub Secret        | What it's for                                    | Required?   |
| -------------------- | ------------------------------------------------ | ----------- |
| `LINEAR_API_KEY`     | Create/log governance events and audit trails    | Yes         |
| `NOTION_API_KEY`     | Read specs/governance rules from Notion          | Yes         |
| `GEMINI_API_KEY`     | Analyze PR diffs in CI for violations            | Recommended |
| `OPENAI_API_KEY`     | Extract and normalize governance rules           | Optional    |
| `GITHUB_TOKEN`       | GitHub API access (auto-provided)                | Auto        |

---

## 🛡️ How It Works

IronSpec validates PRs against your governance rules stored in Notion:

1. **PR opened** → GitHub Action triggers
2. **Extract rules** from your Notion specs and Linear tasks
3. **Analyze changes** using AI to detect violations
4. **Block or warn** based on severity (with override options)
5. **Log audit trail** to Linear for team visibility

### Trust Scoring

| Score     | Severity       | Action                              |
| --------- | -------------- | ----------------------------------- |
| 0-50      | 🚫 Critical    | Hard block (security violations)    |
| 51-80     | ⚠️ Suspicious  | Soft block with override option     |
| 81-100    | ✅ Safe        | Auto-approve                        |

### Override Mechanisms

When you need to bypass governance (emergencies, false positives):

- **Label Override:** Add `governance-override` label to PR
- **Text Override:** Include `[override: your reason here]` in PR description
- **Audit Trail:** All overrides create Linear tickets for team review

### Skip Validation

For infrastructure/CI changes, validation is auto-skipped when PR title contains:
- Keywords: `infra`, `ci`, `workflow`, `dependencies`, `setup`, `chore`, `docs`
- Tags: `[SKIP]` to force skip, `[FORCE]` to override skip detection

---

## 🔒 Privacy & Data Policy

**We do not store your code.** Only structural metadata (function names, imports, patterns) is analyzed. Zero logs retained.

IronSpec communicates only with:
- **Linear API**: Audit logging and governance events
- **Notion API**: Reading your specs and governance rules
- **Gemini/OpenAI API**: AI-powered code analysis
- **GitHub API**: PR comments and metadata

---

## 🛡️ Governance Enforcement

The system **dynamically extracts** governance rules from your Notion workspace:

- **Approved Tech Stack**: Libraries and frameworks from your specs
- **Forbidden Libraries**: Anything explicitly prohibited
- **Security Requirements**: Auth strategies, validation rules
- **Architecture Patterns**: Code organization, design principles

### Fallback Protection

Even if APIs go down, baseline rules are always enforced:
- Forbidden patterns (unsafe fetch, etc.)
- Security violations
- Architecture violations

---

## 🧩 Advanced: Local MCP Server (Optional)

IronSpec also includes an **MCP (Model Context Protocol) server** for local Cursor IDE integration. This gives you real-time governance guidance while coding.

### Setup

```bash
# Clone and install
git clone https://github.com/idanSarfati/IronSpec.git
cd IronSpec
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Register with Cursor
python install_script.py
```

### Activating in Cursor

Open the Composer (`Cmd/Ctrl + I`) and type:

```
"Initialize IronSpec"
```

The agent will execute `bootstrap_project`, injecting governance rules into `.cursor/rules/iron-spec-governance.mdc`. From that moment, the AI will enforce your architecture constraints in real-time.

### MCP Tools

| Tool                       | Capability                                              |
| -------------------------- | ------------------------------------------------------- |
| `search_notion`            | Search Notion workspace for PRDs, Specs, and Tasks      |
| `fetch_project_context`    | Read full page content for deep project knowledge       |
| `append_to_page`           | Document progress or update logs in Notion              |
| `list_directory`           | Scan local files to prevent duplicate code              |
| `list_linear_tasks`        | List active issues (assigned + team)                    |
| `get_linear_task_details`  | Fetch details for a Linear task (e.g., `PROJ-123`)      |
| `bootstrap_project`        | Deploy governance rules locally                         |
| `refresh_governance_rules` | Update rules from latest Notion/Linear data             |

### Linear Integration (MCP)

With the MCP server running, you can manage tasks directly from chat:

* **See your tasks:** Ask *"List my Linear tasks"*
* **Start working:** Ask *"Get details for task PROJ-123"*

### Updating the MCP Server

**Windows:** Double-click `scripts/update.bat`

**Mac/Linux:** Run `./scripts/update.sh`

---

## 🔍 Troubleshooting

If the system behaves unexpectedly:

1. Check the `iron_spec.log` file in the project root
2. API keys and tokens are automatically masked in logs
3. Open a GitHub issue with the log attached

---

## 📋 Prerequisites

**For GitHub Action (most users):**
- Just add the secrets to your repo and copy the workflow

**For MCP Server (advanced):**
- Python 3.10+
- Notion Integration: Create at [Notion My Integrations](https://www.notion.so/my-integrations) and share pages with it
- Linear API Key (optional)
- OpenAI/Gemini API Keys

---

## 🛡 License

IronSpec is open source under the MIT License. See `LICENSE` for details.
