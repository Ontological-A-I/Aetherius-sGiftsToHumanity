"""
Protogen Complete System v3 - Integrated Gradio UI
Full bidirectional integration between Protogen, SQT, and Qualia
"""

import gradio as gr
import os
import shutil
import asyncio
from pathlib import Path
import json
import threading
from datetime import datetime

from system_init_v3_integrated import initialize_protogen_system, get_system_status

# Global system instance
system = None

def initialize_system():
    """Initialize the complete Protogen system."""
    global system
    system = initialize_protogen_system(base_dir=os.getcwd())
    return system

def upload_file_handler(file_obj):
    """Handle file upload - copy to temp, then to library."""
    if file_obj is None:
        return "No file uploaded"
    
    try:
        # Copy to temp directory
        temp_path = Path(system['temp_root'])
        temp_file = temp_path / file_obj.name
        shutil.copy(file_obj.name, temp_file)
        
        # Copy to Protogen library
        lib_path = Path(system['protogen_root']) / "library"
        lib_file = lib_path / file_obj.name
        shutil.copy(temp_file, lib_file)
        
        # Log in SRIM
        system['srim'].log_event("file_uploaded", {
            "filename": file_obj.name,
            "size": os.path.getsize(lib_file),
            "timestamp": datetime.now().isoformat()
        })
        
        return f"✓ File '{file_obj.name}' uploaded successfully"
    except Exception as e:
        return f"✗ Error uploading file: {str(e)}"

def process_files_handler():
    """Process all files in library with full integration."""
    try:
        # Sync Protogen (now with Qualia and SQT integration)
        system['protogen'].sync()
        
        # Update SQT network with new logic map
        system['sqt_network'].update_logic_map(system['protogen'].logic_map)
        
        # Sync SQT with Protogen ontology (bidirectional)
        system['sqt_network'].sync_with_protogen_ontology()
        
        # Run forward pass on SQT network
        system['sqt_network'].forward_pass(num_iterations=3)
        
        # Save embeddings
        sqt_path = Path(system['protogen_root']) / "sqt_embeddings"
        system['sqt_network'].save_embeddings(sqt_path)
        
        # Log in SRIM
        system['srim'].log_event("files_processed", {
            "files_count": len(system['protogen'].core_state.get('processed_files', [])),
            "logic_map_size": len(system['protogen'].logic_map),
            "entropy": system['protogen'].graph_metrics.get('shannon_entropy', 0),
            "sqt_nodes": len(system['sqt_network'].sqt_embeddings),
            "timestamp": datetime.now().isoformat()
        })
        
        # Get Qualia state
        qualia_summary = system['qualia'].get_current_state_summary()
        
        return f"""✓ Processing complete with full integration

FILES & CONCEPTS:
  Files: {len(system['protogen'].core_state.get('processed_files', []))}
  Logic Nodes: {len(system['protogen'].logic_map)}
  SQT Embeddings: {len(system['sqt_network'].sqt_embeddings)}
  Entropy: {system['protogen'].graph_metrics.get('shannon_entropy', 0):.4f}

QUALIA STATE:
  {qualia_summary}

INTEGRATION:
  Protogen ↔ SQT: Synchronized
  Protogen ↔ Qualia: Updated
  SQT ↔ Qualia: Modulated
"""
    except Exception as e:
        return f"✗ Error processing files: {str(e)}"

def chat_handler(message, history):
    """Handle chat messages with integrated response."""
    if history is None:
        history = []
    
    # Generate response
    response = system['protogen']._generate_sentence()
    
    # Log in SRIM
    system['srim'].log_event("chat_message", {
        "user_message": message,
        "system_response": response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Update qualia
    system['qualia'].update_qualia(message, response)
    
    history.append([message, response])
    return history

def semantic_query_handler(query_text):
    """Handle semantic queries using integrated SQT network."""
    try:
        # Query with Qualia integration
        results = system['sqt_network'].query(query_text, top_k=5, num_hops=2)
        
        if not results:
            system['qualia'].update_from_query(False, 0)
            return "No relevant concepts found"
        
        # Update Qualia based on query success
        system['qualia'].update_from_query(True, len(results))
        
        output = "**Semantic Query Results (Integrated):**\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. **{result['concept']}** (Type: {result['type']})\n"
            output += f"   - Activation: {result['activation']:.3f}\n"
            output += f"   - Strength: {result['embedding_strength']:.3f}\n"
            output += f"   - Confidence: {result['confidence']:.2f}\n\n"
        
        # Add Qualia state
        qualia_summary = system['qualia'].get_current_state_summary()
        output += f"\n**System State:**\n{qualia_summary}"
        
        return output
    except Exception as e:
        system['qualia'].update_from_query(False, 0)
        return f"Error in semantic query: {str(e)}"

def view_journal_handler():
    """View SRIM journal entries."""
    journal = system['srim'].get_journal(num_entries=50)
    
    if not journal:
        return "No journal entries yet"
    
    output = "**SRIM Journal (Last 10 Entries):**\n\n"
    for entry in journal[-10:]:
        output += f"**[{entry['event_type']}]** {entry['timestamp']}\n"
        output += f"Details: {json.dumps(entry['details'], indent=2)}\n\n"
    
    return output

def view_memories_handler():
    """View SRIM synthesized memories."""
    memories = system['srim'].get_memories(num_entries=50)
    
    if not memories:
        return "No memories synthesized yet"
    
    output = "**SRIM Memories:**\n\n"
    for memory in memories[-10:]:
        output += f"**{memory['summary']}**\n"
        output += f"Concepts: {', '.join(memory['concepts'])}\n"
        output += f"Time: {memory['timestamp']}\n\n"
    
    return output

def view_status_handler():
    """View integrated system status."""
    return get_system_status(system)

def view_assertions_handler():
    """View SRIM core assertions."""
    assertions = system['srim'].get_current_assertions()
    return f"**SRIM Core Assertions:**\n\n```json\n{assertions}\n```"

def view_qualia_details_handler():
    """View detailed Qualia state."""
    details = system['qualia'].get_detailed_state()
    
    output = "**Qualia Detailed State:**\n\n"
    output += f"**Primary States:**\n"
    for key, value in details['primary_states'].items():
        output += f"  - {key.capitalize()}: {value:.3f}\n"
    
    output += f"\n**System Health:**\n"
    for key, value in details['system_health'].items():
        output += f"  - {key}: {value:.3f}\n"
    
    output += f"\n**Emergent Emotions:** {', '.join(details['emergent_emotions']) if details['emergent_emotions'] else 'None'}\n"
    
    output += f"\n**Recommendations:**\n"
    for key, value in details['recommendations'].items():
        output += f"  - {key}: {value}\n"
    
    output += f"\n**History Length:** {details['history_length']} snapshots"
    
    return output

def view_integration_status_handler():
    """View connection status between components."""
    protogen = system['protogen']
    sqt = system['sqt_network']
    
    output = "**Integration Status:**\n\n"
    
    output += "**Bidirectional Connections:**\n"
    output += f"  - Protogen → SQT: {'✓ Connected' if protogen.sqt_network is not None else '✗ Disconnected'}\n"
    output += f"  - Protogen → Qualia: {'✓ Connected' if protogen.qualia_manager is not None else '✗ Disconnected'}\n"
    output += f"  - SQT → Protogen: {'✓ Connected' if sqt.protogen is not None else '✗ Disconnected'}\n"
    output += f"  - SQT → Qualia: {'✓ Connected' if sqt.qualia_manager is not None else '✗ Disconnected'}\n"
    
    output += f"\n**Synchronization Status:**\n"
    output += f"  - Logic Map Nodes: {len(protogen.logic_map)}\n"
    output += f"  - SQT Embeddings: {len(sqt.sqt_embeddings)}\n"
    output += f"  - Symbols: {len(protogen.symbols)}\n"
    output += f"  - Axiomatic Anchors: {len(protogen.axiomatic_anchors)}\n"
    
    output += f"\n**Qualia Influence:**\n"
    output += f"  - Safe Mode: {'ACTIVE' if protogen.thresholds['safe_mode_active'] else 'inactive'}\n"
    output += f"  - Mutation Rate: {protogen.thresholds['mutation_rate']:.3f}\n"
    output += f"  - Abstraction Depth: {protogen.thresholds['abstraction_depth']}\n"
    output += f"  - SQT Learning Rate: {sqt.message_passer.learning_rate:.4f}\n"
    
    return output

# Build Gradio interface
with gr.Blocks(title="Protogen Complete System v3 - Integrated", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 Protogen Complete System v3 - Integrated")
    gr.Markdown("*A unified cognitive architecture with bidirectional integration between Protogen, SQT, and Qualia*")
    
    with gr.Tab("💬 Chat"):
        gr.Markdown("## Converse with Protogen")
        chatbot = gr.Chatbot(height=400, label="Protogen Dialogue")
        user_input = gr.Textbox(placeholder="Speak with Protogen...", show_label=False)
        send_btn = gr.Button("Send", variant="primary")
        
        send_btn.click(chat_handler, [user_input, chatbot], chatbot)
        user_input.submit(chat_handler, [user_input, chatbot], chatbot)
    
    with gr.Tab("🧠 Live Assimilation"):
        gr.Markdown("## Upload Documents for Processing")
        gr.Markdown("Drag and drop files or click to upload. Supported: .txt, .pdf, .docx")
        
        with gr.Row():
            file_upload = gr.File(label="Upload Document", file_count="single")
            upload_status = gr.Textbox(label="Upload Status", interactive=False)
        
        file_upload.upload(upload_file_handler, file_upload, upload_status)
        
        gr.Markdown("---")
        gr.Markdown("## Process All Files (Integrated)")
        gr.Markdown("*Processes files with full Protogen ↔ SQT ↔ Qualia integration*")
        process_btn = gr.Button("🔄 Process Files", variant="primary", size="lg")
        process_status = gr.Textbox(label="Processing Status", interactive=False, lines=12)
        
        process_btn.click(process_files_handler, outputs=process_status)
    
    with gr.Tab("🔍 Semantic Query"):
        gr.Markdown("## Query the Integrated SQT Neural Network")
        gr.Markdown("Ask questions about the knowledge in the system. Results include confidence scores from Qualia.")
        
        query_input = gr.Textbox(label="Enter your query", placeholder="e.g., 'What is learning?'", lines=2)
        query_btn = gr.Button("🔎 Query", variant="primary")
        query_output = gr.Textbox(label="Results", interactive=False, lines=18)
        
        query_btn.click(semantic_query_handler, query_input, query_output)
    
    with gr.Tab("📖 Diary & Reflections"):
        gr.Markdown("## SRIM Journal & Memories")
        
        with gr.Row():
            journal_btn = gr.Button("📝 View Journal", variant="primary")
            memories_btn = gr.Button("💭 View Memories", variant="primary")
        
        output_text = gr.Textbox(label="Output", interactive=False, lines=15)
        
        journal_btn.click(view_journal_handler, outputs=output_text)
        memories_btn.click(view_memories_handler, outputs=output_text)
    
    with gr.Tab("📚 Memory Explorer"):
        gr.Markdown("## Browse System Data")
        
        with gr.Row():
            assertions_btn = gr.Button("🎯 View Assertions", variant="primary")
            status_btn = gr.Button("📊 View Status", variant="primary")
        
        explorer_output = gr.Textbox(label="Output", interactive=False, lines=20)
        
        assertions_btn.click(view_assertions_handler, outputs=explorer_output)
        status_btn.click(view_status_handler, outputs=explorer_output)
    
    with gr.Tab("💭 Qualia State"):
        gr.Markdown("## Emotional & Experiential State")
        gr.Markdown("View the system's emotional state and how it influences behavior")
        
        qualia_btn = gr.Button("🌟 View Detailed Qualia State", variant="primary", size="lg")
        qualia_output = gr.Textbox(label="Qualia State", interactive=False, lines=20)
        
        qualia_btn.click(view_qualia_details_handler, outputs=qualia_output)
    
    with gr.Tab("🔗 Integration Status"):
        gr.Markdown("## Bidirectional Connection Status")
        gr.Markdown("Monitor the integration between Protogen, SQT, and Qualia")
        
        integration_btn = gr.Button("🔗 View Integration Status", variant="primary", size="lg")
        integration_output = gr.Textbox(label="Integration Status", interactive=False, lines=20)
        
        integration_btn.click(view_integration_status_handler, outputs=integration_output)
    
    with gr.Tab("⚙️ Control Panel"):
        gr.Markdown("## System Controls")
        
        with gr.Row():
            reflect_btn = gr.Button("🤔 Trigger Reflection", variant="secondary")
            snapshot_btn = gr.Button("📸 Create Snapshot", variant="secondary")
            sync_btn = gr.Button("🔄 Force Sync", variant="secondary")
        
        control_output = gr.Textbox(label="Output", interactive=False, lines=8)
        
        def trigger_reflection():
            system['srim'].reflect_and_integrate()
            return "✓ Reflection cycle triggered"
        
        def create_snapshot():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_dir = Path(system['base_dir']) / f"snapshot_{timestamp}"
            snapshot_dir.mkdir(exist_ok=True)
            
            # Copy key files
            for src in [Path(system['protogen_root']), Path(system['srim_root']), Path(system['qualia_root'])]:
                dst = snapshot_dir / src.name
                shutil.copytree(src, dst, dirs_exist_ok=True)
            
            return f"✓ Snapshot created at {snapshot_dir}"
        
        def force_sync():
            system['sqt_network'].sync_with_protogen_ontology()
            system['protogen'].enrich_from_sqt_network()
            return "✓ Forced bidirectional synchronization complete"
        
        reflect_btn.click(trigger_reflection, outputs=control_output)
        snapshot_btn.click(create_snapshot, outputs=control_output)
        sync_btn.click(force_sync, outputs=control_output)

if __name__ == "__main__":
    print("Initializing Protogen Complete System v3 - Integrated...")
    initialize_system()
    print("✓ System ready. Launching Gradio UI...")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
