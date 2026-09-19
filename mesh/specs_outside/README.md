# Outside specs

These five specs were written outside this session, then run through
`python -m buildability.classify mesh/specs_outside`.

Result:

| spec | regime | why |
|---|---|---|
| INCIDENT-LOG | CONSTRUCTION | six elements present; no solver bound (G3) |
| LOG-ROTATOR | CONSTRUCTION | same |
| MARKDOWN-VAULT | CONSTRUCTION | same |
| TASK-QUEUE | INCOHERENT | invariant `log_monotone` names `non-decreasing`, undeclared |
| URL-SHORTENER | INCOHERENT | invariants name `long_url`, undeclared |

The two INCOHERENT verdicts are the framework's honest answer to the
question the format asks: an invariant predicate may only name
identifiers that are declared components. `long_url` and
`non-decreasing` are identifier-like tokens that are not components.
The refusal is correct under the rule; it is not a bug in the
classifier.

To move either spec to CONSTRUCTION, either declare those tokens as
components or reword the invariants so they no longer name undeclared
identifiers. The specs are left as-is so the next outside spec is
tested against the same rule, and the rule's refusals stay on record.

The spec format this reveals is:

- six elements (components, interfaces, invariants, lifecycle,
  substrate, gaps)
- every invariant must name at least one declared component if it
  names any identifier-like token
- the format does not accept invariants that reference data entities
  not present in the component list

That is the demand the classifier makes of its users. It is stated
here because the two INCOHERENT specs are the first place it was
made visible.
