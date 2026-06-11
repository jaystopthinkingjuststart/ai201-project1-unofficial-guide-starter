# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

I chose professor and class reviews at my university. Iowa State University.

Officially no college would tell you students like X or dislike Y about professors or classes. So I took a wide variety of sources so when a student or incoming student asks questions they can get real answers grounded in truth!

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | ISU Rate my professors | overall school-wide ratings | https://www.ratemyprofessors.com/school/452 |
| 2 | Rate My Professors, all ISU professors | Searchable list of every rated prof | https://www.ratemyprofessors.com/search/professors/452?q=* |
| 3 | Coursicle for isu | Reviews tied to the exact courses each professor teaches | https://www.coursicle.com/iastate/professors/ |
| 4 | Uloop for isu | Second review aggregator for cross-coverage of the same profs | https://iastate.uloop.com/professors |
| 5 | ISU CS Department faculty | Official names to courses map, so i can look up the right professors | https://www.cs.iastate.edu/people/faculty |
| 6 | reddit recommended classes | Threads debating best classes regardless of major | https://www.reddit.com/r/iastate/comments/1spwunn/whats_a_class_at_iowa_state_that_youd_recommend/ |
| 7 | reddit best professors | favorite professors across departments | https://www.reddit.com/r/iastate/comments/1al3k6c/best_professors_at_isu/ |
| 8 | reddit worst professors  | professors to watch out for | https://www.reddit.com/r/iastate/comments/1akvev2/worst_professors_at_isu/ |
| 9 | reddit cpre professors to avoid | Which cpre professors to take/avoid | https://www.reddit.com/r/iastate/comments/1isfle3/professors_to_stay_away_from_compe/ |
| 10 | reddit category classes recommended | top category classes recommended | https://www.reddit.com/r/iastate/comments/1gadbt6/any_fun_category_classes/ |
| 11 | reddit simple classes recommended | simple classes recommended by other students | https://www.reddit.com/r/iastate/comments/k8kqz0/what_are_some_fun_simple_classes_youve_taken/ |


---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 chars

**Overlap:** 50 chars

**Reasoning:** Definitely review heavy, mostly short and consistent self contained opinions and messages. I want each chunk to be about one opinion roughly. Longer chunks may accidentally merge multiple professors or classes.

I ended up switching from the fixed 400 char sliding window to boundary based chunking (one chunk per comment, split on blank lines) after I looked at the output. the sliding window was cutting reviews mid sentence which goes against my one chunk is about one opinion goal. the 50 char overlap now only kicks in as a backup when a single comment is over 600 chars. final chunk count was 433.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-minilm-l6-v2 

**Top-k:** 5

**Production tradeoff reflection:** this is the free one i have access to right now, but if cost wasn't an issue I may consider a more expensive model that is trained on a bigger set of data that could handle student language and sarcasm/insults better and subtle meaning that may not always be proper grammar. top 5 allows for sentiment aggregation and trust rather than "1 person said xyz"

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which professors do ISU students name as the best, and in what subjects? | (from row 7 thread — list the professors actually named) |
| 2 | Which Computer Engineering (CPR E) professors do students say to avoid, and why? | (from row 9 thread — the prof names + reasons given) |
| 3 | What are some fun, easy "category"/gen-ed classes students recommend? | (from rows 10 & 11 — the specific classes mentioned) |
| 4 | What class do students recommend taking regardless of major, and why? | (from row 6 — the class + the reason students give) |
| 5 | What do students say about [a specific professor with several RMP reviews]'s grading? | (from rows 1 to 4, summarize that prof's reviews) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. I'm worried about contradictory reviews confusing the model as opposed to being seen as subjective inputs. Or old reviews or professors that have changed courses and may have been good at one course but data hasn't been updated for a new course they're bad at

2. Chunking boundaries could cause an issue with attribution and association (He is very good... bleeding into another that says she is very bad)

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->


┌─────────────────────┐   ┌──────────────┐   ┌────────────────────────┐   ┌──────────────┐   ┌──────────────────┐
│ 1. Doc Ingestion    │   │ 2. Chunking  │   │ 3. Embedding + Vector  │   │ 4. Retrieval │   │ 5. Generation    │
│                     │──▶│              │──▶│    Store               │──▶│              │──▶│                  │
│ .txt files in       │   │ char window  │   │ all-MiniLM-L6-v2       │   │ ChromaDB     │   │ Groq LLM         │
│ documents/ (RMP,    │   │ 400 chars,   │   │ (sentence-transformers)│   │ query,       │   │ (llama-3.x),     │
│ Reddit, Coursicle), │   │ 50 overlap;  │   │ → ChromaDB persistent  │   │ cosine,      │   │ grounded prompt  │
│ Python file reader  │   │ +prof/course │   │ collection (cosine)    │   │ top-k = 5    │   │ → Gradio UI      │
│                     │   │ name prefix  │   │                        │   │              │   │                  │
└─────────────────────┘   └──────────────┘   └────────────────────────┘   └──────────────┘   └──────────────────┘

Thank you genai for the beautiful ascii that would've taken me 500000 years
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

**Milestone 3, ingestion and chunking:**
Tool: Claude Code. I gave it my chunking strategy section plus a couple of my real documents so it could see what the reviews actually look like. I asked it to write the loader that reads every file in documents/ and a chunk function using my size and overlap, with the source name attached to each chunk. to check it I ran it on a reddit file and an RMP file, printed the chunks, and made sure the reviews stayed in one piece and kept their source label.

**Milestone 4, embedding and retrieval:**
Tool: Claude Code. I gave it my retrieval approach section and asked it to embed the chunks with all-MiniLM-L6-v2, store them in a persistent ChromaDB collection using cosine, and write a retrieve() that returns the top 5 chunks with their text, source, and distance. to check it I ran my first eval question, printed the 5 results with distances, and confirmed the closest chunks were actually about the professors named in that thread.

**Milestone 5, generation and interface:**
Tool: Claude Code. I gave it my evaluation plan and my grounding rules, which are answer only from the retrieved reviews, report the consensus, and say so when the reviews don't cover it. I asked it to write a grounded generate_response() and a gradio interface. to check it I ran all 5 eval questions and also asked something that isn't in my docs to make sure it gave the fallback instead of making something up.
