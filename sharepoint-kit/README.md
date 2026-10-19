# Party-aware data rights register: SharePoint kit

Contents
- schema/sharepoint-rights-register-schema.xlsx  Column-level design for 13 lists, plus permissions, flows, and views. Start at README, then Lists.
- schema/sharepoint-rights-register-schema.json  The same design as data, for provisioning scripts (PnP, Graph).
- schema/build_schema.py                         Regenerates both files. Edit the structure here, not the outputs.
- resolve_effective_rights.py                    Turns exported lists into effective rights and coverage.
- sample_data/                                   Fixtures that match the export headers. legal_confirmed is "Yes" in the samples so the tests run. Real rows must be confirmed by Legal.

Run the resolver
    python resolve_effective_rights.py --in sample_data --out out --as-of 2026-10-17
Outputs: effective_rights.csv, coverage_summary.csv, issues.csv. Exit code 1 only when there are errors.
Optional inputs: volumes.csv (party volume per dataset) and pair_volumes.csv (agency x supplier volume, for joint coverage).

Export headers the resolver expects: use the sample_data headers. Lookup columns export display values, so each list keeps plain-text ID copies (profile_id, agreement_id, dataset_id).

Rules
1. No active, confirmed agreement in force on the as-of date: Unknown.
2. Profile term applies unless a dated exception overrides it. Exceptions can loosen or tighten. An unconfirmed exception: Unknown. Several exceptions: most restrictive.
3. The dataset ceiling caps the result. Missing or unconfirmed: Unknown.
4. Derived datasets: Inherit takes the most restrictive parent result. Transform uses parents only to decide inclusion (derivative_data_product), then the dataset's own ceiling.
5. Only Legal sets legal_confirmed. Anything other than Yes is treated as not confirmed.
Order, most restrictive first: Prohibited, Unknown, Conditional, Granted. Eligible = Granted or Conditional.
