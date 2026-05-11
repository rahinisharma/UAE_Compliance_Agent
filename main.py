import os
import gradio as gr
from main_engine import UAEComplianceEngine

# Initialize engine
engine = UAEComplianceEngine()

# Favicon Setup
logo_path = os.path.abspath("logo.png")

# --- THE MATTE CHARCOAL CSS ---
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap');

footer {visibility: hidden !important}

/* 1. Global Layout */
.gradio-container {
    background-color: #111111 !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}

/* 2. TOTAL SILENCE: KILL ALL LOADING SQUARES AND "PROCESSING" TEXT */
.loader, .generating, .progress-parent, .loading, .meta-text, .meta-text-center, .status-text {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
[data-testid="block-info"], .show-api, .wrap.loading { display: none !important; }

/* 3. CLOAKING THE INTERACTION BUTTONS */
.gr-button-container, .download-button, .share-button, .fullscreen-button, 
.icon-button, .retry-button, .undo-button, .clear-button { 
    display: none !important; 
}

.sidebar-logo {
    margin-bottom: 25px !important;
    display: flex !important;
    justify-content: center !important;
}

/* 4. Rounded Buttons & Inputs */
.primary-btn {
    background-color: #2a2a2a !important; 
    border: 1px solid #3a3a3a !important;
    color: white !important;
    border-radius: 12px !important;
    cursor: pointer;
}
.primary-btn:hover { background-color: #333333 !important; }

.rounded-search {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 15px !important;
    padding: 10px 20px !important;
}

/* 5. Typography */
.answer-heading {
    font-family: 'Source Serif 4', serif !important;
    color: #ffffff !important;
    font-size: 2rem !important;
    text-align: center;
    padding: 20px 0;
}

.sidebar-sources {
    background-color: #0d0d0d !important;
    border-right: 1px solid #2a2a2a !important;
    padding: 25px 15px !important;
}

.history-item {
    font-size: 0.85rem !important;
    color: #888888 !important;
    line-height: 1.6 !important;
    margin-bottom: 8px !important;
}

.law-bullets {
    font-size: 0.88rem !important;
    color: #cccccc !important;
    line-height: 2.0 !important;
}

#chatbot-window { background: transparent !important; border: none !important; }
"""

# App State
initial_history = [{"role": "assistant", "content": "Hello! What can I help you with?"}]
history_log = []

def chat_logic(message, history):
    if not message:
        return message, history, gr.update()
    
    bot_response = engine.get_legal_answer(message)
    
    if len(history) == 1 and history[0]["content"] == "Hello! What can I help you with?":
        history = []

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": bot_response})
    
    history_log.insert(0, f"• {message}")
    history_display = "\n\n".join(history_log[:10])
    
    return message, history, history_display

def clear_input():
    return ""

def reset_chat():
    return initial_history, "", gr.update()

with gr.Blocks(title="UAE Compliance Engine") as demo:
    
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["sidebar-sources"]):
            gr.Image("logo.png", width=120, show_label=False, container=False, interactive=False, elem_classes=["sidebar-logo"])
            
            gr.Markdown("### Legal Scope")
            gr.Markdown(
                """
                • Law 47/2022 (Tax)  
                • Law 45/2021 (Privacy)  
                • NESA Regulation  
                • AI Ethics Charter
                """,
                elem_classes=["law-bullets"]
            )
            
            gr.HTML("<hr style='border: 0.1px solid #2a2a2a; margin: 25px 0;'>")
            
            gr.Markdown("### History")
            history_list = gr.Markdown("No history yet.", elem_classes=["history-item"])
            
            new_thread_btn = gr.Button("＋ New Thread", variant="secondary", elem_classes=["primary-btn"])

        with gr.Column(scale=4):
            gr.Markdown("# UAE Compliance Engine", elem_classes=["answer-heading"])
            
            chatbot = gr.Chatbot(value=initial_history, show_label=False, container=False, elem_id="chatbot-window")
            
            with gr.Row(elem_classes=["rounded-search"]):
                msg = gr.Textbox(placeholder="Ask a compliance question...", container=False, scale=10)
                submit_btn = gr.Button("➤", scale=1, elem_classes=["primary-btn"])

    # --- LOGIC FLOW: ENTER KEY & CLICK BINDING ---
    
    # 1. ENTER KEY (msg.submit)
    submit_event = msg.submit(chat_logic, [msg, chatbot], [msg, chatbot, history_list], show_progress="hidden")
    submit_event.then(clear_input, None, [msg])
    
    # 2. SEND BUTTON (submit_btn.click)
    click_event = submit_btn.click(chat_logic, [msg, chatbot], [msg, chatbot, history_list], show_progress="hidden")
    click_event.then(clear_input, None, [msg])

    new_thread_btn.click(reset_chat, None, [chatbot, msg, history_list], show_progress="hidden")

if __name__ == "__main__":
    demo.launch(share=True, css=custom_css, favicon_path=logo_path, allowed_paths=[os.getcwd()])