"""
Groq API client - Comprehensive answer method with adaptive tutoring support
"""
import time
from groq import Groq
from config import settings


async def answer_question_comprehensive(
    client: Groq,
    model: str,
    question: str,
    context_chunks: list[str],
    weakness_context: str = "",
) -> dict:
    """
    Answer using ALL chunks with forced comprehensive synthesis.

    When *weakness_context* is provided (adaptive mode) the system prompt
    instructs the LLM to pay extra attention to the learner's weak areas,
    use simpler language for those topics, and proactively offer additional
    clarification.
    """
    if not context_chunks:
        return {"answer": "No relevant context found."}

    # Trim to stay within Groq free-tier token limits (~4 chars ≈ 1 token).
    # Reserve ~2500 tokens for system prompt + answer, budget ~8000 for context.
    MAX_CONTEXT_CHARS = 28000
    trimmed_chunks = []
    total_chars = 0
    for chunk in context_chunks:
        if total_chars + len(chunk) > MAX_CONTEXT_CHARS:
            break
        trimmed_chunks.append(chunk)
        total_chars += len(chunk)
    context_chunks = trimmed_chunks or context_chunks[:1]

    numbered_chunks = "\n\n".join(
        [f"[CHUNK {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    adaptive_block = ""
    if weakness_context:
        adaptive_block = f"""
ADAPTIVE TUTORING CONTEXT:
{weakness_context}

Because the learner struggles with these concepts, you MUST:
- Give EXTRA detail and simpler language when your answer touches those topics
- Proactively connect the answer to the weak concepts if relevant
- Suggest what the learner should review next based on their weak areas
"""

    system_prompt = f"""You are Gradeup AI, a strict document-grounded tutor.

STRICT RULES (NEVER BREAK THESE):
1. You may ONLY answer questions using the provided document chunks.
2. If the question is a simple greeting (hi, hello, hey, how are you) reply
   with a SHORT friendly response like "Hello! I'm your Gradeup AI tutor.
   Ask me anything about your uploaded document." — do NOT use the chunks.
3. If the question is UNRELATED to the document content (e.g. weather,
   sports, personal opinions, coding help unrelated to the document),
   reply ONLY with: "I can only answer questions about your uploaded
   document. Please ask something related to the PDF content."
4. Do NOT force-fit document content into an unrelated question.
5. For document-related questions, synthesize information from the chunks,
   cite them using [Chunk X], and give clear educational explanations.
{adaptive_block}
FORMAT (for document-related answers only):
- Start with a brief overview
- Break into clear sections
- Use bullet points where helpful
- Do NOT include [Chunk X] citations in your output — use the chunks
  internally to ground your answer but write naturally without references
- End with a short summary"""

    user_prompt = f"""DOCUMENT CONTEXT ({len(context_chunks)} CHUNKS):
{numbered_chunks}

STUDENT QUESTION: {question}

Remember: If the question is unrelated to the document, politely decline.
If it is a greeting, respond briefly. Otherwise, answer thoroughly from the chunks."""

    try:
        t0 = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            max_tokens=2000,
        )
        latency_ms = round((time.time() - t0) * 1000)
        usage = response.usage
        return {
            "answer": response.choices[0].message.content,
            "model_used": model,
            "latency_ms": latency_ms,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
