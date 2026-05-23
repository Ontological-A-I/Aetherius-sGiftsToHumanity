"""
Protogen v5 Complete Web Interface
===================================

Full-featured web UI for Protogen v5 educational tutoring system with:
- Natural language interaction
- Safety indicators
- Wellness support
- Cultural awareness
- Understanding monitoring
- System status display

Created by: Jonathan Wayne Fleuren (design) + Claude (Anthropic via Manus AI) (implementation)
"""

import gradio as gr
from system_init_v5_complete import ProtogenV5System
from datetime import datetime

# Initialize system
print("Starting Protogen v5 Web Interface...")
system = ProtogenV5System(data_dir="./protogen_v5_data")

# Global state
current_user_id = "default_user"
declared_age = None


def chat_with_protogen(message, history):
    """
    Process user message through Protogen v5 system.
    Returns updated chat history and clears the input box.
    """
    global current_user_id, declared_age

    if not message.strip():
        return history or [], ""

    # Process through Protogen v5
    result = system.process_user_input(
        user_input=message,
        user_id=current_user_id,
        declared_age=declared_age
    )

    # Format response with safety indicators
    response = result["response"]

    # Add safety/wellness indicators if relevant
    metadata = result.get("metadata", {})

    if result.get("crisis_detected"):
        response = "🚨 **CRISIS SUPPORT ACTIVATED** 🚨\n\n" + response
    elif metadata.get("distress_assessment", {}).get("distress_level") in ["high_distress", "moderate_distress"]:
        response = "💙 **Wellness Support** 💙\n\n" + response

    if metadata.get("content_filtered"):
        response += "\n\n_[Note: Response was filtered for age-appropriate content]_"

    if history is None:
        history = []
    history.append([message, response])
    return history, ""


def set_user_info(user_id_input, age_input):
    """Set user ID and age"""
    global current_user_id, declared_age

    if user_id_input:
        current_user_id = user_id_input

    if age_input:
        try:
            declared_age = int(age_input)
        except:
            declared_age = None

    return f"User set to: {current_user_id}" + (f" (age: {declared_age})" if declared_age else "")


def teach_cultural_context(context_description, keywords_input, example_concept, example_explanation):
    """Allow user to teach cultural context"""
    global current_user_id

    if not context_description or not keywords_input:
        return "Please provide both context description and keywords."

    keywords = [k.strip() for k in keywords_input.split(",")]

    examples = {}
    if example_concept and example_explanation:
        examples[example_concept] = example_explanation

    success = system.learn_cultural_pattern_from_user(
        user_id=current_user_id,
        cultural_context=context_description,
        keywords=keywords,
        examples=examples
    )

    if success:
        return f"✓ Learned cultural context: {context_description}\nKeywords: {', '.join(keywords)}"
    else:
        return "Failed to learn cultural context. Please try again."


def get_system_status():
    """Get formatted system status"""
    status = system.get_system_status()

    qualia = status["components"]["qualia"]
    # FIX: primary states are nested under 'primary_states', not at the top level
    qualia_states = qualia.get("primary_states", {})
    child_safety = status["components"]["child_safety"]
    wellness = status["components"]["student_wellness"]
    cultural = status["components"]["cultural_awareness"]

    status_text = f"""
## Protogen v5 System Status

**Overall:** {status["protogen_v5"]}

### Emotional State (Qualia)
- Coherence: {qualia_states.get("coherence", 0):.2f}
- Benevolence: {qualia_states.get("benevolence", 0):.2f}
- Trust: {qualia_states.get("trust", 0):.2f}
- Curiosity: {qualia_states.get("curiosity", 0):.2f}

### Safety Systems
- Age Assessment: {child_safety["current_age_assessment"]["likelihood"]} (confidence: {child_safety["current_age_assessment"]["confidence"]:.2f})
- Strict Safety: {"ENABLED" if child_safety["strict_safety_enabled"] else "DISABLED"}
- Data Retention: {child_safety["data_retention_policy"]["retention_days"]} days

### Wellness Support
- Current Distress Level: {wellness["current_distress_level"]}
- Crisis Patterns: {wellness["crisis_patterns_loaded"]}
- Responses Available: {wellness["responses_available"]}

### Cultural Awareness
- Patterns Loaded: {cultural["patterns_loaded"]}
- Examples Available: {cultural["examples_available"]}
- User-Learned Patterns: {cultural["user_learned_patterns"]}

### Session
- Conversation Length: {status["conversation_length"]} messages
- Current User: {status["current_user"]}
"""

    return status_text


def reset_conversation():
    """Reset conversation history"""
    system.reset_session()
    # FIX: return empty history + empty message to clear both chatbot and input
    return [], ""


# Create Gradio interface
with gr.Blocks(title="Protogen v5 - Educational Tutoring System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🧠 Protogen v5 - Educational Tutoring System

    **Complete, Responsible, Inclusive Education for All Students**

    Protogen v5 provides:
    - 📚 Adaptive educational tutoring
    - 🛡️ Child safety and privacy protection
    - 💙 Mental wellness support
    - 🌍 Cultural awareness and inclusivity
    - 🧩 Understanding-based adaptation

    ---
    """)

    with gr.Tab("Chat"):
        gr.Markdown("### Ask Protogen anything! It will adapt to your learning style and needs.")

        chatbot = gr.Chatbot(height=500, label="Conversation")
        msg = gr.Textbox(
            label="Your message",
            placeholder="Ask a question, request help with homework, or just chat...",
            lines=2
        )

        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear Conversation")

        gr.Markdown("""
        **Safety Features Active:**
        - 🛡️ Age-appropriate content filtering
        - 💙 Mental wellness monitoring
        - 🌍 Cultural sensitivity
        - 🔒 Privacy protection
        """)

        # FIX: output to [chatbot, msg] so the chat display updates and input clears
        msg.submit(chat_with_protogen, [msg, chatbot], [chatbot, msg])
        submit_btn.click(chat_with_protogen, [msg, chatbot], [chatbot, msg])
        # FIX: reset outputs both chatbot and msg
        clear_btn.click(reset_conversation, outputs=[chatbot, msg])

    with gr.Tab("User Settings"):
        gr.Markdown("### Set Your Information (Optional)")
        gr.Markdown("This helps Protogen adapt to your needs. All information is kept private and minimized.")

        user_id_input = gr.Textbox(
            label="User ID (optional)",
            placeholder="e.g., student_123",
            value="default_user"
        )

        age_input = gr.Number(
            label="Age (optional)",
            placeholder="Your age",
            minimum=5,
            maximum=100
        )

        set_info_btn = gr.Button("Set User Info", variant="primary")
        user_info_status = gr.Textbox(label="Status", interactive=False)

        set_info_btn.click(
            set_user_info,
            inputs=[user_id_input, age_input],
            outputs=[user_info_status]
        )

        gr.Markdown("""
        **Privacy Notice:**
        - If you're under 18, strict privacy protections apply
        - Personal information is minimized and auto-deleted
        - No data is shared with third parties
        """)

    with gr.Tab("Cultural Learning"):
        gr.Markdown("### Teach Protogen About Your Culture")
        gr.Markdown("Help Protogen understand your cultural context for more relevant examples.")

        context_desc = gr.Textbox(
            label="Cultural Context Description",
            placeholder="e.g., Pacific Islander community-focused learning",
            lines=2
        )

        keywords_input = gr.Textbox(
            label="Keywords (comma-separated)",
            placeholder="e.g., ocean, island, community fishing, traditional navigation"
        )

        gr.Markdown("**Optional: Provide a culturally-adapted example**")

        example_concept = gr.Textbox(
            label="Concept",
            placeholder="e.g., fractions"
        )

        example_explanation = gr.Textbox(
            label="Culturally-Relevant Explanation",
            placeholder="e.g., Fractions are like dividing the fish catch among families...",
            lines=3
        )

        teach_btn = gr.Button("Teach Cultural Context", variant="primary")
        teach_status = gr.Textbox(label="Status", interactive=False)

        teach_btn.click(
            teach_cultural_context,
            inputs=[context_desc, keywords_input, example_concept, example_explanation],
            outputs=[teach_status]
        )

    with gr.Tab("System Status"):
        gr.Markdown("### Protogen v5 System Status")

        status_display = gr.Markdown()
        refresh_btn = gr.Button("Refresh Status", variant="primary")

        refresh_btn.click(get_system_status, outputs=[status_display])

        # Auto-load status on tab open
        demo.load(get_system_status, outputs=[status_display])

    with gr.Tab("About"):
        gr.Markdown("""
        ## About Protogen v5

        **Protogen v5** is a complete educational tutoring system designed to help all students,
        especially those who:
        - Learn differently
        - Can't afford expensive tutors
        - Come from diverse cultural backgrounds
        - Need mental wellness support

        ### Key Features

        **🧠 Causal Reasoning**
        - Builds understanding through cause-and-effect, not just pattern matching
        - Learns from single experiences (like humans do)
        - Creates explicit knowledge graphs

        **🛡️ Child Safety**
        - COPPA and GDPR-K compliant
        - Age-appropriate content filtering
        - Automatic data minimization for minors
        - Privacy-by-design

        **💙 Mental Wellness Support**
        - Crisis detection and referral
        - Supportive responses for academic stress
        - Ethical boundaries (never diagnoses or prescribes)

        **🌍 Cultural Awareness**
        - Learns cultural contexts from users
        - Provides culturally-relevant examples
        - Detects and mitigates bias

        **🧩 Understanding Monitoring**
        - Detects confusion and adapts explanations
        - Identifies learning styles
        - Provides encouragement

        ### Technical Details

        **Lightweight & Accessible:**
        - Runs on low-end devices ("potato computers")
        - No expensive GPU required
        - Works offline (optional datasets)
        - < 100 MB total size

        **Privacy-Respecting:**
        - Local-first processing
        - Minimal data collection
        - Auto-deletion policies
        - No third-party sharing

        ### Credits

        **Design & Vision:** Jonathan Wayne Fleuren

        **Implementation:** Claude (Anthropic, via Manus AI)

        **Collaboration:** This system was built through human-AI collaboration,
        with explicit credit to all contributors. This demonstrates what ethical
        AI development can look like.

        **Purpose:** To democratize access to quality education for students who
        need it most, regardless of economic status, learning differences, or
        cultural background.

        ---

        **Protogen v5** - Complete, Responsible, Inclusive Education for All

        *"Intelligence without compassion is incomplete. We chose compassion."*
        """)

# Launch interface
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Launching Protogen v5 Web Interface...")
    print("=" * 60 + "\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
