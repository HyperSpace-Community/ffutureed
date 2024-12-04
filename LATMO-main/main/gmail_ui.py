import gradio as gr
import json
from typing import Dict, Any, Optional, List
import os
from app import (
    create_gmail_draft_wrapper,
    send_gmail_message_wrapper,
    search_gmail_wrapper,
    get_gmail_message_wrapper,
    get_gmail_thread_wrapper,
    lazy_gmail_toolkit
)

def initialize_gmail():
    """Initialize Gmail toolkit and return status."""
    try:
        if not lazy_gmail_toolkit.is_ready():
            lazy_gmail_toolkit.load_gmail_toolkit()
            return "Gmail toolkit initialized successfully!"
        return "Gmail toolkit already initialized!"
    except Exception as e:
        return f"Error initializing Gmail toolkit: {str(e)}"

def compose_email(
    to: str,
    subject: str,
    message: str,
    html_content: str,
    cc: str,
    bcc: str,
    attachments: List[str],
    action: str
) -> str:
    """Compose and send/draft an email based on user input."""
    try:
        email_data = {
            "to": to,
            "subject": subject,
            "message": message,
        }
        
        if html_content.strip():
            email_data["html_content"] = html_content
        if cc.strip():
            email_data["cc"] = cc
        if bcc.strip():
            email_data["bcc"] = bcc
        if attachments:
            email_data["attachments"] = [file.name for file in attachments]
            
        if action == "Send":
            return send_gmail_message_wrapper(json.dumps(email_data))
        else:
            return create_gmail_draft_wrapper(json.dumps(email_data))
    except Exception as e:
        return f"Error: {str(e)}"

def search_emails(
    query: str,
    max_results: int,
    include_spam_trash: bool,
    newer_than: str,
    older_than: str,
    has_attachment: bool
) -> str:
    """Search emails with advanced filters."""
    try:
        search_data = {
            "query": query,
            "max_results": max_results,
            "include_spam_trash": include_spam_trash,
            "newer_than": newer_than if newer_than else None,
            "older_than": older_than if older_than else None,
            "has_attachment": has_attachment
        }
        return search_gmail_wrapper(json.dumps(search_data))
    except Exception as e:
        return f"Error: {str(e)}"

def view_email(message_id: str) -> str:
    """View a specific email message."""
    try:
        return get_gmail_message_wrapper(json.dumps({"message_id": message_id}))
    except Exception as e:
        return f"Error: {str(e)}"

def view_thread(thread_id: str) -> str:
    """View a specific email thread."""
    try:
        return get_gmail_thread_wrapper(json.dumps({"thread_id": thread_id}))
    except Exception as e:
        return f"Error: {str(e)}"

def create_ui() -> gr.Blocks:
    """Create the Gradio UI interface."""
    with gr.Blocks(title="Gmail Tools") as app:
        gr.Markdown("# Gmail Tools")
        
        with gr.Tab("Initialize"):
            gr.Markdown("### Initialize Gmail Toolkit")
            init_btn = gr.Button("Initialize Gmail")
            init_output = gr.Textbox(label="Initialization Status")
            init_btn.click(fn=initialize_gmail, outputs=init_output)
        
        with gr.Tab("Compose Email"):
            gr.Markdown("### Compose and Send/Draft Email")
            with gr.Row():
                with gr.Column():
                    to_input = gr.Textbox(label="To", placeholder="recipient@example.com")
                    subject_input = gr.Textbox(label="Subject")
                    message_input = gr.Textbox(label="Message", lines=5)
                    html_input = gr.Textbox(label="HTML Content (optional)", lines=5)
                with gr.Column():
                    cc_input = gr.Textbox(label="CC (optional)", placeholder="cc1@example.com, cc2@example.com")
                    bcc_input = gr.Textbox(label="BCC (optional)", placeholder="bcc1@example.com, bcc2@example.com")
                    attachments_input = gr.File(label="Attachments", file_count="multiple")
                    action_input = gr.Radio(choices=["Send", "Draft"], label="Action", value="Draft")
            
            compose_btn = gr.Button("Compose Email")
            compose_output = gr.Textbox(label="Status")
            
            compose_btn.click(
                fn=compose_email,
                inputs=[
                    to_input, subject_input, message_input, html_input,
                    cc_input, bcc_input, attachments_input, action_input
                ],
                outputs=compose_output
            )
        
        with gr.Tab("Search"):
            gr.Markdown("### Search Emails")
            with gr.Row():
                with gr.Column():
                    query_input = gr.Textbox(label="Search Query")
                    max_results_input = gr.Slider(minimum=1, maximum=100, value=10, label="Max Results")
                    include_spam_input = gr.Checkbox(label="Include Spam/Trash")
                with gr.Column():
                    newer_than_input = gr.Textbox(label="Newer Than (e.g., 2d, 1w)", placeholder="2d")
                    older_than_input = gr.Textbox(label="Older Than (e.g., 1w, 1m)", placeholder="1w")
                    has_attachment_input = gr.Checkbox(label="Has Attachment")
            
            search_btn = gr.Button("Search")
            search_output = gr.Textbox(label="Search Results", lines=10)
            
            search_btn.click(
                fn=search_emails,
                inputs=[
                    query_input, max_results_input, include_spam_input,
                    newer_than_input, older_than_input, has_attachment_input
                ],
                outputs=search_output
            )
        
        with gr.Tab("View Message/Thread"):
            gr.Markdown("### View Email Message or Thread")
            with gr.Row():
                with gr.Column():
                    message_id_input = gr.Textbox(label="Message ID")
                    view_message_btn = gr.Button("View Message")
                with gr.Column():
                    thread_id_input = gr.Textbox(label="Thread ID")
                    view_thread_btn = gr.Button("View Thread")
            
            view_output = gr.Textbox(label="Content", lines=10)
            
            view_message_btn.click(fn=view_email, inputs=message_id_input, outputs=view_output)
            view_thread_btn.click(fn=view_thread, inputs=thread_id_input, outputs=view_output)
        
        gr.Markdown("### Note")
        gr.Markdown("""
        - Make sure to initialize Gmail toolkit first
        - For date filters, use format like '2d' (2 days), '1w' (1 week), '1m' (1 month)
        - HTML content is optional and will override plain text message if provided
        - Attachments are limited to 25MB per file
        """)
    
    return app

def main():
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)

if __name__ == "__main__":
    main()
