"""
generator.py — Milestone 5: grounded answer generation.

Takes a user question plus the chunks retrieved for it and asks the LLM to
answer using ONLY those chunks. Reviews are opinions that often disagree, so
the prompt also tells the model to report consensus rather than assert one
opinion as fact (planning.md challenge #1).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"   # Groq free tier (planning.md)

_client = Groq(api_key=GROQ_API_KEY)

FALLBACK = "I don't have enough information on that in the collected ISU reviews."

SYSTEM_PROMPT = (
    "You are an assistant that answers questions about Iowa State University "
    "professors and classes using ONLY the student reviews provided as context. "
    "Rules:\n"
    "1. Use only the information in the context. Do NOT use any outside knowledge "
    "about ISU, its professors, or its classes.\n"
    "2. Student reviews are opinions and often disagree. Report the consensus and "
    "note disagreement (e.g. 'several students say…', 'one reviewer mentions…'). "
    "Do not present a single opinion as established fact.\n"
    "3. Name the specific professor(s) or class(es) the reviews refer to.\n"
    "4. If the context does not contain enough information to answer, reply exactly: "
    f"\"{FALLBACK}\" Do not guess or invent details."
)


def generate_response(query, retrieved_chunks):
    """Return a grounded answer string built only from retrieved_chunks.

    Returns the fallback string (not an error) when no chunks are supplied —
    the caller is expected to have already filtered out weak matches.
    """
    if not retrieved_chunks:
        return FALLBACK

    # Each chunk's text already carries its [source] prefix from ingest.py.
    context = "\n\n---\n\n".join(c["text"] for c in retrieved_chunks)
    user_message = f"Context (student reviews):\n{context}\n\nQuestion: {query}"

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content
