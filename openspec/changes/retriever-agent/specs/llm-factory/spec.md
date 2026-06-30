## ADDED Requirements

### Requirement: Pluggable LLM via environment config
The system SHALL provide a `build_llm(provider, model, api_key)` factory function that returns a LangChain chat model instance based on `LLM_PROVIDER` and `LLM_MODEL` from config, with no code changes required to switch providers.

#### Scenario: Anthropic provider
- **WHEN** `LLM_PROVIDER=anthropic` and `LLM_MODEL=claude-sonnet-4-6`
- **THEN** `build_llm` returns a `ChatAnthropic` instance with `streaming=True`

#### Scenario: OpenAI provider
- **WHEN** `LLM_PROVIDER=openai` and `LLM_MODEL=gpt-4o`
- **THEN** `build_llm` returns a `ChatOpenAI` instance with `streaming=True`

#### Scenario: Ollama provider (no API key)
- **WHEN** `LLM_PROVIDER=ollama` and `LLM_MODEL=llama3`
- **THEN** `build_llm` returns a `ChatOllama` instance without requiring an API key

#### Scenario: Groq provider
- **WHEN** `LLM_PROVIDER=groq` and `LLM_MODEL=llama-3.1-70b-versatile`
- **THEN** `build_llm` returns a `ChatGroq` instance with `streaming=True`

#### Scenario: Google provider
- **WHEN** `LLM_PROVIDER=google` and `LLM_MODEL=gemini-1.5-flash`
- **THEN** `build_llm` returns a `ChatGoogleGenerativeAI` instance

#### Scenario: Unknown provider
- **WHEN** `LLM_PROVIDER` is set to an unrecognised value
- **THEN** `build_llm` raises `ValueError` with a message naming the unsupported provider

---

### Requirement: LLM singleton in DI container
The LLM instance SHALL be registered as a `providers.Singleton` in the container so the model is loaded once per process.

#### Scenario: Single instance across requests
- **WHEN** multiple concurrent requests invoke the `rag_workflow`
- **THEN** all requests share the same LLM instance (no re-instantiation per request)
