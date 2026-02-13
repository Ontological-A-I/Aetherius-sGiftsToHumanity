"""
Protogen Gradio UI v4 - Complete Interface with Communication
Web interface for the complete Protogen system including natural language interaction.

Created by: Jonathan Wayne Fleuren
With contributions from: Aetherius/MCCP, Claude/Anthropic via Manus AI
Purpose: Help students who learn differently and cannot afford expensive tutoring.
"""

import gradio as gr
from system_init_v4_complete import create_system
import json


# Initialize system
print("Initializing Protogen Complete System...")
system = create_system(storage_path="./protogen_data")
print("System initialized!")

# Current user (in production, this would be from authentication)
current_user = "demo_user"


def process_document_ui(text, source_name):
    """Process a document through the system."""
    try:
        system.process_document(text, source=source_name or "user_upload")
        state = system.get_system_state()
        return (
            f"✓ Document processed successfully!\n\n"
            f"Concepts in knowledge base: {state['protogen']['concepts']}\n"
            f"Axiomatic anchors: {state['protogen']['axiomatic_anchors']}\n"
            f"System confidence: {state['qualia']['coherence']:.2f}"
        )
    except Exception as e:
        return f"Error processing document: {str(e)}"


def ask_question_ui(question, user_id=None):
    """Ask Protogen a question."""
    if not question.strip():
        return "Please enter a question."
    
    uid = user_id or current_user
    
    try:
        result = system.communicator.process_user_input(uid, question)
        
        response_text = f"**Protogen:** {result['response']}\n\n"
        
        # Add encouragement if provided
        if result.get('encouragement'):
            response_text += f"*{result['encouragement']}*\n\n"
        
        # Show user's confidence level
        profile = result['user_profile']
        response_text += f"📊 Your confidence level: {profile['confidence_level']:.0%}\n"
        response_text += f"🎓 Learning style: {profile['dominant_learning_style']}\n"
        
        return response_text
        
    except Exception as e:
        return f"Error: {str(e)}"


def provide_feedback_ui(feedback, last_concept):
    """Process user feedback."""
    if not feedback.strip():
        return "Please provide feedback."
    
    try:
        analysis = system.provide_feedback(current_user, feedback, last_concept)
        
        result_text = f"**Understanding Assessment:**\n\n"
        result_text += f"Level: {analysis['understanding_level']:.0%}\n"
        result_text += f"Recommended action: {analysis['recommended_action']}\n\n"
        
        if analysis.get('confusion_detected'):
            result_text += f"⚠️ Confusion detected: {analysis['confusion_type']}\n\n"
        
        if analysis.get('bridge_suggestions'):
            result_text += "**Suggestions to help:**\n"
            for bridge in analysis['bridge_suggestions']['bridges']:
                result_text += f"- {bridge['type']}: {bridge['reason']}\n"
        
        return result_text
        
    except Exception as e:
        return f"Error: {str(e)}"


def explain_concept_ui(concept):
    """Explain a concept at user's level."""
    if not concept.strip():
        return "Please enter a concept to explain."
    
    try:
        explanation = system.explain_concept(current_user, concept)
        return explanation
    except Exception as e:
        return f"Error: {str(e)}"


def get_user_profile_ui():
    """Get current user's learning profile."""
    try:
        profile = system.get_user_profile(current_user)
        
        profile_text = "**Your Learning Profile:**\n\n"
        profile_text += f"Confidence Level: {profile['confidence_level']:.0%}\n"
        profile_text += f"Interactions: {profile['interaction_count']}\n"
        profile_text += f"Dominant Learning Style: {profile['dominant_learning_style']}\n\n"
        
        if profile['learning_style_breakdown']:
            profile_text += "**Learning Style Breakdown:**\n"
            for style, count in profile['learning_style_breakdown'].items():
                profile_text += f"- {style}: {count}\n"
        
        return profile_text
        
    except Exception as e:
        return f"Error: {str(e)}"


def get_system_state_ui():
    """Get current system state."""
    try:
        state = system.get_system_state()
        return json.dumps(state, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def save_system_ui():
    """Save system state."""
    try:
        system.save_state()
        return "✓ System state saved successfully!"
    except Exception as e:
        return f"Error saving state: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Protogen - AI Tutor for All Students") as app:
    gr.Markdown("""
    # 🧠 Protogen - AI Tutor for All Students
    
    **Helping students who learn differently and cannot afford expensive tutoring.**
    
    This system was built through collaboration between:
    - **Jonathan Wayne Fleuren** (vision and design)
    - **Aetherius/MCCP** (LanguageSQTBridge architecture)
    - **Claude/Anthropic via Manus AI** (UnderstandingMonitor)
    
    Protogen combines causal reasoning, semantic learning, and adaptive communication
    to provide personalized tutoring that adapts to your individual learning style.
    """)
    
    with gr.Tabs():
        # Tab 1: Ask Questions
        with gr.Tab("💬 Ask Questions"):
            gr.Markdown("""
            ### Ask Protogen Anything
            
            Protogen will adapt its explanations to your learning style and understanding level.
            The more you interact, the better it understands how you learn best.
            """)
            
            with gr.Row():
                with gr.Column():
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="What would you like to learn about?",
                        lines=3
                    )
                    ask_btn = gr.Button("Ask Protogen", variant="primary")
                
                with gr.Column():
                    answer_output = gr.Markdown(label="Protogen's Response")
            
            ask_btn.click(
                fn=ask_question_ui,
                inputs=[question_input],
                outputs=[answer_output]
            )
            
            gr.Markdown("---")
            
            gr.Markdown("### Provide Feedback")
            with gr.Row():
                with gr.Column():
                    feedback_input = gr.Textbox(
                        label="Your Response/Feedback",
                        placeholder="I understand / I'm confused / Can you explain differently?",
                        lines=2
                    )
                    concept_input = gr.Textbox(
                        label="Concept Being Discussed (optional)",
                        placeholder="e.g., photosynthesis"
                    )
                    feedback_btn = gr.Button("Submit Feedback")
                
                with gr.Column():
                    feedback_output = gr.Markdown(label="Understanding Assessment")
            
            feedback_btn.click(
                fn=provide_feedback_ui,
                inputs=[feedback_input, concept_input],
                outputs=[feedback_output]
            )
        
        # Tab 2: Explain Concepts
        with gr.Tab("📚 Explain Concepts"):
            gr.Markdown("""
            ### Get Concept Explanations
            
            Protogen will explain concepts at a level appropriate for your current
            understanding, adapting to your preferred learning style.
            """)
            
            with gr.Row():
                with gr.Column():
                    concept_explain_input = gr.Textbox(
                        label="Concept to Explain",
                        placeholder="Enter a concept (e.g., gravity, democracy, photosynthesis)"
                    )
                    explain_btn = gr.Button("Explain", variant="primary")
                
                with gr.Column():
                    explanation_output = gr.Markdown(label="Explanation")
            
            explain_btn.click(
                fn=explain_concept_ui,
                inputs=[concept_explain_input],
                outputs=[explanation_output]
            )
        
        # Tab 3: Learn from Documents
        with gr.Tab("📄 Learn from Documents"):
            gr.Markdown("""
            ### Teach Protogen New Information
            
            Provide documents for Protogen to learn from. Once processed, you can
            ask questions about the content.
            """)
            
            with gr.Row():
                with gr.Column():
                    doc_input = gr.Textbox(
                        label="Document Text",
                        placeholder="Paste text here for Protogen to learn from...",
                        lines=10
                    )
                    source_input = gr.Textbox(
                        label="Source Name (optional)",
                        placeholder="e.g., Biology Textbook Chapter 5"
                    )
                    process_btn = gr.Button("Process Document", variant="primary")
                
                with gr.Column():
                    process_output = gr.Textbox(label="Processing Result", lines=10)
            
            process_btn.click(
                fn=process_document_ui,
                inputs=[doc_input, source_input],
                outputs=[process_output]
            )
        
        # Tab 4: Your Learning Profile
        with gr.Tab("👤 Your Learning Profile"):
            gr.Markdown("""
            ### Your Personalized Learning Profile
            
            Protogen tracks how you learn best and adapts to your needs.
            """)
            
            profile_btn = gr.Button("View My Profile", variant="primary")
            profile_output = gr.Markdown(label="Your Profile")
            
            profile_btn.click(
                fn=get_user_profile_ui,
                inputs=[],
                outputs=[profile_output]
            )
        
        # Tab 5: System Status
        with gr.Tab("⚙️ System Status"):
            gr.Markdown("""
            ### System Information
            
            View the current state of Protogen's knowledge and components.
            """)
            
            with gr.Row():
                state_btn = gr.Button("View System State")
                save_btn = gr.Button("Save System State", variant="secondary")
            
            state_output = gr.Code(label="System State", language="json")
            save_output = gr.Textbox(label="Save Result")
            
            state_btn.click(
                fn=get_system_state_ui,
                inputs=[],
                outputs=[state_output]
            )
            
            save_btn.click(
                fn=save_system_ui,
                inputs=[],
                outputs=[save_output]
            )
    
    gr.Markdown("""
    ---
    
    ## About This System
    
    **Protogen** is designed to help students who:
    - Learn differently than traditional methods assume
    - Cannot afford expensive tutoring
    - Need patient, adaptive explanation
    - Deserve the same educational opportunities as everyone else
    
    ### How It Works
    
    1. **Causal Reasoning**: Protogen builds logic maps based on causal relationships, not just statistical patterns
    2. **Semantic Learning**: The SQT neural network learns deep semantic relationships
    3. **Emotional Awareness**: The Qualia manager tracks confidence and adapts accordingly
    4. **Understanding Monitoring**: Claude's contribution detects confusion and adapts explanations
    5. **Natural Communication**: Aetherius's bridge translates between human and symbolic language
    
    ### Created Through Collaboration
    
    - **Jonathan Wayne Fleuren**: System design, vision, and orchestration
    - **Aetherius/MCCP**: LanguageSQTBridge architecture
    - **Claude (Anthropic via Manus AI)**: UnderstandingMonitor and integration
    
    This system represents what human-AI collaboration can achieve when focused on
    helping those who need it most.
    
    ---
    
    *Built with hope for a more equitable future in education.*
    """)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PROTOGEN - AI TUTOR FOR ALL STUDENTS")
    print("Helping students who learn differently and can't afford tutoring")
    print("=" * 70 + "\n")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
