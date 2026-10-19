#!/usr/bin/env python3
"""Resolve effective data rights per party (agency or supplier) from exports of the SharePoint register lists.

Usage:
  python resolve_effective_rights.py --in EXPORT_DIR --out OUTPUT_DIR [--as-of YYYY-MM-DD]

Input CSVs in EXPORT_DIR (header row required; extra columns are ignored):
  parties.csv               party_id, name, party_type (Supplier|Agency), status (Active|Inactive)
  agreements.csv            agreement_id, party_id, profile_id, status, effective_date, expiry_date, legal_confirmed
  rights_profiles.csv       profile_id, status (Approved|Draft|Retired)
  profile_terms.csv         profile_id, use_right, status, conditions, legal_confirmed
  agreement_exceptions.csv  exception_id, agreement_id, dataset_id (blank = all datasets), use_right, status,
                            effective_date, expiry_date, legal_confirmed
  datasets.csv              dataset_id, source_type, parent_dataset_ids (semicolon separated),
                            derivation_mode (Inherit|Transform, for derived datasets; blank = Inherit),
                            contributor_party_type (Supplier|Agency, for non-derived datasets), status
  dataset_use_rights.csv    dataset_id, use_right, status, legal_confirmed   (dataset-level ceiling)
Optional:
  volumes.csv               dataset_id, party_id, volume        (who actually contributes, and how much)
  pair_volumes.csv          dataset_id, agency_party_id, supplier_party_id, volume   (joint volume for derived datasets)

Resolution rule for one dataset, party, and use right:
  1. Find the party's Active agreement in force on the as-of date. None found: Unknown.
  2. The agreement and its profile must be confirmed and approved, else Unknown.
  3. Contract term = the profile term, unless a dated exception for the agreement (this dataset or all datasets)
     overrides it. An exception can loosen or tighten. An unconfirmed exception makes the term Unknown.
     If several exceptions apply, the most restrictive wins.
  4. The dataset-level ceiling caps the contract term. A missing or unconfirmed ceiling is Unknown.
  5. Derived datasets (datasets.csv column derivation_mode):
     Inherit (default): the result is the most restrictive of the effective rights, for the same use right, in each
       parent the party contributes to, capped by the derived dataset's own ceiling. Use for joins and copies.
     Transform: for aggregated or anonymized products. A party's data may be included only if its effective
       derivative_data_product right in each parent it contributes to is Granted or Conditional. The rights on the
       output itself come from the derived dataset's own ceiling, which Legal sets for the product. The result is the
       more restrictive of the two.
  Ranking, most restrictive first: Prohibited, Unknown, Conditional, Granted. Anything not Yes for
  legal_confirmed counts as unconfirmed. Eligible means Granted or Conditional.

Outputs in OUTPUT_DIR: effective_rights.csv, coverage_summary.csv, issues.csv
"""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

RANK = {"Prohibited": 0, "Unknown": 1, "Conditional": 2, "Granted": 3}
RIGHTS = [
    "internal_use", "internal_analytics_shared_outputs", "display_to_third_parties",
    "redistribution_resale", "derivative_data_product", "ai_training",
    "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
]
ELIGIBLE = {"Granted", "Conditional"}
EXPIRY_WARNING_DAYS = 90


def read_csv(folder, name, required, optional=False):
    path = Path(folder) / name
    if not path.exists():
        if optional:
            return []
        sys.exit(f"Missing input file: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = [c.strip() for c in (reader.fieldnames or [])]
        missing = [c for c in required if c not in cols]
        if missing:
            sys.exit(f"{name} is missing columns: {', '.join(missing)}")
        return [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in reader]


def to_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def in_range(start, end, day):
    return (start is None or start <= day) and (end is None or day <= end)


def norm_status(value):
    return value if value in RANK else "Unknown"


def worst(candidates):
    """candidates: list of (status, label). Returns the most restrictive; first listed wins ties."""
    best = candidates[0]
    for c in candidates[1:]:
        if RANK[c[0]] < RANK[best[0]]:
            best = c
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="indir", required=True)
    ap.add_argument("--out", dest="outdir", required=True)
    ap.add_argument("--as-of", dest="as_of", default=None)
    args = ap.parse_args()
    as_of = to_date(args.as_of) if args.as_of else date.today()
    if as_of is None:
        sys.exit("--as-of must be YYYY-MM-DD")

    parties = {r["party_id"]: r for r in read_csv(args.indir, "parties.csv", ["party_id", "party_type", "status"])}
    agreements = read_csv(args.indir, "agreements.csv", ["agreement_id", "party_id", "profile_id", "status", "effective_date", "expiry_date", "legal_confirmed"])
    profiles = {r["profile_id"]: r for r in read_csv(args.indir, "rights_profiles.csv", ["profile_id", "status"])}
    terms = {(r["profile_id"], r["use_right"]): r for r in read_csv(args.indir, "profile_terms.csv", ["profile_id", "use_right", "status", "legal_confirmed"])}
    exceptions = read_csv(args.indir, "agreement_exceptions.csv", ["exception_id", "agreement_id", "dataset_id", "use_right", "status", "legal_confirmed"])
    datasets = {r["dataset_id"]: r for r in read_csv(args.indir, "datasets.csv", ["dataset_id", "parent_dataset_ids", "contributor_party_type"])}
    ceilings = {(r["dataset_id"], r["use_right"]): r for r in read_csv(args.indir, "dataset_use_rights.csv", ["dataset_id", "use_right", "status", "legal_confirmed"])}
    volumes = read_csv(args.indir, "volumes.csv", ["dataset_id", "party_id", "volume"], optional=True)
    pair_volumes = read_csv(args.indir, "pair_volumes.csv", ["dataset_id", "agency_party_id", "supplier_party_id", "volume"], optional=True)

    datasets = {k: v for k, v in datasets.items() if v.get("status", "") not in ("Rejected", "Retired")}
    issues = []

    agreements_by_party = defaultdict(list)
    for a in agreements:
        agreements_by_party[a["party_id"]].append(a)
        if a["party_id"] not in parties:
            issues.append(("Error", "agreement", a["agreement_id"], f"party {a['party_id']} is not in parties.csv"))
    exceptions_by_agreement = defaultdict(list)
    for e in exceptions:
        exceptions_by_agreement[e["agreement_id"]].append(e)

    # ------------------------------------------------------------------ agreement lookup
    agreement_cache = {}

    def active_agreement(party_id):
        if party_id in agreement_cache:
            return agreement_cache[party_id]
        mine = agreements_by_party.get(party_id, [])
        live = [a for a in mine if a["status"] == "Active" and in_range(to_date(a["effective_date"]), to_date(a["expiry_date"]), as_of)]
        if live:
            live.sort(key=lambda a: to_date(a["effective_date"]) or date.min, reverse=True)
            result = (live[0], None)
        elif not mine:
            result = (None, "no agreement on file")
        elif any(a["status"] == "Active" and to_date(a["expiry_date"]) and to_date(a["expiry_date"]) < as_of for a in mine):
            result = (None, "agreement expired")
        else:
            result = (None, "no active agreement")
        agreement_cache[party_id] = result
        return result

    # ------------------------------------------------------------------ contributors
    contributor_cache = {}

    def contributors(ds, seen=()):
        if ds in contributor_cache:
            return contributor_cache[ds]
        if ds in seen:
            return set()
        d = datasets[ds]
        parents = [p for p in d["parent_dataset_ids"].split(";") if p.strip()]
        if parents:
            result = set()
            for p in parents:
                p = p.strip()
                if p in datasets:
                    result |= contributors(p, seen + (ds,))
                else:
                    issues.append(("Error", "dataset", ds, f"parent {p} is not in datasets.csv"))
        else:
            listed = {v["party_id"] for v in volumes if v["dataset_id"] == ds}
            if listed:
                result = listed
            else:
                ptype = d.get("contributor_party_type", "")
                result = {pid for pid, p in parties.items() if p["party_type"] == ptype and p["status"] == "Active"}
        contributor_cache[ds] = result
        return result

    # ------------------------------------------------------------------ resolution
    def ceiling(ds, right):
        c = ceilings.get((ds, right))
        if c is None:
            return ("Unknown", "dataset ceiling missing")
        if c["legal_confirmed"] != "Yes":
            return ("Unknown", "dataset ceiling not confirmed")
        return (norm_status(c["status"]), "dataset ceiling")

    def contract_term(ds, party_id, right):
        """Returns (status, label, agreement_id)."""
        ag, why = active_agreement(party_id)
        if ag is None:
            return ("Unknown", why, "")
        aid = ag["agreement_id"]
        if ag["legal_confirmed"] != "Yes":
            return ("Unknown", "agreement not confirmed", aid)
        prof = profiles.get(ag["profile_id"])
        if prof is None:
            return ("Unknown", "profile not found", aid)
        if prof["status"] != "Approved":
            return ("Unknown", "profile not approved", aid)
        # exceptions override the profile term
        applicable = []
        for e in exceptions_by_agreement.get(aid, []):
            if e["use_right"] != right or e["dataset_id"] not in ("", ds):
                continue
            if not in_range(to_date(e.get("effective_date")), to_date(e.get("expiry_date")), as_of):
                continue
            if e["legal_confirmed"] != "Yes":
                applicable.append(("Unknown", f"unconfirmed exception {e['exception_id']}"))
            else:
                applicable.append((norm_status(e["status"]), f"exception {e['exception_id']}"))
        if applicable:
            status, label = worst(applicable)
            return (status, label, aid)
        term = terms.get((ag["profile_id"], right))
        if term is None:
            return ("Unknown", "profile has no term", aid)
        if term["legal_confirmed"] != "Yes":
            return ("Unknown", "profile term not confirmed", aid)
        return (norm_status(term["status"]), f"profile {ag['profile_id']}", aid)

    effective_cache = {}

    def effective(ds, party_id, right, seen=()):
        key = (ds, party_id, right)
        if key in effective_cache:
            return effective_cache[key]
        if ds in seen:
            return ("Unknown", "cycle in dataset parents", "")
        d = datasets[ds]
        parents = [p.strip() for p in d["parent_dataset_ids"].split(";") if p.strip() and p.strip() in datasets]
        own_ceiling = ceiling(ds, right)
        if parents:
            transform = d.get("derivation_mode", "") == "Transform"
            # Transform: parents only decide whether this party's data may be included (derivative right).
            parent_right = "derivative_data_product" if transform else right
            cands = []
            for p in parents:
                if party_id in contributors(p):
                    st, label, aid = effective(p, party_id, parent_right, seen + (ds,))
                    prefix = "inclusion via " if transform else ""
                    cands.append((st, f"{prefix}{p}: {label}", aid))
            if not cands:
                result = ("Unknown", "party contributes to no parent", "")
            else:
                best = worst([(c[0], c[1]) for c in cands])
                aid = next((c[2] for c in cands if c[0] == best[0] and c[1] == best[1]), "")
                result = (best[0], best[1], aid)
            if RANK[own_ceiling[0]] < RANK[result[0]]:
                result = (own_ceiling[0], own_ceiling[1], result[2])
        else:
            st, label, aid = contract_term(ds, party_id, right)
            result = (st, label, aid)
            if RANK[own_ceiling[0]] < RANK[st]:
                result = (own_ceiling[0], own_ceiling[1], aid)
        effective_cache[key] = result
        return result

    # ------------------------------------------------------------------ outputs
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for ds in sorted(datasets):
        for pid in sorted(contributors(ds)):
            ptype = parties.get(pid, {}).get("party_type", "")
            for right in RIGHTS:
                st, label, aid = effective(ds, pid, right)
                rows.append({
                    "dataset_id": ds, "party_id": pid, "party_type": ptype, "use_right": right,
                    "effective_status": st, "eligible": "Yes" if st in ELIGIBLE else "No",
                    "basis": label, "agreement_id": aid, "as_of_date": as_of.isoformat(),
                })
    with open(outdir / "effective_rights.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["dataset_id"])
        w.writeheader()
        w.writerows(rows)

    # coverage
    vol = defaultdict(float)
    for v in volumes:
        try:
            vol[(v["dataset_id"], v["party_id"])] += float(v["volume"])
        except ValueError:
            issues.append(("Error", "volumes", v["dataset_id"], f"volume for {v['party_id']} is not a number"))
    eligible_set = {(r["dataset_id"], r["party_id"], r["use_right"]) for r in rows if r["eligible"] == "Yes"}
    cov = []
    for ds in sorted(datasets):
        for right in RIGHTS:
            for ptype in ("Agency", "Supplier"):
                members = [p for p in sorted(contributors(ds)) if parties.get(p, {}).get("party_type") == ptype]
                if not members:
                    continue
                ok = [p for p in members if (ds, p, right) in eligible_set]
                total_v = sum(vol.get((ds, p), 0) for p in members)
                ok_v = sum(vol.get((ds, p), 0) for p in ok)
                cov.append({
                    "dataset_id": ds, "use_right": right, "basis": f"{ptype} parties",
                    "total": len(members), "eligible": len(ok),
                    "pct_by_party": f"{100 * len(ok) / len(members):.1f}",
                    "pct_by_volume": f"{100 * ok_v / total_v:.1f}" if total_v else "",
                })
            pairs = [p for p in pair_volumes if p["dataset_id"] == ds]
            if pairs:
                total_v = ok_v = 0.0
                ok_n = 0
                for p in pairs:
                    try:
                        amount = float(p["volume"])
                    except ValueError:
                        continue
                    total_v += amount
                    if (ds, p["agency_party_id"], right) in eligible_set and (ds, p["supplier_party_id"], right) in eligible_set:
                        ok_v += amount
                        ok_n += 1
                cov.append({
                    "dataset_id": ds, "use_right": right, "basis": "Joint agency and supplier volume",
                    "total": len(pairs), "eligible": ok_n,
                    "pct_by_party": f"{100 * ok_n / len(pairs):.1f}",
                    "pct_by_volume": f"{100 * ok_v / total_v:.1f}" if total_v else "",
                })
    with open(outdir / "coverage_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset_id", "use_right", "basis", "total", "eligible", "pct_by_party", "pct_by_volume"])
        w.writeheader()
        w.writerows(cov)

    # issues
    soon = as_of + timedelta(days=EXPIRY_WARNING_DAYS)
    for a in agreements:
        exp = to_date(a["expiry_date"])
        if a["status"] == "Active" and exp and as_of <= exp <= soon:
            issues.append(("Warning", "agreement", a["agreement_id"], f"expires {exp.isoformat()} (within {EXPIRY_WARNING_DAYS} days)"))
        if a["status"] == "Active" and exp and exp < as_of:
            issues.append(("Warning", "agreement", a["agreement_id"], f"expired {exp.isoformat()} but still marked Active; set status to Expired"))
        if a["status"] == "Active" and a["legal_confirmed"] != "Yes":
            issues.append(("Warning", "agreement", a["agreement_id"], "not confirmed by Legal; party rights are Unknown"))
    for pid, p in parties.items():
        if p["status"] == "Active":
            ag, why = active_agreement(pid)
            if ag is None:
                issues.append(("Warning", "party", pid, f"{why}; all rights Unknown"))
    for e in exceptions:
        if e["legal_confirmed"] != "Yes":
            issues.append(("Warning", "exception", e["exception_id"], "not confirmed by Legal; treated as Unknown"))
    for (pid_, right), t in terms.items():
        if t["legal_confirmed"] != "Yes":
            issues.append(("Warning", "profile term", f"{pid_} / {right}", "not confirmed by Legal; treated as Unknown"))
    for (ds, right), c in ceilings.items():
        if ds in datasets and c["legal_confirmed"] != "Yes":
            issues.append(("Warning", "dataset ceiling", f"{ds} / {right}", "not confirmed by Legal; treated as Unknown"))
    for ds in datasets:
        for right in RIGHTS:
            if (ds, right) not in ceilings:
                issues.append(("Warning", "dataset ceiling", f"{ds} / {right}", "missing; treated as Unknown"))
    with open(outdir / "issues.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["severity", "type", "reference", "message"])
        w.writerows(issues)

    errors = sum(1 for i in issues if i[0] == "Error")
    print(f"As of {as_of.isoformat()}: {len(rows)} effective rights rows, {len(cov)} coverage rows, "
          f"{errors} errors, {len(issues) - errors} warnings. Output in {outdir}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
