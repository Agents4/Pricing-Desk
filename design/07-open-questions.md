# Open questions for the owner

Being taken one at a time with the owner. Company-specific values (Council, thresholds, systems, hand-off route) are not design blockers: the pd-setup interview collects them into the context library (09-context-library.md) and they can differ per company. Still open for the design itself: items 6 to 10. Answered so far: anchor deal mechanics (incentives paid to agencies; add-on product priced on look-to-book and other value adds; list price independent of the account).

1. **Council membership and quorum.** Who sits on the Pricing Council, who chairs, and what is delegated to the deal desk? Until set, the OS uses placeholders in the approval matrix.
2. **Approval thresholds.** Discount bands, margin floors and who approves each. Needed for the approval matrix. The OS will not invent them.
3. **Target time to answer.** Deal desk turnaround target and the Council pack lead time. Proposed defaults will be marked as proposals.
4. **Where the price book lives.** SharePoint now, Google Drive after the move. The OS needs one named location and an export format (CSV).
5. **Rights hand-off route.** How does the product manager return an answer: a CSV, a form, a message? Default is a CSV named `rights_answers.csv`.
6. **Real past case for testing.** One real deal, one real quarter of realization data, and one real API access request (anonymized) to run through before release.
7. **Analog verification.** Someone with web access to the vendor pricing pages (Amadeus Self-Service, Duffel, Google Maps Platform) to confirm and add them, or approve a later session to try again.
8. **Wave order.** Confirm the wave 1 list or swap skills in and out.
9. **Rights Desk repo.** Created as `Agents4/data-rights` (2026-10-24). Independent of this design.
10. **PR #6.** Merge the rights split before the restructure starts? The design assumes yes.
