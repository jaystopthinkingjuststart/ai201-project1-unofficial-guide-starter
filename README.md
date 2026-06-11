# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

     I chose professor and class reviews at my university. Iowa State University.

Officially no college would tell you students like X or dislike Y about professors or classes. So I took a wide variety of sources so when a student or incoming student asks questions they can get real answers grounded in truth!

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors, ISU overall | Review aggregator (ratings) | https://www.ratemyprofessors.com/school/452 |
| 2 | Rate My Professors, all ISU professors | Review aggregator (per-professor) | https://www.ratemyprofessors.com/search/professors/452?q=* |
| 3 | Coursicle, ISU professors | Review aggregator (course-linked) | https://www.coursicle.com/iastate/professors/ |
| 4 | Uloop, ISU professors | Review aggregator | https://iastate.uloop.com/professors |
| 5 | ISU CS Department faculty list | Official names to courses reference | https://www.cs.iastate.edu/people/faculty |
| 6 | r/iastate, recommended classes | Reddit thread | https://www.reddit.com/r/iastate/comments/1spwunn/ |
| 7 | r/iastate, best professors | Reddit thread | https://www.reddit.com/r/iastate/comments/1al3k6c/ |
| 8 | r/iastate, worst professors | Reddit thread | https://www.reddit.com/r/iastate/comments/1akvev2/ |
| 9 | r/iastate, CprE professors to avoid | Reddit thread | https://www.reddit.com/r/iastate/comments/1isfle3/ |
| 10 | r/iastate, fun category classes | Reddit thread | https://www.reddit.com/r/iastate/comments/1gadbt6/ |
| 11 | r/iastate, simple/fun classes | Reddit thread | https://www.reddit.com/r/iastate/comments/k8kqz0/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** one chunk per review or comment. I split on blank lines so each chunk is basically one opinion. if a single comment is really long (over 600 chars) it falls back to a 400 char window with 50 overlap.

**Overlap:** 50 characters, but only for that long comment fallback. separate reviews are their own opinions so overlapping between them doesn't really make sense.

**Why these choices fit your documents:** my docs are mostly short reviews and reddit comments so I wanted one chunk to be about one opinion. I first tried a fixed 400 char window but when I looked at the output it was cutting reviews in half and mashing two professors together, which is the opposite of what I wanted. splitting on blank lines fixed that and also dropped a lot of the random username lines on its own.

**Preprocessing before chunking:** I decode html entities like &amp; and &#39;, strip any html tags, and pull out the reddit and RMP junk like "2y ago", "u/name avatar", bullets, "4 more replies", and the RMP rating labels. then I just collapse the extra whitespace.

**Final chunk count:** 433 chunks across 11 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

Model used: all-MiniLM-L6-v2 (sentence-transformers) — local, no API key, strong on short informal text.

Production tradeoff: it's great for being free and fast and it runs right on my machine with no rate limits, but it misses sentiment and nuance that bigger paid models pick up on. if cost wasn't a thing I'd probably look at something like OpenAI's text-embedding-3-large or Voyage or Cohere instead. the things I'd weigh are how well it reads sarcastic or opinionated student writing, whether it can handle longer context so a whole review fits in one vector, and the latency and api dependency you take on by going hosted instead of local. given my main problem was sentiment (see the failure case) I'd lean toward whichever model is best at telling positive from negative, even if it's slower.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** I tell the model to only answer from the reviews I give it and not use anything it already knows about ISU. since reviews are opinions and disagree a lot, I also tell it to report the consensus like "several students say" or "one reviewer mentions" instead of stating one person's take as fact, and to name the actual professor or class. if the reviews don't cover the question it has to say "I don't have enough information on that in the collected ISU reviews." instead of guessing. on top of that I filter weak matches out before the model even sees them, so anything with a distance over 0.55 gets dropped and an uncovered question ends up with no context, which triggers the fallback.

**How source attribution is surfaced in the response:** I don't trust the model to cite, I do it in code. ask() grabs the source filenames from exactly the chunks that made it past the distance filter and into the prompt, then shows them in the "Retrieved from" box. that way the sources you see are always the ones the answer actually came from.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professors do ISU students name as the best, and in what subjects? | names from the best professors thread like Steve Butler and Matthew Tancreti | listed Butler, Tancreti, Simanta Mitra, Michael Bailey, Jeremy Shaeffer, said the subjects were often not mentioned | Relevant | Accurate |
| 2 | Which CprE professors do students say to avoid, and why? | names and reasons from the CprE to avoid thread, including Jim Lathrop (condescending and disorganized) | named Dr. Daniels (just a preference) and the Palo Alto / CprE 326 guy, missed Jim Lathrop, and pulled in some recommendation chunks | Partially relevant | Partially accurate |
| 3 | What are some fun, easy category/gen-ed classes students recommend? | specific classes from the simple and category threads like Sleep & Dreams and easy gen eds | recommended gen eds like history and government, Sleep & Dreams, and the Life Long Leisure Skills category | Relevant | Accurate |
| 4 | What class do students recommend taking regardless of major, and why? | a class and the reason from the recommended classes thread | philosophy because it "makes you think", History of Greece and Rome, and a diffusion of innovation grad class | Relevant | Accurate |
| 5 | What do students say about Professor Steve Butler? | a summary of Butler's reviews | only got "The one and only STEVE BUTLER", so positive but no real detail | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "which Computer Engineering (CprE) professors do students say to avoid, and why?" (Q2)

**What the system returned:** it named Dr. Daniels but said that was just a preference and not bad teaching, plus an unnamed professor from the "Palo Alto / CprE 326" story. it completely missed the clearest avoid review in my docs, which was "stay away from Jim (James) Lathrop. He's condescending and incredibly unorganized." it also pulled in chunks that were actually recommending professors.

**Root cause (tied to a specific pipeline stage):** this is a retrieval and embedding problem. all-MiniLM-L6-v2 embeds based on topic, not whether something is positive or negative, so a chunk praising CprE professors sits really close to one saying to avoid them because they're both "about CprE professors." back in milestone 4 the top results for this query were positive recommendations around 0.38 distance while the "stay away from Lathrop" review was further down around 0.46. with top-k=5 the context got watered down with positive chunks so the model gave a muddled answer. generation can't fix something retrieval barely pulled up.

**What you would change to fix it:** I'd either use an embedding model that picks up sentiment better or add some keyword signal so "avoid/worst/stay away" reviews rank higher on negative questions. raising top-k or adding a little re-ranking would also help so the strongest negative review doesn't get crowded out. I could also tag the worst professors and CprE to avoid threads so negative queries lean toward them.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** writing out my chunking strategy and the challenges before coding gave me something concrete to aim at. my whole "one chunk is about one opinion" idea and my worry about chunk boundaries messing up attribution were exactly the things I looked for when I inspected the chunks in milestone 3. so when I saw reviews getting split in half I already knew it broke my own plan and what I needed to change.

**One way your implementation diverged from the spec, and why:** my plan was a fixed 400 character sliding window with 50 overlap. once I actually looked at the chunks, that window was cutting reviews mid sentence and jamming two professors into one chunk, which is the opposite of one opinion per chunk. so I switched to splitting on blank lines instead and only kept the 400/50 window as a backup for really long comments, then updated planning.md to explain why.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1: chunking**

- *What I gave the AI:* my chunking strategy section from planning.md (400 char window, 50 overlap, lots of short reviews) and a few of my actual documents.
- *What it produced:* an ingest.py that loads, cleans, and chunks the docs with the sliding window I asked for, plus a step that prints 5 chunks and the total count so I could check it.
- *What I changed or overrode:* when I looked at the chunks they were getting cut mid sentence and a bunch of usernames were sneaking in. so I had it switch to splitting on blank lines instead and add cleaning rules for the reddit junk like "2y ago" and "u/name avatar". I basically overrode my own original plan after seeing the real output.

**Instance 2: retrieval and generation**

- *What I gave the AI:* my retrieval approach section (all-MiniLM-L6-v2, ChromaDB, top-k=5) and my grounding rules (only answer from the context, report consensus, cite sources).
- *What it produced:* a retriever.py that embeds and queries ChromaDB for the top chunks, and generator.py and app.py with the grounded prompt and a gradio interface.
- *What I changed or overrode:* I made it do the source citations in code from the chunks that actually passed my distance filter instead of trusting the model to cite, and I added a 0.55 distance cutoff so weak matches never reach it. I checked grounding by asking something not in my docs and making sure it gave the fallback.
