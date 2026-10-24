# Pricing coach (version 0.5.0)

Method questions, quizzes and onboarding for the pricing desk. Contains no company data.

## Upload steps

1. Create a new notebook in Gemini Notebook (or Gemini Notebook Enterprise).
2. Add everything in `sources/`. Importing them as Google Docs first lets you use sync with Drive when they change.
3. Open the chat settings, choose a custom conversational style and paste `chat-instructions.txt`.
4. Use `studio-prompts.md` for overviews, reports, quizzes, flashcards, slide decks and mind maps.

## Sources (5)

| File | Words |
|---|---|
| `01-operating-rules-and-output-conventions.md` | 967 |
| `02-spine-and-rhythms.md` | 1625 |
| `03-frameworks-and-sources.md` | 887 |
| `04-skill-procedures.md` | 14959 |
| `05-system-skill-procedures.md` | 1933 |

Source limits are Google's and change: verify them on Google's usage-limits page before relying on them. Sales-OS notes about 50 sources per notebook on the consumer tier and 300 sources with 500,000 words or 500 MB per source on Enterprise (not re-verified here).

A notebook is a snapshot unless its sources are synced Google Docs. Regenerate after meaningful changes and replace only the changed sources.
