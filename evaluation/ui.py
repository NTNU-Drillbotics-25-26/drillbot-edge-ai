"""Gradio web UI for interactive evaluation testing."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import gradio as gr
except ImportError:
    print("Gradio not installed. Install with: pip install gradio>=4.0")
    sys.exit(1)

from .providers import OllamaLocalProvider, OllamaRemoteProvider, OpenAIProvider
from .runner import retrieve_context, build_prompt, chunks_to_dicts
from .questions import QUICK_TEST, BASIC_QUESTIONS, ALL_QUESTIONS
from .config import OPENAI_API_KEY, PI_HOST


# Initialize providers
providers = {
    "ollama_local": OllamaLocalProvider(),
    "openai": OpenAIProvider(api_key=OPENAI_API_KEY if OPENAI_API_KEY else None),
    "ollama_remote": OllamaRemoteProvider(host=PI_HOST),
}


def check_provider_status():
    """Check which providers are available."""
    status = []
    for name, provider in providers.items():
        available = provider.is_available()
        icon = "✓" if available else "✗"
        status.append(f"{icon} {name} ({provider.model_name})")
    return "\n".join(status)


def run_evaluation(
    question: str,
    use_ollama_local: bool,
    use_openai: bool,
    use_ollama_remote: bool,
    retrieval_mode: str,
):
    """Run evaluation on a single question."""
    if not question.strip():
        return "Please enter a question.", "", "", ""

    # Get retrieval mode (import here to defer app loading)
    from app.hybrid import RetrievalMode
    mode = RetrievalMode(retrieval_mode)

    # Retrieve context (shared)
    chunks, retrieval_ms, mode_str, use_hybrid = retrieve_context(
        question, mode=mode, limit=1
    )
    chunk_dicts = chunks_to_dicts(chunks, use_hybrid)
    prompt = build_prompt(question, chunks, use_hybrid=use_hybrid)

    # Format chunks display
    chunks_display = f"**Retrieval** ({mode_str}, {retrieval_ms:.0f}ms)\n\n"
    if chunk_dicts:
        for i, c in enumerate(chunk_dicts, 1):
            chunks_display += f"**{i}. {c.get('title', 'untitled')}** (score: {c.get('score', 0):.2f})\n"
            text = c.get('text', '')[:300]
            chunks_display += f"```\n{text}...\n```\n\n"
    else:
        chunks_display += "No chunks retrieved."

    results = []

    # Run selected providers
    selected = []
    if use_ollama_local:
        selected.append(providers["ollama_local"])
    if use_openai:
        selected.append(providers["openai"])
    if use_ollama_remote:
        selected.append(providers["ollama_remote"])

    if not selected:
        return chunks_display, "No providers selected.", "", ""

    outputs = []
    for provider in selected:
        if not provider.is_available():
            outputs.append(f"**{provider.name}** ({provider.model_name})\n\n*Not available*\n\n---\n")
            continue

        response = provider.generate(prompt)

        if response.error:
            outputs.append(
                f"**{provider.name}** ({provider.model_name})\n\n"
                f"*Error: {response.error}*\n\n---\n"
            )
        else:
            outputs.append(
                f"**{provider.name}** ({provider.model_name})\n"
                f"*{response.inference_ms:.0f}ms*\n\n"
                f"{response.text}\n\n---\n"
            )

    # Split into columns (up to 2)
    col1 = outputs[0] if len(outputs) > 0 else ""
    col2 = outputs[1] if len(outputs) > 1 else ""
    col3 = outputs[2] if len(outputs) > 2 else ""

    return chunks_display, col1, col2, col3


def load_question_set(set_name: str):
    """Load a predefined question set."""
    sets = {
        "Quick Test (3)": QUICK_TEST,
        "Basic (5)": BASIC_QUESTIONS,
        "All (13)": ALL_QUESTIONS,
    }
    questions = sets.get(set_name, QUICK_TEST)
    return "\n".join(questions)


def create_ui():
    """Create the Gradio interface."""
    with gr.Blocks(title="Drillbot RAG Evaluation") as app:
        gr.Markdown("# Drillbot RAG Evaluation")
        gr.Markdown("Compare LLM responses across different providers.")

        with gr.Row():
            with gr.Column(scale=2):
                question_input = gr.Textbox(
                    label="Question",
                    placeholder="How do I start a manual run?",
                    lines=2,
                )
                with gr.Row():
                    submit_btn = gr.Button("Ask", variant="primary")
                    clear_btn = gr.Button("Clear")

            with gr.Column(scale=1):
                gr.Markdown("**Providers**")
                ollama_local_cb = gr.Checkbox(label="Ollama Local", value=True)
                openai_cb = gr.Checkbox(label="OpenAI", value=True)
                ollama_remote_cb = gr.Checkbox(label="Ollama Remote (Pi)", value=False)

                retrieval_mode = gr.Radio(
                    choices=["fts", "hybrid", "embed"],
                    value="fts",
                    label="Retrieval Mode",
                )

        with gr.Row():
            status_btn = gr.Button("Check Provider Status", size="sm")
            status_output = gr.Textbox(label="Status", lines=3, interactive=False)

        gr.Markdown("---")

        chunks_output = gr.Markdown(label="Retrieved Chunks")

        with gr.Row():
            response1 = gr.Markdown(label="Response 1")
            response2 = gr.Markdown(label="Response 2")
            response3 = gr.Markdown(label="Response 3")

        gr.Markdown("---")
        gr.Markdown("### Test Questions")

        with gr.Row():
            question_set = gr.Dropdown(
                choices=["Quick Test (3)", "Basic (5)", "All (13)"],
                value="Quick Test (3)",
                label="Question Set",
            )
            load_btn = gr.Button("Load Questions")
            questions_output = gr.Textbox(label="Questions", lines=5, interactive=False)

        # Event handlers
        submit_btn.click(
            run_evaluation,
            inputs=[question_input, ollama_local_cb, openai_cb, ollama_remote_cb, retrieval_mode],
            outputs=[chunks_output, response1, response2, response3],
        )

        clear_btn.click(
            lambda: ("", "", "", "", ""),
            outputs=[question_input, chunks_output, response1, response2, response3],
        )

        status_btn.click(check_provider_status, outputs=[status_output])

        load_btn.click(load_question_set, inputs=[question_set], outputs=[questions_output])

    return app


def main():
    """Launch the UI."""
    app = create_ui()
    print("Starting Drillbot RAG Evaluation UI...")
    print("Open http://localhost:7860 in your browser")
    app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
