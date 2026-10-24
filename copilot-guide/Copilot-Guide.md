# Using Microsoft Copilot for the Pricing Desk

*Setup, workflows and guardrails, without creating agents. Checked against Microsoft documentation in October 2026. Features and licensing change, so confirm the items marked "Check" with your administrator. Prices, customers and agreements in examples are invented.*

## 1. The short version

- **Copilot drafts, extracts and organizes.** The calculators and the Pricing Council decide.
- **You do not need agents.** A Notebook that holds the playbooks file, saved prompts, and custom instructions gives most of the value.
- **Numbers get checked.** Copilot can slip on arithmetic. Every price comes from a calculation you can see and recompute.
- **Every price covers a stated right.** For data and API products, say what the customer may do with it. An API price buys the use it states; collecting or keeping data through an API is a data right. Whether we may grant a right is the product manager's call, not Copilot's.
- **Copilot sees what you can open.** Keep contracts in a locked library so the wrong people cannot pull them into a prompt.

## 2. What Copilot can and cannot do here

<table data-border="1" data-cellpadding="4">
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th>Good use</th>
<th>Needs a second check</th>
<th>Do not use Copilot for</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Summarize a customer request and the right it asks for<br />
Draft questions for the product manager and Legal<br />
Draft deal approval memos from a deal request<br />
Build risk registers, notice calendars, communication outlines<br />
Design interview guides and questionnaires<br />
Summarize and compare drafts</td>
<td>Any arithmetic or waterfall<br />
Counts across large files<br />
What a contract permits (Legal decides)<br />
Comparing a price with benchmarks<br />
Deal and customer classifications</td>
<td>Approving anything or deciding whether we may grant a right<br />
Contacting customers<br />
Final prices without a visible calculation<br />
Inferring competitor prices</td>
</tr>
</tbody>
</table>

## 3. Features you can use without creating agents

| Feature                               | Use it for                                                                               | Notes and checks                                                                                                                                                                                                                                                                      |
|---------------------------------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Copilot Chat                          | Day-to-day prompts with attached files.                                                  | Check: whether your tenant has Copilot Chat only or a Microsoft 365 Copilot license. Some features below differ.                                                                                                                                                                      |
| Custom instructions                   | Standing rules that apply to your chats.                                                 | Chat settings, Personalization, Custom instructions. Microsoft does not state a character limit on that page, so keep it short. Check whether admin has turned it off.                                                                                                                |
| Notebooks                             | The desk workspace: playbooks, price book, deals.                                        | Up to 300 reference files. Accepts Word, PowerPoint, Excel, PDF, Copilot Pages, Loop, OneNote and web pages. No .md, .csv or .json: convert to Word or Excel. Per-notebook instructions. No charts inside a notebook. Deleting is permanent. You need SharePoint or OneDrive storage. |
| Pages                                 | Save and share the checked result with named people.                                     | Can be converted to Word or PowerPoint. Colleagues can open the page without seeing your chat.                                                                                                                                                                                        |
| Prompt Gallery                        | Save and share the prompts in the playbooks.                                             | Your Prompts, and Teams for shared prompts. Microsoft documents that admins can report on saved, liked and shared prompts.                                                                                                                                                            |
| Built-in agents (Researcher, Analyst) | Use, not create. Analyst reads Excel and CSV attachments and produces tables and charts. | Check: Analyst may be unavailable if admin has not enabled it. A third-party source says some of these need the paid license. Microsoft's Analyst page does not state whether it runs Python, so do not rely on it for final numbers.                                                 |
| Copilot in Excel and Word             | Formulas, summaries and drafts inside the file.                                          | Check: reported to need the paid license. Put data in an Excel table before asking for analysis.                                                                                                                                                                                      |

**Ask your administrator:** which license you have, whether Notebooks, Pages and the Prompt Gallery are on, whether Analyst is enabled, and whether you can share a Page with a named group.

## 4. Setup in about 20 minutes

1.  **Make one home for the inputs.** In a SharePoint site you own, create folders: Playbooks, Price book, Deals, and Contracts. Give Contracts to the people who need them and Legal only.
2.  **Set custom instructions.** In Copilot Chat open settings at the top right, then Chat settings, Personalization, Custom instructions, Edit instructions. Paste the text from custom-instructions.txt and save.
3.  **Create the notebook** named "Pricing Desk". Add Copilot-Playbooks.docx, the blueprint exported to Word or PDF, and the price book as .xlsx. Paste notebook-instructions.txt into the notebook's instructions. Add important files directly; when you add a folder, Copilot picks only the most relevant files.
4.  **Save the prompts.** In the Prompt Gallery choose Your Prompts and add one prompt per playbook, named "PD Deal review", "PD Price book" and so on. Keep customer names out of saved prompts; use the \[BRACKETS\]. Share them with your team if you can.
5.  **Run a test** on an invented API request. Ask for Playbook 3 on a customer who wants to "pull all fares for the next year into our database". Confirm that it asks what they will do with the responses, treats collecting data as a data right, and does not price it at the per-call booking rate.

## 5. The routine for any task

1.  Open the Pricing Desk notebook.
2.  Name the input files in the prompt. Do not paste whole contracts.
3.  Paste the prompt for the playbook and replace the \[BRACKETS\].
4.  Check the answer with that playbook's "Check before you use it" list.
5.  Save the checked result to a Page. Send questions about whether we may grant a right to the product manager, and contract questions to Legal.

## 6. Workflow quick reference

| Playbook                              | Attach                                                                        | Check before you use it                                                                                                |
|---------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| 1 Price setting                       | Costs, segments and value sources, comparables, WTP points, the right granted | Recompute floor and one value price. Inputs have sources. Every price says which right it covers.                      |
| 2 Price book                          | Corridor results, past deals                                                  | Each data and API line states its right. Floor not above list. No tier overlaps or cliffs.                             |
| 3 Data licence or data-access request | Request, price book                                                           | API request to collect data priced as a data right, not at the booking rate. Question for the product manager written. |
| 4 Deal desk review                    | Deal, price book, approval matrix, comparables                                | Recompute the waterfall. Tier equals first rule tripped.                                                               |
| 5 Price realization                   | Billing, price book, deal log                                                 | Reconcile first. Stop over 1 percent gap. Approved versus unexplained discount kept apart.                             |
| 6 API tier fit                        | Usage, plans, price book, call classes                                        | Call classes defined. Machine traffic and possible data collection labeled "to confirm".                               |
| 7 Price change                        | Change, customers, contract summary, price book                               | Clause references quoted. Ranges, not points. Legal items escalated.                                                   |
| 8 WTP study                           | Decision and concept, or responses                                            | Sample size beside every figure. Stated is not forecast.                                                               |
| 9 Import price book                   | Existing price book (Excel or CSV), revenue per product                       | Nothing invented. Blanks listed. Product types confirmed. Row counts match the source.                                 |

## 7. Keeping numbers right

- Ask for a table of every input, formula in words, and result.
- Recompute two or three numbers yourself in Excel: the floor, a total, one discount.
- For sums over big files, put the data in an Excel table and ask Copilot in Excel for formulas, not values. Read the formulas.
- Check totals against the source, units, percent versus fraction, and currency.
- Run the same prompt twice. If the numbers differ, use neither and move to a script or Excel.
- For the price corridor and price book checks, use the scripts in the package. Ask someone with Python to run them, or bring the files to Claude. Treat Copilot's figures as a draft to compare.
- Large files: ask for row counts first, then work by dataset or by month.

## 8. Data handling

- **Permissions:** Copilot works within your access. Keep contract text in a locked library.
- **Prompts:** reference files by name; do not paste whole contracts or customer lists.
- **Sharing:** share Notebooks and Pages with named people. Deleting a notebook or page cannot be undone.
- **Saved prompts:** admins can report on saved and shared prompts. Use placeholders instead of customer names or prices.
- **Competitors:** use public information or customer-supplied quotes with a source. Do not ask Copilot to infer competitor prices, and do not share your pricing with competitors.
- **Willingness to pay:** individual answers stay out of shared notebooks. Share ranges.
- **Policy:** follow your company's AI-use policy for supplier and customer confidential data. If unsure, ask Security or Legal before uploading.

## 9. Troubleshooting

| Symptom                      | What to do                                                                                                      |
|------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Ignores the playbook         | Name the playbook and section in the prompt. Ask it to list the steps it will follow before it starts.          |
| Invents a clause or a number | Require a quote and location for each clause and a source for each number. Add: "If not stated, write Unknown." |
| Answer too long or generic   | Add: "Headline first, then one table. Under 300 words."                                                         |
| Cannot read a file           | Convert to .docx, .xlsx or .pdf. CSV to .xlsx. Markdown to Word.                                                |
| Misses files                 | Add files directly, not just a folder. A folder gives only the most relevant files, up to 300.                  |
| Numbers differ between runs  | Move the calculation to Excel formulas or a script.                                                             |
| A feature is missing         | Ask the administrator. Analyst, Notebooks, Pages and in-app Copilot can depend on license and settings.         |

## 10. Limits and open points

- Microsoft's pages I checked do not publish limits for custom instruction or prompt length. The prompts here are short on purpose and the detail sits in the playbooks file.
- Notebooks do not show charts. Ask for tables, then chart in Excel.
- Claude skills in this package do not load into Copilot. The playbooks are the Copilot version of the same procedures. Both follow the same pricing rules.
- Where a source was a third-party article rather than Microsoft, the table says so. Confirm licensing with your administrator.

## Sources

- Microsoft Support, How Microsoft Copilot Notebooks works: support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-notebooks-works
- Microsoft Support, Customize how Microsoft 365 Copilot responds to you: support.microsoft.com/en-US/microsoft-365-copilot/customize-how-microsoft-365-copilot-responds-to-you
- Microsoft Learn, Copilot Prompt Gallery: learn.microsoft.com/en-us/microsoft-365/copilot/copilot-prompt-gallery
- Microsoft Support, How Microsoft Copilot Pages works: support.microsoft.com/microsoft-365-copilot/how-microsoft-365-copilot-pages-works
- Microsoft Support, Use Analyst for deep data analysis: support.microsoft.com/en-US/Microsoft-365-Copilot/use-analyst-for-deep-data-analysis
- Microsoft 365 message center RM534606, SharePoint list agent (via mc.merill.net)
- Third party: nextstart.ai, Copilot Chat vs Microsoft 365 Copilot (October 2026), for license differences. Unverified by Microsoft.
