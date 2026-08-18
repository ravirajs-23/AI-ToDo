"""
AI To-Do List — FastAPI backend.

Takes raw, scattered notes ("Finish PPT, check AWS logs, call client")
and turns them into a structured to-do list with priority and category,
using the Claude API (Anthropic) for the actual understanding.

If no ANTHROPIC_API_KEY is configured, falls back to a simple built-in
heuristic parser so the app still works for a quick demo — but for real
use, set ANTHROPIC_API_KEY.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

app = FastAPI(title="AI To-Do List")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class OrganizeRequest(BaseModel):
    notes: str
    categories: Optional[List[str]] = None  # optional custom category hints


class Task(BaseModel):
    title: str
    priority: str  # High | Medium | Low
    category: str
    notes: Optional[str] = ""


class OrganizeResponse(BaseModel):
    tasks: List[Task]
    source: str  # "claude" or "fallback-heuristic"


SYSTEM_PROMPT = """You are an assistant that turns a messy, unstructured brain-dump of \
work notes into a clean, structured to-do list for an employee.

Rules:
- Split the input into individual, atomic action items (one task per item).
- For each task, assign a "priority" of exactly "High", "Medium", or "Low", based on \
urgency/impact language (e.g. words like "urgent", "ASAP", "today", "client", "deadline" \
usually mean High; routine/admin/no time pressure usually mean Low).
- Assign a short "category" label such as "Work", "Admin", "Meetings", "Technical", \
"Personal", or another concise category that fits — group similar tasks under the same \
category name.
- Keep each task "title" short and action-oriented (start with a verb where natural).
- Preserve useful detail in a short "notes" field only if extra context was given (else "").
- Output ONLY valid JSON: a list of objects with keys: title, priority, category, notes. \
No prose, no markdown fences, no commentary — just the JSON array.
"""


def call_claude(notes: str) -> List[dict]:
    from anthropic import Anthropic

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": notes}],
    )
    text = "".join(
        block.text for block in message.content if getattr(block, "type", "") == "text"
    ).strip()

    # Strip accidental markdown fences if the model adds them anyway.
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip()).strip()

    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list from Claude")
    return data


HIGH_KEYWORDS = [
    "urgent", "asap", "today", "now", "immediately", "deadline", "client",
    "critical", "escalat", "production", "prod ", "down", "outage", "fix now",
]
LOW_KEYWORDS = ["someday", "later", "maybe", "when possible", "low priority", "optional"]

CATEGORY_RULES = [
    ("Meetings", ["meeting", "call", "sync", "standup", "1:1", "1-1", "zoom", "meet with"]),
    ("Technical", ["aws", "server", "deploy", "bug", "log", "code", "api", "database", "db ",
                   "server", "ec2", "s3", "ci/cd", "pipeline", "repo", "git"]),
    ("Admin", ["invoice", "expense", "report", "timesheet", "hr", "form", "approval",
               "reimbursement", "policy"]),
    ("Work", []),  # default fallback
]


def split_notes(notes: str) -> List[str]:
    # Split on newlines, bullets, or commas/semicolons acting as separators.
    raw = re.split(r"[\n\r]+|(?<=[a-zA-Z0-9])\s*[•\-•]\s+", notes)
    items: List[str] = []
    for chunk in raw:
        chunk = chunk.strip(" \t-•*")
        if not chunk:
            continue
        # Further split comma-separated short clauses often used in brain dumps.
        parts = re.split(r",\s+(?=[A-Za-z])", chunk)
        for p in parts:
            p = p.strip()
            if p:
                items.append(p)
    return items or [notes.strip()]


def _contains_keyword(lower: str, keyword: str) -> bool:
    """Whole-word-ish match so e.g. 'repo' doesn't match inside 'report'."""
    pattern = r"(?<![a-z])" + re.escape(keyword.strip()) + r"(?![a-z])"
    return re.search(pattern, lower) is not None


def heuristic_parse(notes: str) -> List[dict]:
    items = split_notes(notes)
    tasks = []
    for item in items:
        lower = item.lower()
        if any(_contains_keyword(lower, k) for k in HIGH_KEYWORDS):
            priority = "High"
        elif any(_contains_keyword(lower, k) for k in LOW_KEYWORDS):
            priority = "Low"
        else:
            priority = "Medium"

        category = "Work"
        for cat, keywords in CATEGORY_RULES:
            if keywords and any(_contains_keyword(lower, k) for k in keywords):
                category = cat
                break

        title = item[0].upper() + item[1:] if item else item
        tasks.append({"title": title, "priority": priority, "category": category, "notes": ""})
    return tasks


@app.get("/")
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok", "claude_configured": bool(ANTHROPIC_API_KEY)}


@app.post("/api/organize", response_model=OrganizeResponse)
def organize(req: OrganizeRequest):
    notes = (req.notes or "").strip()
    if not notes:
        return OrganizeResponse(tasks=[], source="none")

    if ANTHROPIC_API_KEY:
        try:
            data = call_claude(notes)
            tasks = [
                Task(
                    title=str(d.get("title", "")).strip() or "Untitled task",
                    priority=str(d.get("priority", "Medium")).strip().title()
                    if str(d.get("priority", "Medium")).strip().title() in {"High", "Medium", "Low"}
                    else "Medium",
                    category=str(d.get("category", "Work")).strip() or "Work",
                    notes=str(d.get("notes", "") or ""),
                )
                for d in data
            ]
            return OrganizeResponse(tasks=tasks, source="claude")
        except Exception:
            # Fall through to heuristic if the API call fails for any reason.
            pass

    data = heuristic_parse(notes)
    tasks = [Task(**d) for d in data]
    return OrganizeResponse(tasks=tasks, source="fallback-heuristic")
