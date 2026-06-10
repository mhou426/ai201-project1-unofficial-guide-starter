# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
This project focuses on the reality of living in Stony Brook University on-campus housing. This knowledge is valuable because the university does not officially disclose issues like mold, pests, thin walls, or unpleasant odors. Students must rely on peer-shared knowledge to learn the truth about these buildings.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RateMyDorm | Chapin (Graduate Housing) review — weekly cleaning, thin walls, no AC, quiet, family-friendly | documents/ratemydorm_chapin.txt (ratemydorm.com) |
| 2 | RateMyDorm | Hendrix College review — close to Javits, has A/C, mold on carpets, first-floor bugs in fall | documents/ratemydorm_hendrix.txt (ratemydorm.com) |
| 3 | RateMyDorm | Lauterbur Hall review — suite-style, good natural light, near West Side Dining | documents/ratemydorm_lauterbur.txt (ratemydorm.com) |
| 4 | RateMyDorm | Toscanini College review — small rooms, slow elevator, far from WSD and LIRR, 4 flights of stairs | documents/ratemydorm_toscanini.txt (ratemydorm.com) |
| 5 | r/SBU | Kelly Quad — black mold on bathroom ceiling, slow RA/facilities response, who to contact | documents/reddit_kelly.txt (reddit.com/r/SBU) |
| 6 | r/SBU | West C Apartments — mold concern, reported as a summer/humidity issue rather than year-round | documents/reddit_westC.txt (reddit.com/r/SBU) |
| 7 | r/SBU | Keller — cricket and spider infestation, suggested fixes (towel, glue traps, work order) | documents/reddit_keller.txt (reddit.com/r/SBU) |
| 8 | r/SBU | Yang Hall — weed smell coming through AC vents, escalation to RA/RHD | documents/reddit_yang.txt (reddit.com/r/SBU) |
| 9 | r/SBU | Yang Hall — ant and spider problem, note that Roosevelt is notorious for bugs | documents/reddit_yang_2.txt (reddit.com/r/SBU) |
| 10 | r/SBU | Cardozo College — persistent putrid outdoor odor near Cardozo and Roth café | documents/reddit_cardozo.txt (reddit.com/r/SBU) |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->


**Chunk size:** ~300–500 characters (roughly 2–4 sentences)

**Overlap:** ~50–100 characters (roughly 1 sentence)

**Reasoning:** Review and forum text packs a complete opinion into 1–3 sentences, so small chunks keep each retrievable thought intact without diluting it. The overlap keeps a fact that straddles a line break from being split across two chunks.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->
**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers, runs locally)

**Top-k:** 4

**Production tradeoff reflection:** For real users I would weigh API-vs-local cost, context length, multilingual support, accuracy on domain-specific slang (dorm and quad names), and latency. MiniLM is free, local, and fast but less accurate than larger paid API models.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which dorms have students reported mold problems in? | Kelly (black mold on bathroom ceiling), West C (mold during summer due to humidity), and Hendrix (mold on the carpets). Sources: reddit_kelly, reddit_westC, ratemydorm_hendrix. |
| 2 | What should I do if I find mold in my dorm? | Contact the area office in person; SBU is slow to respond so be persistent; stay out of the affected room until it's handled. Source: reddit_kelly. |
| 3 | Which dorm has good natural light? | Lauterbur Hall — reviewers note the rooms get pretty good natural light. Source: ratemydorm_lauterbur. |
| 4 | Is mold in West Apartments a year-round problem? | No — it is mainly a summer issue caused by high humidity; students living there during the school year report no real problems. Source: reddit_westC. (Likely failure case: retrieval may oversimplify the seasonal nuance.) |
| 5 | Which dorms have bug problems, and what can I do about them? | Keller (crickets and spiders), Yang/Roosevelt (ants and spiders; Roosevelt is notorious), and Hendrix (first-floor bugs in early fall). Fixes mentioned: towel under the door, glue traps, submit a work order, or call the exterminator/FixIt. Sources: reddit_keller, reddit_yang_2, ratemydorm_hendrix. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Reddit threads often drift off-topic, which may pull irrelevant chunks into results. Retrieval may also oversimplify nuanced situations, such as the seasonal nature of mold in West C. 

2. Finally, because the corpus is small, some queries rely on only a single supporting source.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
   (.txt files in        (custom        (all-MiniLM-L6-v2    (top-4 by      (Groq
   documents/,           chunker,        → ChromaDB)         cosine          llama-3.3-70b,
   loaded + cleaned)     ~300–500 char)                      similarity)     grounded prompt)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** I will give Claude my Documents and Chunking Strategy sections and ask it to implement a script that loads the .txt files from documents/, attaches the source filename as metadata, and splits each document into ~300–500 character chunks with ~1 sentence of overlap. I will verify by printing 5 sample chunks and checking they are self-contained and correctly attributed.

**Milestone 4 — Embedding and retrieval:** I will give Claude my Retrieval Approach section and ask it to embed the chunks with all-MiniLM-L6-v2, store them in ChromaDB with source metadata, and write a retrieval function returning the top-4 chunks with distance scores. I will verify by querying 3 of my evaluation questions and confirming the returned chunks are relevant and score below ~0.5.

**Milestone 5 — Generation and interface:** I will give Claude my grounding requirement (answer only from retrieved chunks, cite sources, refuse when context is insufficient) and ask it to wire Groq generation plus a Gradio interface. I will verify by testing an in-scope query, checking the cited source matches the answer, and testing an out-of-scope query to confirm the system refuses rather than inventing an answer.
