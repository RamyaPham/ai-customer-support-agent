# Chapter 2: How We Talk to an LLM -- APIs, Models, and Configuration

## LLMs Are Remote Services

You do not run an LLM on your laptop. Companies like OpenAI and Groq host these massive models on their servers. Your application sends an HTTP request containing your prompt, and the API sends back a completion. It works exactly like calling any REST API -- except the response is generated text instead of database rows.

**Analogy:** Imagine a consulting firm. You email them a question (the prompt), they think about it, and email back an answer (the completion). You pay per page of the question and the answer (tokens). You never see their internal process -- you just get the result.

## How Our Project Connects

Here is the actual code that configures which LLM our agent talks to:

```python
# backend/app/agent/llm.py
def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        )
```

Notice three critical settings:

- **model**: Which LLM to use. `gpt-4o-mini` (OpenAI) and `llama-3.1-8b-instant` (Groq, free) are both fast and affordable. Bigger models are smarter but slower and more expensive.
- **api_key**: A secret token that authenticates your application. Stored in environment variables, never in code.
- **temperature**: Controls randomness. `0` means "give the most predictable, consistent answer every time." For customer support, we want reliability, not creativity. Setting it to `1` would produce more varied responses -- useful for creative writing, dangerous for refund decisions.

## The Request/Response Cycle

1. Customer types: "I want a refund for order ORD-42"
2. Our FastAPI backend packages this into a list of messages (including the system prompt from Chapter 5)
3. LangChain sends these messages to the OpenAI API
4. OpenAI returns a completion -- either a text response or a request to call a tool
5. Our backend processes the result and responds to the customer

Every call costs money. A typical support conversation uses around 2,000-5,000 tokens, costing fractions of a cent with `gpt-4o-mini`.

## Why This Matters

Understanding the API-based model means understanding your dependencies: network latency, API rate limits, costs, and the fact that your application's intelligence lives on someone else's server. Design accordingly.

## Key Takeaways

- LLMs are accessed via APIs -- your code sends prompts and receives completions over HTTP.
- Temperature controls randomness: 0 for deterministic tasks, higher for creative ones.
- Model choice is a trade-off between intelligence, speed, and cost.
- API keys must be kept secret and stored in environment variables, never hardcoded.
- LangChain provides a uniform interface so you can swap between Groq, OpenAI, and other providers with a single config change.
