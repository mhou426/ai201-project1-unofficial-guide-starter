import os
from dotenv import load_dotenv
from groq import Groq
from embed import retrieve

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask(question: str):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set in .env")

    chunks = retrieve(question, k=4)
    sources = []
    for c in chunks:
        if c["source"] not in sources:
            sources.append(c["source"])

    context = "\n\n".join(f"SOURCE: {c['source']}\n{c['text']}" for c in chunks)
    system_prompt = (
        "You are a retrieval-augmented assistant. "
        "Answer ONLY using the provided context. "
        "If the answer is not in the context, respond exactly: "
        "I don't have enough information on that."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=512,
    )
    answer = response.choices[0].message.content.strip()
    if not answer:
        answer = "I don't have enough information on that."
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    out = ask("Which dorms have mold problems?")
    print(out["answer"])
    print("Sources:", out["sources"])
