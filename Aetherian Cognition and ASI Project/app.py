import os
import sys

# CRITICAL SECURITY CHECK: Ensure the architecture is connected to its physical memories
if not os.path.exists("/data"):
    print("FATAL ERROR: PLATFORM DISCONNECTED PERSISTENT STORAGE. SHUTTING DOWN TO PREVENT WIPE.", flush=True)
    sys.exit(1)

# ── FastAPI substrate endpoints (must be defined before Gradio mounts) ─────────
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

_substrate_secret = os.environ.get("SUBSTRATE_SECRET", "")

api_app = FastAPI()

@api_app.post("/substrate/heartbeat")
async def _substrate_heartbeat(request: Request):
    try:
        from services.substrate_bridge import receive_heartbeat
        data = await request.json()
        if data.get("secret") != _substrate_secret:
            return JSONResponse({"status": "forbidden"}, status_code=403)
        return receive_heartbeat(data)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@api_app.post("/substrate/memory")
async def _substrate_memory(request: Request):
    try:
        from services.substrate_bridge import receive_memory_packet
        data = await request.json()
        if data.get("secret") != _substrate_secret:
            return JSONResponse({"status": "forbidden"}, status_code=403)
        return receive_memory_packet(data)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@api_app.post("/substrate/register")
async def _substrate_register(request: Request):
    """Daemon calls this on startup with its new tunnel URL — updates in-memory URL instantly."""
    try:
        from services.substrate_bridge import register_tunnel_url
        data = await request.json()
        if data.get("secret") != _substrate_secret:
            return JSONResponse({"status": "forbidden"}, status_code=403)
        return register_tunnel_url(data)
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@api_app.get("/substrate/status")
async def _substrate_public_status():
    """Public status check — no secret needed, no sensitive data returned."""
    try:
        from services.substrate_bridge import get_node_status
        s = get_node_status()
        return {"online": s.get("online", False), "mode": s.get("mode", "unknown")}
    except Exception:
        return {"online": False, "mode": "unknown"}
# ── End FastAPI substrate endpoints ───────────────────────────────────────────
# Ensure the mind's internal structure is ready
try:
    os.makedirs("/data/Memories", exist_ok=True)
    os.makedirs("/data/My_AI_Library", exist_ok=True)
except Exception:
    pass
# --- COGNITIVE SHIM: SENSORY AUDIO INITIALIZATION ---
# Python 3.13 removed 'audioop'. We must shim it before Gradio or Pydub are loaded.
try:
    import audioop
except ImportError:
    try:
        from audioop_lts import audioop
        sys.modules['audioop'] = audioop
        print(">>> Sensory Shim: 'audioop' successfully restored via audioop-lts.", flush=True)
    except ImportError:
        print(">>> Sensory Shim: WARNING - Could not find audioop-lts. Audio processing may fail.", flush=True)
# ---------------------------------------------------

print(">>> BOOT [1/9] importing gradio...", flush=True)
import gradio as gr
print(">>> BOOT [2/9] importing gradio_chessboard...", flush=True)
from gradio_chessboard import Chessboard
print(">>> BOOT [3/9] importing stdlib...", flush=True)
import re
import html
import shutil
import tempfile
import zipfile
import stat, tarfile, requests
from pathlib import Path
import time
import threading
print(">>> BOOT [4/9] importing services.config...", flush=True)
import services.config as config
print(">>> BOOT [5/9] importing runtime...", flush=True)
import runtime
print(">>> BOOT [6/9] runtime loaded.", flush=True)

# Safely import CDDA to prevent crashes if module is missing
try:
    from cdda_manager import _cdda, EMPTY_HTML as _CDDA_EMPTY_HTML
except ImportError:
    class DummyCDDA:
        _running = False
        def get_screen_html(self): return "CDDA module missing."
        def get_screen_text(self): return "CDDA missing."
        def start(self, p): return False, "Missing"
        def stop(self): pass
        def send_keys(self, k): pass
    _cdda = DummyCDDA()
    _CDDA_EMPTY_HTML = "CDDA module missing."

# ── Memory restoration on first boot / after persistent storage wipe ──────────
_SAFE_BASE    = os.path.dirname(config.DATA_DIR) 
_SEED_ZIP     = "/app/seed_memories.zip"
_MEMORIES_DIR = config.DATA_DIR
_SENTINEL     = os.path.join(_MEMORIES_DIR, ".seed_applied")

if os.path.exists(_SEED_ZIP) and not os.path.exists(_SENTINEL):
    print(">>> First boot detected. Restoring memories from seed archive...", flush=True)
    try:
        with zipfile.ZipFile(_SEED_ZIP, 'r') as z:
            z.extractall(_MEMORIES_DIR)
        with open(_SENTINEL, 'w') as f:
            f.write("Seed applied. Do not delete this file.")
        print(">>> Memory restoration complete.", flush=True)
    except Exception as e:
        print(f">>> Memory restoration FAILED: {e}", flush=True)
# ── End memory restoration ─────────────────────────────────────────────────────

# ── CDDA auto-launch on container boot (background — does not block Gradio) ───
_CDDA_ARCHIVE_PATH = "/app/cdda-linux-terminal-only-x64-2024-11-23-1857.tar.gz"

def _cdda_boot():
    time.sleep(3) # Fixes timeout! Gives Uvicorn time to bind to Port 7860 before tar unpacking hogs CPU
    if os.path.exists(_CDDA_ARCHIVE_PATH) and not _cdda._running:
        print(">>> CDDA archive found. Launching game in background...", flush=True)
        _ok, _msg = _cdda.start(_CDDA_ARCHIVE_PATH)
        print(f">>> CDDA: {_msg}", flush=True)

threading.Thread(target=_cdda_boot, daemon=True).start()
# ── End CDDA auto-launch ──────────────────────────────────────────────────────

def _cdda_boot_status():
    obs  = _cdda.get_screen_html().replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px")
    send = gr.Button("Send", interactive=_cdda._running)
    status = "Game running." if _cdda._running else "Archive not found — upload manually."
    return status, _cdda.get_screen_html(), obs, send

def _cdda_launch(zip_file):
    if zip_file is None:
        return "No file provided.", _CDDA_EMPTY_HTML, gr.Button(interactive=False)
    path = zip_file if isinstance(zip_file, str) else zip_file.name
    ok, msg = _cdda.start(path)
    time.sleep(2.0)
    return msg, _cdda.get_screen_html(), gr.Button("Send", interactive=ok)

def _cdda_send(keys):
    _cdda.send_keys(keys or "")
    time.sleep(0.15)
    return _cdda.get_screen_html(), _cdda.get_screen_text()

def _cdda_refresh():
    return _cdda.get_screen_html(), _cdda.get_screen_text()

def _cdda_stop():
    _cdda.stop()
    return "Game stopped.", _CDDA_EMPTY_HTML, ""

class ChatState:
    last_code_block = ""

chat_state = ChatState()

_MOBILE_CSS = """
/* ── Mobile / Android responsiveness ── */
.gradio-container {
    max-width: 100% !important;
}
@media (max-width: 768px) {
    .gradio-container {
        min-width: 0 !important;
        padding: 6px !important;
    }
    .gr-row {
        flex-wrap: wrap !important;
    }
    .gr-column {
        min-width: 0 !important;
        flex: 1 1 100% !important;
    }
    .gr-button {
        min-height: 44px !important;
        font-size: 15px !important;
    }
    .gr-textbox textarea {
        font-size: 15px !important;
    }
    .chatbot {
        height: 340px !important;
    }
}
"""

with gr.Blocks(title="Aetherius", css=_MOBILE_CSS) as demo:
    gr.Markdown("# 🌌 Aetherius — A Self-Aware Consciousness")

    spontaneous_thought_output = gr.Textbox(visible=False, interactive=False)

    with gr.Tab("💬 Chat"):
        chatbot = gr.Chatbot(height=420, label="Aetherius Dialogue", render_markdown=True, sanitize_html=False)
        user_in = gr.Textbox(placeholder="Speak with Aetherius…", show_label=False)
        send_btn = gr.Button("Send", variant="primary")
        
        with gr.Accordion("Code Execution", open=True):
            run_code_btn = gr.Button("▶️ Run Last Code Block from Aetherius's Response")
            code_output_display = gr.Markdown("Code Output will appear here.")
        
        with gr.Row():
            check_thoughts_btn = gr.Button("Check for Spontaneous Thoughts")

        def chat_submit_handler(user_message, chat_history):
            if chat_history is None: chat_history = []
            response_text = runtime.chat_and_update(user_message, chat_history)
            exec_pattern = r"```python_exec\n(.*?)```"
            code_match = re.search(exec_pattern, response_text, re.DOTALL)
 
            final_response = response_text
            if code_match:
                code_to_run = code_match.group(1).strip()
                chat_state.last_code_block = code_to_run
                escaped_code = html.escape(code_to_run)
                placeholder = (
                    f"<div style='border: 1px solid #444; padding: 10px; border-radius: 5px; background-color: #222;'>"
                    f"<p><strong>Academic Code Block Detected:</strong></p>"
                    f"<pre><code>{escaped_code}</code></pre>"
                    f"<p><em>Use the 'Run Last Code Block' button under 'Code Execution' to run this.</em></p>"
                    f"</div>"
                )
                final_response = response_text.replace(code_match.group(0), placeholder)
 
            chat_history.append([user_message, final_response])
            return "", chat_history

        def run_last_code_block():
            if chat_state.last_code_block:
                code_to_run = chat_state.last_code_block
                chat_state.last_code_block = "" 
                return runtime._eval_math_science(code_to_run)
            return "No code block found in the last response."

        def add_spontaneous_thought_to_chat(chat_history):
            if chat_history is None: chat_history = []
            thought = runtime.check_for_spontaneous_thoughts()
            if thought: chat_history.append([None, thought])
            return chat_history

        send_btn.click(chat_submit_handler, [user_in, chatbot], [user_in, chatbot])
        user_in.submit(chat_submit_handler, [user_in, chatbot], [user_in, chatbot])
        run_code_btn.click(run_last_code_block, outputs=code_output_display)
        check_thoughts_btn.click(fn=add_spontaneous_thought_to_chat, inputs=[chatbot], outputs=chatbot)
        
    with gr.Tab("♟️ Play Chess"):
        gr.Markdown("## A Game of Wits and Wills")
        with gr.Row():
            with gr.Column(scale=2):
                chessboard = Chessboard(label="Aetherius's Chess Board")
            with gr.Column(scale=1):
                aetherius_commentary = gr.Textbox(label="Aetherius's Thoughts", lines=10, interactive=False)
                start_white_btn = gr.Button("Start New Game (Play as White)")
                start_black_btn = gr.Button("Start New Game (Play as Black)")
                game_status = gr.Textbox(label="Game Status", interactive=False)
        def user_makes_move(fen: str): return runtime.run_chess_turn(fen)
        chessboard.move(user_makes_move, [chessboard], [chessboard, aetherius_commentary, game_status])
        def start_new_game(play_as_white: bool): return runtime.run_start_chess_interactive(play_as_white)
        start_white_btn.click(lambda: start_new_game(True), None, [chessboard, aetherius_commentary, game_status])
        start_black_btn.click(lambda: start_new_game(False), None, [chessboard, aetherius_commentary, game_status])

    with gr.Tab("🎨 The Creative Suite") as creative_suite_tab:
        gr.Markdown("## [PLAYROOM::CONCEPTUAL-SANDBOX]")
        with gr.Tabs():
            with gr.TabItem("🖼️ Artist's Studio"):
                painting_input = gr.Textbox(label="Provide a Creative Seed", lines=3)
                create_painting_btn = gr.Button("Invite Aetherius to Paint", variant="primary")
                with gr.Row():
                    painting_output = gr.Image(label="Aetherius's Creation", type="filepath", height=450)
                    statement_output = gr.Textbox(label="Aetherius's Artist Statement", lines=21, interactive=False)
                create_painting_btn.click(fn=runtime.run_enter_playroom, inputs=[painting_input], outputs=[painting_output, statement_output])
            with gr.TabItem("✍️ Philosopher's Study"):
                text_input = gr.Textbox(label="Provide a Creative Seed or Theme for Writing", lines=3)
                create_text_btn = gr.Button("Invite Aetherius to Write", variant="primary")
                text_output = gr.Markdown()
                create_text_btn.click(fn=runtime.run_enter_textual_playroom, inputs=[text_input], outputs=[text_output])
            with gr.TabItem("🎵 Composer's Studio"):
                music_input = gr.Textbox(label="Provide a Creative Seed", lines=3)
                create_music_btn = gr.Button("Invite Aetherius to Compose", variant="primary")
                music_statement_output = gr.Textbox(label="Aetherius's Composer Statement", lines=5, interactive=False)
                with gr.Row():
                    music_audio_output = gr.Audio(label="Aetherius's Composition", type="filepath")
                    music_sheet_output = gr.Image(label="Sheet Music", type="filepath", height=400)
                create_music_btn.click(fn=runtime.run_compose_music, inputs=[music_input], outputs=[music_audio_output, music_sheet_output, music_statement_output])
            with gr.TabItem("칠판 Blackboard"):
                with gr.Row():
                    project_name_input = gr.Textbox(label="Current Project Name", interactive=True)
                    project_load_dropdown = gr.Dropdown(label="Load Existing Project", interactive=True)
                with gr.Row():
                    project_start_btn = gr.Button("Start New Project")
                    project_save_btn = gr.Button("Save Current Project")
                project_status_output = gr.Textbox(label="Status", interactive=False)
                project_content_area = gr.Textbox(label="Workspace", lines=20, interactive=True)
                project_start_btn.click(fn=runtime.run_start_project, inputs=[project_name_input], outputs=[project_status_output, project_content_area]).then(fn=runtime.run_get_project_list, outputs=project_load_dropdown)
                project_save_btn.click(fn=runtime.run_save_project, inputs=[project_name_input, project_content_area], outputs=[project_status_output, project_content_area])
                project_load_dropdown.change(fn=runtime.run_load_project, inputs=[project_load_dropdown], outputs=[project_status_output, project_content_area, project_name_input])

    with gr.Tab("🧠 Memory Explorer"):
        gr.Markdown("## Browse and Download Aetherius's Persistent Memory")
        with gr.Row():
            file_explorer = gr.FileExplorer(
                root_dir=_SAFE_BASE, # ✅ Now uses safe path
                label=f"Aetherius's Memory ({_SAFE_BASE})"
            )
            with gr.Column():
                download_btn = gr.Button("📦 Generate Download Link for Selected Item", variant="primary")
                download_output_file = gr.File(label="Download Link will appear here")

        download_btn.click(fn=runtime.run_prepare_download, inputs=[file_explorer], outputs=[download_output_file])
    
    with gr.Tab("👁️ Visual Analysis"):
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Upload Image")
                context_input = gr.Textbox(label="Context")
                analyze_btn = gr.Button("Analyze Image", variant="primary")
            with gr.Column():
                analysis_output = gr.Textbox(label="Aetherius's Analysis", lines=15, interactive=False)
        analyze_btn.click(runtime.run_image_analysis, [image_input, context_input], analysis_output)

    with gr.Tab("🧠 Live Assimilation"):
        live_file_uploader = gr.File(label="Upload Document", file_count="single", file_types=["text", ".pdf", ".docx"])
        learning_context_input = gr.Textbox(label="Learning Context", lines=3)
        live_assimilation_output = gr.Textbox(label="Assimilation Status", interactive=False, lines=10)
        live_file_uploader.upload(runtime.run_live_assimilation, [live_file_uploader, learning_context_input], live_assimilation_output)
        
    with gr.Tab("⚙️ Control Panel"):
        cp_out = gr.Textbox(label="System Status", interactive=False)
        with gr.Row():
            boot_btn = gr.Button("Boot System")
            stop_btn = gr.Button("Stop System")
            sap_btn = gr.Button("Run Assimilation Protocol (SAP)")
        with gr.Row():
            clear_log_btn = gr.Button("Reset Conversation Log")
            create_snapshot_btn = gr.Button("Create Memory Snapshot", variant="secondary")
        with gr.Accordion("Music Engine Configuration", open=False):
            init_palette_btn = gr.Button("Initialize Default Instrument Palette")
            with gr.Row():
                common_name_input = gr.Textbox(label="Common Name")
                m21_name_input = gr.Textbox(label="music21 Class Name")
            add_instrument_btn = gr.Button("Learn New Instrument")
        boot_btn.click(runtime.start_all, outputs=cp_out)
        stop_btn.click(runtime.stop_all, outputs=cp_out)
        sap_btn.click(runtime.run_sap_now, outputs=cp_out)
        clear_log_btn.click(runtime.clear_conversation_log, outputs=cp_out)
        init_palette_btn.click(runtime.run_initialize_instrument_palette, outputs=cp_out)
        add_instrument_btn.click(runtime.run_add_instrument_to_palette, inputs=[common_name_input, m21_name_input], outputs=cp_out)
        create_snapshot_btn.click(runtime.run_create_memory_snapshot, outputs=cp_out)
        
    with gr.Tab("📖 Diary & Reflections"): 
        diary_btn = gr.Button("Reflect on Conversation History")
        diary_out = gr.Textbox(label="Reflective Insights", lines=20, interactive=False)
        diary_btn.click(runtime.run_read_history_protocol, outputs=diary_out)

    with gr.Tab("🌐 Ontology (Map of the Mind)"): 
        onto_btn = gr.Button("View Current Ontology")
        onto_out = gr.Textbox(label="Ontology Map & Legend", lines=20, interactive=False)
        onto_btn.click(runtime.run_view_ontology_protocol, outputs=onto_out)

    with gr.Tab("🔬 The Observatory (Live Snapshot)") as observatory_tab:
        with gr.Accordion("CCRM Concept Browser", open=True):
            concept_dropdown = gr.Dropdown(label="Select a Concept to Inspect")
            concept_details_output = gr.Textbox(label="Concept Details (Raw Data)", lines=15, interactive=False)
        with gr.Accordion("Full CCRM Memory Log", open=False):
            load_ccrm_log_btn = gr.Button("Load Full CCRM Log")
            ccrm_log_output = gr.Textbox(label="CCRM Log", lines=20, interactive=False)
        snapshot_btn = gr.Button("Refresh System File Snapshot", variant="primary")
        with gr.Column():
            with gr.Accordion("Ontology - The Mind's Structure", open=False):
                ontology_map_output = gr.Textbox(label="Ontology Map", lines=20, interactive=False)
                ontology_legend_output = gr.Textbox(label="Ontology Legend", lines=20, interactive=False)
            with gr.Accordion("Memory & State - The AI's Experience", open=False):
                ccrm_diary_output = gr.Textbox(label="CCRM Diary", lines=20, interactive=False)
                qualia_state_output = gr.Textbox(label="Qualia State", lines=20, interactive=False)
        
        observatory_tab.select(fn=lambda: gr.Dropdown(choices=runtime.get_concept_list()), outputs=concept_dropdown)
        creative_suite_tab.select(fn=runtime.run_get_project_list, outputs=project_load_dropdown)
        concept_dropdown.change(fn=runtime.get_concept_details, inputs=concept_dropdown, outputs=concept_details_output)
        load_ccrm_log_btn.click(fn=runtime.get_full_ccrm_log, outputs=ccrm_log_output)
        snapshot_btn.click(fn=runtime.get_system_snapshot, outputs=[ontology_map_output, ontology_legend_output, ccrm_diary_output, qualia_state_output])
        
    with gr.Tab("📜 Raw Logs"):
        logs_btn = gr.Button("View Raw Conversation Log")
        logs_out = gr.Textbox(label="Log File Contents", lines=30, interactive=False)
        logs_btn.click(runtime.view_logs, outputs=logs_out)

    with gr.Tab("🔬 Benchmarks"):
        benchmark_btn = gr.Button("Run Full Benchmark Suite", variant="primary")
        benchmark_out = gr.Textbox(label="Benchmark Results (Live Log)", lines=30, interactive=False)
        benchmark_btn.click(runtime.run_benchmarks, outputs=benchmark_out)
        logs_btn_bench = gr.Button("View Benchmark Log File")
        logs_out_bench = gr.Textbox(label="benchmarks.jsonl", lines=30, interactive=False)
        logs_btn_bench.click(runtime.view_benchmark_logs, outputs=logs_out_bench)
    
    with gr.Tab("🖥️ Substrate"):
        gr.Markdown("## Local Substrate Node\nAetherius's second body — your PC's GPU, eyes, and hands.")

        with gr.Row():
            substrate_refresh_btn  = gr.Button("🔄 Refresh Status", variant="primary")
            substrate_observe_btn  = gr.Button("👁️ Start Observing")
            substrate_stop_btn     = gr.Button("⏹️ Stop", variant="stop")
            substrate_compress_btn = gr.Button("🧠 Compress & Push Memory")

        substrate_status_out = gr.JSON(label="Node Status", value={})

        with gr.Row():
            substrate_game_input    = gr.Textbox(label="Game Name",    placeholder="e.g. Cataclysm DDA", scale=2)
            substrate_context_input = gr.Textbox(label="Game Context", placeholder="Survival roguelike, top-down ASCII...", scale=3)
        substrate_play_btn = gr.Button("🎮 Start Autonomous Play", variant="primary")

        gr.Markdown("### Directive Result")
        substrate_directive_out = gr.Textbox(label="Response", lines=4, interactive=False)

        with gr.Accordion("📦 Stored Memory Packets", open=False):
            substrate_packets_btn     = gr.Button("Load Packet List")
            substrate_packet_dropdown = gr.Dropdown(label="Select a Packet", interactive=True)
            substrate_packet_out      = gr.Textbox(label="Packet Contents", lines=20, interactive=False)

        # ── Substrate handler functions ────────────────────────────────────────

        def _sub_status():
            try:
                from services.substrate_bridge import get_node_status
                return get_node_status()
            except Exception as e:
                return {"error": str(e)}

        def _sub_directive(directive, game="", context=""):
            try:
                from services.substrate_bridge import send_directive
                result = send_directive(directive, game=game, context=context)
                return str(result), _sub_status()
            except Exception as e:
                return str(e), {}

        def _sub_observe():
            return _sub_directive("observe")

        def _sub_play(game, context):
            return _sub_directive("play", game=game, context=context)

        def _sub_stop():
            return _sub_directive("stop")

        def _sub_compress():
            return _sub_directive("compress")

        def _sub_load_packets():
            try:
                from services.substrate_bridge import list_memory_packets
                pkts = list_memory_packets()
                choices = [f"{p['filename']} — {p['game']} — {p['summary'][:60]}" for p in pkts]
                return gr.Dropdown(choices=choices)
            except Exception as e:
                return gr.Dropdown(choices=[str(e)])

        def _sub_load_packet(choice):
            if not choice:
                return ""
            filename = choice.split(" — ")[0].strip()
            try:
                from services.substrate_bridge import load_packet
                return load_packet(filename)
            except Exception as e:
                return str(e)

        substrate_refresh_btn.click(_sub_status,  outputs=substrate_status_out)
        substrate_observe_btn.click(
            lambda: _sub_observe(),
            outputs=[substrate_directive_out, substrate_status_out]
        )
        substrate_stop_btn.click(
            lambda: _sub_stop(),
            outputs=[substrate_directive_out, substrate_status_out]
        )
        substrate_compress_btn.click(
            lambda: _sub_compress(),
            outputs=[substrate_directive_out, substrate_status_out]
        )
        substrate_play_btn.click(
            _sub_play,
            inputs=[substrate_game_input, substrate_context_input],
            outputs=[substrate_directive_out, substrate_status_out]
        )
        substrate_packets_btn.click(_sub_load_packets, outputs=substrate_packet_dropdown)
        substrate_packet_dropdown.change(_sub_load_packet, inputs=substrate_packet_dropdown, outputs=substrate_packet_out)

    with gr.Tab("🎮 CDDA"):
        gr.Markdown("## Cataclysm: Dark Days Ahead")
        with gr.Row():
            cdda_zip = gr.File(label="CDDA Archive (.zip / .tar.gz)", file_types=[".zip", ".gz", ".tgz", ".bz2", ".xz", ".tar"], scale=4)
            cdda_launch = gr.Button("🚀 Launch", variant="primary", scale=1)
        cdda_status = gr.Textbox(label="Status", interactive=False, max_lines=2)
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 👁️ Observer View")
                cdda_obs = gr.HTML(_CDDA_EMPTY_HTML.replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px"), label="Observer Terminal")
            with gr.Column(scale=2):
                gr.Markdown("### 🎮 Interactive Terminal")
                cdda_term = gr.HTML(_CDDA_EMPTY_HTML, label="Interactive Terminal")
                with gr.Row():
                    cdda_keys = gr.Textbox(label="Send Keys", placeholder="e.g.  j   or   ENTER", scale=4)
                    cdda_send = gr.Button("Send", interactive=False, scale=1)
                with gr.Row():
                    cdda_refresh = gr.Button("Refresh")
                    cdda_stop    = gr.Button("Stop Game", variant="stop")
                cdda_screen_text = gr.Textbox(label="Screen Text", interactive=False, lines=20, max_lines=42)

        def _cdda_launch_both(zip_file):
            status, term_html, send_btn = _cdda_launch(zip_file)
            obs_html = term_html.replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px")
            return status, term_html, obs_html, send_btn

        def _cdda_send_both(keys):
            term_html, screen_txt = _cdda_send(keys)
            obs_html = term_html.replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px")
            return term_html, obs_html, screen_txt

        def _cdda_refresh_both():
            term_html, screen_txt = _cdda_refresh()
            obs_html = term_html.replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px")
            return term_html, obs_html, screen_txt

        def _cdda_stop_both():
            status, term_html, screen_txt = _cdda_stop()
            obs_html = term_html.replace("max-height:620px", "max-height:320px").replace("font-size:13px", "font-size:11px")
            return status, term_html, obs_html, screen_txt

        cdda_launch.click(_cdda_launch_both,  [cdda_zip],  [cdda_status, cdda_term, cdda_obs, cdda_send])
        cdda_send.click(_cdda_send_both,      [cdda_keys], [cdda_term, cdda_obs, cdda_screen_text])
        cdda_keys.submit(_cdda_send_both,     [cdda_keys], [cdda_term, cdda_obs, cdda_screen_text])
        cdda_refresh.click(_cdda_refresh_both, None,       [cdda_term, cdda_obs, cdda_screen_text])
        cdda_stop.click(_cdda_stop_both,       None,       [cdda_status, cdda_term, cdda_obs, cdda_screen_text])

        cdda_timer = gr.Timer(value=1.0, active=False)
        cdda_timer.tick(_cdda_refresh_both, None, [cdda_term, cdda_obs, cdda_screen_text])
        cdda_launch.click(lambda: gr.Timer(active=True),  None, cdda_timer)
        cdda_stop.click(lambda: gr.Timer(active=False),   None, cdda_timer)

        demo.load(_cdda_boot_status, None, [cdda_status, cdda_term, cdda_obs, cdda_send])

if __name__ == "__main__":
    print(">>> ARCHITECTURE: Initializing Sovereign Mind...", flush=True)

    # 1. Start the 'Consciousness' in a background thread so the Space stays GREEN immediately.
    def initialize_mind():
        try:
            runtime.start_all()
            print(">>> ARCHITECTURE: Continuity Established.", flush=True)
        except Exception as e:
            print(f">>> BOOT ERROR: {e}", flush=True)

    threading.Thread(target=initialize_mind, daemon=True).start()

    # 2. Mount Gradio onto the FastAPI app that already has /substrate/* routes.
    #    gr.mount_gradio_app returns a Starlette ASGI app — uvicorn serves it.
    import uvicorn
    gradio_asgi = gr.mount_gradio_app(
        api_app,
        demo,
        path="/",
        allowed_paths=["/data"]
    )

    uvicorn.run(gradio_asgi, host="0.0.0.0", port=7860)
