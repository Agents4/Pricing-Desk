---
name: capabilities
description: How to detect what the agent can do here, and what to do when a capability is missing
---

# Capabilities

Check your tools before promising anything.

| You can | If not |
|---|---|
| Read and write files in the workspace | Ask the user to paste what you need. Return each output in one delimited block, ending with a FILING NOTE (where to save it) and a CONTEXT UPDATES block (what to change in the context library). |
| Run scripts (`python3`) | Say the check was not run and give the inputs and expected command. Mark computed numbers A. |
| Search and read public web pages | Work from what the user supplies. Mark analogs "to verify". Never present remembered prices as sourced. |
| Use Google Drive, Docs, Sheets | Work from pasted content or exports (CSV). |
| Run a fresh reviewer (subagent) | Walk the rubric (`references/output-check.md`) yourself and say the review was not independent. |

A "Resource deadlock avoided" error or a timeout when reading a file usually means a Google Drive file is online-only. Ask the user to set the folder to Available offline or to paste the content.

Never write outside the workspace and the output paths named in a skill. Never send, post or publish.
