---
name: "regex-commenting"
description: "Require a short explanatory comment whenever the agent creates a regex pattern."
alwaysActive: true
---

## Rule

Every time the agent creates a regular expression literal or compiled regex, it must include a brief explanatory comment describing:

- what the regex is matching
- why it is needed in the current logic
- any important constraint the pattern enforces

## Required behavior

- Add the comment immediately before or beside the regex definition.
- Keep the explanation short but specific.
- Do not introduce a regex without explanation.
- If a regex is complex, the comment should clarify the business or technical intent, not just restate the syntax.

## Examples

```python
# Match support ticket IDs in the format TKT-12345.
pattern = re.compile(r"^TKT-\d{5}$")
```

```ts
// Accept ISO dates in YYYY-MM-DD format from client payloads.
const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;
```

## Verification

A regex is compliant only when it is paired with an explanation that makes its purpose clear to another developer without needing to reverse-engineer the pattern.
