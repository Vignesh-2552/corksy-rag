from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def build_llm(provider: str, model: str, api_key: str = "") -> BaseChatModel:
    match provider:
        case "anthropic":
            return ChatAnthropic(model=model, api_key=api_key, streaming=True)
        case "openai":
            return ChatOpenAI(model=model, api_key=api_key, streaming=True)
        case "openrouter":
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=OPENROUTER_BASE_URL,
                streaming=True,
            )
        case "ollama":
            return ChatOllama(model=model)
        case "groq":
            return ChatGroq(model=model, api_key=api_key, streaming=True)
        case "google":
            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        case _:
            raise ValueError(
                f"Unknown LLM provider: '{provider}'. "
                "Supported: anthropic, openai, openrouter, ollama, groq, google"
            )
