# Architecture Decisions

Every choice below is a decision the repo has already made. Each is stated
as: name, choice, evidence (a path that exists, or a command that runs).

## AD-1 Kernel

Choice: nine primitives, six constructors, everything else derived.

Evidence: `substrate/__init__.py`.
`python substrate/tests.py` prints 21 ok, 0 fail.

## AD-2 Semantics

Choice: every primitive denotes a domain; `nat` rejects bool; no coercion.

Evidence: `substrate/semantics.py`.
`python substrate/tests_semantics.py` prints 17 ok, 0 fail.

## AD-3 Types

Choice: composition requires matching domain and codomain.

Evidence: `substrate/typesys.py`.
`python substrate/tests_typesys.py` prints 13 ok, 0 fail.

## AD-4 Reduction

Choice: seven named rules; every step recorded; nested reduction to a value.

Evidence: `substrate/reduce.py`.
`python substrate/tests_reduce.py` prints 16 ok, 0 fail.

## AD-5 Vocabulary

Choice: six levels, nine dimensions, forty-seven gateway verbs; every name a term.

Evidence: `substrate/vocabulary.py`.
`python substrate/vocabulary.py` prints layers=6 dimensions=9 verbs=47 terms=62.

## AD-6 Enterprise

Choice: thirty layers, one hundred ninety-three items; each layer a collection.

Evidence: `substrate/enterprise.py`.
`python substrate/enterprise.py` prints layers=30 items=193.

## AD-7 Graphs

Choice: 331 acronyms named; kernel K, observable X, update F as terms.

Evidence: `substrate/graphs.py`.
`python substrate/graphs.py` prints graphs=331 kernel=5 observable=5.

## AD-8 Denotation

Choice: the first acronym with a real meaning is DAG; `denotes_dag` returns a Verdict.

Evidence: `substrate/dag.py`.
`python substrate/dag.py` prints 6 ok, 0 fail.

## AD-9 Homeostat

Choice: thirteen drives in bands; kernel refuses and names the failing drive.

Evidence: `homeostasis/__init__.py`.
`python homeostasis/tests.py` prints 13 ok, 0 fail.

## AD-10 Regulator

Choice: greedy controller; no overshoot; refuses if it cannot converge.

Evidence: `homeostasis/regulate.py`.
`python homeostasis/tests_regulate.py` prints 8 ok, 0 fail.

## AD-11 Pipeline

Choice: one command, six inputs, six targets, four audit checks.

Evidence: `omni/cli.py`.
`python -m omni --input url --value https://example.com --target localhost`.

## AD-12 Classifier

Choice: gate the factory; refuse and name the failing gate.

Evidence: `packages/buildability/`.
`./scripts/verify.sh` runs eleven stages.

## AD-13 Work

Choice: the pasted document is source, not code. It is structured, indexed,
copyleft, and parsed into a skills manifest.

Evidence: `work/source.txt`, `work/features.json`, `work/copyleft.txt`,
`work/pi_agent.json`.

## AD-14 Ominouscent

Choice: a separate project at `~/OMINOUSCENT`. Sensor threads write events
to SQLite. `seal_ledger` folds the event hashes. Editable install uses
compat mode.

Evidence: `~/OMINOUSCENT/ominouscent/core/db.py`.
`ominousctl tail` reads events. `ominousctl seal` returns a non-zero root.

## AD-15 Relationship

Choice: `~/workspace` and `~/OMINOUSCENT` are separate projects. They share
one pattern: read the file, name the failing line, fix that line, verify,
commit.

Evidence: this file.
