"""
app.py — Milestone 5: end-to-end query + Gradio interface.

ask() ties the pipeline together: retrieve -> filter weak matches -> generate.
Source attribution is programmatic — the sources shown are exactly the chunks
that fed the answer, so attribution can't drift from what the LLM did.

Run:  python app.py   (then open http://localhost:7860)
"""

import gradio as gr
from retriever import retrieve, ingest_if_empty
from generator import generate_response

# Drop chunks weaker than this before they reach the LLM. Tuned from Milestone 4:
# real matches scored 0.19–0.46; off-topic queries land above ~0.6.
DISTANCE_CUTOFF = 0.55


def ask(question):
    """Full pipeline. Returns {'answer': str, 'sources': list[str]}."""
    if not question or not question.strip():
        return {"answer": "Ask a question about ISU professors or classes.", "sources": []}

    chunks = retrieve(question)
    relevant = [c for c in chunks if c["distance"] <= DISTANCE_CUTOFF]
    answer = generate_response(question, relevant)
    sources = sorted({c["source"] for c in relevant})
    return {"answer": answer, "sources": sources}


def handle_query(question):
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sufficiently relevant sources)"
    return result["answer"], sources


with gr.Blocks(title="ISU Unofficial Guide") as demo:
    gr.Markdown(
        "# 🎓 ISU Unofficial Guide\n"
        "Ask about Iowa State professors and classes — answers come **only** from "
        "real student reviews (Rate My Professors, Coursicle, r/iastate)."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which professors do students recommend?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    ingest_if_empty()   # ensure the vector store is populated before serving
    demo.launch()
