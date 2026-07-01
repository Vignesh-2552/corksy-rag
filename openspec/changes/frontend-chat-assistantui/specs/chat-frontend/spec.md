## ADDED Requirements

### Requirement: Chat page route
The frontend SHALL expose a `/chat` route that renders a full-page conversational interface for asking questions against the RAG backend.

#### Scenario: Chat page loads
- **WHEN** a user navigates to `/chat`
- **THEN** the page SHALL display a message thread area, a composer input, and a send button

#### Scenario: Empty state shown
- **WHEN** no messages have been sent in the current session
- **THEN** the thread SHALL display a welcome or placeholder message prompting the user to ask a question

---

### Requirement: Streaming answer display
The chat UI SHALL stream assistant responses token-by-token using the backend `POST /api/v1/ask/stream` SSE endpoint.

#### Scenario: User sends a question
- **WHEN** the user types a question and submits the composer
- **THEN** the user's message SHALL appear in the thread immediately and the assistant response SHALL begin streaming without a full-page reload

#### Scenario: Stream completes
- **WHEN** the SSE stream emits `data: [DONE]`
- **THEN** the assistant message SHALL be marked complete and the composer SHALL be re-enabled for the next question

#### Scenario: No documents found
- **WHEN** the backend stream returns a fallback message with no retrieved documents
- **THEN** the fallback text SHALL be displayed as the assistant message in the thread

---

### Requirement: Source citation display
The chat UI SHALL display source references returned by the backend when available.

#### Scenario: Sources shown after answer
- **WHEN** the backend returns source references for a question
- **THEN** the UI SHALL render each source with `source_file`, relevance `score`, and a text `snippet`

#### Scenario: No sources available
- **WHEN** the backend returns an empty `sources` array
- **THEN** the UI SHALL omit the sources section without error

---

### Requirement: Session continuity
The chat UI SHALL maintain a `session_id` across messages within a browser session.

#### Scenario: Session ID generated on first message
- **WHEN** the user sends their first message
- **THEN** the frontend SHALL generate a UUID `session_id` and include it in every subsequent API request

#### Scenario: Session persists on page refresh
- **WHEN** the user refreshes the page within the same browser tab
- **THEN** the `session_id` SHALL be preserved via `sessionStorage` so the backend can correlate the conversation

---

### Requirement: Assistant-ui component integration
The chat interface SHALL be built using `@assistant-ui/react` primitives with the official shadcn/ui theme.

#### Scenario: Thread primitives used
- **WHEN** a developer inspects the chat page implementation
- **THEN** it SHALL use `AssistantRuntimeProvider`, `Thread`, `Composer`, and `Message` from the assistant-ui component set under `src/components/assistant-ui/`

#### Scenario: Markdown rendering enabled
- **WHEN** the assistant response contains markdown (headings, lists, code blocks)
- **THEN** the message SHALL render formatted markdown via `@assistant-ui/react-markdown`

---

### Requirement: Error handling in chat
The chat UI SHALL handle API failures gracefully without crashing the page.

#### Scenario: Backend unreachable
- **WHEN** the API request fails due to network error or non-2xx response
- **THEN** the UI SHALL display a user-friendly error message in the thread and re-enable the composer

#### Scenario: Request in progress
- **WHEN** a question is being processed
- **THEN** the composer submit button SHALL be disabled to prevent duplicate sends
