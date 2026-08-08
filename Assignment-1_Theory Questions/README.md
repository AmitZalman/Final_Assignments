# NLP, RAG, Docker, and AI Agents — Q&A

Here are my explanations of some basic topics from NLP and AI.

## 1. What is tokenization?

Tokenization basically means breaking text into smaller pieces that a model can work with. These pieces are called tokens. A token can be a whole word, part of a word, a number, or even punctuation.

For example, the sentence:

```text
I'm learning NLP in 2025!
```

could be split like this:

```python
["I", "'m", "learning", "NLP", "in", "2025", "!"]
```

This is only one possible result. Different tokenizers may split the same sentence in slightly different ways.

## 2. What is the difference between stemming and lemmatization?

Both of them try to reduce a word to a simpler form, but they do it differently.

Stemming uses simple rules to cut endings from words. It is fast, but sometimes the result is not a real word or is not the correct base form.

- `running` → `run`
- `better` → `better` in many stemmers, since it is an irregular word

Lemmatization is more careful. It uses vocabulary and grammar to find the word's actual dictionary form.

- `running` → `run`
- `better` → `good`, when `better` is being used as an adjective

So, lemmatization usually keeps more of the original meaning. Stemming is simpler and faster, but also less accurate.

## 3. What does TF-IDF stand for?

TF-IDF stands for **Term Frequency–Inverse Document Frequency**.

The easiest way to understand it is that it asks two things: How often does this word appear in the current document, and how rare is it in the rest of the documents?

The word `the` gets a very low score because it appears almost everywhere. It does not tell us much about the topic. On the other hand, `photosynthesis` may get a high score if it appears several times in one document but hardly appears in the others. That would be a good clue that the document is about biology or plants.

## 4. What is a sentence embedding?

A sentence embedding is a list of numbers that represents the general meaning of a sentence.

One-hot encoding is much more basic. It gives every word its own position in a large vector, with a `1` in that position and `0` everywhere else. This shows which word is present, but it does not really understand relationships between words.

For example, the sentences `I bought a new car` and `I purchased a new vehicle` have almost the same meaning. A good embedding should place them close together. One-hot encoding does not naturally understand that `car` and `vehicle` are related.

That ability to compare meaning is one of the main advantages of embeddings.

## 5. What is cosine similarity?

I think of each vector as an arrow. Cosine similarity checks the angle between two arrows instead of only checking how long they are.

If two document vectors point in almost the same direction, it usually means the documents are about similar things. A score close to `1` means they are very similar, while a score around `0` means there is not much similarity.

Euclidean distance can be less useful for text because it also cares about the size of the vectors. Because of that, a long article and a short summary of the same article might look farther apart than expected.

## 6. Why can't `LIKE '%pizza%'` perform semantic search?

This SQL query:

```sql
WHERE description LIKE '%pizza%'
```

only looks for the exact text `pizza`. It will not automatically find something like `an Italian restaurant serving tomato, cheese, and wood-fired dishes`, even though that description may clearly be related.

A vector index works with embeddings instead of only matching letters. It compares the meaning of the search query with the stored documents and quickly returns the closest matches. Normal SQL filters are still useful, and they can be used together with vector search.

## 7. What problem does RAG solve?

A normal LLM does not automatically know about private files or information published after its training. It can also answer confidently even when it does not have enough information.

RAG, which stands for **Retrieval-Augmented Generation**, first searches a selected collection of documents for relevant information. It then gives that information to the LLM together with the user's question.

For example, suppose a school changed its exam rules this week. A plain LLM may not know about the update. With RAG, the new rules can be stored and retrieved, so the answer is based on the actual document.

I would choose RAG when the answer needs to come from specific material, such as company documents, course notes, support guides, or updated policies.

## 8. What are the main steps in a RAG pipeline?

There are two parts: preparing the documents and answering a question.

### Ingestion time

This happens when the documents are added to the system:

1. **Chunk:** Break each document into smaller sections.
2. **Embed:** Turn every section into a vector.
3. **Store:** Save the text, vectors, and useful details such as the document name or page number.

### Query time

This happens whenever the user asks something:

1. **Embed the question:** Turn the user's question into a vector.
2. **Retrieve:** Find the stored chunks that are most similar to that vector.
3. **Generate:** Give the question and retrieved chunks to the LLM so it can write an answer based on them.

In short, the documents are prepared in advance, but retrieval and generation happen again for every question.

## 9. What is the difference between a Docker image and a Docker container?

A Docker image is the packaged setup for an application. It contains the code, dependencies, and configuration needed to run it. A container is what you get when that image is actually running.

One way to picture it is a game installation and a game session. The image is like the installation package, while the container is a running session created from it. You can start several separate containers from the same image.

## 10. How is an AI agent with tools different from a simple LLM chatbot?

A basic LLM chatbot mainly reads a message and writes a response. An agent can also decide to use tools, check the result, and continue with another step if needed.

For example, a calendar tool could let an agent check available times and create a meeting after receiving permission. Without the tool, the chatbot could suggest a time or explain how to create the meeting, but it could not check the real calendar or add the event itself.

The tools are what allow the agent to work with live information and do more than just generate text.

## 11. What is MCP?

MCP stands for **Model Context Protocol**. It gives AI applications a standard way to connect to outside tools and sources of information.

Without a common protocol, developers may need to create a different custom integration for every database, issue tracker, or file system. MCP gives those systems a shared way to describe what they offer, which makes them easier for compatible assistants to use.

For example, an MCP server could provide:

- Access to issues and project information from an issue tracker.
- Access to database schemas and approved queries.

The simplest analogy is a common adapter: the assistant still needs permission to use each system, but it does not need a completely new connection method every time.

## 12. What are Agent Skills?

Agent Skills are reusable instruction packages for AI assistants. They are a bit like playbooks for specific jobs. A skill can contain steps to follow, useful scripts, reference material, or templates.

A normal prompt is usually written for one request. A skill can be reused whenever a matching task comes up. The assistant first sees the skill's name and description, and if the skill is relevant, it loads the full instructions.

A basic `SKILL.md` metadata block could look like this:

```yaml
---
name: mongodb-query-optimizer
description: Analyze slow MongoDB queries and recommend useful indexes. Use when a user asks why a MongoDB query is slow or how to improve its performance.
---
```

The rest of the file would explain the actual process the assistant should follow. The metadata helps it decide when the skill is relevant, so the user does not need to paste the same long instructions every time.
