# Evals

Each case checks that a skill behaves under the rules. A case is a folder `evals/cases/NN-name/` with:

- `input.md`: the request and any material, as a user would give it.
- `expected.md`: first line `Skill: <skill-name>` (the skill that should run), then the checks the output must pass, one per line, each starting `- `. Say what must be true, and what must not appear.

`evals/rubric.md` lists the checks that apply to every case. Run `python3 tools/pdos.py evals` to confirm every case is well formed and names a real skill. To score a case, give `input.md` to the agent with the skills loaded, save the reply, run `python3 tools/pdos.py lint <reply.md>`, and walk `expected.md` and the rubric by hand. Record a miss as a lesson with `pd-ratchet`.
