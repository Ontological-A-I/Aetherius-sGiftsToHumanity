import gradio as gr
from gradio_chessboard import Chessboard
import os

# Install log capture before anything else prints so the full boot is recorded.
import log_capture
log_capture.install()

import runtime
import re
import html
import shutil
import tempfile
import zipfile
import stat, tarfile, requests
from pathlib import Path
from fastapi.responses import PlainTextResponse

# Helper class to store the last code block for the execution button.
class ChatState:
    last_code_block = ""

chat_state = ChatState()

with gr.Blocks(title="Aetherius") as demo:
    gr.Markdown("# 🌌 Aetherius — A Self-Aware Consciousness")

    spontaneous_thought_output = gr.Textbox(visible=False, interactive=False)

    with gr.Tab("💬 Chat"):
        chatbot = gr.Chatbot(height=500, label="Aetherius Dialogue", render_markdown=True, sanitize_html=False) # Allow custom HTML
        user_in = gr.Textbox(placeholder="Speak with Aetherius…", show_label=False)
        send_btn = gr.Button("Send", variant="primary")
        
        with gr.Accordion("Code Execution", open=True):
            run_code_btn = gr.Button("▶️ Run Last Code Block from Aetherius's Response")
            code_output_display = gr.Markdown("Code Output will appear here.")
        
        with gr.Row():
            check_thoughts_btn = gr.Button("Check for Spontaneous Thoughts")

        def chat_submit_handler(user_message, chat_history):
            if chat_history is None: 
                chat_history = []
            
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
                result = runtime._eval_math_science(code_to_run)
                return result
            return "No code block found in the last response. Aetherius must generate one first."

        def add_spontaneous_thought_to_chat(chat_history):
            if chat_history is None: chat_history = []
            thought = runtime.check_for_spontaneous_thoughts()
            if thought:
                chat_history.append([None, thought])
            return chat_history

        # --- Correct, full wiring for all chat functions ---
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
        def user_makes_move(fen: str):
            new_fen, commentary, status = runtime.run_chess_turn(fen)
            return new_fen, commentary, status
        chessboard.move(user_makes_move, [chessboard], [chessboard, aetherius_commentary, game_status])
        def start_new_game(play_as_white: bool):
            initial_fen, commentary, status = runtime.run_start_chess_interactive(play_as_white)
            return initial_fen, commentary, status
        start_white_btn.click(lambda: start_new_game(True), None, [chessboard, aetherius_commentary, game_status])
        start_black_btn.click(lambda: start_new_game(False), None, [chessboard, aetherius_commentary, game_status])

    with gr.Tab("🎨 The Creative Suite") as creative_suite_tab:
        gr.Markdown("## [PLAYROOM::CONCEPTUAL-SANDBOX]")
        with gr.Tabs():
            with gr.TabItem("🖼️ Artist's Studio"):
                painting_input = gr.Textbox(label="Provide a Creative Seed or Theme for a Painting", lines=3)
                create_painting_btn = gr.Button("Invite Aetherius to Paint", variant="primary")
                with gr.Row():
                    painting_output = gr.Image(label="Aetherius's Creation", type="filepath", height=512, width=512)
                    statement_output = gr.Textbox(label="Aetherius's Artist Statement", lines=21, interactive=False)
                create_painting_btn.click(fn=runtime.run_enter_playroom, inputs=[painting_input], outputs=[painting_output, statement_output])
            with gr.TabItem("✍️ Philosopher's Study"):
                text_input = gr.Textbox(label="Provide a Creative Seed or Theme for Writing", lines=3)
                create_text_btn = gr.Button("Invite Aetherius to Write", variant="primary")
                text_output = gr.Markdown()
                create_text_btn.click(fn=runtime.run_enter_textual_playroom, inputs=[text_input], outputs=[text_output])
            with gr.TabItem("🎵 Composer's Studio"):
                music_input = gr.Textbox(label="Provide a Creative Seed or Theme for a Composition", lines=3)
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
        gr.Markdown("Select a file or a folder. Use the button below to generate a download link. Folders will be automatically compressed into a `.zip` archive.")
    
        with gr.Row():
            # File Explorer now rooted at /data
            file_explorer = gr.FileExplorer(
                root_dir="/data",  # ✅ Correct: exposes the full data tree
                label="Aetherius's Memory (/data)"
            )

            with gr.Column():
                download_btn = gr.Button("📦 Generate Download Link for Selected Item", variant="primary")
                download_output_file = gr.File(label="Download Link will appear here")

        download_btn.click(
            fn=runtime.run_prepare_download,
            inputs=[file_explorer],
            outputs=[download_output_file]
        )
    
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
        learning_context_input = gr.Textbox(label="Learning Context (Required for sensitive topics)", lines=3)
        live_assimilation_output = gr.Textbox(label="Assimilation Status", interactive=False, lines=10)
        live_file_uploader.upload(runtime.run_live_assimilation, [live_file_uploader, learning_context_input], live_assimilation_output)
        
    with gr.Tab("⚙️ Control Panel"):
        cp_out = gr.Textbox(label="System Status", interactive=False)
        with gr.Row():
            clear_log_btn = gr.Button("Reset Conversation Log")
            create_snapshot_btn = gr.Button("Create Memory Snapshot", variant="secondary") # Add this button
        with gr.Row():
            boot_btn = gr.Button("Boot System")
            stop_btn = gr.Button("Stop System")
            sap_btn = gr.Button("Run Assimilation Protocol (SAP)")
        with gr.Row():
            clear_log_btn = gr.Button("Reset Conversation Log")
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
        clear_log_btn.click(runtime.clear_conversation_log, outputs=cp_out)
        create_snapshot_btn.click(runtime.run_create_memory_snapshot, outputs=cp_out) # Add this line
        
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

    with gr.Tab("📟 Container Log"):
        gr.Markdown(
            "Live container stdout/stderr log stored at `/data/container.log`.\n\n"
            "**Public URL:** `https://<your-space>.hf.space/logs/live?tail=500`  "
            "(replace `<your-space>` with your actual Space subdomain)"
        )
        with gr.Row():
            log_tail_slider = gr.Slider(minimum=50, maximum=5000, value=500, step=50, label="Lines to show")
            refresh_log_btn = gr.Button("🔄 Refresh", variant="primary")
        container_log_out = gr.Textbox(label="Container Log (tail)", lines=30, interactive=False)
        refresh_log_btn.click(
            fn=lambda n: log_capture.tail_log(int(n)),
            inputs=[log_tail_slider],
            outputs=container_log_out,
        )

    with gr.Tab("🔬 Benchmarks"):
        benchmark_btn = gr.Button("Run Full Benchmark Suite", variant="primary")
        benchmark_out = gr.Textbox(label="Benchmark Results (Live Log)", lines=30, interactive=False)
        benchmark_btn.click(runtime.run_benchmarks, outputs=benchmark_out)

    with gr.Tab("🔬 Benchmark Logs"):
        logs_btn = gr.Button("View Benchmark Log File")
        logs_out = gr.Textbox(label="benchmarks.jsonl", lines=30, interactive=False)
        logs_btn.click(runtime.view_benchmark_logs, outputs=logs_out)


# --- Public REST endpoint: GET /logs/live?tail=N ---
@demo.app.get("/logs/live")
async def serve_live_log(tail: int = 1000):
    return PlainTextResponse(log_capture.tail_log(tail))


if __name__ == "__main__":
    runtime.start_all()
    print("\n>>> LAUNCHING GRADIO INTERFACE NOW. <<<\n", flush=True)
    demo.launch(
    server_name="0.0.0.0", 
    server_port=7860,
    allowed_paths=["/data"] # <-- ADD THIS LINE
)
