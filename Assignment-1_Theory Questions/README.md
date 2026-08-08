# NLP, RAG, Docker, and AI Agents — Questions & Answers

This document gives short, practical explanations of several core ideas in natural language processing and modern AI systems.

## 1. What is tokenization?

Tokenization is the process of splitting text into smaller units called **tokens**. A token may be a full word, part of a word, a number, or a punctuation mark. Models work with token IDs rather than raw sentences, so tokenization prepares the text for processing.

For example, one possible tokenization of:

```text
I'm learning NLP in 2025!
```

is:

```python
["I", "'m", "learning", "NLP", "in", "2025", "!"]
```

The exact result can differ between tokenizers. Some may keep `I'm` as one token, while others may divide it into smaller subword pieces.

---

## 2. What is the difference between stemming and lemmatization?

Both techniques reduce words to simpler forms, but they use different methods.

**Stemming** applies basic rules to remove prefixes or suffixes. It is quick, although the result is not always a valid dictionary word.

- `running` → `run`
- `better` → `better` in many common stemmers, because it is irregular

**Lemmatization** uses vocabulary and grammatical information to find the correct base form, known as a lemma.

- `running` → `run`
- `better` → `good` when the word is treated as an adjective

Lemmatization generally preserves more linguistic meaning because it considers the role and meaning of the word, not only its spelling.

---

## 3. What does TF-IDF stand for?

**TF-IDF** stands for **Term Frequency–Inverse Document Frequency**. It estimates how useful a word is in one document compared with an entire collection of documents.

The word `the` usually receives a score close to zero because it appears in nearly every kind of document. Since it is so common, it provides very little information about the document's subject.

The word `photosynthesis` is much less common. If it appears several times in one document but rarely across the rest of the collection, it will receive a higher score and strongly suggest that the document discusses plants or biology.

---

## 4. What is a sentence embedding?

A sentence embedding is a compact numerical vector designed to represent the meaning of a complete sentence.

One-hot encoding works differently. It creates a long, mostly empty vector in which one position represents one vocabulary item. It records identity, but it does not naturally represent relationships between words or sentences.

Embeddings make similarity comparisons possible. For instance, vectors for `The doctor examined the patient` and `A physician checked the patient` should be relatively close, even though the sentences do not use exactly the same words. One-hot vectors do not capture that relationship directly.

---

## 5. What is cosine similarity?

Cosine similarity compares the direction of two vectors rather than focusing on their total size. It measures the angle between them.

If two document vectors point in almost the same direction, the documents probably contain similar topics or meaning. A value close to `1` indicates strong similarity, while a value closer to `0` indicates little similarity.

Euclidean distance can sometimes be less suitable for text because it is affected by vector magnitude. A long article and a short summary may discuss the same subject but still have different vector lengths.

---

## 6. Why is `LIKE '%pizza%'` not enough for semantic search?

A query such as:

```sql
WHERE description LIKE '%pizza%'
```

looks for the exact character sequence `pizza`. It may miss a description such as `wood-fired Italian food with tomato and mozzarella`, even though the meaning is closely related.

A vector index supports efficient similarity search over embeddings. The query is converted into a vector, and the index retrieves document vectors that are nearest to it. This allows the system to find related content even when the wording is different. Vector search can also be combined with normal SQL filters, such as date, category, or user ID.

---

## 7. What problem does RAG solve?

**Retrieval-Augmented Generation (RAG)** helps a language model answer questions using information that was not included in its original training data. This is useful for private, recent, or frequently updated material. It also gives the model relevant evidence to use instead of relying only on memory.

For example, imagine a university publishes a new course handbook this week. A plain LLM may not know its updated attendance rules. With RAG, the handbook can be indexed, the relevant section can be retrieved, and that text can be supplied to the model before it answers.

RAG is the better choice when an answer must be grounded in a specific set of documents rather than in general knowledge alone.

---

## 8. What are the main steps in a RAG pipeline?

### Ingestion time

This stage usually happens when documents are first added or updated.

1. **Chunk:** Split each document into smaller sections.
2. **Embed:** Convert every chunk into a numerical vector.
3. **Store:** Save the vectors, text, and useful metadata in a searchable database.

### Query time

This stage runs whenever a user submits a question.

1. **Embed the query:** Convert the question into a vector using a compatible embedding model.
2. **Retrieve:** Search for the chunks whose vectors are most similar to the query vector.
3. **Generate:** Send the question and retrieved context to the LLM so it can produce a grounded answer.

---

## 9. What is the difference between a Docker image and a Docker container?

A **Docker image** is a fixed package containing the application, its dependencies, and the instructions needed to run it. A **Docker container** is a running instance created from that image.

A useful analogy is a blueprint and a building. The image is the blueprint: it describes what should be created. The container is the actual building produced from it. Multiple containers can be started from the same image, just as the same blueprint can be used to construct several similar buildings.

---

## 10. How is an AI agent with tools different from a simple LLM chatbot?

A simple LLM chatbot mainly generates a response from the conversation and its trained knowledge. An AI agent can decide to use external tools, inspect the result, and continue through several steps before giving its final response.

One example is a database tool. If a user asks, `How many orders were placed today?`, the agent can run an approved query against the current database and answer using live results. Without that tool, the model could explain how to write the query but would not know the real number.

Tools make an agent more capable because they let it access current information and perform actions beyond text generation.

---

## 11. What is MCP?

**MCP** stands for **Model Context Protocol**. It is a shared protocol that lets AI applications connect to external tools and data sources through a consistent interface.

For a coding assistant, MCP reduces the need to build a completely different integration for every service. Once an MCP server describes the capabilities it provides, a compatible assistant can discover and use them under the permissions available to it.

An MCP server might expose:

- A repository tool that lists issues or reads selected project files.
- A database tool that shows schemas and runs permitted queries.

MCP acts like a common connector between the AI assistant and the systems around it.

---

## 12. What are Agent Skills?

Agent Skills are reusable packages of instructions and optional resources that teach an AI coding assistant how to handle a particular type of task. A skill can include a workflow, domain rules, scripts, references, or templates.

A normal prompt usually provides instructions for one conversation. A skill is reusable: the assistant can select it when its metadata matches the user's request and then load the detailed instructions only when they are relevant. This keeps the main prompt smaller and makes repeated tasks more consistent.

A minimal `SKILL.md` may begin with YAML metadata like this:

```yaml
---
name: mongodb-query-optimizer
description: Analyze slow MongoDB queries and recommend indexes. Use when a user asks why a MongoDB query is slow or how to improve its performance.
---
```

The rest of the file would contain the actual workflow the assistant should follow. The metadata helps the system decide when the skill is appropriate, while the body provides the detailed instructions after the skill is selected.
