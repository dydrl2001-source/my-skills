# A small interface over substantial behavior

Work within the requested change. A useful module concentrates ordering rules, validation, errors and orchestration that callers would otherwise duplicate. Judge depth by what callers no longer need to know, not by implementation line count.

For the affected interface, establish:

1. What the caller supplies and receives, including relevant failure and performance behavior.
2. Which orchestration and invariants the implementation should own.
3. Which actual inputs or dependencies vary, and how to substitute those during verification.

For example, repeated `probe → choose frames → extract → make sheets → write manifest` call sequences can become one `inspect_video(...)` operation. Keep an existing targeted-frame operation if callers genuinely need it. Optional transcription can remain separate or be an explicit option; a new abstraction should simplify real callers.

Use the deletion test: if removing a wrapper eliminates complexity, consider inlining it; if the same complex rules reappear in several callers, it is earning its place. Do not add configuration, adapters or layers solely for a hypothetical future use. Preserve a repository's clearer existing terminology; explain the design plainly rather than imposing an English vocabulary.

Test observable behavior at the useful interface. Pure computations can run directly; local I/O can use real temporary fixtures. Isolate a remote service at the point where real network behavior makes tests impractical. A test substitute must preserve the outcome and error contract being verified.

Keep regressions protected throughout a refactor. Remove an old test only after confirming it is redundant with replacement coverage and its deletion belongs to the requested change. A broad integration test does not automatically replace every narrower test.
