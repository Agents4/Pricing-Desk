---
name: output-conventions
description: Where outputs are filed, the header every output carries, and the handoff and filing blocks
---

# Output conventions

## Header

Every output starts with:

```
# <Title>
**Answer:** <the answer or the decision needed, one or two lines>
**Decision and owner:** <the decision this serves> / <who decides>
Status: Draft | For decision               Handling: Internal | Shareable      Date: <YYYY-MM-DD>
```

## Where files go

| Output | Path in the workspace |
|---|---|
| Account price sheet, deal package | `workspace/accounts/<account>/` |
| Price book, change log, notice calendar | `workspace/price-book/` |
| Reviews, packs, research, memos | `workspace/outputs/<yyyy-mm>/` |
| Decision log | `workspace/outputs/decision-log.md` (append only) |
| Learning log | `workspace/context-library/lessons.md` |
| Analog entries | `workspace/context-library/analogs/` |

Names: lowercase, hyphens, ISO dates (`2026-10-24-weekly-review.md`).

## Handoff block

```
## Handoff
Done: ...
Not done: ...
You decide: ...
Watch: ...
```

## Chat-only surfaces

End the reply with:

```
FILING NOTE: save as <path>
CONTEXT UPDATES: <file>: <line to add or change> (or "none")
```

Never write to the context library without approval. Propose the change and wait.
