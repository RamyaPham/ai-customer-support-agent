# Chapter 1: What Is AI? What Are Large Language Models?

## The Big Picture

Artificial Intelligence (AI) is software that performs tasks traditionally requiring human intelligence -- understanding language, making decisions, recognizing patterns. But most "AI" you hear about today is a specific type called **machine learning**: software that learns patterns from massive amounts of data rather than following hand-written rules.

The breakthrough behind modern AI assistants is the **Large Language Model (LLM)**. An LLM is a program that has read billions of pages of text -- books, websites, code, conversations -- and learned the statistical patterns of how words follow each other. When you give it a sentence, it predicts what words should come next, one piece at a time.

**Analogy:** Think of an LLM as an extremely well-read intern. This intern has read every customer service manual, every product guide, and millions of support conversations. They can produce fluent, helpful responses. But they have never actually looked at *your* database, never processed a real refund, and sometimes confidently say things that sound right but are wrong. That is exactly the challenge we solve in this project.

## Key Terms You Will See Everywhere

- **Prompt**: The text you send to the LLM. "Help me with a refund for order #1234" is a prompt.
- **Completion**: The text the LLM generates in response.
- **Token**: The unit an LLM reads and writes. A token is roughly 3/4 of a word. "customer support agent" is about 3 tokens. You pay per token.
- **Context window**: The maximum number of tokens an LLM can consider at once (prompt + completion). GPT-4o has a 128,000-token window -- roughly a 300-page book.
- **Hallucination**: When the LLM generates something that sounds correct but is factually wrong. This is why our project never lets the LLM make refund decisions on its own.

## Why This Matters

In our AI Customer Support Agent, the LLM is the "brain" that understands what the customer is asking and decides which tools to use. But understanding what it *can* and *cannot* do is the foundation of building a system that is both powerful and safe. The LLM handles language; deterministic code handles decisions.

## Key Takeaways

- AI is software that learns patterns from data rather than following hand-coded rules.
- An LLM predicts the next token based on patterns learned from billions of text examples.
- LLMs are fluent but not infallible -- they can hallucinate facts.
- Tokens are the currency of LLMs: you pay for them and they limit how much text the model can process.
- Understanding the LLM's strengths (language) and weaknesses (factual accuracy, real-world actions) is essential before building on top of one.
