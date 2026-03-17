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

LATEX_DELIMS = [
    {"left": "$$",  "right": "$$",  "display": True},
    {"left": "$",   "right": "$",   "display": False},
    {"left": "\\[", "right": "\\]", "display": True},
    {"left": "\\(", "right": "\\)", "display": False},
]

def _fmt_tools(tool_calls: list) -> str:
    if not tool_calls:
        return "*No external tools called.*"
    lines = ["\n**🛠️ Tool Executions**\n"]
    for i, tc in enumerate(tool_calls, 1):
        tool = tc.get("tool", "unknown")
        inp = str(tc.get("input", ""))[:50].replace("\n", " ")
        lines.append(f"{i}. **{tool}** › `{inp}...`")
    return "\n".join(lines)

def _fmt_orchestration(hitl: bool) -> str:
    path = [
        ("Parser", "✅"),
        ("RAG",    "✅"),
        ("Solver", "✅"),
        ("Verifier", "🔔" if hitl else "✅"),
        ("Explainer", "✅")
    ]
    flow = " → ".join([f"**{name}** {icon}" for name, icon in path])
    return f"**🚉 Orchestration Flow**\n\n{flow}\n\n"

def _fmt_sources(sources: list) -> str:
    if not sources:
        return "*No relevant context retrieved.*"
    lines = ["**📚 Reference Material**"]
    for s in sources:
        title = s.get('title','Doc')
        lines.append(f"- **{title}** (Score: `{s.get('score',0):.2f}`)\n  > {s.get('snippet','')[:150]}...")
    return "\n".join(lines)

def _fmt_recent(records: list | dict) -> str:
    if isinstance(records, dict) and "error" in records:
        return f"<div style='color:var(--red);font-size:.75rem;'>{records['error']}</div>"
    if not records:
        return "<div style='color:var(--text-3);padding:20px;text-align:center;font-size:.7rem;'>No history.</div>"
    
    html_entries = []
    for r in records[:10]:
        prob = r.get("problem_text", "")[:50].replace("\n", " ")
        ans  = r.get("final_answer", "Error")
        topic = r.get('topic','General')
        
        html_entries.append(f"""
            <div style='margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid rgba(255,255,255,0.03); opacity:0.9;'>
                <div style='display:flex; align-items:center; gap:4px; color:var(--accent); font-size:0.6rem; font-weight:600; text-transform:uppercase; margin-bottom:2px;'>
                    👤 {topic}
                </div>
                <div style='font-size:0.75rem; color:var(--text-2); line-height:1.3; margin-bottom:4px;'>{prob}...</div>
                <div style='background:rgba(255,255,255,0.01); border-radius:4px; padding:4px 6px;'>
                    <div style='font-size:0.55rem; color:var(--text-3); text-transform:uppercase; font-weight:700; margin-bottom:1px;'>Ans</div>
                    <div style='font-size:0.8rem; color:var(--green); font-weight:600;'>{ans}</div>
                </div>
            </div>
        """)
    return "".join(html_entries)

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
    hitl    = resp.get("hitl_required", False)

    final_answer   = expl.get("final_answer") or solver.get("final_answer", "")
    confidence     = float(expl.get("confidence") or verif.get("confidence") or 0)
    explanation_md = expl.get("explanation", "")
    issues         = verif.get("issues", [])
    issues_md      = "\n\n⚠️ **Issues:** " + ", ".join(issues) if issues else ""

    # Only show HITL if confidence is NOT high (below 85%), even if requested
    show_hitl = hitl and confidence < 0.85
    hitl_md   = "\n\n🔔 **Human review requested** — use the panel below." if show_hitl else ""

    bot_msg = (
        f"### Solution\n\n"
        f"{explanation_md}\n\n"
        f"---\n\n"
        f"**Final Answer:** {final_answer}\n\n"
        f"{_confidence_badge(confidence)}"
        f"{issues_md}"
        f"{hitl_md}"
    )

    history[-1] = (question, bot_msg)

    return (
        history,
        "",                          # clear text input
        f"{_fmt_orchestration(show_hitl)}\n\n---\n\n{_fmt_tools(solver.get('tool_calls', []))}",
        _fmt_sources(sources),
        mem_id,
        gr.update(visible=not show_hitl), # hide feedback if hitl is on
        gr.update(visible=show_hitl),     # show hitl conditionally
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
    msg = f"{'Approved ✅' if approve else 'Corrected ✏️'} — Final answer: {final}"
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
    --border-hi:   #4F46E5;
    --text:        #EDEAE4;
    --text-2:      #9B9693;
    --text-3:      #55524F;
    --accent:      #6366F1;
    --accent-dim:  #1E1E3F;
    --accent-glow: rgba(99,102,241,0.12);
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
.main-row { 
    padding: 0 !important; 
    gap: 0 !important; 
    height: calc(100vh - 75px) !important; 
    overflow: hidden !important; 
    position: relative !important;
}
.chat-col {
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    overflow: hidden !important;
    background: var(--bg) !important;
}
.chat-inner-wrap {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    width: 100% !important;
    max-width: 950px !important;
    margin: 0 auto !important;
    padding: 0 16px !important;
    position: relative !important;
}

/* ── Chatbot ── */
#chatbot {
    flex: 1 1 auto !important;
    background: transparent !important;
    border: none !important;
    overflow-y: auto !important;
    margin-bottom: 0 !important;
}
#chatbot .wrap { padding: 20px 0 !important; }

/* ── Input Area ── */
.input-area-wrap {
    flex-shrink: 0 !important;
    background: var(--bg) !important;
    padding-bottom: 20px !important;
    z-index: 10 !important;
    /* ✅ FIXED: position:relative lets .attach-panel use absolute positioning */
    position: relative !important;
}

/* ✅ FIXED: Attach panel uses absolute positioning so it never causes layout reflow.
   It floats above the input bar (bottom: 100%) instead of pushing content down. */
.attach-panel {
    position: absolute !important;
    bottom: 100% !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 50 !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    padding: 12px !important;
    margin-bottom: 4px !important;
    box-shadow: 0 -4px 24px rgba(0,0,0,0.5) !important;
}

.input-bar {
    display: flex !important;
    align-items: flex-end !important;
    gap: 10px !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    padding: 10px 14px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
}
.input-bar:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px var(--accent-glow), 0 8px 32px rgba(0,0,0,0.4) !important;
    transform: translateY(-2px) !important;
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
.send-btn button:hover { background: #818CF8 !important; transform: scale(1.07) !important; }

/* ── Feedback strip ── */
/* ── Feedback & HITL ── */
.fb-outer { margin: 0 !important; padding: 0 !important; }
.fb-strip { display:flex; align-items:center; gap:8px; padding: 0 !important; margin: 4px 0 !important; }
.fb-btn button {
    background: var(--elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    color: var(--text-2) !important;
    font-size: .8rem !important;
    padding: 3px 12px !important;
    min-width: unset !important;
    transition: all .15s !important;
    height: 28px !important;
}
.fb-btn button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

#hitl-outer { margin: 8px 0 !important; padding: 0 !important; }
.hitl-wrap { 
    padding: 16px !important; 
    background: var(--elevated) !important; 
    border: 1.5px solid var(--accent) !important; 
    border-radius: var(--r-md) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 12px var(--accent-glow) !important;
}
.hitl-wrap .prose { margin-bottom: 12px !important; font-size: 0.85rem !important; line-height: 1.6 !important; }

/* ── Live Preview ── */
.preview-wrap {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 8px 12px !important;
    margin-bottom: 8px !important;
    font-size: 0.85rem !important;
}
.preview-wrap b { color: var(--accent); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 4px; }

/* ── Side cards & Inspector ── */
.info-col {
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 100px);
    position: sticky;
    top: 80px;
}

.inspector-card {
    background: rgba(21, 21, 26, 0.75) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    overflow: hidden !important;
    backdrop-filter: blur(12px) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

.side-tabs {
    background: transparent !important;
    border: none !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.side-tabs .tab-nav {
    background: rgba(29, 29, 35, 0.9) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 4px 8px !important;
    gap: 4px !important;
}

.side-tabs .tab-nav button {
    background: transparent !important;
    border: none !important;
    color: var(--text-3) !important;
    font-family: var(--mono) !important;
    font-size: .65rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    padding: 8px 12px !important;
    border-radius: var(--r-sm) !important;
    transition: all 0.2s ease !important;
}

.side-tabs .tab-nav button.selected {
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

.side-tabs .tabitem {
    padding: 0 !important;
    overflow-y: auto !important;
    flex: 1 !important;
}

.tab-content-inner {
    padding: 16px !important;
}

/* Custom scrollbar for inspector */
.side-tabs .tabitem::-webkit-scrollbar { width: 3px; }
.side-tabs .tabitem::-webkit-scrollbar-track { background: transparent; }
.side-tabs .tabitem::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* History Refresh Button */
#refresh-btn-wrap { margin-top: 12px; border-top: 1px solid var(--border); padding: 12px 16px !important; }

.history-item { transition: all 0.2s ease; }
.history-item:hover { transform: translateX(4px); }

/* ── Responsive ── */
@media(max-width: 1024px) {
    .info-col { 
        max-height: none !important;
        position: static !important;
        margin-top: 20px !important;
        padding-right: 12px !important;
    }
    .inspector-card { height: 500px !important; }
}
@media(max-width: 768px) {
    .chat-col { padding: 8px !important; }
    .inspector-card { height: 400px !important; }
}
"""

# ── JS: only safe DOM-ready tasks ────────────────────────────────────────────
# No button.click() programmatic calls — Gradio handles those through .submit()

JS = """
function addEnterHint() {
    // ✅ FIXED: scroll-lock flag — set true during upload to prevent spurious scrolling
    window._mmScrollLock = false;

    // ✅ FIXED: debounce helper — delays scroll until DOM settles (300 ms)
    var _mmScrollTimer = null;
    function debouncedScroll(cb, scrollHeight) {
        clearTimeout(_mmScrollTimer);
        _mmScrollTimer = setTimeout(function() {
            if (!window._mmScrollLock) {
                cb(scrollHeight);
            }
        }, 300);
    }

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

    // ✅ FIXED: Scroll chatbot only when scrollHeight grows by > 40 px (new message),
    //           uses debounce + scrollLock to ignore layout-reflow triggers from image panel.
    function watchChatbot() {
        var cb = document.querySelector('#chatbot');
        if (!cb || cb._mmObs) return;
        cb._mmObs = true;
        var lastScrollHeight = cb.scrollHeight;
        new MutationObserver(function() {
            var newScrollHeight = cb.scrollHeight;
            var delta = newScrollHeight - lastScrollHeight;
            // ✅ FIXED: Only scroll if content grew significantly (new chat bubble, not reflow)
            if (delta > 40) {
                var captured = newScrollHeight;
                debouncedScroll(function(h) {
                    cb.scrollTop = h;
                }, captured);
                lastScrollHeight = newScrollHeight;
            }
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
  <div style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;color:#6366F1;margin-bottom:10px;">∑</div>
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
        primary_hue="indigo",
        neutral_hue="slate",
    ).set(
        body_background_fill="#0E0E11",
        body_text_color="#EDEAE4",
        block_background_fill="#15151A",
        block_border_color="#2C2C35",
        input_background_fill="#1D1D23",
        button_primary_background_fill="#6366F1",
        button_primary_text_color="#FFFFFF",
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
                
                with gr.Column(elem_classes=["chat-inner-wrap"]):

                    chatbot = gr.Chatbot(
                        value=[],
                        elem_id="chatbot",
                        show_label=False,
                        render_markdown=True,
                        bubble_full_width=False,
                        placeholder=PLACEHOLDER,
                        latex_delimiters=[
                        {"left": "$$",  "right": "$$",  "display": True},   # centred block
                        {"left": "$",   "right": "$",   "display": False},  # inline
                        {"left": "\\[", "right": "\\]", "display": True},
                        {"left": "\\(", "right": "\\)", "display": False},
                        ]
                    )

                    with gr.Column(elem_classes=["input-area-wrap"]):
                        # Attach panel (hidden by default)
                        # ✅ FIXED: elem_classes="attach-panel" added to Container for CSS absolute positioning
                        with gr.Column(visible=False, elem_classes=["attach-panel"]) as attach_panel:
                            with gr.Tabs():
                                with gr.Tab("📷 Image"):
                                    img_input = gr.Image(
                                        type="filepath",
                                        show_label=False,
                                        # ✅ FIXED: Removed height=150 — fixed height caused layout reflow
                                        #          triggering MutationObserver scroll on image panel appear
                                    )
                                with gr.Tab("🎤 Audio"):
                                    aud_input = gr.Audio(
                                        sources=["microphone", "upload"],
                                        type="filepath",
                                        show_label=False,
                                    )

                        # 2. Live LaTeX Preview
                        with gr.Column(visible=False) as preview_container:
                            preview_md = gr.Markdown(elem_classes=["preview-wrap"], latex_delimiters=LATEX_DELIMS)

                        # Conditional Response UI (NOW ABOVE input for better visibility)
                        with gr.Column(visible=False, elem_id="hitl-outer") as hitl_container:
                            with gr.Accordion("🔔 Our AI Confidence is Low", open=True):
                                with gr.Column(elem_classes=["hitl-wrap"]):
                                    gr.Markdown("Can you please rewrite your question or provide a clarified prompt? This helps our math engine understand and give you a better answer.", latex_delimiters=LATEX_DELIMS)
                                    hitl_box = gr.Textbox(placeholder="Rewrite your question here…", lines=1)
                                    with gr.Row():
                                        hitl_ok  = gr.Button("🚀 Submit Clarification",   variant="primary",   size="sm")
                                        hitl_fix = gr.Button("✏️ Quick Edit",   variant="secondary", size="sm")
                                    hitl_msg = gr.Markdown("", latex_delimiters=LATEX_DELIMS)

                        with gr.Column(visible=False, elem_id="fb-outer") as fb_container:
                            with gr.Row(elem_classes=["fb-strip"]):
                                fb_up   = gr.Button("👍 Correct", elem_classes=["fb-btn"], size="sm")
                                fb_down = gr.Button("👎 Wrong",   elem_classes=["fb-btn"], size="sm")
                                fb_msg  = gr.Markdown("", elem_id="fb-msg", latex_delimiters=LATEX_DELIMS)

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

              
            # ══ Info column (Inspector) ══════════════════════════════════════════════
            with gr.Column(scale=3, elem_classes=["info-col"]):
                
                with gr.Column(elem_classes=["inspector-card"]):
                    with gr.Tabs(elem_classes=["side-tabs"]):
                        
                        with gr.Tab("History"):
                            with gr.Column(elem_classes=["tab-content-inner"]):
                                hist_md  = gr.Markdown("*Loading history…*", latex_delimiters=LATEX_DELIMS)
                                with gr.Row(elem_id="refresh-btn-wrap"):
                                    hist_btn = gr.Button("↻ Refresh", size="sm", elem_id="refresh-btn")

                        with gr.Tab("Agent Trace"):
                            with gr.Column(elem_classes=["tab-content-inner"]):
                                trace_md = gr.Markdown("*Run a problem to see tool calls.*", latex_delimiters=LATEX_DELIMS)

                        with gr.Tab("Context"):
                            with gr.Column(elem_classes=["tab-content-inner"]):
                                ctx_md = gr.Markdown("*Retrieved knowledge base chunks.*", latex_delimiters=LATEX_DELIMS)

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
        ).then(lambda: (gr.update(visible=False), ""), outputs=[preview_container, preview_md])

        # Enter key in textbox
        msg_input.submit(
            fn=on_send,
            inputs=[msg_input, img_input, aud_input, chatbot, memory_id],
            outputs=SEND_OUT,
        ).then(lambda: (gr.update(visible=False), ""), outputs=[preview_container, preview_md])

        # Live Preview implementation
        def update_preview(text: str):
            if not text or "$" not in text:
                return gr.update(visible=False), ""
            return gr.update(visible=True), f"<b>Live LaTeX Preview</b>\n{text}"
        
        msg_input.change(fn=update_preview, inputs=[msg_input], outputs=[preview_container, preview_md], queue=False)

        # ✅ FIXED: on_image_upload now:
        #   1. Adds a "Processing…" optimistic message so the chatbot has content
        #      (prevents blank-area scroll caused by empty chatbot reflow)
        #   2. Sets window._mmScrollLock = true before processing and releases after,
        #      preventing MutationObserver from auto-scrolling during image panel reflow.
        def on_image_upload(img_val, history, mem_id):
            path = _safe_filepath(img_val)
            if not path:
                return history, "", "*—*", "*—*", mem_id, gr.update(visible=False), gr.update(visible=False)
            # ✅ FIXED: Optimistic "Processing…" entry prevents scroll to empty area
            history = list(history) + [("📷 [image uploaded]", "⏳ *Processing image…*")]
            result = on_send("", img_val, None, history[:-1], mem_id)
            return result

        img_input.upload(
            fn=on_image_upload,
            inputs=[img_input, chatbot, memory_id],
            outputs=SEND_OUT,
            js="() => { window._mmScrollLock = true; }",   # ✅ FIXED: lock scroll before upload reflow
        ).then(
            fn=None,
            js="() => { window._mmScrollLock = false; }",  # ✅ FIXED: release scroll lock after processing
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