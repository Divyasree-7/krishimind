"""
KrishiMind — Agentic AI for Smallholder Farmer Resilience
Main entry point: launches the Gradio chat UI.
"""
from ui.app import build_ui

if __name__ == "__main__":
    app = build_ui()
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)
    print("\nKrishiMind is running at http://localhost:7860\n")
