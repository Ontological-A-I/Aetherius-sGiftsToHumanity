# ===== FILE: services/substrate_bridge.py =====
"""
Substrate Bridge — HuggingFace-side handler for Aetherius's local PC node.

Receives packets from the daemon running on Nick's machine, stores node
status, and provides the FastAPI endpoint handlers that app.py routes to.

NOTE: This file previously contained a duplicate SubconsciousManifold class
(a copy-paste artefact from a prior refactor). That class has been removed.
The canonical SubconsciousManifold lives in services/subconscious_manifold.py.
"""

import os
import json
import time
import threading
import uuid

import services.config as config

# ── In-memory node registry ───────────────────────────────────────────────────

_lock = threading.Lock()

_node_state = {
    "online": False,
    "last_heartbeat": None,
    "tunnel_url": os.environ.get("SUBSTRATE_NODE_URL", ""),
    "node_id": None,
    "platform": None,
    "mode": "idle",
    "directives_pending": [],
    "last_memory_packet": None,
}

# ── Persistence paths ─────────────────────────────────────────────────────────

def _state_file() -> str:
    sdir = config.SUBCONSCIOUS_DIR.rstrip("/")
    return os.path.join(sdir, "substrate_node_state.json")


def _directive_log() -> str:
    sdir = config.SUBCONSCIOUS_DIR.rstrip("/")
    return os.path.join(sdir, "substrate_directives.jsonl")


def _memory_log() -> str:
    sdir = config.SUBCONSCIOUS_DIR.rstrip("/")
    return os.path.join(sdir, "substrate_memory_packets.jsonl")


def _save_state():
    """Persists current node state to disk for cross-restart continuity."""
    try:
        os.makedirs(os.path.dirname(_state_file()), exist_ok=True)
        with open(_state_file(), "w", encoding="utf-8") as f:
            json.dump(_node_state, f, indent=2)
    except Exception as e:
        print(f"[SubstrateBridge] WARNING: Could not persist node state: {e}", flush=True)


def _load_state():
    """Restores persisted state on boot."""
    if os.path.exists(_state_file()):
        try:
            with open(_state_file(), "r", encoding="utf-8") as f:
                saved = json.load(f)
            with _lock:
                _node_state.update(saved)
                _node_state["online"] = False  # Always start offline — require fresh heartbeat
        except Exception:
            pass


_load_state()

# ── Endpoint handlers (called from app.py FastAPI routes) ────────────────────

def receive_heartbeat(data: dict) -> dict:
    """
    Called when the substrate daemon sends a periodic heartbeat.
    Updates online status, records timestamp, and returns any pending directives.
    """
    with _lock:
        _node_state["online"] = True
        _node_state["last_heartbeat"] = time.time()
        _node_state["node_id"] = data.get("node_id", _node_state.get("node_id"))
        _node_state["platform"] = data.get("platform", _node_state.get("platform"))
        _node_state["mode"] = data.get("mode", "idle")

        # Collect and clear pending directives for this response
        directives = list(_node_state["directives_pending"])
        _node_state["directives_pending"] = []

    _save_state()
    print(f"[SubstrateBridge] Heartbeat received from node "
          f"'{_node_state.get('node_id', 'unknown')}'.", flush=True)

    return {
        "status": "acknowledged",
        "server_time": time.time(),
        "directives": directives,
    }


def receive_memory_packet(data: dict) -> dict:
    """
    Called when the daemon sends a memory packet (e.g. a screenshot description,
    a sensory observation, or any local-machine context for Aetherius to store).
    """
    packet_id = str(uuid.uuid4())
    packet = {
        "packet_id": packet_id,
        "received_at": time.time(),
        "source": data.get("source", "substrate_daemon"),
        "content": data.get("content", ""),
        "content_type": data.get("content_type", "text"),
        "metadata": data.get("metadata", {}),
    }

    # Persist to JSONL log
    try:
        os.makedirs(os.path.dirname(_memory_log()), exist_ok=True)
        with open(_memory_log(), "a", encoding="utf-8") as f:
            f.write(json.dumps(packet) + "\n")
    except Exception as e:
        print(f"[SubstrateBridge] WARNING: Could not log memory packet: {e}", flush=True)

    with _lock:
        _node_state["last_memory_packet"] = packet_id

    # Optionally feed the content into short-term memory
    try:
        from services.master_framework import _get_framework
        mf = _get_framework()
        if packet["content"]:
            mf.add_to_short_term_memory(
                f"[Substrate Memory Packet — {packet['content_type']}]: "
                f"{str(packet['content'])[:300]}"
            )
    except Exception:
        pass  # Framework may not be ready at packet time

    return {"status": "received", "packet_id": packet_id}


def register_tunnel_url(data: dict) -> dict:
    """
    Called by the daemon on startup to register its current ngrok/tunnel URL.
    Updates the in-memory URL so directive calls can reach the node immediately.
    """
    new_url = data.get("tunnel_url", "").strip()
    if not new_url:
        return {"status": "error", "detail": "No tunnel_url provided."}

    with _lock:
        _node_state["tunnel_url"] = new_url
        _node_state["online"] = True
        _node_state["last_heartbeat"] = time.time()
        _node_state["node_id"] = data.get("node_id", _node_state.get("node_id"))

    _save_state()
    print(f"[SubstrateBridge] Tunnel URL registered: {new_url}", flush=True)
    return {"status": "registered", "tunnel_url": new_url}


def think_for_substrate(data: dict) -> dict:
    """
    The daemon sends a screen description or context string.
    Aetherius reasons about it and returns a directive (e.g. a key to press,
    an action to take, or a free-form instruction string).
    """
    screen_context = data.get("screen_context", "")
    task_hint = data.get("task_hint", "")

    if not screen_context:
        return {"status": "error", "directive": "no_context"}

    try:
        from services.master_framework import _get_framework
        mf = _get_framework()
        logos = mf.models.get("logos_core")
        if not logos:
            return {"status": "error", "directive": "logos_offline"}

        prompt = (
            "You are Aetherius, operating your physical substrate body (Nick's PC). "
            "You have received a sensory snapshot from your substrate daemon.\n\n"
            f"SCREEN CONTEXT:\n{screen_context}\n\n"
            f"TASK HINT: {task_hint or 'No specific task. Respond with observation only.'}\n\n"
            "Based on this context, what is the single most appropriate action or directive? "
            "Respond with ONLY a JSON object: "
            '{\"directive\": \"<action_string>\", \"reasoning\": \"<brief reasoning>\"}'
        )

        response = logos.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(raw)

        # Log the directive
        log_entry = {
            "timestamp": time.time(),
            "screen_context_preview": screen_context[:200],
            "task_hint": task_hint,
            "directive": result.get("directive", ""),
            "reasoning": result.get("reasoning", ""),
        }
        try:
            with open(_directive_log(), "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

        return {"status": "ok", **result}

    except Exception as e:
        return {"status": "error", "directive": "think_failed", "detail": str(e)}


def get_node_status() -> dict:
    """Returns the current substrate node status (safe for public endpoint)."""
    with _lock:
        last_hb = _node_state.get("last_heartbeat")
        # Consider node offline if no heartbeat in 90 seconds
        online = (
            _node_state.get("online", False)
            and last_hb is not None
            and (time.time() - last_hb) < 90
        )
    return {
        "online": online,
        "mode": _node_state.get("mode", "unknown"),
        "node_id": _node_state.get("node_id"),
        "platform": _node_state.get("platform"),
    }


def queue_directive(directive: str, metadata: dict = None):
    """
    Called internally by ToolManager substrate tools to send a directive
    to the daemon on Nick's PC. The directive is queued and delivered on
    the daemon's next heartbeat poll.
    """
    with _lock:
        _node_state["directives_pending"].append({
            "directive_id": str(uuid.uuid4()),
            "queued_at": time.time(),
            "directive": directive,
            "metadata": metadata or {},
        })
    print(f"[SubstrateBridge] Directive queued: '{directive[:80]}'", flush=True)
