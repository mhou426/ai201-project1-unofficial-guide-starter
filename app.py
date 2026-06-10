import gradio as gr
from query import ask


def answer_question(question: str):
    if not question or not question.strip():
        return "", ""
    result = ask(question.strip())
    return result["answer"], "\n".join(result["sources"])


if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("# RAG Question Answering")
        question = gr.Textbox(lines=2, placeholder="Ask a question about the documents...", label="Question")
        answer = gr.Textbox(lines=10, label="Answer")
        sources = gr.Textbox(lines=5, label="Sources")
        ask_btn = gr.Button("Ask")
        ask_btn.click(fn=answer_question, inputs=question, outputs=[answer, sources])
    demo.launch()
