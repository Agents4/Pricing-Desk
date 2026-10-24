---
name: output-check
description: The closing check every pricing output passes before it is handed over, and that an independent reviewer walks
---

# Output check

Walk this list before you finish. Answer each line yes, no or not applicable, and fix every no. When a shell exists, `python3 tools/pdos.py lint <file>` and the skill's checker do the mechanical parts; say so, or say they were not run. A reviewer who did not write the output walks the same list (rule 7).

## Every output

- [ ] Line one under the title is `**Answer:**` and states the answer or the decision needed (rule 1).
- [ ] `**Decision and owner:**` names the pricing decision and who decides. The decider comes from `pricing-governance.md`, or is Unknown (rules 2, 14).
- [ ] `Status:` is Draft or For decision. Nothing is marked Approved, sent or published (rules 6, 10).
- [ ] `Handling: Internal` or `Handling: Shareable` is stated. A Shareable output names no customer, floor or incentive term (rule 4).
- [ ] Every number carries F, I, A or U. Each F has a source; each A has an owner and a date to confirm (rule 3).
- [ ] Every computed number came from a script, with the inputs shown, or is marked A with the reason the script did not run (rule 9).
- [ ] No threshold, band, floor, name, window or count appears that did not come from the context library or the user. Blanks say Unknown and name the file to fill (rule 14).
- [ ] There is a Missing list, and it holds every Unknown and every assumption.
- [ ] The hand-off has four parts: Done, Not done, You decide, Watch (rule 5).

## Pricing outputs

- [ ] Every data or API price states the right it grants, one of the nine. An API price buys only the use it names (rule 8).
- [ ] Keeping or collecting data is priced as a data licence with a minimum commitment, a retention term and an audit right (rule 8).
- [ ] Whether we hold a right is not answered here. The right is stated and the product is on the hand-off list (rule 12).
- [ ] List price was set without knowing the account. Any account effect is a give tied to a get, inside the approved band, and logged (rule 13).
- [ ] No deal price is below its floor without an exception request.
- [ ] Usage patterns are worded "pattern to confirm with the account owner". Nobody is accused and no intent is assumed.

## Research and outside facts

- [ ] Every outside price or fact has a public URL and an access date, and a stated unit and scope (rule 11).
- [ ] Nothing came from a login, a competitor contact or a customer's data.
- [ ] Something that describes the world as it is now was looked up, not remembered.

## Price books and releases

- [ ] The checker ran in release mode with no errors, and the change log and notice calendar are attached.
- [ ] The rights hand-off list is current.

## Review note

Write who reviewed (a person, or a fresh reviewer using this list), what they changed, and what they could not check.
