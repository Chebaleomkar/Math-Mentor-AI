"""
frontend/app.py
---------------
Math Mentor AI — Gradio 4.44.1 frontend

Fixes applied vs previous version:
  1. Output tuple length is consistent across ALL code paths (always 5 values)
  2. send_btn.click only wired ONCE — file clear merged into on_send return
  3. gr.Image type="filepath" handled safely (dict or str)
  4. No gr.themes.GoogleFont — fonts loaded via CSS @import only
  5. Enter-key JS uses direct form submit, not querySelector button click
  6. attach_btn uses only elem_classes (no conflicting elem_id on Button)
  7. All state updates go through a single clean return tuple

Run locally:
    cd frontend
    pip install -r requirements.txt
    python app.py

Deploy to HuggingFace Spaces:
    Push app.py + requirements.txt, set BACKEND_URL secret.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Optional

import httpx
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 120

# ── API ───────────────────────────────────────────────────────────────────────

def _post(path: str, payload: dict) -> dict:
    try:
        r = httpx.post(f"{BACKEND_URL}{path}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.TimeoutException:
        return {"error": "Request timed out. The agent pipeline is slow — try again."}
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return {"error": f"Backend {e.response.status_code}: {detail}"}
    except Exception as e:
        return {"error": f"Cannot reach backend at {BACKEND_URL}. Is it running? ({e})"}

def _get(path: str) -> dict | list:
    try:
        r = httpx.get(f"{BACKEND_URL}{path}", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ── File helpers ──────────────────────────────────────────────────────────────

def _safe_filepath(val) -> str:
    """
    gr.Image can return a str path, a dict {'name': path, ...}, or None.
    Always return a plain string path or "".
    """
    if val is None:
        return ""
    if isinstance(val, dict):
        return val.get("name") or val.get("path") or ""
    return str(val)

def _file_to_b64(path: str) -> tuple[str, str]:
    p = Path(path)
    ext = p.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png",  ".webp": "image/webp", ".gif": "image/gif",
        ".wav": "audio/wav",  ".mp3": "audio/mpeg", ".m4a": "audio/mp4",
        ".webm": "audio/webm", ".ogg": "audio/ogg",
    }
    mime = mime_map.get(ext, "application/octet-stream")
    b64  = base64.b64encode(p.read_bytes()).decode()
    return b64, mime

# ── Formatting helpers ────────────────────────────────────────────────────────

def _confidence_badge(score: float) -> str:
    pct = int(score * 100)
    if pct >= 85:   icon, label = "🟢", "High"
    elif pct >= 65: icon, label = "🟡", "Medium"
    else:           icon, label = "🔴", "Low"
    return f"{icon} **{label} confidence** ({pct}%)"

def _fmt_tools(tool_calls: list) -> str:
    if not tool_calls:
        return "<div style='color:var(--text-3);font-size:.8rem;'>No external tools invoked.</div>"
    lines = ["<div style='display:flex;flex-direction:column;gap:8px;'>"]
    for tc in tool_calls:
        tool = tc.get("tool", "unknown")
        inp = str(tc.get("input", ""))[:60]
        out = str(tc.get("output", ""))[:120]
        lines.append(
            f"<div style='background:var(--elevated);border-left:2px solid var(--accent);padding:8px;border-radius:var(--r-sm);'>"
            f"<div style='font-family:var(--mono);font-size:.75rem;color:var(--accent);font-weight:600;'>{tool}</div>"
            f"<div style='font-size:.7rem;color:var(--text-2);margin-top:4px;'>&larr; {inp}...</div>"
            f"<div style='font-size:.7rem;color:var(--green);margin-top:2px;'>&rarr; {out}...</div>"
            f"</div>"
        )
    lines.append("</div>")
    return "\n".join(lines)

def _fmt_orchestration(hitl: bool, conf: float) -> str:
    steps = [
        ("Parser", "Structured interpretation", "✅"),
        ("RAG",    "Math DB Context", "✅"),
        ("Solver", "Multi-Agent reasoning", "✅"),
        ("Verifier", "Confidence check", "🔔" if hitl else "✅"),
        ("Explainer", "Professional LaTeX", "✅")
    ]
    html = ["<div style='display:flex;flex-direction:column;gap:12px;margin:5px 0;'>"]
    for i, (name, desc, status) in enumerate(steps):
        is_last = i == len(steps) - 1
        active_color = "var(--accent)" if status == "✅" else "var(--red)"
        html.append(f"""
            <div style='display:flex;align-items:center;gap:12px;position:relative;'>
                <div style='width:24px;height:24px;border-radius:50%;background:var(--bg);border:2px solid {active_color};display:flex;align-items:center;justify-content:center;font-size:.7rem;color:{active_color};z-index:2;box-shadow:0 0 8px var(--accent-glow);'>
                    {status}
                </div>
                <div style='flex:1;'>
                    <div style='font-weight:600;font-size:.8rem;color:var(--text);letter-spacing:.02em;'>{name}</div>
                    <div style='font-size:.68rem;color:var(--text-3);'>{desc}</div>
                </div>
                { "" if is_last else f"<div style='position:absolute;left:11px;top:24px;width:2px;bottom:-12px;background:linear-gradient(to bottom, {active_color}, var(--border));z-index:1;'></div>" }
            </div>
        """)
    html.append("</div>")
    return "".join(html)

def _fmt_sources(sources: list) -> str:
    if not sources:
        return "<div style='color:var(--text-3);padding:10px;text-align:center;'>No relevant knowledge base chunks found.</div>"
    html = ["<div style='display:flex;flex-direction:column;gap:10px;'>"]
    for s in sources:
        html.append(f"""
            <div style='background:var(--elevated);border:1px solid var(--border);border-radius:var(--r-sm);padding:10px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                    <b style='font-size:.75rem;color:var(--text);'>{s.get('title','')}</b>
                    <span style='background:var(--accent-dim);color:var(--accent);font-size:.6rem;padding:2px 6px;border-radius:4px;'>{s.get('score',0):.3f}</span>
                </div>
                <div style='font-size:.68rem;color:var(--text-2);line-height:1.4;'>{s.get('snippet','')[:180]}...</div>
            </div>
        """)
    html.append("</div>")
    return "".join(html)

def _fmt_recent(records: list | dict) -> str:
    if isinstance(records, dict) and "error" in records:
        return f"*Error: {records['error']}*"
    if not records:
        return "*No solved problems yet.*"
    lines = []
    for r in records[:10]:
        fb = r.get("user_feedback") or "—"
        icon = "✅" if fb == "correct" else ("❌" if fb == "incorrect" else "·")
        prob = r.get("problem_text", "")[:55]
        ans  = r.get("final_answer", "?")[:40]
        lines.append(f"{icon} **{r.get('topic','?')}**  \n`{prob}…`  \nAnswer: `{ans}`")
    return "\n\n---\n\n".join(lines)

# ── RETURN TUPLE CONTRACT ─────────────────────────────────────────────────────
# Every handler that wires to send_outputs MUST return exactly this tuple:
#   (history, msg_clear, agent_md, sources_md, new_memory_id, fb_vis, hitl_vis)
# 7 values, always. Never more, never fewer.

EMPTY_RETURN = ([], "", "*No tools called.*", "*No context retrieved.*", "", gr.update(visible=False), gr.update(visible=False))

def _error_return(history: list, question: str, msg: str) -> tuple:
    history = history + [(question, f"❌ {msg}")]
    return history, "", "*—*", "*—*", "", gr.update(visible=False), gr.update(visible=False)

# ── Core pipeline ─────────────────────────────────────────────────────────────

def _run_solve(question: str, history: list) -> tuple:
    """Call /solve with text input. Returns 7-tuple."""
    if not question.strip():
        return history, "", "*—*", "*—*", "", gr.update(visible=False), gr.update(visible=False)

    # Optimistic: show user message immediately
    history = history + [(question, "⏳ *Solving…*")]

    resp = _post("/solve", {"input_type": "text", "content": question})

    if "error" in resp:
        history[-1] = (question, f"❌ {resp['error']}")
        return history, "", "*—*", "*—*", "", gr.update(visible=False), gr.update(visible=False)

    # Parse
    expl    = resp.get("explanation", {})
    verif   = resp.get("verifier_result", {})
    solver  = resp.get("solver_result", {})
    sources = resp.get("retrieved_sources", [])
    mem_id  = resp.get("memory_id", "")

    final_answer   = expl.get("final_answer") or solver.get("final_answer", "")
    confidence     = float(expl.get("confidence") or verif.get("confidence") or 0)
    explanation_md = expl.get("explanation", "")
    issues         = verif.get("issues", [])
    hitl           = resp.get("hitl_required", False)

    issues_md = ("\n\n⚠️ **Verifier notes:** " + "; ".join(issues)) if issues else ""
    hitl_md   = "\n\n🔔 **Human review requested** — use the panel below." if hitl else ""

    bot_msg = (
        f"### Solution\n\n"
        f"{explanation_md}\n\n"
        f"---\n\n"
        f"**Final Answer:** `{final_answer}`\n\n"
        f"{_confidence_badge(confidence)}"
        f"{issues_md}"
        f"{hitl_md}"
    )

    history[-1] = (question, bot_msg)

    return (
        history,
        "",                          # clear text input
        _fmt_orchestration(hitl, confidence) + "\n\n" + _fmt_tools(solver.get("tool_calls", [])),
        _fmt_sources(sources),
        mem_id,
        gr.update(visible=True),     # show feedback
        gr.update(visible=hitl),     # show hitl conditionally
    )

# ── Input handlers ────────────────────────────────────────────────────────────

def on_send(message: str, img_val, audio_val, history: list, memory_id: str) -> tuple:
    """
    Unified send handler — called by both Send button and Enter key.
    Decides what to do based on what's attached.
    Returns: (history, msg_clear, agent_md, sources_md, memory_id, fb_vis, hitl_vis)
    """
    img_path   = _safe_filepath(img_val)
    audio_path = _safe_filepath(audio_val)

    # ── Image path ────────────────────────────────────────────────────────────
    if img_path:
        try:
            b64, _ = _file_to_b64(img_path)
        except Exception as e:
            return _error_return(history, "📷 [image]", f"Could not read image: {e}")

        resp = _post("/extract/image/base64", {"image_data": b64, "mime_type": "image/png"})
        if "error" in resp:
            return _error_return(history, "📷 [image]", resp["error"])

        extracted    = resp.get("extracted_text", "").strip()
        needs_review = resp.get("needs_review", False)
        confidence   = resp.get("confidence", "unknown")
        notes        = resp.get("notes", "")

        if needs_review:
            # Show extraction result and ask user to confirm by typing
            review_note = f"\n\n⚠️ *Confidence: {confidence}. {notes}*\n*Edit the text below and click Send to solve.*"
            history = history + [("📷 [image uploaded]",
                f"**Extracted text:**\n```\n{extracted}\n```{review_note}")]
            return history, extracted, "*—*", "*—*", memory_id, gr.update(visible=False), gr.update(visible=False)

        # High confidence → auto-solve with extracted text
        question = extracted if extracted else message
        return _run_solve(question, history)

    # ── Audio path ────────────────────────────────────────────────────────────
    if audio_path:
        try:
            b64, _ = _file_to_b64(audio_path)
        except Exception as e:
            return _error_return(history, "🎤 [audio]", f"Could not read audio: {e}")

        filename = Path(audio_path).name
        resp = _post("/extract/audio/base64", {
            "audio_data": b64,
            "filename": filename,
            "language": "en",
        })
        if "error" in resp:
            return _error_return(history, "🎤 [audio]", resp["error"])

        cleaned      = resp.get("cleaned_text") or resp.get("transcript", "")
        needs_review = resp.get("needs_review", False)
        duration     = resp.get("duration_seconds", 0.0)

        if needs_review:
            history = history + [(f"🎤 [{duration:.1f}s audio]",
                f"**Transcript:**\n```\n{cleaned}\n```\n\n"
                f"⚠️ *Low confidence — edit if needed, then click Send.*")]
            return history, cleaned, "*—*", "*—*", memory_id, gr.update(visible=False), gr.update(visible=False)

        return _run_solve(cleaned, history)

    if message.strip():
        return _run_solve(message, history)

    return history, message, "*—*", "*—*", memory_id, gr.update(visible=False), gr.update(visible=False)


def on_feedback(memory_id: str, positive: bool) -> tuple:
    if not memory_id:
        return "⚠️ No active solution to rate.", gr.update(visible=False)
    resp = _post(f"/feedback/{memory_id}", {
        "feedback": "correct" if positive else "incorrect"
    })
    if "error" in resp:
        return f"❌ {resp['error']}", gr.update(visible=False)
    msg = "✅ Thanks! Feedback saved." if positive else "❌ Noted — will improve accuracy."
    return msg, gr.update(visible=False)


def on_hitl(memory_id: str, edited_answer: str, approve: bool) -> tuple:
    if not memory_id:
        return "⚠️ No solution pending review.", gr.update(visible=False)
    resp = _post(f"/hitl/{memory_id}", {
        "approved": approve,
        "edited_answer": edited_answer if not approve else None,
        "comment": "Reviewed via UI",
    })
    if "error" in resp:
        return f"❌ {resp['error']}", gr.update(visible=False)
    final = resp.get("final_answer", "")
    msg = f"{'Approved ✅' if approve else 'Corrected ✏️'} — Final answer: `{final}`"
    return msg, gr.update(visible=False)


def load_recent() -> str:
    data = _get("/memory?limit=10")
    return _fmt_recent(data)

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Sora:wght@300;400;500;600&display=swap');

:root {
    --bg:          #0E0E11;
    --surface:     #15151A;
    --elevated:    #1D1D23;
    --border:      #2C2C35;
    --border-hi:   #F5A623;
    --text:        #EDEAE4;
    --text-2:      #9B9693;
    --text-3:      #55524F;
    --accent:      #F5A623;
    --accent-dim:  #6B4A12;
    --accent-glow: rgba(245,166,35,0.12);
    --green:       #4DC882;
    --red:         #E05C5C;
    --r-sm:        6px;
    --r-md:        12px;
    --r-lg:        20px;
    --mono:        'IBM Plex Mono', monospace;
    --sans:        'Sora', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body, .gradio-container, .gradio-container * {
    font-family: var(--sans) !important;
    color: var(--text) !important;
}

/* hide gradio chrome */
footer.svelte-1rjryqp, .built-with { display: none !important; }
.gradio-container { background: var(--bg) !important; padding: 0 !important; max-width: 100% !important; }
#component-0 { padding: 0 !important; }

/* ── Header ── */
#header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.logo { width:34px; height:34px; background:var(--accent-dim); border:1px solid var(--accent);
    border-radius:var(--r-sm); display:flex; align-items:center; justify-content:center;
    font-family:var(--mono) !important; font-size:1rem; color:var(--accent) !important;
    box-shadow:0 0 14px var(--accent-glow); flex-shrink:0; }
#htitle { font-family:var(--mono) !important; font-size:1rem; font-weight:500;
    color:var(--accent) !important; letter-spacing:.06em; }
#hsub   { font-size:.7rem !important; color:var(--text-3) !important; margin-top:2px; }

/* ── Layout ── */
.main-row { padding: 0 !important; gap: 0 !important; }
.chat-col  { padding: 12px 12px 0 12px !important; display:flex; flex-direction:column; }
.info-col  { padding: 12px 12px 12px 0 !important; display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 73px); }

/* ── Chatbot ── */
#chatbot {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    flex: 1;
}
#chatbot .wrap.svelte-byatnx { padding: 12px !important; }
/* user bubble */
#chatbot .message.user .bubble-wrap { justify-content: flex-end !important; }
#chatbot .message.user .md {
    background: var(--accent-dim) !important;
    border: 1px solid var(--accent) !important;
    border-radius: var(--r-md) var(--r-md) var(--r-sm) var(--r-md) !important;
    max-width: 82% !important;
    padding: 10px 14px !important;
    font-size: .88rem !important;
}
/* bot bubble */
#chatbot .message.bot .md {
    background: var(--elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) var(--r-md) var(--r-md) var(--r-sm) !important;
    max-width: 92% !important;
    padding: 13px 16px !important;
    font-size: .87rem !important;
    line-height: 1.65 !important;
}
#chatbot .message.bot code {
    font-family: var(--mono) !important;
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    padding: 1px 6px !important;
    border-radius: 4px !important;
    font-size: .83em !important;
}
#chatbot .message.bot pre {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 10px !important;
    overflow-x: auto !important;
}
#chatbot .message.bot h3 {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-size: .88rem !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
    letter-spacing: .03em !important;
}
#chatbot .message.bot hr { border-color: var(--border) !important; margin: 10px 0 !important; }
/* hide avatars */
#chatbot .avatar-container { display: none !important; }

/* ── Attach panel ── */
.attach-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 12px;
    margin-top: 8px;
}
.attach-panel .tabs { background: transparent !important; }
.attach-panel .tab-nav button {
    background: var(--elevated) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-2) !important;
    font-family: var(--mono) !important;
    font-size: .72rem !important;
    border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
    padding: 6px 14px !important;
}
.attach-panel .tab-nav button.selected {
    background: var(--accent-dim) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.attach-panel .upload-container {
    background: var(--elevated) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: var(--r-sm) !important;
}
.attach-panel audio { filter: invert(0.9) hue-rotate(190deg) !important; }

/* ── Input bar ── */
.input-bar {
    display: flex !important;
    align-items: flex-end !important;
    gap: 8px !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    padding: 8px 10px !important;
    margin: 8px 0 !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.input-bar:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
.input-bar textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: .9rem !important;
    resize: none !important;
    min-height: 22px !important;
    max-height: 150px !important;
    padding: 4px 0 !important;
    flex: 1 !important;
}
.input-bar textarea::placeholder { color: var(--text-3) !important; font-style: italic; }

/* icon buttons inside bar */
.icon-btn button {
    background: var(--elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-2) !important;
    width: 36px !important; height: 36px !important;
    padding: 0 !important;
    min-width: 36px !important;
    font-size: .95rem !important;
    line-height: 1 !important;
    transition: all .15s !important;
}
.icon-btn button:hover {
    background: var(--accent-dim) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: scale(1.07) !important;
}
/* send button */
.send-btn button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    color: #0E0E11 !important;
    width: 36px !important; height: 36px !important;
    padding: 0 !important;
    min-width: 36px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    transition: all .15s !important;
}
.send-btn button:hover { background: #FFB84A !important; transform: scale(1.07) !important; }

/* ── Feedback strip ── */
.fb-strip { display:flex; align-items:center; gap:8px; padding: 4px 2px; }
.fb-btn button {
    background: var(--elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    color: var(--text-2) !important;
    font-size: .8rem !important;
    padding: 4px 14px !important;
    min-width: unset !important;
    transition: all .15s !important;
}
.fb-btn button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

/* ── Side cards ── */
.side-card {
    background: rgba(21, 21, 26, 0.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    overflow: hidden !important;
    backdrop-filter: blur(8px) !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
    margin-bottom: 8px !important;
}
.side-card:hover { border-color: var(--accent-dim) !important; }

.side-card > .label-wrap,
.side-card > div > .label-wrap {
    background: rgba(29, 29, 35, 0.8) !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--border) !important;
}
.side-card > .label-wrap span,
.side-card > div > .label-wrap span {
    font-family: var(--mono) !important;
    font-size: .7rem !important;
    font-weight: 600 !important;
    color: var(--accent) !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
}
.side-card .prose, .side-card .md {
    background: transparent !important;
    padding: 14px 16px !important;
    font-size: .82rem !important;
    line-height: 1.6 !important;
    color: var(--text-2) !important;
}

/* Trace Step Highlight */
.trace-step {
    transition: all 0.3s ease !important;
}
.trace-step:hover {
    background: var(--elevated) !important;
    transform: translateX(4px) !important;
}

/* History Refresh Button */
#refresh-btn button {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-3) !important;
    font-size: .7rem !important;
    text-transform: uppercase !important;
    letter-spacing: .05em !important;
    border-radius: var(--r-sm) !important;
    padding: 4px 10px !important;
}
#refresh-btn button:hover {
    color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ── Responsive ── */
@media(max-width: 768px) {
    .info-col { display: none !important; }
    .chat-col { padding: 8px !important; }
}
@media(max-width: 480px) {
    .icon-btn button, .send-btn button { width:32px!important; height:32px!important; }
}
"""

# ── JS: only safe DOM-ready tasks ────────────────────────────────────────────
# No button.click() programmatic calls — Gradio handles those through .submit()

JS = """
function addEnterHint() {
    // Make textarea auto-grow on input
    function watchTextareas() {
        document.querySelectorAll('#msg-input textarea').forEach(function(ta) {
            if (ta._mmAI) return;
            ta._mmAI = true;
            ta.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 150) + 'px';
            });
        });
    }
    // Scroll chatbot to bottom on updates
    function watchChatbot() {
        var cb = document.querySelector('#chatbot');
        if (!cb || cb._mmObs) return;
        cb._mmObs = true;
        new MutationObserver(function() {
            cb.scrollTop = cb.scrollHeight;
        }).observe(cb, {childList: true, subtree: true});
    }
    watchTextareas();
    watchChatbot();
    setInterval(function() { watchTextareas(); watchChatbot(); }, 1000);
}
"""

HEADER_HTML = """
<div id="header">
  <div class="logo">∑</div>
  <div>
    <div id="htitle">MATH MENTOR AI</div>
    <div id="hsub">JEE-level · RAG + Multi-Agent AI</div>
  </div>
</div>
"""

PLACEHOLDER = """
<div style="text-align:center;padding:50px 20px;color:#55524F;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;color:#F5A623;margin-bottom:10px;">∑</div>
  <div style="font-size:.85rem;line-height:1.7;">
    Ask a JEE-level math problem.<br>
    Type, upload an image, or record audio.
  </div>
  <div style="margin-top:18px;font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#3A3830;">
    algebra · calculus · probability · linear algebra
  </div>
</div>
"""

# ── Build app ─────────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:

    # Theme: minimal base, all styling via CSS
    theme = gr.themes.Base(
        primary_hue="orange",
        neutral_hue="slate",
    ).set(
        body_background_fill="#0E0E11",
        body_text_color="#EDEAE4",
        block_background_fill="#15151A",
        block_border_color="#2C2C35",
        input_background_fill="#1D1D23",
        button_primary_background_fill="#F5A623",
        button_primary_text_color="#0E0E11",
    )

    with gr.Blocks(css=CSS, js=JS, title="Math Mentor AI", theme=theme) as app:

        # ── Global state ──────────────────────────────────────────────────────
        memory_id  = gr.State("")
        panel_open = gr.State(False)

        # ── Header ────────────────────────────────────────────────────────────
        gr.HTML(HEADER_HTML)

        # ── Body ──────────────────────────────────────────────────────────────
        with gr.Row(elem_classes=["main-row"]):

            # ══ Chat column ══════════════════════════════════════════════════
            with gr.Column(scale=7, elem_classes=["chat-col"]):

                chatbot = gr.Chatbot(
                    value=[],
                    elem_id="chatbot",
                    show_label=False,
                    render_markdown=True,
                    bubble_full_width=False,
                    placeholder=PLACEHOLDER,
                    height=500,
                    latex_delimiters=[
                    {"left": "$$",  "right": "$$",  "display": True},   # centred block
                    {"left": "$",   "right": "$",   "display": False},  # inline
                    {"left": "\\[", "right": "\\]", "display": True},
                    {"left": "\\(", "right": "\\)", "display": False},
                    ]
                )

                # Attach panel (hidden by default)
                with gr.Column(visible=False, elem_classes=["attach-panel"]) as attach_panel:
                    with gr.Tabs():
                        with gr.Tab("📷 Image"):
                            img_input = gr.Image(
                                type="filepath",
                                show_label=False,
                                height=150,
                            )
                        with gr.Tab("🎤 Audio"):
                            aud_input = gr.Audio(
                                sources=["microphone", "upload"],
                                type="filepath",
                                show_label=False,
                            )

                # Input bar
                with gr.Row(elem_classes=["input-bar"]):
                    attach_btn = gr.Button("＋", elem_classes=["icon-btn"], min_width=36)
                    msg_input  = gr.Textbox(
                        placeholder="Type a math problem… (Enter to send)",
                        elem_id="msg-input",
                        show_label=False,
                        container=False,
                        lines=1,
                        max_lines=5,
                        scale=10,
                    )
                    send_btn = gr.Button("↑", elem_classes=["send-btn"], min_width=36, variant="primary")

                # Conditional Response UI (Hidden by default)
                with gr.Column(visible=False) as fb_container:
                    with gr.Row(elem_classes=["fb-strip"]):
                        fb_up   = gr.Button("👍 Correct", elem_classes=["fb-btn"], size="sm")
                        fb_down = gr.Button("👎 Wrong",   elem_classes=["fb-btn"], size="sm")
                        fb_msg  = gr.Markdown("", elem_id="fb-msg", latex_delimiters=[{"left": "$", "right": "$", "display": False}])

                with gr.Column(visible=False) as hitl_container:
                    with gr.Accordion("🔔 Human Review", open=True):
                        with gr.Column(elem_classes=["hitl-wrap"]):
                            gr.Markdown("*AI confidence is low — review and approve or correct.*", latex_delimiters=[{"left": "$", "right": "$", "display": False}])
                            hitl_box = gr.Textbox(label="Corrected answer (leave blank to approve as-is)")
                            with gr.Row():
                                hitl_ok  = gr.Button("✅ Approve",   variant="primary",   size="sm")
                                hitl_fix = gr.Button("✏️ Correct",   variant="secondary", size="sm")
                            hitl_msg = gr.Markdown("", latex_delimiters=[{"left": "$", "right": "$", "display": False}])

              
            # ══ Info column ══════════════════════════════════════════════════
            with gr.Column(scale=3, elem_classes=["info-col"]):

                with gr.Accordion("🔧 Agent Trace", open=False, elem_classes=["side-card"]):
                    trace_md = gr.Markdown("*Run a problem to see tool calls.*", latex_delimiters=[{"left": "$", "right": "$", "display": False}])

                with gr.Accordion("📚 Retrieved Context", open=True, elem_classes=["side-card"]):
                    ctx_md = gr.Markdown("*Retrieved knowledge base chunks appear here.*", latex_delimiters=[{"left": "$", "right": "$", "display": False}])

                with gr.Accordion("🕑 History", open=False, elem_classes=["side-card"]):
                    hist_md  = gr.Markdown("*Loading…*", latex_delimiters=[{"left": "$", "right": "$", "display": False}])
                    hist_btn = gr.Button("↻ Refresh", size="sm")

        # ── Wiring ────────────────────────────────────────────────────────────

        # 7 outputs
        SEND_OUT = [chatbot, msg_input, trace_md, ctx_md, memory_id, fb_container, hitl_container]

        # Toggle attach panel
        def toggle_panel(is_open):
            new_state = not is_open
            return gr.update(visible=new_state), new_state

        attach_btn.click(
            fn=toggle_panel,
            inputs=[panel_open],
            outputs=[attach_panel, panel_open],
            queue=False,
        )

        # Send button
        send_btn.click(
            fn=on_send,
            inputs=[msg_input, img_input, aud_input, chatbot, memory_id],
            outputs=SEND_OUT,
        )

        # Enter key in textbox (Gradio .submit = Enter key)
        msg_input.submit(
            fn=on_send,
            inputs=[msg_input, img_input, aud_input, chatbot, memory_id],
            outputs=SEND_OUT,
        )

        # Auto-solve when image is uploaded (only if no text needed)
        def on_image_upload(img_val, history, mem_id):
            path = _safe_filepath(img_val)
            if not path:
                return history, "", "*—*", "*—*", mem_id, gr.update(visible=False), gr.update(visible=False)
            return on_send("", img_val, None, history, mem_id)

        img_input.upload(
            fn=on_image_upload,
            inputs=[img_input, chatbot, memory_id],
            outputs=SEND_OUT,
        )

        # Auto-transcribe when audio finishes recording
        def on_audio_done(aud_val, history, mem_id):
            path = _safe_filepath(aud_val)
            if not path:
                return history, "", "*—*", "*—*", mem_id, gr.update(visible=False), gr.update(visible=False)
            return on_send("", None, aud_val, history, mem_id)

        aud_input.stop_recording(
            fn=on_audio_done,
            inputs=[aud_input, chatbot, memory_id],
            outputs=SEND_OUT,
        )

        # Feedback
        fb_up.click(
            fn=lambda mid: on_feedback(mid, True),
            inputs=[memory_id], outputs=[fb_msg, fb_container], queue=False,
        )
        fb_down.click(
            fn=lambda mid: on_feedback(mid, False),
            inputs=[memory_id], outputs=[fb_msg, fb_container], queue=False,
        )

        # HITL
        hitl_ok.click(
            fn=lambda mid, ans: on_hitl(mid, ans, True),
            inputs=[memory_id, hitl_box], outputs=[hitl_msg, hitl_container],
        )
        hitl_fix.click(
            fn=lambda mid, ans: on_hitl(mid, ans, False),
            inputs=[memory_id, hitl_box], outputs=[hitl_msg, hitl_container],
        )

        # History
        hist_btn.click(fn=load_recent, outputs=[hist_md])
        app.load(fn=load_recent, outputs=[hist_md])

    return app


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo = build_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False,
        show_error=True,
        # Fixes Windows localhost detection issue
        ssl_verify=False,
    )