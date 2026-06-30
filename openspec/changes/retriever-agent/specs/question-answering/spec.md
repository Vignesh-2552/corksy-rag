## ADDED Requirements

### Requirement: Synchronous question answering
The system SHALL expose `POST /api/v1/ask` that accepts a question and returns a complete answer with source references in a single JSON response.

#### Scenario: Successful answer with sources
- **WHEN** a client sends `POST /api/v1/ask` with `{"question": "What is the return policy?", "session_id": "abc", "top_k": 5}`
- **THEN** the system returns HTTP 200 with `{"answer": "<text>", "sources": [...], "session_id": "abc"}`

#### Scenario: No relevant documents found
- **WHEN** a client asks a question that matches no indexed content
- **THEN** the system returns HTTP 200 with a graceful fallback message in `answer` and an empty `sources` array

#### Scenario: Missing required field
- **WHEN** a client sends `POST /api/v1/ask` without the `question` field
- **THEN** the system returns HTTP 422 with a validation error

---

### Requirement: Streaming question answering
The system SHALL expose `POST /api/v1/ask/stream` that streams answer tokens as Server-Sent Events (SSE).

#### Scenario: Successful streaming response
- **WHEN** a client sends `POST /api/v1/ask/stream` with a valid `AskRequest`
- **THEN** the system returns `Content-Type: text/event-stream` and emits `data: <token>\n\n` lines until the answer is complete

#### Scenario: Stream ends with done event
- **WHEN** the LLM finishes generating
- **THEN** the system emits a final `data: [DONE]\n\n` event and closes the stream

---

### Requirement: Source references in response
The system SHALL include source references for every chunk used to generate the answer.

#### Scenario: Source fields are populated
- **WHEN** the retrieval step returns at least one chunk
- **THEN** each `SourceReference` in the response MUST include `doc_id`, `source_file`, `score` (cosine similarity, float 0–1), and `snippet` (first 200 chars of chunk text)

---

### Requirement: Configurable retrieval depth
The `AskRequest` SHALL accept an optional `top_k` integer (default `5`, min `1`, max `20`) controlling how many chunks are retrieved from Qdrant.

#### Scenario: Default top_k used when omitted
- **WHEN** a client sends `POST /api/v1/ask` without `top_k`
- **THEN** the system retrieves 5 chunks

#### Scenario: Custom top_k respected
- **WHEN** a client sends `top_k: 10`
- **THEN** the system retrieves up to 10 chunks from Qdrant
