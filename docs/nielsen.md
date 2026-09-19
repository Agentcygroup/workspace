# Nielsen heuristics, mapped to the console

Ten heuristics. Each row names the UI element that satisfies it.

1. Visibility of system status — `#health-status`, `#pipe-table` (PASS/FAIL column), all fetch results.
2. Match between system and the real world — labels are "corpus", "regime", "pipe", "standards", not internal names.
3. User control and freedom — every action is a button; nothing runs automatically.
4. Consistency and standards — one table style, one button style, one status color scheme.
5. Error prevention — buttons disabled during fetch; auth token required; chain refuses before handler.
6. Recognition rather than recall — the four corpora are a select; the token is printed in the footer.
7. Flexibility and efficiency of use — `python -m buildability.classify` still works from the shell for power users.
8. Aesthetic and minimalist design — four cards, no chrome, no decoration.
9. Help users recognize, diagnose, recover from errors — every error is a `.status.fail` with a specific reason.
10. Help and documentation — this document, `docs/runbook.md`, `mesh/specs_outside/README.md`.
