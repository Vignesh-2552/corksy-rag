## ADDED Requirements

### Requirement: LangGraph stateful RAG workflow
The system SHALL implement a LangGraph `StateGraph` with a typed `RAGState` that carries `session_id`, `question`, `top_k`, `retrieved_docs`, `answer`, and `sources` across nodes.

#### Scenario: State initialised correctly
- **WHEN** the workflow is invoked with `{"session_id": "x", "question": "Q", "top_k": 5}`
- **THEN** `retrieved_docs`, `answer`, and `sources` start as empty / default values

---

### Requirement: Retrieve node
The `retrieve` node SHALL embed the question using the same `HuggingFaceEmbeddings` model used during indexing and search Qdrant for the top-K most similar chunks.

#### Scenario: Chunks returned
- **WHEN** `retrieve` runs with a question that matches indexed content
- **THEN** `state["retrieved_docs"]` contains up to `top_k` `Document` objects with `page_content` and `metadata` (including `source_file`, `score`)

#### Scenario: No chunks returned
- **WHEN** `retrieve` runs and Qdrant returns zero results
- **THEN** `state["retrieved_docs"]` is an empty list

---

### Requirement: Conditional routing after retrieve
After `retrieve`, the workflow SHALL route to `generate` if documents were found, or to `fallback` if the list is empty.

#### Scenario: Route to generate
- **WHEN** `retrieved_docs` is non-empty
- **THEN** the next node executed is `generate`

#### Scenario: Route to fallback
- **WHEN** `retrieved_docs` is empty
- **THEN** the next node executed is `fallback`

---

### Requirement: Generate node
The `generate` node SHALL construct a prompt from the retrieved chunks and call the injected LLM to produce an answer.

#### Scenario: Answer generated with context
- **WHEN** `generate` runs with non-empty `retrieved_docs`
- **THEN** `state["answer"]` contains the LLM response and `state["sources"]` contains a `SourceReference` for each chunk

#### Scenario: System prompt constrains the LLM
- **WHEN** `generate` calls the LLM
- **THEN** the system message instructs the model to answer ONLY from the provided context and say "I don't know" if the answer is not present

---

### Requirement: Fallback node
The `fallback` node SHALL set a fixed graceful message when no documents are found.

#### Scenario: Fallback message returned
- **WHEN** `fallback` runs
- **THEN** `state["answer"]` is `"I couldn't find relevant information for your question. Please contact our support team for help."` and `state["sources"]` is empty
