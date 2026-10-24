# Phase 3: Architecture

Status: draft for confirmation. Follows Sales-OS and the os-builder standard v1.

## Layout
```
pricing-desk/
  os.manifest.json            skills source, commands, registries, protect paths, platforms
  VERSION  CHANGELOG.md
  core/
    methodology/              frameworks.md (from 04), fidelity ledger
    shared/                   operating-rules.md (from 03), skill-authoring.md
    skills/<name>/            SKILL.md, scripts/, references/, assets/   (single source)
    templates/                decision pack, corridor memo, deal package, weekly review
    rubrics/                  review rubric per deliverable
    lenses/                   stakeholder lenses
    analog-library/           dated analog entries
    notebook-packs/           source lists for Gemini Notebook
  tools/pdos.py               validate, build, doctor, lint, new-instance, upgrade-instance, release
  workspace/                  instance data (protected): context library, price book, decision log, learning log
  local/skills/               instance-only skills (protected)
  adapters/                   google (Gemini CLI, Gemini app, Notebook), microsoft (legacy Copilot), claude
  evals/                      cases/NN-name/{input.md,expected.md}, rubric.md
  docs/                       architecture, rollout playbook, security and governance, roadmap
  design/                     this pack (kept as history)
  -- generated, never edited by hand --
  skills/  commands/  agents/  hooks/  GEMINI.md  gemini-extension.json  .claude/  dist/
```

## Decisions
1. **One source, generated targets.** `core/skills/` is edited; `skills/`, `commands/`, `.claude/skills`, `dist/` are built by `tools/pdos.py build`. The Gemini extension keeps working because its root files are generated.
2. **Name stays Pricing Desk.** Extension name `pricing-desk`, commands `/pricing:*`. Existing nine skill names unchanged. Version 0.3.0 to 0.4.0 for the restructure, 1.0.0 when the waves ship.
3. **Python stdlib tool** modelled on Sales-OS `tools/sos.py`, about 1,500 lines for the first cut. The existing scripts (checker, importer, corridor) move under their skills unchanged.
4. **Instance split.** Product content is shared; `workspace/` and `local/` are per company and never overwritten by upgrade. Company floors, approval matrix and customer data live only in the instance.
5. **Platforms first:** Gemini CLI extension and Gemini app / Notebook (notebook packs list which files to load as sources and carry the instruction text). Microsoft Copilot docs stay as a legacy adapter until the move to Google completes. Claude files are generated for authoring.
6. **Chat tools cannot write files.** In chat-only surfaces every output ends with a FILING NOTE (where to save it) and a CONTEXT UPDATES block (what to change in the context library).
7. **Evals:** one case per skill at minimum, plus cases for the five domain rules (harvest request, "do we have the right", floor breach, untagged number, status Approved attempt).
8. **Doctor:** checks manifest against files, skill counts in registries, line limits, frontmatter, links, rule checks, and that generated targets are current.
9. **Hooks:** the existing guard stays (Approved status). A second hook may warn when a price book is saved without running the checker; decide in the build.
10. **Rights Desk stays a separate repo.** The OS reads its hand-off answer through a file (`rights_answers.csv`) or the user pastes it; no code dependency.

## Build order
Stage A: restructure with no behavior change (manifest, core/, tool, generated targets identical). Stage B: operating rules, templates, evals scaffold. Stage C: wave 1 skills one at a time with an eval each. Stage D: Google adapters and notebook packs. Stage E: test on a real past case (a real quote, a real quarter), fix, release 0.4.0. Waves 2 and 3 after.
