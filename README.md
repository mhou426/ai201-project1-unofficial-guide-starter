# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

A Retrieval-Augmented Generation (RAG) system that answers plain-language questions about living in Stony Brook University on-campus housing, grounded in real student reviews and Reddit threads.
---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
This system covers the lived reality of SBU on-campus housing, mold, pests, noise, natural light, odors, and the practical question of what to do when something goes wrong. This knowledge is valuable because the university does not officially disclose these problems; nothing in the housing portal will tell you which dorm has black mold or which building is known for bugs. Students learn it only from each other, scattered across reviews and forum threads, which makes it hard to find and easy to miss when choosing where to live.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->
Documents were collected manually, since both Reddit and RateMyDorm are JavaScript-rendered and resist automated scraping.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | RateMyDorm | Dorm review | documents/ratemydorm_chapin.txt (ratemydorm.com) |
| 2 | RateMyDorm | Dorm review | documents/ratemydorm_hendrix.txt (ratemydorm.com) |
| 3 | RateMyDorm | Dorm review | documents/ratemydorm_lauterbur.txt (ratemydorm.com) |
| 4 | RateMyDorm | Dorm review | documents/ratemydorm_toscanini.txt (ratemydorm.com) |
| 5 | r/SBU | Reddit thread | documents/reddit_kelly.txt (reddit.com/r/SBU — "Black Mold") |
| 6 | r/SBU | Reddit thread | documents/reddit_westC.txt (reddit.com/r/SBU — mold in West Apartments) |
| 7 | r/SBU | Reddit thread | documents/reddit_keller.txt (reddit.com/r/SBU — bugs in Keller) |
| 8 | r/SBU | Reddit thread | documents/reddit_yang.txt (reddit.com/r/SBU — weed smell through vents) |
| 9 | r/SBU | Reddit thread | documents/reddit_yang_2.txt (reddit.com/r/SBU — ants and spiders) |
| 10 | r/SBU | Reddit thread | documents/reddit_cardozo.txt (reddit.com/r/SBU — outdoor odor) |

The sources cover a deliberate spread of subtopics: mold (Kelly, West C, Hendrix), pests (Keller, Yang, Roosevelt), odors (Cardozo, Yang), room quality and light (Lauterbur, Toscanini, Chapin), and the logistics of reporting problems.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** ~300–500 characters (roughly 2–4 sentences).

**Overlap:** ~75 characters (roughly one sentence).

**Why these choices fit your documents:** The documents are short, single reviews and brief forum posts where a complete opinion usually fits in one to three sentences. Small chunks keep each retrievable thought intact instead of diluting it with unrelated content, which matters for opinion-based text where one sentence often carries the whole answer. The overlap is meant to keep a fact that straddles a line break from being split cleanly between two chunks. Before chunking, I removed boilerplate from each document: Reddit sidebars, moderator lists, rules, footer links, and reCAPTCHA text, and RateMyDorm ads and navigation, keeping only titles, post bodies, substantive comments, and the dorm name, which appears on the first line of each file for attribution.

**Final chunk count:** 21 chunks across the 10 documents. The count is low because several documents were short enough to remain nearly whole after chunking, a point that turned out to matter for retrieval (see Failure Case).

---

### Sample Chunks

**Chunk 1 — ratemydorm_chapin.txt**
> Chapin (Graduate Housing) Thankfully a cleaning crew comes every week to maintain communal areas like taking out trash, recycling, vacuuming, and cleaning the bathrooms. You keep your own room clean. The bedroom carpets are nasty. You can request them to be deep cleaned or buy a rug. The bathrooms and kitchen are dated. You share with roommates. No washing machine. Washer and dryers are available for students. There is a small playground for families with kids.

**Chunk 2 — ratemydorm_chapin.txt**
> ...There is a small playground for families with kids. The 'common area' has a gym, a mini self-service shop, study area with two private rooms to study in, two printers, and a package room. Students who require a handicapped accessible bathroom stall with a shower can find these bathrooms in the commons if they are unable to book a dorm with an accessible bathroom.

**Chunk 3 — ratemydorm_hendrix.txt**
> Hendrix College Roth quad is the nicest and closest dorm to the academic buildings for lower-classman. Most of the buildings in the quad have A/C. Hendrix is the closest to Javits (literally can roll out of bed 10 mins. before class). The building layout is more open than other buildings (like Gershwin and Whitman). The common lounge is nice when you want to watch movies with your friends. I also think Hendrix is the only building in the quad that has a functioning elevator for daily use.

**Chunk 4 — ratemydorm_hendrix.txt**
> ...the only building in the quad that has a functioning elevator for daily use. Only con is the mold problem on the carpets. Chose the second floor if you don't want bugs during the beginning of the fall semester.

**Chunk 5 — reddit_kelly.txt**
> Kelly Quad — "Black Mold" — Yoo I'm in Kelly quad and we have black mold on our ceiling in the bathroom (we discovered it on Friday) and the RA said "well good luck- no one go in there. They can fix it on Monday". I think that's unacceptable... Does anyone know who to contact for like a complaint. My roommate has been sick and lowkey it may be because of that mold.

---

## Retrieval Test Examples

These examples show the top chunks returned by the retriever (top k = 4) for three test queries, identified by their source files.

**Query 1: "Which dorm has good natural light?"**
Retrieved: ratemydorm_lauterbur.txt, ratemydorm_hendrix.txt, ratemydorm_chapin.txt, ratemydorm_toscanini.txt
Relevance: The Lauterbur chunk explicitly states the rooms get good natural light, which directly answers the query. The other dorm reviews were pulled because they share vocabulary about room conditions, so they sit close in the embedding space even though Lauterbur is the one that answers the question.

**Query 2: "What should I do if I find mold in my dorm?"**
Retrieved: reddit_kelly.txt, reddit_westC.txt
Relevance: The Kelly thread contains the procedural advice the query asks for, such as contacting the area office and being persistent. The West C thread was retrieved because it also discusses mold, so both chunks land close to the query in the embedding space.

**Query 3: "Which dorms have bug problems, and what can I do about them?"**
Retrieved: reddit_yang_2.txt, reddit_keller.txt, reddit_kelly.txt
Relevance: The Yang and Keller chunks directly describe the infestations and suggested fixes that the query asks about, making them strong matches. The Kelly chunk is a weaker match, retrieved because it shares the broad theme of reporting a dorm problem rather than mentioning bugs specifically.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2, via sentence-transformers, with chunks stored in a local ChromaDB collection. It runs locally with no API key or rate limits, which suits a small free-tier project.

**Production tradeoff reflection:** For a real deployment serving live users, I would weigh several factors when choosing a model. Accuracy on domain-specific text matters most here, the corpus is full of dorm and quad names (Roth, H-quad, Lauterbur) that a general-purpose model may not embed precisely, and a larger paid model would likely distinguish them better. I would also weigh context length, since longer reviews could be embedded whole rather than split; multilingual support, if the student body writes in more than one language; and the latency and cost of an API-hosted model against the privacy and zero-cost of running locally. MiniLM trades some accuracy for being free, fast, and self-contained, which is the right tradeoff for this project but not necessarily for production.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The model (llama-3.3-70b-versatile via Groq, temperature 0) is instructed to answer using only the provided context, and if the context does not contain the answer, to reply exactly "I don't have enough information on that." The retrieved chunks are passed in as clearly labeled context blocks, each prefixed with its source, so the model can only draw on what was retrieved rather than its general training knowledge. Temperature 0 keeps answers consistent and reduces the chance of the model embellishing beyond the context.

**How source attribution is surfaced in the response:** Attribution is handled structurally, not left to the model. After retrieval, the system collects the source filename from each retrieved chunk's metadata, de-duplicates them, and returns them alongside the answer. Because the source list is built programmatically from what was actually retrieved, every response is guaranteed to show its sources rather than relying on the LLM to cite them correctly.

---

## Query Interface

The interface is a Gradio web application launched with python app.py. It has one input field, a Question textbox for plain-language questions, and two output fields: an Answer box showing the grounded response and a Sources box listing the document filenames the answer drew from. The user types a question, clicks Ask, and reviews the answer and its sources.

Sample interaction:

Question: What should I do if I find mold in my dorm?
Answer: Contact the area office in person, and if they don't respond quickly, hassle them until they fix the issue. It's also suggested to try to be outside of your dorm as much as possible until the issue is resolved.
Sources: reddit_kelly.txt, reddit_westC.txt

Screenshots of the running interface are included in the repository.

---

## Example Responses

**In-scope example 1**
Question: Which dorm has good natural light?
Answer: Lauterbur Hall has pretty good natural light that comes into the room.
Sources: ratemydorm_lauterbur.txt, ratemydorm_hendrix.txt, ratemydorm_chapin.txt, ratemydorm_toscanini.txt

**In-scope example 2**
Question: Is mold in West Apartments a year-round problem?
Answer: No, according to the context, mold in West Apartments is primarily an issue during the summertime due to high humidity, and not typically a problem during the school year.
Sources: reddit_westC.txt, reddit_kelly.txt, ratemydorm_hendrix.txt

**Out-of-scope example**
Question: What's the best parking garage on campus?
Answer: I don't have enough information on that.
Evaluation: The system correctly declined to answer, since no document in the corpus covers parking. This confirms the grounding instruction is working: instead of inventing an answer from general knowledge, the system returned its fallback response.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which dorms have students reported mold problems in? | Kelly, West C, and Hendrix | Named West C and an "unnamed" dorm from the Kelly source; did not name Kelly or include Hendrix | Partially relevant | Partially accurate |
| 2 | What should I do if I find mold in my dorm? | Contact the area office in person, be persistent, stay out of the room | Contact the area office, hassle them until fixed, stay outside the dorm as much as possible | Relevant | Accurate |
| 3 | Which dorm has good natural light? | Lauterbur | "Lauterbur Hall has pretty good natural light that comes into the room." | Relevant | Accurate |
| 4 | Is mold in West Apartments a year-round problem? | No, mainly a summer/humidity issue | "No... primarily an issue during the summertime due to high humidity, and not typically a problem during the school year." | Relevant | Accurate |
| 5 | Which dorms have bug problems, and what can I do about them? | Keller, Yang/Roosevelt; fixes include work orders, traps, exterminator | Named Yang, Keller, and Roosevelt; suggested exterminator, reporting to management, staying out of the dorm | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target

**Response accuracy:** Accurate / Partially accurate / Inaccurate

Four of five questions returned accurate, well-grounded answers. Question 1 was only partially accurate, which is analyzed below.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Which dorms have students reported mold problems in?"

**What the system returned:** It named West C Apartments correctly but referred to the Kelly source as "another dorm (unnamed)," even though that document is titled "Kelly Quad," and it omitted Hendrix's carpet mold entirely. The expected answer was Kelly, West C, and Hendrix.

**Root cause (tied to a specific pipeline stage):** This is a chunking-and-retrieval failure, not a generation failure. First, chunk boundaries split the building name from the problem: in the Hendrix document, the name "Hendrix" sits in chunk 3 while the mold mention ("Only con is the mold problem on the carpets") sits in chunk 4, so any chunk carrying the mold fact may not carry the dorm name. The same pattern affected Kelly, where the retrieved chunk contained the mold description without the clearly attached building name. Second, the corpus is small, only 21 chunks, and with top-k set to 4, retrieval surfaced the two strongest mold signals (Kelly and West C) but never pulled the Hendrix mold chunk into the context window, so the model had no way to mention it.

**What you would change to fix it:** I would switch to a sentence-aware splitter that keeps each dorm's name attached to its associated facts within the same chunk, and I would either raise top-k or store the dorm name as metadata on every chunk so it is always available for attribution regardless of where the boundary falls.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the chunking and retrieval sections of planning.md before any code meant I could hand an AI tool a precise specification, chunk size, overlap, top-k, and embedding model, rather than a vague request. The generated pipeline matched my intended design closely because the spec told it exactly what to build, which saved time I would otherwise have spent correcting generic code.

**One way your implementation diverged from the spec, and why:** I planned for a corpus of many small chunks, but because my source documents were so short, the pipeline produced only 21 chunks, with several documents staying nearly whole. This meant retrieval often pulled entire documents rather than targeted passages, and the character-based overlap occasionally cut mid-sentence. This divergence directly contributed to the Question 1 failure, and it is something I would address by collecting longer documents or refining the splitter.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My planning.md chunking and retrieval sections, plus my architecture diagram, with a request to generate the full pipeline, ingestion, chunking, embedding, ChromaDB storage, retrieval, generation, and the Gradio interface.
- *What it produced:* Four working files, but the first version used outdated ChromaDB APIs (`chroma_db_impl="duckdb+parquet"` and `client.persist()`) and called a non-existent Groq "responses" endpoint with custom response-parsing logic.
- *What I changed or overrode:* I tested each file rather than trusting the output, found both bugs at runtime, and replaced them with the current ChromaDB `PersistentClient` API and Groq's standard `chat.completions.create` call. I verified the fix by running the pipeline end to end until it returned a correctly grounded answer with sources.

**Instance 2**

- *What I gave the AI:* Rough ideas for evaluation questions and my list of 10 documents, asking it to help turn them into specific, verifiable test questions.
- *What it produced:* A set of candidate questions with suggested expected answers mapped to my documents.
- *What I changed or overrode:* I reviewed each against my actual corpus and kept only those with clear ground-truth answers. I deliberately retained Question 4 (seasonal West C mold) as a nuance test and Question 1 (mold across multiple documents) because I anticipated it might expose a retrieval weakness, directing which questions to keep rather than accepting the full set.
