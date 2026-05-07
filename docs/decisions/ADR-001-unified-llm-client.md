# ADR-001: Unified LLMClient over Direct SDK Calls

## Status

Accepted

## Context

`agent-api` supports Anthropic, OpenAI, and local Ollama. Each provider has a
different SDK or HTTP interface, error model, token accounting shape, and setup
requirements. Application code should not need provider-specific imports or
branching to make one LLM call.

## Decision

Expose one public client, `LLMClient`, with a single
`call(system, user, model=None)` method. Backend selection is environment-based,
and provider-specific behavior is isolated in `agent_api/providers/`.

Provider adapters return `(text, tokens_in, tokens_out)` to the client. The
client is responsible for retry behavior, canary application, output scrubbing,
cost estimation, logging metadata, and construction of `LLMResponse`.

## Alternatives Rejected

- Multiple public methods such as `call_anthropic`, `call_openai`, and
  `call_ollama`: this would push provider decisions into callers.
- Direct provider SDK usage in application code: this would duplicate retry,
  error handling, and prompt-injection guard behavior.
- A broad dependency-injection framework: this would add complexity before the
  library needs runtime provider plugins.

## Consequences

- Callers get a stable interface across supported backends.
- Provider-specific behavior remains testable behind small adapters.
- Public API changes to `LLMClient` require changelog updates and, when
  significant, a new ADR.
